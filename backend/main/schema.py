
from ninja import Schema

from typing import List, Union
from datetime import date

from main.models import User, Attendee, Abstract, OnSiteAttendee, Institution
from main.utils import docx_to_html, odt_to_html

class LoginSchema(Schema):
    email: str
    password: str

class ResendVerificationSchema(Schema):
    email: str
    verification_key: str

class GenerateVerificationKeySchema(Schema):
    email: str

class VerificationKeyResponseSchema(Schema):
    key: str

class MessageSchema(Schema):
    code: str
    message: str = ""

class InstitutionSchema(Schema):
    id: int
    name_en: str
    name_ko: str

class InstitutionCreateSchema(Schema):
    name_en: str
    name_ko: str = ""

class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    middle_initial: str
    korean_name: str
    last_name: str
    name: str
    orcid: str
    nationality: int
    job_title: str
    department: str
    institute: str
    disability: str
    dietary: str
    is_staff: bool
    is_active: bool
    date_joined: str
    email_verified: bool

    @staticmethod
    def resolve_orcid(user: User) -> str:
        linked_accounts = user.socialaccount_set.filter(provider='orcid')
        if linked_accounts.count() > 0:
            return linked_accounts[0].uid
        return ""

    @staticmethod
    def resolve_name(user: User) -> str:
        name = user.first_name
        if user.middle_initial:
            name += " " + user.middle_initial
        name += " " + user.last_name
        return name

    @staticmethod
    def resolve_date_joined(user: User) -> str:
        return user.date_joined.isoformat()

    @staticmethod
    def resolve_email_verified(user: User) -> bool:
        from allauth.account.models import EmailAddress
        email_address = EmailAddress.objects.filter(user=user, primary=True).first()
        if email_address:
            return email_address.verified
        return False

class EventSchema(Schema):
    id: int
    name: str
    description: str
    link_info: str
    start_date: date
    end_date: date
    venue: str
    venue_address: str
    venue_latitude: Union[float, None]
    venue_longitude: Union[float, None]
    organizers: str
    registration_deadline: Union[date, None]
    accepts_abstract: bool
    abstract_deadline: Union[date, None]

class PaginatedEventsSchema(Schema):
    events: List[EventSchema]
    total: int
    offset: int
    limit: int
    
class VenueSchema(Schema):
    short_name: str
    long_name: str

class EmailTemplateSchema(Schema):
    subject: str
    body: str

class EventAdminSchema(Schema):
    id: int
    name: str
    description: str
    link_info: str
    start_date: date
    end_date: date
    venue: str
    venue_address: str
    venue_latitude: Union[float, None]
    venue_longitude: Union[float, None]
    organizers: str
    registration_deadline: Union[date, None]
    capacity: int
    accepts_abstract: bool
    abstract_deadline: Union[date, None]
    capacity_abstract: Union[int, None]
    max_votes: Union[int, None]
    email_template_registration: Union[EmailTemplateSchema, None]
    email_template_abstract_submission: Union[EmailTemplateSchema, None]

class RegistrationStatusSchema(Schema):
    registered: bool

class QuestionSchema(Schema):
    id: int
    question: dict

class AnswerSchema(Schema):
    id: int
    reference: QuestionSchema
    question: str
    answer: Union[str, int]

class StatsSchema(Schema):
    registered: int
    abstracts: int

class AttendeeSchema(Schema):
    id: int
    user: UserSchema
    first_name: str
    middle_initial: str
    last_name: str
    name: str
    nationality: int
    institute: str
    department: str
    job_title: str
    disability: str
    dietary: str
    custom_answers: List[AnswerSchema]

    @staticmethod
    def resolve_name(da: Attendee) -> str:
        name = da.first_name
        if da.middle_initial:
            name += " " + da.middle_initial
        name += " " + da.last_name
        return name

class SpeakerSchema(Schema):
    id: int
    name: str
    email: str
    affiliation: str
    is_domestic: bool
    type: str

class AbstractShortSchema(Schema):
    id: int
    attendee: AttendeeSchema
    title: str
    is_oral: bool
    is_accepted: bool
    votes: int
    link: str
    @staticmethod
    def resolve_votes(abstract: Abstract) -> int:
        return abstract.votes.count()
    @staticmethod
    def resolve_link(abstract: Abstract) -> str:
        from django.conf import settings
        import os
        full_path = os.path.join(settings.HEADLESS_URL_ROOT, settings.MEDIA_URL, abstract.file_path)
        return full_path
    
class AbstractSchema(Schema):
    id: int
    attendee: AttendeeSchema
    title: str
    body: str
    is_oral: bool
    is_accepted: bool
    votes: int
    link: str
    @staticmethod
    def resolve_votes(abstract: Abstract) -> int:
        return abstract.votes.count()
    @staticmethod
    def resolve_body(abstract: Abstract) -> str:
        from django.conf import settings
        import os
        full_path = os.path.join(settings.MEDIA_ROOT, abstract.file_path)
        try:
            if full_path.endswith(".docx"):
                return docx_to_html(full_path)
            elif full_path.endswith(".odt"):
                return odt_to_html(full_path)
        except:
            return "An error occured while trying to convert the file to HTML. Please contact the administrator."
    @staticmethod
    def resolve_link(abstract: Abstract) -> str:
        from django.conf import settings
        import os
        full_path = os.path.join(settings.HEADLESS_URL_ROOT, settings.MEDIA_URL, abstract.file_path)
        return full_path
    
class AbstractVoteSchema(Schema):
    id: int
    reviewer: AttendeeSchema
    voted_abstracts: List[AbstractShortSchema]

class OnSiteAttendeeSchema(Schema):
    id: int
    first_name: str
    middle_initial: str
    last_name: str
    name: str
    institute: str
    job_title: str

    @staticmethod
    def resolve_name(da: OnSiteAttendee) -> str:
        name = da.first_name
        if da.middle_initial:
            name += " " + da.middle_initial
        name += " " + da.last_name
        return name