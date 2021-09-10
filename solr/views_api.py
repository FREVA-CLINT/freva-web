import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from django.conf import settings
from paramiko import AuthenticationException

from plugins.utils import ssh_call, get_scheduler_hosts
import json


@api_view(['POST'])
@login_required()
def ncdump(request):
    fn = request.data.get('file')
    user_pw = request.data.get('pass')
    command = '%s %s' % (settings.NCDUMP_BINARY, fn, )
    if not request.user.has_perm('history.browse_full_data'):
        ncdump_out = 'Guest users are not allowed to use this command.<br/>Normally you would see the output of <strong>ncdump</strong> here.'
        return Response(
            json.dumps(dict(ncdump=mark_safe(ncdump_out), error_msg='')),
            status=200
        )

    try:
        result = ssh_call(base64.b64decode('azIwNDIzMA=='),
                          base64.b64decode('U2NodzRyIXprMHBmZg=='),
                          command)
        ncdump_out = mark_safe(result[1].read())
        ncdump_err = mark_safe(result[2].read())
        return Response(dict(ncdump=ncdump_out,
                             error_msg=ncdump_err),
                        status=200, content_type='text/html')
    except AuthenticationException:
        return Response('AuthenticationException', status=500)
