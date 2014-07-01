from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.flatpages.models import FlatPage
from django.utils.html import escape
import datatableview
from datatableview import helpers
from datatableview.views import DatatableView
from datatableview.utils import get_datatable_structure
from django.views.generic.base import TemplateView

from django_evaluation.ldaptools import miklip_user_information

import json
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.model.db import _result_preview, UserDB
from evaluation_system.model.user import User
from evaluation_system.misc import utils

from models import History, Result, ResultTag
from django_evaluation import settings
from plugins.utils import ssh_call

from history.utils import FileDict

from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.db.models import Q

import logging




class history(DatatableView):
    model = History

    datatable_options = {
        'columns' : [('', '', 'checkbox'),
                     ('Id', 'id'),
                     ('User', 'uid'),
                     ('Tool', 'tool'),
                     ('Version', 'version'),
                     ('Timestamp', 'timestamp', helpers.format_date('%d.%m.%Y %H:%M:%S')),
                     ('Status', 'status', 'display_status'),
                     ('Info', 'configuration', 'info_button'),
                    ]
    } 

    def get_queryset(self):
        user = self.kwargs.get('uid', self.request.user)

        if not (user and
                self.request.user.has_perm('history.results_view_others')):
            user = self.request.user


        objects = History.objects.order_by('-id').filter(uid=user)

        status = int(self.request.GET.get('status', -1))
        flag = int(self.request.GET.get('flag', -1))

        if status >= 0:
            objects = objects.filter(status=status)
     
        if flag >= 0:
            objects = objects.filter(flag=flag)
        else:
            objects = objects.filter(~Q(flag=History.Flag.deleted))

        return objects

        # return History.objects.order_by('-id').filter(uid=user)
        # MyModel.objects.filter(user=self.request.user)

    # def get_context_data(self, **kwargs):
        # context = super(DatatableView, self).get_context_data(**kwargs)

        # try:
        #     pass
            # context['filter_status'] = request.GET['status']
        # except:
        #     pass

        # return context

    def display_status(self, instance, *args, **kwargs):
        return instance.get_status_display()

    def checkbox(self, instance, *args, **kwargs):
        id = "cb_%i"  % instance.id
        cb = '<input type="checkbox" id="%s" class="chksel">' % id
        return cb

    def info_button(self, instance, *args, **kwargs):
        # default text and format (scheduled jobs)
        information = 'Information to scheduled job:'
        css_class = "class='btn btn-primary btn-sm ttbtn'"
        button_text = 'Info'

        # change things for manually started jobs slightly
        if instance.slurm_output == '0':
            information = 'Restricted information to manually started job:'
            css_class = "class='btn btn-info btn-sm ttbtn'"
            button_text = 'info'

        try:
            url = reverse('history:jobinfo', args=[instance.id])
            href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))

        tooltip_style = "data-toggle='tooltip' data-placement='left'"

        config = '%s<br><br><table class="table-condensed">' % information
        
        # fill configuration
        try:
            for key, value in instance.config_dict().items():
                config = config + "<tr><td>%s</td><td>%s<td></tr>" % (key, escape(str(value)))
        except Exception, e:
            print "Tooltip error:", e
 
        config = config + "</table>"

        title = "title='%s'" % config

        info_button = "<a %s %s %s %s>%s</a>" % (css_class,
                                                 href,
                                                 tooltip_style,
                                                 title,
                                                 button_text)


        result_text = 'Results'
        style = "class='btn btn-success btn-sm' style='width:80px'"

        try:
            url = reverse('history:results', args=[instance.id])
            href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))
        
        second_button_text = 'Edit Config'
        second_button_style = 'class="btn btn-success btn-sm" style="width:90px;"'
        second_button_onclick = ''

        try:
            url = reverse('plugins:setup', args=[instance.tool, instance.id])
            second_button_href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))
        


        if instance.status in [instance.processStatus.finished_no_output,
                               instance.processStatus.broken,
                               instance.processStatus.not_scheduled,
                              ]:
             result_text = 'Report'

        elif instance.status in [instance.processStatus.scheduled,
                                 instance.processStatus.running,
                                ]:
            result_text = 'Progress'
            second_button_text = 'Cancel Job'
            second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel" style="width:90px;"'

            second_button_href = 'onclick="cancelDialog.show(%i);"' % instance.id

        result_button = "<a  %s %s>%s</a>" % (style, href, result_text)

        second_button = "<a %s %s>%s</a>" % (second_button_style,
                                             second_button_href,
                                             second_button_text,)

        return '%s\n%s\n%s' % (result_button, second_button, info_button)


    template_name = 'history/history_list.html'

    # def get_datatable(self, uid=None, flag=None, status=None):
    def get_datatable(self):
        """
        Customized implementation of the structure getter.  The custom argument ``type`` is managed
        by us, and is used in the context and GET parameters to control which table we return.
        """

        datatable_options = self.get_datatable_options()

        uid = self.kwargs.get('uid', self.request.user)

        status = int(self.request.GET.get('status', -1))

        flag = int(self.request.GET.get('flag', -1))
 
        ajax_url = (self.request.path +
                    "?status={status}".format(status=status) +
                    "&flag={flag}".format(flag=flag))
 
        datatable = get_datatable_structure(ajax_url, datatable_options)
 
        return datatable


    def get_context_data(self, **kwargs):
        context = super(history, self).get_context_data(**kwargs)

        flag = int(self.request.GET.get('flag', -1))
        status = int(self.request.GET.get('status', -1))
        uid = self.kwargs.get('uid', self.request.user)
 

        context['STATUS_CHOICES'] = History.STATUS_CHOICES
        context['flag'] = flag
        context['status'] = status
        context['uid'] = uid

        return context

# # @login_required
# class history_view(TemplateView):
#     def get_context_data(self, **kwargs):
#         context = super(history_view, self).get_context_data(**kwargs)
#         table_view = history_table()
#         options = table_view.get_datatable_options()
#         datatable = get_datatable_structure(reverse('historytable'), options)
#         context['datatable'] = datatable
#         return context




@login_required
def changeFlag(request):
    ids = json.loads(request.POST.get('ids', ''))
    flag = request.POST.get('flag', None)


    user = str(request.user)
    db = UserDB(user)

    changed = 0
    
    if not (flag is None or request.user.isGuest()):
        for id in ids:
            changed += 1
            try:
                db.changeFlag(id, user, flag)
            except:
                changed -= 1

    retstr = ''

    if changed != len(ids):
        retstr = 'Changed %i of %i entries' % (changed, len(ids))

    return HttpResponse(retstr, content_type="text/plain")


@login_required
def jobinfo(request, id):
    return results(request, id, True)

def results(request, id, show_output_only = False):
    from history.utils import pygtailwrapper
    
    
    #get history object
    history_object = get_object_or_404(History, id=id)


    # check if the user has the permission to access the result
    flag = history_object.flag

    if not flag == History.Flag.free:
        if not request.user.is_authenticated():
            from django.contrib.auth.views import redirect_to_login
            path = request.get_full_path()
            return redirect_to_login(path)

        elif not history_object.uid == request.user:
            if request.user.isGuest():
                if flag != History.Flag.guest:
                    raise PermissionDenied


            elif not (request.user.has_perm('history.results_view_others')
                      and flag in [History.Flag.public,
                                   History.Flag.shared,
                                   History.Flag.guest]):

                raise PermissionDenied

    try:
        documentation = FlatPage.objects.get(title__iexact=history_object.tool)
    except FlatPage.DoesNotExist:
        documentation = None

    try:
        logging.debug(history_object.uid.email)
    except: 
        pass

    analyze_command = 'An error occured'
    try:
        analyze_command = pm.getCommandString(int(id))
    except Exception, e:
        logging.debug(e)
    analyze_command = pm.getCommandString(int(id))

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

    # init result object
    result_object = -1
    file_tree = None

    collapse = []
    
    if history_object.status in [History.processStatus.finished, History.processStatus.finished_no_output]:
        result_object = history_object.result_set.filter(~Q(preview_file = '')).order_by('output_file')
        
        # build the file structure
        fd = FileDict()
        
        for r in result_object:
            caption = ResultTag.objects.filter(result_id_id=r.id).order_by('-id')

            result_info = {}

            result_info['preview_file'] = r.preview_file

            if caption:
                result_info['caption'] = caption[0].text

            fd.add_file(r.output_file, result_info)
    
        file_tree = fd.compressed_copy()
        file_tree.uncompress_single_files()
        
        collapse.append('results')

    else:
        collapse.append('output')

    if show_output_only:
        collapse = ['output']
        
        
    # repository stuff
    repos = history_object.version_details.repository
    
    tool_repos = repos.split(';')[0]
    api_repos= repos.split(';')[1]
    tool_version = history_object.version_details.internal_version_tool
    api_version = history_object.version_details.internal_version_api
        
    return render(request, 'history/results.html', {'history_object': history_object,
                                                    'result_object' : result_object,
                                                    'file_content' : file_content,
                                                    'collapse' : collapse,
                                                    'PREVIEW_URL' : settings.PREVIEW_URL,
                                                    'file_list' : file_tree ,
                                                    'documentation' : documentation,
                                                    'analyze_command' : analyze_command,
                                                    'api_repos' : api_repos,
                                                    'tool_repos' : tool_repos,
                                                    'api_version' : api_version,
                                                    'tool_version' : tool_version,})
        
        
@login_required()
def tailFile(request, id):
    from history.utils import pygtailwrapper

    history_object = get_object_or_404(History, id=id)
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
	result = ssh_call(username=request.user.username, password=request.POST['password'], command='bash -c "source /client/etc/profile.miklip > /dev/null; scancel  %s 2>&1;exit 0"' % (slurm_id,), hostnames=settings.SCHEDULER_HOSTS)
        #logging.debug(result[1].readlines())
	history_item.status=2
	history_item.save()
	return HttpResponse(json.dumps(result[2].readlines()), content_type="application/json")
    except AuthenticationException:
        return HttpResponse(json.dumps('wrong password'), content_type="application/json")    
    
    
    
@login_required()
def sendMail(request):
    import base64
    import json

    action = request.POST['action']
    rec = request.POST['rec'].split(',')
    user_text = request.POST['text']


    status = '<h4>Status:</h4><p>'
    addresses = []
    names = []

    user_info = miklip_user_information() 

    for uid in rec:
        info= user_info.get_user_info(uid)
        names.append("%s %s" % (info[2], info[1]))
        addresses.append(info[3])


    if action == 'results':
        url = request.POST['url']
        subject = '%s %s shares results with you' % (request.user.first_name, request.user.last_name)

        index = 0

        for addr in addresses:
            text = 'Dear %s,\n\n' % names[index]
            text += 'you can access my new results from the MiKlip evaluation system\'s web page.\n'
            text += '%s\n\n' % url

            if user_text:
                text += 'Message from the user:\n%s\n\n' % user_text
                
            text += 'Best regards,\n%s %s\n\n\n' % (request.user.first_name, request.user.last_name)
 
            text += '--------------------------------------------------------------------------------\n'
            text += 'This email has been automatically generated by the web server of the\n'
            text += 'MiKlip evaluation system (www-miklip.dkrz.de)'

            from_email = request.user.email

            to_email = [addresses[index]]

            replyto = {'Reply-To' : request.user.email}

            try:
                email = EmailMessage(subject,
                                     text,
                                     from_email,
                                     to_email,
                                     headers = replyto)

                email.send()

                status = '%sSent to %s<br>' % (status, names[index])
            except Exception, e:
                print e
                status = '%s<font color="red">WARNING: Not sent to %s</font><br>' % (status, names[index])

            index = index + 1

        status = status + "</p>"
    return HttpResponse(status)

