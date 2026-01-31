from celery import shared_task
import base64

from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMessage
from django.conf import settings

@shared_task
def send_mail(subject, body, to):
    print(f"Sending email to {to}...")
    try:
        django_send_mail(subject, body, settings.EMAIL_FROM, [to], fail_silently=False)
        print(f"Mail sent to {to}!")
    except Exception as e:
        print(f"Error sending email to {to}: {e}")

@shared_task
def send_mail_with_attachment(subject, body, to, attachment_name, attachment_base64, attachment_mimetype='application/pdf'):
    """Send an email with a file attachment."""
    print(f"Sending email with attachment to {to}...")
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_FROM,
            to=[to]
        )
        attachment_data = base64.b64decode(attachment_base64)
        email.attach(attachment_name, attachment_data, attachment_mimetype)
        email.send(fail_silently=False)
        print(f"Mail with attachment sent to {to}!")
    except Exception as e:
        print(f"Error sending email with attachment to {to}: {e}")
