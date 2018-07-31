import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django_evaluation.monitor import _restart
from django.conf import settings
from django.core.urlresolvers import reverse
from subprocess import Popen, STDOUT, PIPE
from django.core.exceptions import PermissionDenied
from evaluation_system.misc import config


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
    
                    if forward:
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
                  {'login_failed': login_failed,
                   'guest_login': guest_login,
                   'next': next_page})


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
    return render(request, 'base/wiki.html', {'page': 'https://code.zmaw.de/projects/miklip-d-integration/wiki'})


@login_required()
def shell_in_a_box(request):
    """
    View for the shell in a box iframe
    """
    if request.user.groups.filter(
        name=config.get('external_group', 'noexternalgroupset')
    ).exists():
        shell_url = '/shell2/'
    else:
        shell_url = '/shell/'
    
    return render(request, 'base/shell-in-a-box.html',
                  {'shell_url': shell_url})


@login_required()
def contact(request):
    """
    View rendering the iFrame for the wiki page.
    """
    if request.method == 'POST':
        from templated_email import send_templated_mail
        from django_evaluation.ldaptools import get_ldap_object
        user_info = get_ldap_object() 
        myinfo = user_info.get_user_info(str(request.user))
        try:
            myemail = myinfo[3]
            username = request.user.get_full_name()
        # TODO: Exception too broad!
        except:
            myemail = settings.SERVER_EMAIL
            username = 'guest'
        mail_text = request.POST.get('text')
        send_templated_mail(
            template_name='mail_to_admins',
            from_email=myemail,
            recipient_list=[a[1] for a in settings.ADMINS],
            context={
                'username': username,
                'text': mail_text,
                'project': config.get('project_name'),
                'website': config.get('project_website')
            },
            headers={'Reply-To': myemail},
        )
        return HttpResponseRedirect('%s?success=1' % reverse('base:contact'))
    success = True if request.GET.get('success', None) else False
    return render(request, 'base/contact.html', {'success': success})


def logout(request):
    """
    Logout view.
    """
    auth.logout(request)
    
    return render(request, 'base/home.html', {'k': 'logged out'})


@login_required()
@user_passes_test(lambda u: u.is_superuser)
def restart(request):
    """
    Restart form for the webserver
    """
    try:
        if request.POST['restart'] == '1':
            _restart(path=None)
    # TODO: Exception too broad!
    except:
        return render(request, 'base/restart.html')

    return render(request, 'base/home.html')


@login_required()
def forecast_frontend(request):
    """
    Forecast frontend
    """
    if request.user.isGuest():
        raise PermissionDenied
    lang = request.GET.get('lang', 'en')
    return render(request, 'base/forecast_frontend.html', {'lang': lang}) 



def ncdump(request):
    """
    test for ncdump
    """
    
    file = request.POST.get('ncd_file', '')
    stdout = ''
    stderr = ''
    exception = ''
    command = ''

    if file is not None:
        command = '/usr/local/www-bin/ncdump ' + file
        try:
            p = Popen(command, stdout=PIPE, stderr=STDOUT)
            (stdout, stderr) = p.communicate()
        except Exception, e:
            exception = str(e)

    return render(request, 'base/ncdump.html', {'ncd_file': file,
                                                'ncd_out': stdout,
                                                'ncd_err': stderr,
                                                'ncd_exc': exception,
                                                'ncd_cmd': command})
