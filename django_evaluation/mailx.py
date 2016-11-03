from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.core.mail.utils import DNS_NAME
import os


class EmailBackend(BaseEmailBackend):
    """
    Simple mail backend that uses bash mailx with a system command
    """ 
    def send_messages(self, email_messages):

        if not email_messages:
            return

        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        return num_sent


    def _send(self, email_message):

        if not email_message.recipients():
            return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        for recipient in recipients:
            cmd = 'echo "%s" | mail -s "%s" %s' % (email_message.body, email_message.subject, recipient)
            print os.popen(cmd).read()
        return True

