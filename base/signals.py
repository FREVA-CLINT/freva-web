from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django_evaluation import settings
from ipware.ip import get_real_ip, get_ip
from datetime import datetime


def send_mail_after_guest_login(sender, user, request, **kwargs):
    """
    This function will be called after login (via event see below)
    and sends an email to the administrators.
    """
    admin_mail_addresses = []

    for admin in settings.ADMINS:
        admin_mail_addresses.append(admin[1])


    is_guest = user.groups.filter(name='Guest')

    if  is_guest and settings.SEND_MAIL_AT_GUEST_LOGIN:
        ip = ''

        try:
            ip = get_real_ip(request)
        except:
            ip = ''

        if not ip:
            try:
                ip = get_ip(request)
            except:
                ip = ''


        message = "Guest login from %s at %s" % (ip,
                                                 datetime.now().isoformat())

        print "Send: ", message, " to ", admin_mail_addresses

        send_mail('[miklip-guest] Guest Login',
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  admin_mail_addresses,
                  fail_silently = True) 

# connect the function with the message
user_logged_in.connect(send_mail_after_guest_login)
