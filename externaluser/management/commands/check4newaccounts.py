from django.core.management.base import BaseCommand
from externaluser.models import ExternalUser
from templated_email import send_templated_mail
from django.conf import settings
from evaluation_system.misc import config


class Command(BaseCommand):
    """
    Check for new created accounts and send confirmation email
    """
    def handle(self, *args, **kwargs):
        
        new_users = ExternalUser.objects.filter(status='account_created')
        
        for user in new_users:
            
            # send email to new user
            send_templated_mail(
                'external_user_activated',
                settings.EMAIL_HOST_USER,
                [user.email],
                context={
                        'user': user,
                        'project': config.get('project_name'),
                        'website': config.get('project_website')
                },
            )
            
            user.status = 'active'
            user.save()
