""" Views for the plugins application """

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django.views.decorators.http import require_POST 
from django.contrib.flatpages.models import FlatPage

import evaluation_system.api.plugin_manager as pm

from evaluation_system.model.user import User
from evaluation_system.misc import config

from plugins.utils import get_plugin_or_404, ssh_call, get_scheduler_hosts
from plugins.forms import PluginForm, PluginWeb
from history.models import History, Configuration

import logging
import time
import urllib
import os
import json


@login_required()
def home(request):
    """ Default view for the root """    
    user_can_submit = request.user.has_perm('history.history_submit_job')

    if user_can_submit:
        user = User(request.user.username, request.user.email)
    else:
        user = User()
    home_dir = user.getUserHome()
    scratch_dir = None
    try:
        scratch_dir = user.getUserScratch()
    except:
        pass
    
    exported_plugin = os.environ.get("EVALUATION_SYSTEM_PLUGINS_%s" % request.user, None)
    
    pm.reloadPlugins(request.user.username)
    tools = pm.getPlugins(request.user.username) 
    return render(request, 'plugins/home.html', 
                  {'tool_list': sorted(tools.iteritems()),
                   'home_dir': home_dir,
                   'scratch_dir': scratch_dir,
                   'exported_plugin': exported_plugin})


@login_required()
def detail(request, plugin_name):
    pm.reloadPlugins(request.user.username)
    plugin = get_plugin_or_404(plugin_name, user_name=request.user.username)
    plugin_web = PluginWeb(plugin)
    try:
        docu_flatpage = FlatPage.objects.get(title__iexact=plugin_name)
    except FlatPage.DoesNotExist:
        docu_flatpage = None
    
    return render(request, 'plugins/detail.html', {'plugin': plugin_web, 'docu': docu_flatpage})


@login_required()
def search_similar_results(request, plugin_name=None, history_id=None):
    pm.reloadPlugins(request.user.username)

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
    
    if request.user.isGuest():
        hist_objects = History.objects.filter(uid=request.user).filter(tool=plugin_name)
    else:    
        if history_id is not None:
            o = Configuration.objects.filter(history_id_id=history_id)
            hist_objects = History.find_similar_entries(o, max_entries=5)

        else:
            # create the tool
            tool = pm.getPluginInstance(plugin_name,
                                        user_name=request.user.username)
            param_dict = tool.__parameters__
            param_dict.synchronize(plugin_name)
            plugin_fields = param_dict.keys()
            
            # don't search for empty form fields
            for key, val in request.GET.iteritems():
                if val != '':
                    if key in plugin_fields:
                        data[key] = val

            o = pm.dict2conf(plugin_name, data, user_name=request.user.username)
            hist_objects = History.find_similar_entries(o, uid=request.user.username, max_entries=5)

    res = list()
    for obj in hist_objects:
        res.append(hist_to_dict(obj))
#    data = serializers.serialize('json',hist_objects,fields=('preview'))
    return HttpResponse(json.dumps(res))


@sensitive_post_parameters('password_hidden')
@sensitive_variables('password')
@login_required()    
def setup(request, plugin_name, row_id=None):
    pm.reloadPlugins(request.user.username)

    user_can_submit = request.user.has_perm('history.history_submit_job')

    if user_can_submit:
        user = User(request.user.username, request.user.email)
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
    
    error_msg = pm.getErrorWarning(plugin_name)[0]
        
    if request.method == 'POST':
        form = PluginForm(request.POST, tool=plugin, uid=request.user.username)
        if form.is_valid():
            # read the configuration
            config_dict = dict(form.data)

            # read the caption
            caption = config_dict[form.caption_field_name][0].strip()
            
            if not caption:
                caption = None
            
            unique_output = config_dict['unique_output_id'][0]
            
            # empty values in the form will not be added to the dictionary.
            # as a consequence we can not submit intentionally blank fields.
            tmp_dict = dict()
            for k, v in config_dict.items():
                if v[0]:
                    tmp_dict[str(k)] = '\'%s\'' % str(v[0])

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
            hostnames = list(get_scheduler_hosts(request.user))

            logging.error(hostnames)
            # compose the plugin command
            try:
                slurm_options = config.get_section('scheduler_options')
            except: 
                slurm_options = False
                try:
                    old_row_id = History.objects.filter(status=History.processStatus.running, uid=request.user).order_by('-timestamp')[0].id
                except:
                    old_row_id = 0
                # nohup output file
                log_path = '/kp/kp06/integra/mavis/misc4freva/db4freva/slurm/%s' % plugin_name
                if not os.path.exists(log_path):
                    os.makedirs(log_path)
                    os.chmod(log_path, 0o777)
                log_file = '%s/nohup-%s.out' % (log_path, time.time())
            load_module = settings.LOAD_MODULE
            
            if "EVALUATION_SYSTEM_PLUGINS_%s" % request.user in os.environ:
                plugin_str = os.environ['EVALUATION_SYSTEM_PLUGINS_%s' % request.user] 
                export_user_plugin = 'export EVALUATION_SYSTEM_PLUGINS=%s;'\
                    % plugin_str
            else:
                export_user_plugin = ''
            
            command = plugin.composeCommand(config_dict,
                                            batchmode='web' if slurm_options else False,
                                            caption=caption,
                                            unique_output=unique_output)
            # wrap command in nohup call
            if not slurm_options:
                command = 'nohup %s > /dev/null 2>&1 > %s &' % (command, log_file)

            # finally send the ssh call
            stdout = ssh_call(username=username,
                              password=password,
                              # we use "bash -c because users with other login shells can't use "export"
                              # not clear why we removed this in the first place...
                              command='bash -c "%s"' % (load_module + export_user_plugin + command),
                              hostnames=hostnames)
                        
            # get the text form stdout
            out = stdout[1].readlines()
            err = stdout[2].readlines()
          
            logging.debug("command:" + str(command))
            logging.debug("output of analyze:" + str(out))
            logging.debug("errors of analyze:" + str(err))

            # THIS IS HOW WE DETERMINE THE ID USING A SCHEDULER
            if slurm_options:
                substr = 'Scheduled job with history'
                # find first line containing the substr
                scheduler_output = next((s for s in out if substr in s), None)  # returns 'abc123'
                if scheduler_output:
                    row_id = int(scheduler_output.split(' ')[-1])
                else:
                    raise Exception, "Unexpected output of analyze:\n[%s]\n[%s]" % (out, err)

            else:
                # IF WE SEND USING NOHUP WE DON'T GET ANY FEEDBACK ABOUT THE ID
                # SO WE MAKE A GUESS THAT IT WAS THE LAST ISSUED BY A USER
                # TODO: This is probably not robust enought, if user starts multiple runs
                row_id = old_row_id
                while row_id == old_row_id:
                     try:
                         obj = History.objects.filter(status=History.processStatus.running, uid=request.user).order_by('-timestamp')[0]
                         row_id = obj.id    
                     except: 
                         pass
                     time.sleep(1)                
                obj.slurm_output = log_file
                obj.save()

            return redirect('history:results', id=row_id)  # should be changed to result page
            
    else:
        # load data into form, when a row id is given.
        if row_id:
            h = History.objects.get(pk=row_id)
            config_dict = h.config_dict()
            f = PluginForm(tool=plugin, uid=user.getName())
            config_dict[f.caption_field_name] = h.caption
        else:
            config_dict = plugin.setupConfiguration(check_cfg=False, substitute=True)
                  
        form = PluginForm(initial=config_dict, tool=plugin, uid=user.getName())

    return render(request, 'plugins/setup.html', {'tool': plugin_web,
                                                  'form': form,
                                                  'user_home': home_dir,
                                                  'user_scratch': scratch_dir,
                                                  'error_message': error_msg,
                                                  'restricted_user': not user_can_submit,
                                                  'PREVIEW_URL': settings.PREVIEW_URL})
  

@login_required()
def dirlist(request):
    r = ['<ul class="jqueryFileTree" style="display: none;">']
    files = list()
    # we can specify an ending in GET request
    file_type = request.GET.get('file_type', 'nc')
    try:
        r = ['<ul class="jqueryFileTree" style="display: none;">']
        d = urllib.unquote(request.POST.get('dir'))
        for f in sorted(os.listdir(d)):
            if f[0] != '.':
                ff = os.path.join(d, f)
                if os.path.isdir(ff):
                    r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff, f))
                else:
                    e = os.path.splitext(f)[1][1:]  # get .ext and remove dot
                    if e == file_type:
                        files.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e, ff, f))
        r = r+files
        r.append('</ul>')
    except Exception, e:
        r.append('Could not load directory: %s' % str(e))
        r.append('</ul>')
    return HttpResponse(''.join(r))  


def list_docu(request):
    return render(request, 'plugins/list-docu.html')


@require_POST
@login_required()
def export_plugin(request):
    """
    Website version of "export EVALUATION_SYSTEM_PLUGINS=..."
    """
    try:
        del os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user]
        return redirect('plugins:home')
    except:
        fn = request.POST.get('export_file')
        if fn is not None and os.path.isfile(fn):
            parts = fn.split('/')
            path = '/'.join(parts[:-1])
            module = parts[-1].split('.')[0]
            os.environ["EVALUATION_SYSTEM_PLUGINS_%s" % request.user] =\
                "%s,%s" % (path, module)
    
    return redirect('plugins:home')
