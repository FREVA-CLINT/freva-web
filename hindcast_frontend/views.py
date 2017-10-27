from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def hindcast_frontend(request):
    return render(request, 'plugins/list.html', {'title': 'Hindcast Frontend'})