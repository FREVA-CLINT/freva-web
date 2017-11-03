from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


@login_required()
def hindcast_frontend(request):
    if request.user.isGuest():
        raise PermissionDenied
    return render(request, 'plugins/list.html', {'title': 'Hindcast Frontend'})
