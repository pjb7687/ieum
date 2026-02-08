from allauth.account.adapter import DefaultAccountAdapter
from main.tasks import send_mail


class CeleryEmailAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        print(msg.subject, msg.body, email)
        send_mail.delay(msg.subject, msg.body, email)
