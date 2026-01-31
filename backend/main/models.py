from django.contrib.auth.models import AbstractUser
from django.db import models

def default_main_languages():
    return ['en']

class Institution(models.Model):
    """
    Institution model - stores institution names in both English and Korean
    """
    name_en = models.CharField(max_length=1000, unique=True)
    name_ko = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} ({self.name_ko})" if self.name_ko else self.name_en

class User(AbstractUser):
    """
    User model
    
    Extends Django's AbstractUser model, which provides the following fields:
    - username
    - first_name
    - last_name
    - email
    - is_staff
    - is_active
    - date_joined
    """

    # Add additional fields here
    NATIONALITY_CHOICES = [
        (1, 'Korean'),
        (2, 'Non-Korean'),
        (3, 'Prefer not to respond'),
    ]
    middle_initial = models.CharField(max_length=1, blank=True)
    korean_name = models.CharField(max_length=1000, blank=True)
    nationality = models.IntegerField(choices=NATIONALITY_CHOICES, default=1)
    job_title = models.CharField(max_length=1000, blank=True)
    institute = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    department = models.CharField(max_length=1000, blank=True)
    disability = models.TextField(blank=True)
    dietary = models.TextField(blank=True)

    @property
    def name(self):
        return f'{self.first_name}{" " + self.middle_initial if self.middle_initial else ""} {self.last_name}'

    def __str__(self):
        return self.username
class Attendee(models.Model):
    """
    Attendee model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=1000)
    middle_initial = models.CharField(max_length=1, blank=True)
    last_name = models.CharField(max_length=1000)
    korean_name = models.CharField(max_length=1000, blank=True)
    nationality = models.IntegerField()
    institute = models.CharField(max_length=1000)  # English name
    institute_ko = models.CharField(max_length=1000, blank=True)  # Korean name
    department = models.CharField(max_length=1000, blank=True)
    job_title = models.CharField(max_length=1000, blank=True)
    disability = models.TextField(blank=True)
    dietary = models.TextField(blank=True)
    @property
    def name(self):
        return f'{self.first_name}{" " + self.middle_initial if self.middle_initial else ""} {self.last_name}'

class OnSiteAttendee(models.Model):
    """
    OnSiteAttendee model
    """
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='onsite_attendees')
    name = models.CharField(max_length=1000)
    email = models.EmailField(blank=True)
    institute = models.CharField(max_length=1000)
    job_title = models.CharField(max_length=1000, blank=True)

    @property
    def korean_name(self):
        return self.name

    @property
    def first_name(self):
        return self.name

    @property
    def last_name(self):
        return ''

    def __str__(self):
        return self.name

class Setting(models.Model):
    """
    Setting model
    """
    key = models.CharField(max_length=100)
    value = models.TextField() # JSON

    def __str__(self):
        return self.key

class Event(models.Model):
    """
    Event model
    """
    CATEGORY_CHOICES = [
        ('workshop', 'Workshop'),
        ('hackathon', 'Hackathon'),
        ('symposium', 'Symposium'),
        ('meeting', 'Meeting'),
        ('conference', 'Conference'),
    ]

    link_info = models.URLField(blank=True)
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='conference')
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=1000)  # Venue display name (English)
    venue_ko = models.CharField(max_length=1000, blank=True)  # Venue display name (Korean)
    venue_address = models.CharField(max_length=1000, blank=True)  # Full address
    venue_latitude = models.FloatField(blank=True, null=True)  # Latitude for map
    venue_longitude = models.FloatField(blank=True, null=True)  # Longitude for map
    organizers = models.ManyToManyField('User', related_name='organized_events', blank=True)
    main_languages = models.JSONField(default=default_main_languages)  # Array of language codes: ['ko', 'en']
    registration_deadline = models.DateField(blank=True, null=True)
    capacity = models.IntegerField()
    registration_fee = models.IntegerField(blank=True, null=True)
    accepts_abstract = models.BooleanField(default=False)
    abstract_deadline = models.DateField(blank=True, null=True)
    capacity_abstract = models.IntegerField(null=True)
    max_votes = models.IntegerField(null=True)
    email_template_registration = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, blank=True, null=True, related_name='email_template_registration')
    email_template_abstract_submission = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, blank=True, null=True, related_name='email_template_abstract_submission')
    email_template_certificate = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, blank=True, null=True, related_name='email_template_certificate')
    invitation_code = models.CharField(max_length=100, blank=True)  # Empty = public event, non-empty = invitation only
    attendees = models.ManyToManyField('Attendee', related_name='events', blank=True)
    reviewers = models.ManyToManyField('Attendee', related_name='reviewed_events', blank=True)
    admins = models.ManyToManyField('User', related_name='admins', blank=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def organizers_en(self):
        """Return formatted organizers in English: First Last (Institution)"""
        organizer_list = []
        for org in self.organizers.all():
            name = f"{org.first_name} {org.last_name}"
            # Get institution English name
            institute = org.institute.name_en if org.institute else ""
            if institute:
                organizer_list.append(f"{name} ({institute})")
            else:
                organizer_list.append(name)
        return ", ".join(organizer_list)

    @property
    def organizers_ko(self):
        """Return formatted organizers in Korean: 한글이름 (기관명)"""
        organizer_list = []
        for org in self.organizers.all():
            # Use Korean name if available, otherwise fall back to English name
            name = org.korean_name if org.korean_name else f"{org.first_name} {org.last_name}"
            # Get institution Korean name, fall back to English if not available
            institute = (org.institute.name_ko or org.institute.name_en) if org.institute else ""
            if institute:
                organizer_list.append(f"{name} ({institute})")
            else:
                organizer_list.append(name)
        return ", ".join(organizer_list)

    def delete(self, *args, **kwargs):
        if self.email_template_registration:
            self.email_template_registration.delete()
        if self.email_template_abstract_submission:
            self.email_template_abstract_submission.delete()
        if self.email_template_certificate:
            self.email_template_certificate.delete()
        super().delete(*args, **kwargs)

class Speaker(models.Model):
    """
    Speaker model
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=254)
    affiliation = models.CharField(max_length=1000, blank=True)
    is_domestic = models.BooleanField(default=False)
    type = models.CharField(max_length=1000, choices=[
        ('keynote', 'Keynote Talk'),
        ('invited', 'Invited Talk'),
        ('contributed', 'Contributed Talk'),
        ('short', 'Short Talk'),
        ('poster', 'Poster'),
    ])

class AbstractVote(models.Model):
    """
    AbstractVote model
    """
    reviewer = models.ForeignKey('Attendee', on_delete=models.CASCADE)
    voted_abstracts = models.ManyToManyField('Abstract', related_name='votes')

class Abstract(models.Model):
    """
    Abstract model
    """
    attendee = models.ForeignKey(Attendee, null=True, on_delete=models.CASCADE, related_name='abstracts')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='abstracts')
    title = models.CharField(max_length=1000)
    file_path = models.CharField(max_length=1000)
    is_oral = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    def delete(self):
        try:
            import os, shutil
            from django.conf import settings
            shutil.rmtree(os.path.dirname(os.path.join(settings.MEDIA_ROOT, self.file_path)))
        except:
            pass
        super(Abstract, self).delete()

class CustomQuestion(models.Model):
    """
    CustomQuestion model
    """
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='custom_questions')
    question = models.JSONField() # {'type': one of 'text' or 'textarea' or 'checkbox' or 'dropdown',
                                  #  'question': 'What is your favorite color?',
                                  #  'detail': 'Please select one color.',
                                  #  'options': ['Red', 'Green', 'Blue']}

class CustomAnswer(models.Model):
    """
    CustomAnswer model
    """
    reference = models.ForeignKey(CustomQuestion, null=True, blank=True, on_delete=models.SET_NULL)
    attendee = models.ForeignKey(Attendee, null=True, on_delete=models.CASCADE, related_name='custom_answers')
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)

class EmailTemplate(models.Model):
    """
    EmailTemplates model
    """
    subject = models.CharField(max_length=1000)
    body = models.TextField()

class EmailVerificationKey(models.Model):
    """
    Temporary verification keys for email verification resend
    """
    email = models.EmailField()
    verification_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'verification_key']),
        ]