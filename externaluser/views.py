from django.shortcuts import render
from externaluser.forms import ExternalUserForm
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from templated_email import send_templated_mail
from django.conf import settings
from evaluation_system.misc import config


def external_register(request):
    
    show_success = request.GET.get('success', False)
    if request.method == 'POST':
        
        form = ExternalUserForm(request.POST)
        if form.is_valid():
            form.save()

            # send mail to admins
            send_templated_mail(
                template_name='new_external_user',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[a[1] for a in settings.ADMINS],
                context={
                    'project': config.get('project_name'),
                    'website': config.get('project_website')
                },
            )

            return HttpResponseRedirect('%s?success=true' % reverse('external:external_register'))
    else:
        form = ExternalUserForm()
    
    return render(request, 'externaluser/register.html',
                  {'form': form, 'show_success': show_success})
