from allauth.account.signals import email_changed
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def reset_deletion_warning_on_login(sender, user, request, **kwargs):
    """
    Reset the deletion_warning_sent flag when a user logs in.
    This ensures users who received a warning but then logged in
    won't have stale warning flags.
    """
    if user.deletion_warning_sent:
        user.deletion_warning_sent = False
        user.save(update_fields=['deletion_warning_sent'])


@receiver(email_changed)
def sync_username_on_email_change(sender, request, user, from_email_address, to_email_address, **kwargs):
    """
    Keep username in sync with primary email when it changes via allauth.
    """
    user.username = to_email_address.email
    user.save(update_fields=['username'])
