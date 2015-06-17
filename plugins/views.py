""" Views for the plugins application """

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django.contrib.flatpages.models import FlatPage
from django.core import serializers

import evaluation_system.api.plugin_manager as pm
import evaluation_system.api.parameters as param

from evaluation_system.model.user import User
from evaluation_system.model.solr import SolrFindFiles
from evaluation_system.model.slurm import slurm_file
from evaluation_system.misc import config

from plugins.utils import get_plugin_or_404, ssh_call
from plugins.forms import PluginForm, PluginWeb
from history.models import History, Configuration
from django_evaluation import settings

import logging
import paramiko # this is the ssh client

import urllib, os
import json

@login_required()
def home(request):
    """ Default view for the root """    
    tools = pm.getPlugins()    
    return render(request, 'plugins/home.html', {'tool_list': sorted(tools.iteritems())})

@login_required()
def detail(request, plugin_name):
    
    plugin = get_plugin_or_404(plugin_name)
    plugin_web = PluginWeb(plugin)
    #logging.debug(plugin.__long_description__)    
    try:
        docu_flatpage = FlatPage.objects.get(title__iexact=plugin_name)
    except FlatPage.DoesNotExist:
        docu_flatpage = None
    
    return render(request, 'plugins/detail.html', {'plugin':plugin_web, 'docu': docu_flatpage})

@login_required()
def search_similar_results(request,plugin_name=None, history_id=None):
    
    def hist_to_dict(h_obj):
        hist_dict = dict()
        results = h_obj.result_set.filter(file_type=1)  
        hist_dict['preview'] = ''
        if len(results) > 0:
            hist_dict['preview'] = results[0].preview_file
        hist_dict['pk'] = h_obj.pk
        hist_dict['tool'] = h_obj.tool
        hist_dict['uid'] = str(h_obj.uid)
        return hist_dict

    data = {}    
    hist_objects = []
    
    if request.user.isGuest():
        hist_objects = History.objects.filter(uid=request.user).filter(tool=plugin_name)
    else:    
        if not history_id is None:
            o = Configuration.objects.filter(history_id_id=history_id)
            hist_objects = History.find_similar_entries(o, max_entries = 5)

        else:
            # create the tool
            tool = pm.getPluginInstance(plugin_name)
            param_dict = tool.__parameters__
            param_dict.synchronize(plugin_name)
            plugin_fields = param_dict.keys()
            
            #don't search for empty form fields
            for key,val in request.GET.iteritems():
                if val != '':
                    if key in plugin_fields:
                        data[key]=val

            o = pm.dict2conf(plugin_name, data)
            hist_objects = History.find_similar_entries(o, uid=request.user.username, max_entries = 5)

    res = list()
    for obj in hist_objects:
        res.append(hist_to_dict(obj))
#    data = serializers.serialize('json',hist_objects,fields=('preview'))
    return HttpResponse(json.dumps(res))
  
@sensitive_post_parameters('password_hidden')
@sensitive_variables('password')
@login_required()    
def setup(request, plugin_name, row_id = None):
    
    user = None

    user_can_submit = request.user.has_perm('history.history_submit_job')

    if user_can_submit:
        user = User('integra')#request.user.username, request.user.email)
    else:
        user = User()

    home_dir = user.getUserHome()
    scratch_dir = None

    try:
        scratch_dir = user.getUserScratch()
    except:
        pass

    plugin = get_plugin_or_404(plugin_name, user=user)
    plugin_web = PluginWeb(plugin)
    
    errormsg = pm.getErrorWarning(plugin_name)[0]
        
    if request.method == 'POST':
        form = PluginForm(request.POST, tool=plugin, uid=request.user.username)#uid=user.getName())
        if form.is_valid():
            # read the configuration
            config_dict = dict(form.data)

            # read the caption
            caption = config_dict[form.caption_field_name][0].strip()
            
            if not caption:
                caption = None
            
            # empty values in the form will not be added to the dictionary.
            # as a consequence we can not submit intentionally blank fields.
            tmp_dict = dict()
            for k, v in config_dict.items():
                if v[0]:
                    tmp_dict[str(k)]='\'%s\'' % str(v[0])
                    
            config_dict = tmp_dict
                    
            config_dict = tmp_dict
            
            
            del config_dict['password_hidden'], config_dict['csrfmiddlewaretoken']
            try:
                del config_dict[form.caption_field_name]
            except:
                pass

            logging.debug(config_dict)

            # start the scheduler via sbatch
            username = request.user.username
            password = request.POST['password_hidden']
            hostnames = list(settings.SCHEDULER_HOSTS)

            # compose the plugin command
            slurm_options = config.get_section('scheduler_options')
	    # dirtyhack = 'export PYTHONPATH=/miklip/integration/evaluation_system/src;/sw/centos58-x64/python/python-2.7-ve0-gccsys/bin/python /miklip/integration/evaluation_system/bin/'
            command = plugin.composeCommand(config_dict,
                                            batchmode='web',
                                            email=user.getEmail(),
                                            caption=caption)
            # create the directories when necessary
            stdout = ssh_call(username=username,
                              password=password,
                              command=(load_module + command),
#                              command='bash -c "%s"' % (load_module + command),
#                              command='bash -c "%s"' % (dirtyhack + command),
                              hostnames=hostnames)
                        
            # get the text form stdout
            out=stdout[1].readlines()
            err=stdout[2].readlines()

            logging.debug("command:" + str(command))
            logging.debug("output of analyze:" + str(out))
            logging.debug("errors of analyze:" + str(err))
            # get the very first line only
            out_first_line = out[0]
            
            # read the id from stdout
            if out_first_line.split(' ')[0] == 'Scheduled':
                row_id = int(out_first_line.split(' ')[-1])
            else:
                row_id = 0
                raise Http404, "Unexpected output of analyze:\n[%s]\n[%s]" % (out, err)            
                
            return redirect('history:results', id=row_id) #should be changed to result page 
            
    else:
        config_dict = None
        
        # load data into form, when a row id is given.
        if row_id:
            h = History.objects.get(pk=row_id)
            config_dict = h.config_dict()
        else:
            config_dict = plugin.setupConfiguration(check_cfg=False, substitute=True)
                  
        form = PluginForm(initial=config_dict,tool=plugin, uid=user.getName())
    
    
    return render(request, 'plugins/setup.html', {'tool' : plugin_web,
                                                  'form': form,
                                                  'user_home': home_dir,
                                                  'user_scratch': scratch_dir,
                                                  'error_message': errormsg,
                                                  'restricted_user':not user_can_submit,
						  'PREVIEW_URL' : settings.PREVIEW_URL,})
  
@login_required()  
def dirlist(request):
    r=['<ul class="jqueryFileTree" style="display: none;">']
    files = list()
    try:
        r=['<ul class="jqueryFileTree" style="display: none;">']
        d=urllib.unquote(request.POST.get('dir'))
        for f in sorted(os.listdir(d)):
            if f[0] != '.':
                ff=os.path.join(d,f)
                if os.path.isdir(ff):
                    r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
                else:
                    e=os.path.splitext(f)[1][1:] # get .ext and remove dot
                    if e == 'nc':
                        files.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
        r = r+files
        r.append('</ul>')
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
        r.append('</ul>')
    return HttpResponse(''.join(r))  

def listDocu(request):
    return render(request, 'plugins/list-docu.html')


    
    
  
