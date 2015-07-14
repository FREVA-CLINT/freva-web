""" Views for the base application """

import logging

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django_evaluation.monitor import _restart
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from subprocess import Popen, STDOUT, PIPE


@sensitive_variables('passwd')
@sensitive_post_parameters('password')
def home(request):
    """ Default view for the root """    
        
    login_failed = False

    guest_login = None

    next_page = request.GET.get('next', None)
    forward = request.POST.get("next", None)

    if not request.user.is_authenticated():
        try:
            user = request.POST.get("user", "")
            passwd = request.POST.get("password", "")
            
            if user:
                u = auth.authenticate(username=user, password=passwd)
    
                if u:
                    auth.login(request, u)
    
                    guest_login = u.groups.filter(name='Guest')
    
                    if(forward):
                        return HttpResponseRedirect(forward)

                else:
                    raise Exception('Login failed')

        except Exception, e:

            # do not forget the forward after failed login
            if forward:
                next_page = forward

            login_failed = True
            logging.debug(str(e))


    return render(request, 'base/home.html',
                  {'login_failed':login_failed,
                   'guest_login' : guest_login,
                   'next' : next_page})
    
    # return render(request, 'base/home.html',{'login_failed':login_failed})

def dynamic_css(request):
    main_color = settings.MAIN_COLOR
    hover_color = settings.HOVER_COLOR
    border_color = settings.BORDER_COLOR
    return render(request, 'base/freva.css', {'main_color': main_color,
                                              'hover_color': hover_color,
                                              'border_color': border_color},
                  content_type='text/css')

def wiki(request):
    """
    View rendering the iFrame for the wiki page.
    """
    return render(request, 'base/wiki.html', {'page':'https://code.zmaw.de/projects/miklip-d-integration/wiki'})

def contact(request):
    """
    View rendering the iFrame for the wiki page.
    """
    if request.method == 'POST':
        from templated_email import send_templated_mail
        from django_evaluation.ldaptools import get_ldap_object
        user_info = get_ldap_object() 
        myinfo = user_info.get_user_info(str(request.user))
        myemail = myinfo[3]
        mail_text = request.POST.get('text')
        a=send_templated_mail(
            template_name='mail_to_admins',
            from_email=myemail,
            recipient_list=[a[1] for a in settings.ADMINS],
            context={
                'username':request.user.get_full_name(),
                'text':mail_text,
            },
            headers={'Reply-To' : myemail},
        )
        return HttpResponseRedirect('%s?success=1' % reverse('base:contact'))
    success = True if request.GET.get('success',None) else False
    return render(request, 'base/contact.html', {'success': success})

def logout(request):
    """
    Logout view.
    """
    auth.logout(request)
    
    return render(request, 'base/home.html',{'k':'logged out'})

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def restart(request):
    """
    Restart formular for the webserver
    """
    
    try:
        if request.POST['restart']=='1':
            _restart(path=None)
    except:
        return render(request, 'base/restart.html')

    return render(request, 'base/home.html')


def ncdump(request):
    """
    test for ncdump
    """
    
    file = request.POST.get('ncd_file', '')
    stdout = ''
    stderr = ''
    exception = ''
    command = ''

    if not file is None:
        command = '/usr/local/www-bin/ncdump ' + file
        try:
            p = Popen(command, stdout=PIPE, stderr=STDOUT)
            (stdout, stderr) = p.communicate()
        except Exception, e:
            exception = str(e)

    return render(request, 'base/ncdump.html', {'ncd_file': file,
                                                'ncd_out' : stdout,
                                                'ncd_err' : stderr,
                                                'ncd_exc' : exception,
                                                'ncd_cmd' : command})
