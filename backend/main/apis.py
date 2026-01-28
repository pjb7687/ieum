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

from main.models import Event, EmailTemplate, Attendee, CustomQuestion, CustomAnswer, Abstract, AbstractVote, OnSiteAttendee, Institution
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
    # Clean up any verification keys for this user's email when they successfully authenticate
    from main.models import EmailVerificationKey
    EmailVerificationKey.objects.filter(email=request.user.email).delete()

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
    user.middle_initial = data.get("middle_initial", "")
    user.korean_name = data.get("korean_name", "")
    user.nationality = int(data["nationality"])
    user.job_title = data.get("job_title", "")
    user.department = data.get("department", "")

    # Assign institution by ID
    institute_id = data.get("institute")
    if institute_id:
        try:
            institution = Institution.objects.get(id=int(institute_id))
            user.institute = institution
        except (Institution.DoesNotExist, ValueError):
            return api.create_response(
                request,
                {"error": "Invalid institution"},
                status=400,
            )
    else:
        user.institute = None

    user.disability = data.get("disability", "")
    user.dietary = data.get("dietary", "")
    user.save()
    return user

@api.get("/csrftoken", auth=None)
def get_csrf_token(request):
    token = get_token(request)
    return {"csrftoken": token}

@api.get("/institutions", response=List[InstitutionSchema])
def search_institutions(request, search: str = ""):
    from django.db.models import Q

    institutions = Institution.objects.all()

    if search:
        institutions = institutions.filter(
            Q(name_en__icontains=search) | Q(name_ko__icontains=search)
        )

    return list(institutions[:50])  # Limit to 50 results

@api.post("/institutions", response=InstitutionSchema)
def create_institution(request, data: InstitutionCreateSchema):

    # Check if institution already exists
    existing = Institution.objects.filter(name_en=data.name_en).first()
    if existing:
        return existing

    institution = Institution.objects.create(
        name_en=data.name_en,
        name_ko=data.name_ko
    )
    return institution

@ensure_staff
@api.get("/admin/institutions", response=List[InstitutionSchema])
def get_admin_institutions(request, offset: int = 0, limit: int = 100, search: str = ""):
    from django.db.models import Q

    institutions = Institution.objects.all()

    if search:
        institutions = institutions.filter(
            Q(name_en__icontains=search) | Q(name_ko__icontains=search)
        )

    institutions = institutions.order_by('name_en')
    total = institutions.count()
    institutions = institutions[offset:offset + limit]

    return list(institutions)

@ensure_staff
@api.get("/admin/institution/{institution_id}", response=InstitutionSchema)
def get_admin_institution(request, institution_id: int):

    try:
        institution = Institution.objects.get(id=institution_id)
        return institution
    except Institution.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Institution not found"},
            status=404,
        )

@ensure_staff
@api.post("/admin/institution/{institution_id}/update", response=InstitutionSchema)
def update_institution(request, institution_id: int, data: InstitutionCreateSchema):

    try:
        institution = Institution.objects.get(id=institution_id)
        institution.name_en = data.name_en
        institution.name_ko = data.name_ko
        institution.save()
        return institution
    except Institution.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Institution not found"},
            status=404,
        )

@ensure_staff
@api.post("/admin/institution/{institution_id}/delete", response=MessageSchema)
def delete_institution(request, institution_id: int):

    try:
        institution = Institution.objects.get(id=institution_id)
        institution.delete()
        return {"code": "success", "message": "Institution deleted successfully"}
    except Institution.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "Institution not found"},
            status=404,
        )

@ensure_staff
@api.get("/admin/events", response=List[EventAdminSchema])
def get_admin_events(request):
    events = Event.objects.all()
    return events

@api.get("/events", response=PaginatedEventsSchema, auth=None)
def get_events(request, offset: int = 0, limit: int = 20, year: str = None, search: str = None, showOnlyOpen: bool = False):
    from django.db.models import Q

    events = Event.objects.all()

    # Apply filters
    if year and year != 'all':
        events = events.filter(start_date__year=int(year))

    if search:
        events = events.filter(
            Q(name__icontains=search) |
            Q(venue__icontains=search) |
            Q(organizers__icontains=search)
        )

    if showOnlyOpen:
        from datetime import datetime
        today = datetime.now().date()
        events = events.filter(Q(registration_deadline__isnull=True) | Q(registration_deadline__gte=today))

    # Sort by start_date descending
    events = events.order_by('-start_date')

    # Get total count before pagination
    total = events.count()

    # Apply pagination
    events = events[offset:offset + limit]

    return {
        "events": list(events),
        "total": total,
        "offset": offset,
        "limit": limit
    }

@ensure_staff
@api.post("/admin/event/add", response=MessageSchema)
def add_event(request):
    data = json.loads(request.body)
    if not data["name"] or not data["organizers"] or not data["venue"] or not data["start_date"] or not data["end_date"] or not data["capacity"]:
        return api.create_response(
            request,
            {"code": "missing_fields", "message": "Please fill all required fields."},
            status=400,
        )

    # Parse and validate main_languages
    main_languages_value = data.get("main_languages", [])
    if isinstance(main_languages_value, str):
        main_languages = json.loads(main_languages_value) if main_languages_value else []
    else:
        main_languages = main_languages_value

    # Set default to English if not provided
    if not main_languages:
        main_languages = ['en']
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

    # Use provided link_info or default to empty (will be set after event creation)
    link_info = data.get("link_info", "").strip()

    event = Event.objects.create(
        name=data["name"],
        description=data.get("description", ""),
        category=data.get("category", "conference"),
        link_info=link_info if link_info else "temp",  # Temporary value
        start_date=data["start_date"],
        end_date=data["end_date"],
        venue=data["venue"],
        venue_address=data.get("venue_address", ""),
        venue_latitude=float(data["venue_latitude"]) if data.get("venue_latitude") else None,
        venue_longitude=float(data["venue_longitude"]) if data.get("venue_longitude") else None,
        organizers=data["organizers"],
        main_languages=main_languages,
        registration_deadline=data["registration_deadline"] if data["registration_deadline"] else None,
        capacity=data["capacity"],
        accepts_abstract=data["accepts_abstract"] == "true",
        email_template_registration=email_template_registration,
        email_template_abstract_submission=email_template_abstract_submission,
    )

    # Set default link_info if not provided
    if not link_info:
        event.link_info = f"{settings.HEADLESS_URL_ROOT}/event/{event.id}"
        event.save()

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
    event.description = data.get("description", "")
    event.category = data.get("category", "conference")
    # Set default link_info if not provided or empty
    link_info = data.get("link_info", "").strip()
    event.link_info = link_info if link_info else f"{settings.HEADLESS_URL_ROOT}/event/{event.id}"
    event.start_date = data["start_date"]
    event.end_date = data["end_date"]
    event.venue = data["venue"]
    event.venue_address = data.get("venue_address", "")
    event.venue_latitude = float(data["venue_latitude"]) if data.get("venue_latitude") else None
    event.venue_longitude = float(data["venue_longitude"]) if data.get("venue_longitude") else None
    event.organizers = data["organizers"]
    # Parse main_languages if it's a JSON string, otherwise use the array directly
    main_languages_value = data.get("main_languages", [])
    if isinstance(main_languages_value, str):
        main_languages = json.loads(main_languages_value) if main_languages_value else []
    else:
        main_languages = main_languages_value
    # Set default to English if empty
    event.main_languages = main_languages if main_languages else ['en']
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
    attendee.first_name = data.get("first_name", "")
    attendee.middle_initial = data.get("middle_initial", "")
    attendee.last_name = data.get("last_name", "")
    attendee.korean_name = data.get("korean_name", "")
    attendee.nationality = data["nationality"]

    # Get institution by ID to retrieve both English and Korean names
    institute_id = data.get("institute")
    if institute_id:
        try:
            institution = Institution.objects.get(id=int(institute_id))
            attendee.institute = institution.name_en
            attendee.institute_ko = institution.name_ko
        except (Institution.DoesNotExist, ValueError):
            return api.create_response(
                request,
                {"code": "invalid_institution", "message": "Invalid institution"},
                status=400,
            )

    attendee.department = data.get("department", "")
    attendee.job_title = data.get("job_title", "")
    attendee.disability = data.get("disability", "")
    attendee.dietary = data.get("dietary", "")
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

    # Get institution by ID to retrieve both English and Korean names
    institute_id = data.get("institute")
    if institute_id:
        try:
            institution = Institution.objects.get(id=int(institute_id))
            institute_name_en = institution.name_en
            institute_name_ko = institution.name_ko
        except (Institution.DoesNotExist, ValueError):
            return api.create_response(
                request,
                {"code": "invalid_institution", "message": "Invalid institution"},
                status=400,
            )
    else:
        return api.create_response(
            request,
            {"code": "missing_institute", "message": "Institute is required"},
            status=400,
        )

    attendee = Attendee.objects.create(
        user=user,
        event=event,
        first_name=data.get("first_name", ""),
        middle_initial=data.get("middle_initial", ""),
        last_name=data.get("last_name", ""),
        korean_name=data.get("korean_name", ""),
        nationality=data["nationality"],
        institute=institute_name_en,
        institute_ko=institute_name_ko,
        department=data.get("department", ""),
        job_title=data.get("job_title", ""),
        disability=data.get("disability", ""),
        dietary=data.get("dietary", "")
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

@ensure_staff
@api.get("/admin/users", response=List[UserSchema])
def get_all_users(request):
    return User.objects.all().order_by('-date_joined')

@ensure_staff
@api.post("/admin/user/{user_id}/toggle-active", response=MessageSchema)
def toggle_user_active(request, user_id: int):
    # Prevent users from deactivating themselves
    if request.user.id == user_id:
        return api.create_response(
            request,
            {"code": "self_action_denied", "message": "You cannot deactivate yourself."},
            status=400,
        )

    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        return {"code": "success", "message": f"User {status} successfully."}
    except User.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "User not found."},
            status=404,
        )

@ensure_staff
@api.post("/admin/user/{user_id}/toggle-verified", response=MessageSchema)
def toggle_user_verified(request, user_id: int):
    from allauth.account.models import EmailAddress
    try:
        user = User.objects.get(id=user_id)
        email_address = EmailAddress.objects.filter(user=user, primary=True).first()
        if email_address:
            email_address.verified = not email_address.verified
            email_address.save()
            status = "verified" if email_address.verified else "unverified"
            return {"code": "success", "message": f"User email {status} successfully."}
        else:
            return api.create_response(
                request,
                {"code": "not_found", "message": "Email address not found."},
                status=404,
            )
    except User.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "User not found."},
            status=404,
        )

@api.post("/generate-verification-key", response=VerificationKeyResponseSchema, auth=None)
def generate_verification_key(request, data: GenerateVerificationKeySchema):
    import secrets
    from datetime import timedelta
    from django.utils import timezone
    from allauth.account.models import EmailAddress
    from main.models import EmailVerificationKey

    email = data.email

    try:
        user = User.objects.get(email__iexact=email)
        email_address = EmailAddress.objects.filter(user=user, email__iexact=email).first()

        # If not found, try getting the primary email
        if not email_address:
            email_address = EmailAddress.objects.filter(user=user, primary=True).first()

        if email_address and not email_address.verified:
            # Generate random alphanumeric key
            verification_key = secrets.token_urlsafe(32)

            # Delete any existing keys for this email older than 1 hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            EmailVerificationKey.objects.filter(email=email, created_at__lt=one_hour_ago).delete()

            # Delete any existing keys for this email to prevent duplicates
            EmailVerificationKey.objects.filter(email=email).delete()

            # Store in database
            EmailVerificationKey.objects.create(
                email=email,
                verification_key=verification_key
            )

            return {"key": verification_key}
        else:
            # Email is verified or not found, return empty key
            return {"key": ""}
    except User.DoesNotExist:
        return {"key": ""}

@api.post("/resend-verification", response=MessageSchema, auth=None)
def resend_verification_email(request, data: ResendVerificationSchema):
    from datetime import timedelta
    from django.utils import timezone
    from allauth.account.models import EmailAddress
    from allauth.account.utils import send_email_confirmation
    from main.models import EmailVerificationKey

    email = data.email
    verification_key = data.verification_key

    # Verify the key from database
    try:
        # Keys older than 1 hour are considered expired
        one_hour_ago = timezone.now() - timedelta(hours=1)
        key_record = EmailVerificationKey.objects.filter(
            email=email,
            verification_key=verification_key,
            created_at__gte=one_hour_ago
        ).first()

        if not key_record:
            return api.create_response(
                request,
                {"code": "invalid_key", "message": "Invalid or expired verification key."},
                status=401,
            )

        user = User.objects.get(email=email)
        email_address = EmailAddress.objects.filter(user=user, email=email).first()

        if email_address and not email_address.verified:
            # Use allauth's internal function to send verification email
            send_email_confirmation(request, user)

            # Delete the used key
            key_record.delete()

            return {"code": "success", "message": "Verification email sent successfully."}
        elif email_address and email_address.verified:
            # Clean up the key
            key_record.delete()
            return api.create_response(
                request,
                {"code": "already_verified", "message": "Email is already verified."},
                status=400,
            )
        else:
            return api.create_response(
                request,
                {"code": "not_found", "message": "Email address not found."},
                status=404,
            )
    except User.DoesNotExist:
        return api.create_response(
            request,
            {"code": "not_found", "message": "User not found."},
            status=404,
        )

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

@api.post("/event/{event_id}/onsite", auth=None)
def register_on_site(request, event_id: int):
    event = Event.objects.get(id=event_id)
    data = json.loads(request.body)
    # Auto-create institution if it doesn't exist
    institute_name = data.get("institute", "")
    if institute_name:
        institution, _ = Institution.objects.get_or_create(
            name_en=institute_name,
            defaults={'name_ko': ''}
        )
        institute_name = institution.name_en

    oa = OnSiteAttendee.objects.create(
        event=event,
        first_name=data.get("first_name"),
        middle_initial=data.get("middle_initial"),
        last_name=data.get("last_name"),
        institute=institute_name,
        job_title=data.get("job_title", "")
    )
    return {"code": "success", "message": "Successfully registered on-site.", "id": oa.id}

@ensure_event_staff
@api.get("/event/{event_id}/onsite", response=List[OnSiteAttendeeSchema])
def get_on_site_attendees(request, event_id: int):
    event = Event.objects.get(id=event_id)
    return event.onsite_attendees.all()

@ensure_event_staff
@api.post("/event/{event_id}/onsite/{onsite_id}/delete", response=MessageSchema)
def delete_on_site_attendee(request, event_id: int, onsite_id: int):
    event = Event.objects.get(id=event_id)
    oa = OnSiteAttendee.objects.get(id=onsite_id, event=event)
    oa.delete()
    return {"code": "success", "message": "On-site attendee deleted."}

@ensure_event_staff
@api.post("/event/{event_id}/onsite/{onsite_id}/update", response=MessageSchema)
def update_on_site_attendee(request, event_id: int, onsite_id: int):
    event = Event.objects.get(id=event_id)
    oa = OnSiteAttendee.objects.get(id=onsite_id, event=event)
    data = json.loads(request.body)
    oa.first_name = data.get("first_name")
    oa.middle_initial = data.get("middle_initial")
    oa.last_name = data.get("last_name")

    # Auto-create institution if it doesn't exist
    institute_name = data.get("institute", "")
    if institute_name:
        institution, _ = Institution.objects.get_or_create(
            name_en=institute_name,
            defaults={'name_ko': ''}
        )
        oa.institute = institution.name_en
    else:
        oa.institute = institute_name

    oa.job_title = data.get("job_title")
    oa.save()
    return {"code": "success", "message": "On-site attendee updated."}