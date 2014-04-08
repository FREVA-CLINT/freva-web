from django import template

register = template.Library()

@register.inclusion_tag('history/templatetags/dialog.html')
def cancel_dialog():
    return {}

@register.inclusion_tag('history/templatetags/sendmail_dialog.html')
def send_mail_dialog():
    return {}