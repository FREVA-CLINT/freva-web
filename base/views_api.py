
import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView

from base.exceptions import UserNotFoundError
from base.Users import OpenIdUser
from base.views import ensure_url_scheme

from .serializers import UserSerializer

HOP_BY_HOP = {
    'connection','keep-alive','proxy-authenticate','proxy-authorization',
    'te','trailers','transfer-encoding','upgrade'
}
class AuthenticatedUser(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        if request.user.is_authenticated:
            try:
                user = OpenIdUser(request.user.username, request=request)
            except UserNotFoundError:
                user = None
            return Response(
                self.serializer_class(request.user, context={"user": user, "request": request}).data
            )
        return Response({})

def proxy_auth_view(request, path):
    """Proxy auth requests to Freva-REST, preserving redirects, headers, and bodies."""

    backend_url = f"{ensure_url_scheme(settings.FREVA_REST_URL).rstrip('/')}/api/freva-nextgen/auth/{path}"

    # forward all client headers except hop-by-hop and host
    forwarded_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_BY_HOP.union({'host', 'content-length'})
    }

    # raw body (works for JSON, form, binary, etc.)
    body = request.body or None

    resp = requests.request(
        method=request.method,
        url=backend_url,
        params=request.GET.dict(),
        data=body,
        headers=forwarded_headers,
        timeout=10,
        allow_redirects=False
    )

    # If Freva-REST sent a redirect, hand it straight back
    if 300 <= resp.status_code < 400 and 'Location' in resp.headers:
        redirect = HttpResponseRedirect(resp.headers['Location'])
        if 'Set-Cookie' in resp.headers:
            redirect['Set-Cookie'] = resp.headers['Set-Cookie']
        return redirect

    response = HttpResponse(resp.content, status=resp.status_code)
    # copy all safe headers
    for header, val in resp.headers.items():
        if header.lower() not in HOP_BY_HOP:
            response[header] = val
    return response