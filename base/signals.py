from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django_evaluation import settings
from ipware.ip import get_real_ip, get_ip
from datetime import datetime
import requests

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


        try: 
            api_key = '28e6f13bda7c619201630b904b36a3c53b02a49b'
            url = 'http://api.db-ip.com/addrinfo?addr=%s&api_key=%s' % (ip,api_key,)
            r = requests.get(url)
            val = r.json()
            val = 'Country: %s\nState/Prov: %s\n City: %s' % (val['country'],val['stateprov'],val['city'],)
        except:
            val = ''
        message = "Guest login from %s at %s" % (ip,
                                                 datetime.now().isoformat())
        message += '\n\n%s\n\nMore information https://db-ip.com/%s' % (val,ip)
        print "Send: ", message, " to ", admin_mail_addresses

        send_mail('[miklip-guest] Guest Login',
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  admin_mail_addresses,
                  fail_silently = True) 

# connect the function with the message
user_logged_in.connect(send_mail_after_guest_login)
