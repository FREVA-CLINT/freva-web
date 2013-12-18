from django.shortcuts import render
from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.debug import sensitive_post_parameters

import json
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.model.db import _result_preview
from evaluation_system.model.user import User
from evaluation_system.misc import utils

from models import History, Result
from django_evlauation import settings


import logging


@login_required()
def history(request):
    
    
    try: 
        request.GET['uid']
        user = request.GET['uid']
    except KeyError:
        user = request.user
        
    try:
        tool = request.GET['plugin']
        history = History.objects.filter(uid=user).filter(tool=tool).order_by('-id')
    except KeyError:
        history = History.objects.order_by('-id').filter(uid=user)

    return render(request, 'history/history.html', {'history': history})

@login_required
def jobinfo(request, id, show_results = False):
    from history.utils import pygtailwrapper
    
    #get history object
    history_object = History.objects.get(id=id)
    
    history_object = History.objects.get(id=id)
    file_content = []

    # ensure that this process has been started with slurm
    if history_object.slurm_output == '0':
        file_content = [ 'This job has been started manually.', 'No further information is available.']
        
    else:
        # for a read-protected directory this will fail
        try:
            for line in pygtailwrapper(id, restart=True):
                file_content.append(line)
        except IOError:
            file_content =  [ 'WARNING:',
                               'This is not the content of the file \'' + history_object.slurm_output + '\'.',
                               'Probably, your home directory denies read access to the file.',
                               'In this case the results will be shown after the tool has finished.',
                               'You can view the tool\'s progress in a terminal with the command',
                               'tail -f ' + history_object.slurm_output]
            
            # make sure that the file exists
            try:
                if not os.path.isfile(history_object.slurm_output):
                    file_content = ['Can not locate the slurm file \'%s\'' %  history_object.slurm_output]
            except IOError:
                pass
        
    if show_results and history_object.status in [History.processStatus.finished, History.processStatus.finished_no_output]:
        return render(request, 'history/results.html', {'file_content':file_content, 'history_object': history_object, 'result_object' : -1})
    else:
        return render(request, 'history/jobinfo.html', {'file_content':file_content, 'history_object': history_object, 'result_object' : -1})
    


@login_required()
def results(request, id):
    from history.utils import pygtailwrapper
    
    #get history object
    history_object = History.objects.get(id=id)
    
    if history_object.status in [History.processStatus.running, History.processStatus.scheduled, History.processStatus.broken]:
        history_object = History.objects.get(id=id)
        file_content = []

        # ensure that this process has been started with slurm
        if history_object.slurm_output == '0':
            file_content = [ 'This job has been started manually.', 'No further information is available.']
            
        else:
            # for a read-protected directory this will fail
            try:
                for line in pygtailwrapper(id, restart=True):
                    file_content.append(line)
            except IOError:
                file_content =  [ 'WARNING:',
                                   'This is not the content of the file \'' + history_object.slurm_output + '\'.',
                                   'Probably, your home directory denies read access to the file.',
                                   'In this case the results will be shown after the tool has finished.',
                                   'You can view the tool\'s progress in a terminal with the command',
                                   'tail -f ' + history_object.slurm_output]
                
                # make sure that the file exists
                try:
                    if not os.path.isfile(history_object.slurm_output):
                        file_content = ['Can not locate the slurm file \'%s\'' %  history_object.slurm_output]
                except IOError:
                    pass
        
        return render(request, 'history/results.html', {'file_content':file_content, 'history_object': history_object, 'result_object' : -1})
    
    else:
        # result_object = Result.objects.order_by('id').filter(history_id = id).filter(preview_file_ne='')
        result_object = history_object.result_set.filter(~Q(preview_file = '')).order_by('preview_file')
        return render(request, 'history/results.html', {'history_object': history_object, 'result_object' : result_object, 'PREVIEW_URL' : settings.PREVIEW_URL })
        
        
@login_required()
def tailFile(request, id):
    from history.utils import pygtailwrapper

    history_object = History.objects.get(id=id)
    new_lines = list()
    
    try: 
        for lines in pygtailwrapper(id):
            line = lines.replace('\n', '<br/>');
            new_lines.append(line)
    except IOError:
        pass
        
    if history_object.status < 2:
        new_lines = False
    
    return HttpResponse(json.dumps(new_lines), content_type="application/json")
    
@sensitive_post_parameters('password')
@login_required()
def cancelSlurmjob(request):
    from paramiko import AuthenticationException
    history_item = History.objects.get(pk=request.POST['id'])
    if history_item.status < 3:
        return HttpResponse(json.dumps('Job already finished'), content_type="application/json")
    
    slurm_id = history_item.slurmId()
    try:
        result = ssh_call(request.user.username, request.POST['password'], 'scancel %s' % (slurm_id,), settings.SCHEDULER_HOST)
        return HttpResponse(json.dumps(result[1]), content_type="application/json")
    except AuthenticationException:
        return HttpResponse(json.dumps('wrong password'), content_type="application/json")    
    
    
    
    
