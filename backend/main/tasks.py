from celery import shared_task
import base64
from datetime import timedelta
import logging

from django.core.mail import send_mail as django_send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

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


@shared_task
def check_inactive_users():
    """
    Check for inactive users and handle account deletion warnings/deletions.

    - Users inactive for (deletion_period - warning_period): Send warning email
    - Users inactive for deletion_period or more: Delete account (preserving Attendee records)
    """
    from main.models import User, Attendee, AccountSettings

    account_settings = AccountSettings.get_instance()
    now = timezone.now()
    deletion_days = account_settings.account_deletion_period
    warning_days = account_settings.account_warning_period

    deletion_threshold = now - timedelta(days=deletion_days)
    warning_threshold = now - timedelta(days=deletion_days - warning_days)

    # Find users to delete (inactive for deletion_period or more)
    users_to_delete = User.objects.filter(
        last_login__lte=deletion_threshold,
        is_staff=False,  # Don't delete staff accounts
        is_superuser=False,  # Don't delete superuser accounts
    )

    deleted_count = 0
    for user in users_to_delete:
        email = user.email
        logger.info(f"Deleting inactive user account: {email} (last login: {user.last_login})")

        # Preserve attendee records by marking them with deletion timestamp and email
        Attendee.objects.filter(user=user).update(
            user_deleted_at=now,
            user_email=email
        )

        user.delete()
        deleted_count += 1

    if deleted_count > 0:
        logger.info(f"Deleted {deleted_count} inactive user accounts")

    # Find users to warn (inactive for almost deletion_period, not yet warned)
    users_to_warn = User.objects.filter(
        last_login__lte=warning_threshold,
        last_login__gt=deletion_threshold,
        deletion_warning_sent=False,
        is_staff=False,
        is_superuser=False,
    )

    warned_count = 0
    for user in users_to_warn:
        deletion_date = user.last_login + timedelta(days=deletion_days)
        subject = f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}Account Deletion Warning"
        body = f"""Dear {user.first_name or user.username},

Your account has been inactive for a long time. According to our data retention policy, accounts that have been inactive for {deletion_days} days will be automatically deleted.

Your account will be deleted on {deletion_date.strftime('%Y-%m-%d')} unless you log in before that date.

To keep your account active, please log in to our website.

If you no longer wish to use our service, you can ignore this email and your account will be automatically deleted.

Best regards,
The IEUM Team
"""
        try:
            django_send_mail(subject, body, settings.EMAIL_FROM, [user.email], fail_silently=False)
            user.deletion_warning_sent = True
            user.save(update_fields=['deletion_warning_sent'])
            warned_count += 1
            logger.info(f"Sent deletion warning to: {user.email}")
        except Exception as e:
            logger.error(f"Failed to send deletion warning to {user.email}: {e}")

    if warned_count > 0:
        logger.info(f"Sent {warned_count} deletion warning emails")

    return {
        'deleted': deleted_count,
        'warned': warned_count,
    }


@shared_task
def cleanup_old_data():
    """
    Clean up old PaymentHistory records based on retention settings.

    - PaymentHistory records: Deleted after payment_retention_years from payment (created_at)
    """
    from main.models import PaymentHistory, AccountSettings

    account_settings = AccountSettings.get_instance()
    now = timezone.now()

    # Calculate retention threshold (from payment date)
    payment_threshold = now - timedelta(days=account_settings.payment_retention_years * 365)

    # Delete old payment history records (only those where attendee is null AND older than retention period from payment)
    old_payments = PaymentHistory.objects.filter(
        attendee__isnull=True,  # Attendee was deleted
        created_at__lte=payment_threshold  # Payment is older than retention period
    )
    payment_count = old_payments.count()
    old_payments.delete()

    if payment_count > 0:
        logger.info(f"Deleted {payment_count} old payment history records (retention: {account_settings.payment_retention_years} years from payment)")

    return {
        'payments_deleted': payment_count,
    }
