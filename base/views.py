""" Views for the base application """

import logging

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django_evaluation.monitor import _restart

@sensitive_variables('passwd')
@sensitive_post_parameters('password')
def home(request):
    """ Default view for the root """    
        
    login_failed = False

    guest_login = None

    if not request.user.is_authenticated():
        try:
            user = request.POST["user"]
            passwd = request.POST["password"]
            forward = request.POST["next"]

            u = auth.authenticate(username=user, password=passwd)

            if u:
                auth.login(request, u)
                login_failed = False

                guest_login = u.groups.filter(name='Guest')

                if(forward):
                    return HttpResponseRedirect(forward)

        except Exception, e:
            logging.debug(str(e))
        
    return render(request, 'base/home.html',{'login_failed':login_failed, 'guest_login' : guest_login})
    
    # return render(request, 'base/home.html',{'login_failed':login_failed})

def wiki(request):
    """
    View rendering the iFrame for the wiki page.
    """
    return render(request, 'base/wiki.html', {'page':'https://code.zmaw.de/projects/miklip-d-integration/wiki'})

def contact(request):
    """
    View rendering the iFrame for the wiki page.
    """
    return render(request, 'base/wiki.html', {'page':'https://code.zmaw.de/projects/miklip-d-integration/issues/new'})

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
