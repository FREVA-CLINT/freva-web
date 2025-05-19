# base/views.py
import logging

import django.contrib.auth as auth
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from evaluation_system.misc import config

from base.models import UIMessages
from django_evaluation.monitor import _restart


def home(request):
    """Default view for the root"""
    messages = UIMessages.objects.order_by("-id").filter(resolved=False)
    
    context = {
        "messages": messages,
        "next": request.GET.get("next", None),
    }
    
    return render(request, "base/home.html", context)


def dynamic_css(request):
    main_color = settings.MAIN_COLOR
    hover_color = settings.HOVER_COLOR
    border_color = settings.BORDER_COLOR
    return render(
        request,
        "base/freva.css",
        {
            "main_color": main_color,
            "hover_color": hover_color,
            "border_color": border_color,
        },
        content_type="text/css",
    )


def wiki(request):
    """
    View rendering the iFrame for the wiki page.
    """
    return render(
        request,
        "base/wiki.html",
        {
            "page": "https://freva.gitlab-pages.dkrz.de/evaluation_system/sphinx_docs/index.html"
        },
    )


@login_required()
def shell_in_a_box(request):
    """
    View for the shell in a box iframe
    """
    if request.user.groups.filter(
        name=config.get("external_group", "noexternalgroupset")
    ).exists():
        shell_url = "/shell2/"
    else:
        shell_url = "/shell/"

    return render(
        request, "base/shell-in-a-box.html", {"shell_url": shell_url}
    )


@login_required()
def contact(request):
    """
    View rendering the iFrame for the wiki page.
    """
    if request.method == "POST":
        from templated_email import send_templated_mail

        myemail = settings.SERVER_EMAIL
        username = "freva-system"
        mail_text = request.POST.get("text")
        send_templated_mail(
            template_name="mail_to_admins",
            from_email=myemail,
            recipient_list=settings.CONTACTS,
            context={
                "username": username,
                "text": mail_text,
                "project": config.get("project_name"),
                "website": config.get("project_website"),
            },
            headers={"Reply-To": myemail},
        )
        return HttpResponseRedirect("%s?success=1" % reverse("base:contact"))
    success = True if request.GET.get("success", None) else False
    return render(request, "base/contact.html", {"success": success})


def logout(request):
    """
    logout that clears both Django and Keycloak sessions
    """
    id_token = request.session.get('oidc_id_token', '')

    auth.logout(request)
    
    if id_token:
        keycloak_base_url = settings.OIDC_URL + '/protocol/openid-connect/logout'
        # TODO: I wish I had a better way to get the redirect_uri
        scheme = request.scheme
        host = request.get_host()
        redirect_uri = f"{scheme}://{host}"
        logout_url = f"{keycloak_base_url}?post_logout_redirect_uri={redirect_uri}&id_token_hint={id_token}"
        return HttpResponseRedirect(logout_url)
    
    return HttpResponseRedirect("/")

def edit_account(request):
    """
    Edit account information
    """
    return HttpResponseRedirect(
        settings.OIDC_URL + "/account"
    )

@login_required()
@user_passes_test(lambda u: u.is_superuser)
def restart(request):
    """
    Restart form for the webserver
    """
    try:
        if request.POST["restart"] == "1":
            _restart(path=None)
    # TODO: Exception too broad!
    except:
        return render(request, "base/restart.html")

    return render(request, "base/home.html")