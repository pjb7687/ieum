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
