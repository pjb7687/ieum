import json
import base64
import uuid

from datetime import datetime
from typing import List

from ninja import NinjaAPI
from ninja.security import django_auth

from django.middleware.csrf import get_token
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.template import Template, Context

from django.conf import settings

from main.models import Event, EmailTemplate, Attendee, CustomQuestion, CustomAnswer, Abstract, AbstractVote, OnSiteAttendee
from main.schema import *

from .tasks import send_mail

api = NinjaAPI(csrf=True, auth=django_auth)

def ensure_staff(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        user = request.user
        if not user.is_staff:
            return api.create_response(
                request,
                {"code": "permission_denied", "message": "Permission denied"},
                status=403,
            )
        return func(*args, **kwargs)
    return wrapper

def ensure_event_staff(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        event_id = kwargs["event_id"]
        user = request.user
        if not (user.is_staff or user in Event.objects.get(id=event_id).admins.all()):
            return api.create_response(
                request,
                {"code": "permission_denied", "message": "Permission denied"},
                status=403,
            )
        return func(*args, **kwargs)
    return wrapper

@api.get("/me", response=UserSchema)
def get_user(request):
    return request.user

@api.post("/me", response=UserSchema)
def update_user(request):
    data = json.loads(request.body)
    # check if mandatory fields are filled
    if not data["first_name"] or not data["last_name"] or not data["nationality"] or not data["institute"]:
        return api.create_response(
            request,
            {"errors": [{"message": "Required fields are not filled", "code": "invalid"}]},
            status=400,
        )
    user = request.user
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.middle_initial = data["middle_initial"]
    user.nationality = data["nationality"]
    user.job_title = data["job_title"]
    user.department = data["department"]
    user.institute = data["institute"]
    user.disability = data["disability"]
    user.dietary = data["dietary"]
    user.save()
    return user

@api.get("/csrftoken", auth=None)
def get_csrf_token(request):
    token = get_token(request)
    return {"csrftoken": token}

@ensure_staff
@api.get("/admin/events", response=List[EventAdminSchema])
def get_admin_events(request):
    events = Event.objects.all()
    return events

@api.get("/events", response=List[EventSchema], auth=None)
def get_events(request):
    events = Event.objects.all()
    return events

@ensure_staff
@api.post("/admin/event/add", response=MessageSchema)
def add_event(request):
    data = json.loads(request.body)
    if not data["name"] or not data["link_info"] or not data["organizers"] or not data["venue"] or not data["start_date"] or not data["end_date"] or not data["capacity"]:
        return api.create_response(
            request,
            {"code": "missing_fields", "message": "Please fill all required fields."},
            status=400,
        )
    email_template_registration = EmailTemplate.objects.create(
        subject=settings.ACCOUNT_EMAIL_SUBJECT_PREFIX+"Registration Confirmation for {{ event.name }}",
        body="Dear {{ attendee.first_name }},\n\n"
            "Thank you for registering for {{ event.name }}! Your registration has been confirmed.\n\n"
            "Event Details:\n"
            " - Dates: {{ event.start_date|date:'F d, Y' }} - {{ event.end_date|date:'F d, Y' }}\n"
            " - Venue: {{ event.venue }}\n"
            " - Event Link: {{ event.link_info }}\n\n"
            "If you have any questions, please contact us at: " + settings.EMAIL_FROM + "\n\n"
            "We look forward to seeing you at the event!\n\n"
            "Warm regards,\n"
            "{{ event.organizers }}"
    )
    email_template_abstract_submission = EmailTemplate.objects.create(
        subject=settings.ACCOUNT_EMAIL_SUBJECT_PREFIX+"Abstract Submission Confirmation for {{ event.name }}",
        body="Dear {{ attendee.first_name }},\n\n"
            "Thank you for submitting your abstract for {{ event.name }}! Your submission has been confirmed.\n\n"
            "Abstract Details:\n"
            " - Title: {{ abstract.title }}\n"
            " - Presentation Type: {% if abstract.is_oral %}Oral Presentation{% else %}Poster Presentation{% endif %}\n\n"
            "If you need to make any changes to your submission, please contact us at: " + settings.EMAIL_FROM + "\n\n"
            "Thank you for your contribution to {{ event.name }}. We appreciate your participation.\n\n"
            "Warm regards,\n"
            "{{ event.organizers }}"
    )
    event = Event.objects.create(
        name=data["name"],
        link_info=data["link_info"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        venue=data["venue"],
        organizers=data["organizers"],
        registration_deadline=data["registration_deadline"] if data["registration_deadline"] else None,
        capacity=data["capacity"],
        accepts_abstract=data["accepts_abstract"] == "true",
        email_template_registration=email_template_registration,
        email_template_abstract_submission=email_template_abstract_submission,
    )

    if data["accepts_abstract"] == "true":
        event.abstract_deadline = data["abstract_deadline"]
        event.capacity_abstract = data["capacity_abstract"]
        event.max_votes = data["max_votes"]
        event.save()

    return {"code": "success", "message": "Event added."}

@api.get("/event/{event_id}", response=EventSchema, auth=None)
def get_event(request, event_id: int):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Event not found."},
            status=404,
        )
    return event

@api.get("/admin/event/{event_id}", response=EventAdminSchema, auth=None)
def get_admin_event(request, event_id: int):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return api.create_response(
            request,
            {},
            status=404,
        )
    return event

@ensure_event_staff
@api.post("/event/{event_id}/update", response=MessageSchema)
def update_event(request, event_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)
    event.name = data["name"]
    event.link_info = data["link_info"]
    event.start_date = data["start_date"]
    event.end_date = data["end_date"]
    event.venue = data["venue"]
    event.organizers = data["organizers"]
    event.registration_deadline = data["registration_deadline"] if data["registration_deadline"] else None
    event.capacity = data["capacity"]
    event.accepts_abstract = data["accepts_abstract"] == "true"
    event.save()
    if event.accepts_abstract:
        event.abstract_deadline = data["abstract_deadline"] if data["abstract_deadline"] else None
        event.capacity_abstract = data["capacity_abstract"]
        event.max_votes = data["max_votes"]
        event.save()

    return {"code": "success", "message": "Event updated."}

@ensure_staff
@api.post("/admin/event/{event_id}/delete", response=MessageSchema)
def delete_event(request, event_id: int):
    try:
        Event.objects.get(id=event_id).delete()
    except Event.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Event not found."},
            status=404,
        )
    return {"code": "success", "message": "Event deleted."}

@ensure_event_staff
@api.post("/event/{event_id}/emailtemplates", response=MessageSchema)
def update_event_emailtemplates(request, event_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)
    event.email_template_registration.subject = data["email_template_registration_subject"]
    event.email_template_registration.body = data["email_template_registration_body"]
    event.email_template_registration.save()
    event.email_template_abstract_submission.subject = data["email_template_abstract_submission_subject"]
    event.email_template_abstract_submission.body = data["email_template_abstract_submission_body"]
    event.email_template_abstract_submission.save()
    return {"code": "success", "message": "Email templates updated."}

@api.get("/event/{event_id}/registered", response=RegistrationStatusSchema)
def check_registration_status(request, event_id: int):
    user = request.user
    registered = Event.objects.get(id=event_id).attendees.filter(user__id=user.id).exists()
    return {"registered": registered}

@api.get("/event/{event_id}/questions", response=List[QuestionSchema])
def get_event_questions(request, event_id: int):
    event = Event.objects.get(id=event_id)
    questions = event.custom_questions.all()
    return questions

@ensure_event_staff
@api.post("/event/{event_id}/questions", response=MessageSchema)
def update_event_questions(request, event_id: int):
    event = Event.objects.get(id=event_id)
    data = json.loads(request.body)
    for q in event.custom_questions.all():
        if not any(q.id == q2.get("id") for q2 in data["questions"]):
            q.delete()
    for q in data["questions"]:
        if q.get("id") == -1:
            cq = CustomQuestion.objects.create(
                event=event,
                question=q["question"]
            )
        else:
            cq = CustomQuestion.objects.get(id=q["id"])
            cq.question = q["question"]
            cq.save()
            for ca in CustomAnswer.objects.filter(reference=cq):
                ca.question = q["question"]["question"]
                ca.save()
    return {"code": "success", "message": "Questions updated."}

@ensure_event_staff
@api.get("/event/{event_id}/stats", response=StatsSchema)
def get_event_stats(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return {
        "registered": event.attendees.count(),
        "abstracts": event.abstracts.count(),
    }

@ensure_event_staff
@api.get("/event/{event_id}/attendees", response=List[AttendeeSchema])
def get_event_attendees(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.attendees.all()

@ensure_event_staff
@api.post("/event/{event_id}/attendee/{attendee_id}/update", response=MessageSchema)
def update_attendee(request, event_id: int, attendee_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)
    attendee = Attendee.objects.get(id=attendee_id, event=event)
    attendee.first_name = data["first_name"]
    attendee.middle_initial = data["middle_initial"]
    attendee.last_name = data["last_name"]
    attendee.nationality = data["nationality"]
    attendee.institute = data["institute"]
    attendee.department = data["department"]
    attendee.job_title = data["job_title"]
    attendee.disability = data["disability"]
    attendee.dietary = data["dietary"]
    attendee.save()
    return {"code": "success", "message": "Successfully updated."}

@ensure_event_staff
@api.post("/event/{event_id}/attendee/{attendee_id}/answers", response=MessageSchema)
def update_event_answers(request, event_id: int, attendee_id: int):
    data = json.loads(request.body)
    answers = data.get("answers", [])
    references = [a["reference_id"] for a in answers if a["reference_id"] is not None]
    if len(references) != len(set(references)):
        return api.create_response(
            request,
            {"code": "duplicated_references", "message": "Duplicated references found."},
            status=400,
        )
    event = Event.objects.get(id=event_id)
    attendee = Attendee.objects.get(id=attendee_id, event=event)
    custom_answer = CustomAnswer.objects.filter(attendee=attendee)
    custom_answer.delete()
    for a in answers:
        reference_question = CustomQuestion.objects.get(id=a["reference_id"]) if not (a["reference_id"] == -1 or a["reference_id"] is None) else None
        CustomAnswer.objects.create(
            reference=reference_question,
            attendee=attendee,
            question=reference_question.question["question"] if reference_question else a["question"],
            answer=a["answer"]
        )
    return {"code": "success", "message": "Answers updated."}

@api.post("/event/{event_id}/register", response=MessageSchema)
def register_event(request, event_id: int):
    # get the deadline for registration
    user = request.user
    event = Event.objects.get(id=event_id)
    if event.registration_deadline is not None and datetime.now().date() > event.registration_deadline:
            return api.create_response(
                request,
                {"code": "deadline_passed", "message": "Sorry, registration deadline has passed."},
                status=400,
            )
    if event.capacity > 0 and event.capacity <= event.attendees.count():
        return api.create_response(
            request,
            {"code": "event_full", "message": "Sorry, event is full."},
            status=400,
        )

    if event.attendees.filter(user=user).exists():
        return api.create_response(
            request,
            {"code": "already_registered", "message": "You are already registered."},
            status=400,
        )
    
    data = json.loads(request.body)
    for q in event.custom_questions.all():
        if q.question["type"] == "select":
            for oidx, option in enumerate(q.question["options"]):
                if not data.get(f"{q.id}"):
                    return api.create_response(
                        request,
                        {"code": "missing_answer", "message": "Please select an option for the question: "+ q.question['question']},
                        status=400,
                    )
    
    attendee = Attendee.objects.create(
        user=user,
        event=event,
        first_name=data["first_name"],
        middle_initial=data["middle_initial"],
        last_name=data["last_name"],
        nationality=data["nationality"],
        institute=data["institute"],
        department=data["department"],
        job_title=data["job_title"],
        disability=data["disability"],
        dietary=data["dietary"]
    )

    for q in event.custom_questions.all():
        if q.question["type"] == "checkbox":
            answer = '\n'.join([f"- {option}: {data.get(f"{q.id}_{oidx}")}" for oidx, option in enumerate(q.question["options"])])
        else:
            answer = data.get(f"{q.id}")
        CustomAnswer.objects.create(
            reference=q,
            attendee=attendee,
            question=q.question["question"],
            answer=answer
        )

    event.attendees.add(attendee)

    send_mail.delay(
        Template(event.email_template_registration.subject).render(Context({"event": event, "attendee": attendee})),
        Template(event.email_template_registration.body).render(Context({"event": event, "attendee": attendee})),
        user.email
    )

    return {"code": "success", "message": "Successfully registered."}

@ensure_event_staff
@api.post("/event/{event_id}/attendee/{attendee_id}/deregister", response=MessageSchema)
def deregister_event(request, event_id: int, attendee_id: int):
    event = Event.objects.get(id=event_id)
    Attendee.objects.get(id=attendee_id, event=event).delete()
    return {"code": "success", "message": "Successfully deregistered!"}

@api.post("/event/{event_id}/abstract", response=MessageSchema)
def submit_abstract(request, event_id: int):
    event = Event.objects.get(id=event_id)
    if not event.accepts_abstract:
        return api.create_response(
            request,
            {"code": "not_accepted", "message": "This event does not accept abstracts."},
            status=400,
        )

    attendee = Attendee.objects.get(user=request.user, event=event)
    if attendee.abstracts.filter(event_id=event_id).exists():
        return api.create_response(
            request,
            {"code": "already_submitted", "message": "You have already submitted an abstract."},
            status=400,
        )

    data = json.loads(request.body)
    if event.abstract_deadline is not None and datetime.now().date() > event.abstract_deadline:
        return api.create_response(
            request,
            {"code": "deadline_passed", "message": "Sorry, abstract submission deadline has passed."},
            status=400,
        )
    
    if event.capacity_abstract > 0 and event.capacity_abstract <= event.abstracts.count():
        return api.create_response(
            request,
            {"code": "event_full", "message": "Sorry, abstract submission limit reached."},
            status=400,
        )

    # create the abstract with the post json data
    data = json.loads(request.body)
    file_name = data["file_name"]
    file_content = base64.b64decode(data["file_content"].split(",")[1])
    file_path = f"abstracts/{uuid.uuid4()}/{file_name}"
    file = ContentFile(file_content)
    default_storage.save(file_path, file)

    Abstract.objects.create(
        attendee=attendee,
        event=event,
        title=data["title"],
        is_oral=data["is_oral"] == "true",
        file_path=file_path,
    )

    send_mail.delay(
        Template(event.email_template_abstract_submission.subject).render(Context({"event": event, "abstract": Abstract.objects.get(attendee=attendee, event=event)})),
        Template(event.email_template_abstract_submission.body).render(Context({"attendee": attendee, "event": event, "abstract": Abstract.objects.get(attendee=attendee, event=event)})),
        attendee.user.email
    )

    return {"code": "success", "message": "Successfully submitted!"}

@ensure_event_staff
@api.get("/event/{event_id}/speakers", response=List[SpeakerSchema])
def get_speakers(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.speakers.all()

@ensure_event_staff
@api.post("/event/{event_id}/speaker/add", response=MessageSchema)
def add_speaker(request, event_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)

    if not data.get("name") or not data.get("email") or not data.get("affiliation") or not data.get("is_domestic") or not data.get("type"):
        return api.create_response(
            request,
            {"code": "missing_fields", "message": "Please fill all fields."},
            status=400,
        )

    speaker = event.speakers.create(
        name=data["name"],
        email=data["email"],
        affiliation=data["affiliation"],
        is_domestic=data["is_domestic"],
        type=data["type"],
    )
    return {"code": "success", "message": "Speaker added."}

@ensure_event_staff
@api.post("/event/{event_id}/speaker/{speaker_id}/update", response=MessageSchema)
def update_speaker(request, event_id: int, speaker_id: int):
    event = Event.objects.get(id=event_id)
    speaker = event.speakers.get(id=speaker_id)
    data = json.loads(request.body)
    speaker.name = data["name"]
    speaker.email = data["email"]
    speaker.affiliation = data["affiliation"]
    speaker.is_domestic = data["is_domestic"]
    speaker.type = data["type"]
    speaker.save()
    return {"code": "success", "message": "Speaker updated."}

@ensure_event_staff
@api.post("/event/{event_id}/speaker/{speaker_id}/delete", response=MessageSchema)
def delete_speaker(request, event_id: int, speaker_id: int):
    event = Event.objects.get(id=event_id)
    speaker = event.speakers.get(id=speaker_id)
    speaker.delete()
    return {"code": "success", "message": "Speaker deleted."}

@ensure_event_staff
@api.post("/event/{event_id}/send_emails", response=MessageSchema)
def send_emails(request, event_id: int):
    data = json.loads(request.body)
    receipents = data["to"].split("; ")
    for receipent in receipents:
        send_mail.delay(
            data['subject'],
            data['body'],
            receipent
        )
    return {"code": "success", "message": "Emails sent."}

@ensure_event_staff
@api.get("/event/{event_id}/reviewers", response=List[AttendeeSchema])
def get_reviewers(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.reviewers.all()

@ensure_event_staff
@api.post("/event/{event_id}/reviewer/add", response=MessageSchema)
def add_reviewer(request, event_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)
    attendee = Attendee.objects.get(event=event, id=data["id"])
    # check if the user is already a reviewer
    if attendee in event.reviewers.all():
        return api.create_response(
            request,
            {"code": "already_reviewer", "message": "User is already a reviewer."},
            status=400,
        )
    event.reviewers.add(attendee)
    AbstractVote.objects.create(reviewer=attendee)
    return {"code": "success", "message": "Reviewer added."}

@ensure_event_staff
@api.post("/event/{event_id}/reviewer/{reviewer_id}/delete", response=MessageSchema)
def delete_reviewer(request, event_id: int, reviewer_id: int):
    event = Event.objects.get(id=event_id)
    attendee = Attendee.objects.get(event=event, id=reviewer_id)
    event.reviewers.remove(attendee)
    AbstractVote.objects.get(reviewer=attendee).delete()
    return {"code": "success", "message": "Reviewer deleted."}

@api.get("/event/{event_id}/abstracts", response=List[AbstractShortSchema])
def get_abstracts(request, event_id: int):
    user = request.user
    if not (user.is_staff or
            user in Event.objects.get(id=event_id).admins.all() or
            user in Event.objects.get(id=event_id).reviewers.all()):
        return api.create_response(
            request,
            {"code": "permission_denied", "message": "Permission denied"},
            status=403,
        )
    event = Event.objects.get(id=event_id)
    abstracts = event.abstracts.all()
    return abstracts

@api.get("/event/{event_id}/abstract", response=AbstractSchema)
def get_user_abstract(request, event_id: int):
    user = request.user
    event = Event.objects.get(id=event_id)
    attendee = Attendee.objects.get(user=user, event=event)
    try:
        abstract = attendee.abstracts.get(event_id=event_id)
    except Abstract.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Abstract not found."},
            status=404,
        )
    return abstract

@api.get("/event/{event_id}/abstract/{abstract_id}", response=AbstractSchema)
def get_abstract(request, event_id: int, abstract_id: int):
    user = request.user
    if not (user.is_staff or
            user in Event.objects.get(id=event_id).admins.all() or
            user in Event.objects.get(id=event_id).reviewers.all()):
        return api.create_response(
            request,
            {"code": "permission_denied", "message": "Permission denied"},
            status=403,
        )
    event = Event.objects.get(id=event_id)
    abstract = event.abstracts.get(id=abstract_id)
    return abstract

@ensure_event_staff
@api.post("/event/{event_id}/abstract/{abstract_id}/update", response=MessageSchema)
def update_abstract(request, event_id: int, abstract_id: int):
    event = Event.objects.get(id=event_id)
    abstract = event.abstracts.get(id=abstract_id)
    data = json.loads(request.body)
    abstract.title = data["title"]
    abstract.is_oral = data["is_oral"]
    abstract.is_accepted = data["is_accepted"]
    abstract.save()
    return {"code": "success", "message": "Abstract updated."}

@ensure_event_staff
@api.post("/event/{event_id}/abstract/{abstract_id}/delete", response=MessageSchema)
def delete_abstract(request, event_id: int, abstract_id: int):
    event = Event.objects.get(id=event_id)
    abstract = event.abstracts.get(id=abstract_id)
    abstract.delete()
    return {"code": "success", "message": "Abstract deleted."}

@api.get("/event/{event_id}/reviewer", response=bool)
def is_reviewer(request, event_id: int):
    event = Event.objects.get(id=event_id)
    if not event.accepts_abstract:
        return False # Event does not accept abstracts
    user = request.user
    try:
        attendee = Attendee.objects.get(user=user, event_id=event_id)
    except Attendee.DoesNotExist:
        return False # User is not registered to the event
    return attendee in Event.objects.get(id=event_id).reviewers.all()

@api.get("/event/{event_id}/reviewer/vote", response=AbstractVoteSchema)
def get_reviewer_votes(request, event_id: int):
    event = Event.objects.get(id=event_id)
    if not event.accepts_abstract:
        return api.create_response(
            request,
            {"code": "not_accepted", "message": "This event does not accept abstracts."},
            status=400,
        )
    if event.abstract_deadline is not None and datetime.now().date() < event.abstract_deadline:
        return api.create_response(
            request,
            {"code": "deadline_not_passed", "message": "Abstract submission deadline has not passed."},
            status=400,
        )
    user = request.user
    if not (user.is_staff or
            user in Event.objects.get(id=event_id).admins.all() or
            user in Event.objects.get(id=event_id).reviewers.all()):
        return api.create_response(
            request,
            {"code": "permission_denied", "message": "Permission denied"},
            status=403,
        )
    event = Event.objects.get(id=event_id)
    reviewer = Attendee.objects.get(user=user, event=event)
    votes = AbstractVote.objects.get(reviewer=reviewer)
    return votes

@api.post("/event/{event_id}/reviewer/vote", response=MessageSchema)
def vote_abstract(request, event_id: int):
    event = Event.objects.get(id=event_id)
    if not event.accepts_abstract:
        return api.create_response(
            request,
            {"code": "not_accepted", "message": "This event does not accept abstracts."},
            status=400,
        )
    if event.abstract_deadline is not None and datetime.now().date() < event.abstract_deadline:
        return api.create_response(
            request,
            {"code": "deadline_not_passed", "message": "Abstract submission deadline has not passed."},
            status=400,
        )
    user = request.user
    event = Event.objects.get(id=event_id)
    reviewer = Attendee.objects.get(user=user, event=event)
    data = json.loads(request.body)
    vote = AbstractVote.objects.get(reviewer=reviewer)
    for abstract_id in data["voted_abstracts"]:
        vote.voted_abstracts.add(Abstract.objects.get(id=abstract_id))
    return {"code": "success", "message": "Votes submitted."}

@ensure_event_staff
@api.get("/users", response=List[UserSchema])
def get_users(request):
    return User.objects.all()

@ensure_event_staff
@api.get("/event/{event_id}/eventadmins", response=List[UserSchema])
def get_event_admins(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.admins.all()

@ensure_event_staff
@api.post("/event/{event_id}/eventadmin/add", response=MessageSchema)
def add_event_admin(request, event_id: int):
    data = json.loads(request.body)
    event = Event.objects.get(id=event_id)
    user = User.objects.get(id=data["id"])
    if user in event.admins.all():
        return api.create_response(
            request,
            {"code": "already_admin", "message": "User is already an admin."},
            status=400,
        )
    event.admins.add(user)
    return {"code": "success", "message": "Admin added."}

@ensure_event_staff
@api.post("/event/{event_id}/eventadmin/{admin_id}/delete", response=MessageSchema)
def delete_event_admin(request, event_id: int, admin_id: int):
    event = Event.objects.get(id=event_id)
    user = User.objects.get(id=admin_id)
    event.admins.remove(user)
    return {"code": "success", "message": "Admin deleted."}

@ensure_event_staff
@api.get("/event/{event_id}/email_templates", response=dict[str, EmailTemplateSchema])
def get_email_templates(request, event_id: int):
    event = Event.objects.get(id=event_id)
    rtn = {
        "registration": event.email_template_registration,
        "abstract": event.email_template_abstract_submission
    }
    return rtn

@api.post("/event/{event_id}/onsite")
def register_on_site(request, event_id: int):
    event = Event.objects.get(id=event_id)
    data = json.loads(request.body)
    oa = OnSiteAttendee.objects.create(
        event=event,
        first_name=data.get("first_name"),
        middle_initial=data.get("middle_initial"),
        last_name=data.get("last_name"),
        institute=data.get("institute"),
        job_title=data.get("job_title", "")
    )
    return {"code": "success", "message": "Successfully registered on-site.", "id": oa.id}

@ensure_event_staff
@api.get("/event/{event_id}/onsite", response=List[OnSiteAttendeeSchema])
def get_on_site_attendees(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.onsite_attendees.all()