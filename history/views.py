from django.shortcuts import render
from django.http import HttpResponse
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
from evaluation_system.model.db import _result_preview
from evaluation_system.model.user import User
from evaluation_system.misc import utils

from models import History, Result, ResultTag
from django_evaluation import settings
from plugins.utils import ssh_call

from history.utils import FileDict

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

import logging




@login_required()
def history(request):
    user = request.GET.get('uid', None)

    if not (user and request.user.has_perm('history.results_view_others')):
        user = request.user
    
    
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

class history_view(TemplateView):
    template_name = 'history/history_list.html'

    def get_context_data(self, **kwargs):
        context = super(history_view, self).get_context_data(**kwargs)
 
        htable = history_table()
        options = htable.get_datatable_options()
        datatable = get_datatable_structure('table', options)
 
        context['datatable'] = datatable
        context['user'] = self.kwargs.get('uid', None)
        return context
 

# @login_required
class history_table(DatatableView):
    model = History

    datatable_options = {
        'columns' : [('Row Id', 'id'),
                     ('User', 'uid'),
                     ('Tool', 'tool'),
                     ('Version', 'version'),
                     ('Timestamp', 'timestamp', helpers.format_date('%d.%m.%Y %H:%M:%S')),
                     ('Status', 'status', 'display_status'),
                     ('Info', 'configuration', 'info_button'),
                    ]
    } 

    def get_queryset(self):
        user = None
        user = self.datatable_options.get('uid', None)
        if not (user and
                self.request.user.has_perm('history.results_view_others')):
            user = self.request.user

        # status = self.get_context_data().get('filter_status', None)

        status = self.datatable_options.get('status', 0)
     
        print 'STATUS STATUS STATUS:', status, user

        # return History.objects.all()
        if status:
            return History.objects.order_by('-id').filter(uid=user).filter(status=status)

        return History.objects.order_by('-id').filter(uid=user)
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
@login_required
def jobinfo(request, id):
    return results(request, id, True)

@login_required()
def results(request, id, show_output_only = False):
    from history.utils import pygtailwrapper
    
    
    #get history object
    history_object = get_object_or_404(History, id=id)
    try:
        documentation = FlatPage.objects.get(title__iexact=history_object.tool)
    except FlatPage.DoesNotExist:
        documentation = None

    # check user permissions
    if str(history_object.uid) != str(request.user.username):
        if not request.user.has_perm('history.results_view_others'):
            raise PermissionDenied
    
    
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
    file_list = None

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
        
        file_list = file_tree.get_list()

        collapse.append('results')

    else:
        collapse.append('output')

    if show_output_only:
        collapse = ['output']
        
    return render(request, 'history/results.html', {'history_object': history_object,
                                                    'result_object' : result_object,
                                                    'file_content' : file_content,
                                                    'collapse' : collapse,
                                                    'PREVIEW_URL' : settings.PREVIEW_URL,
                                                    'file_list' : file_tree ,
                                                    'documentation' : documentation,
                                                    'analyze_command' : analyze_command})
        
        
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
    #slurm_id=2151
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

            try:
                send_mail(subject=subject, message=text, from_email = from_email, recipient_list = to_email)
                status = '%sSent to %s<br>' % (status, names[index])
            except Exception, e:
                print e
                status = '%s<font color="red">WARNING: Not sent to %s</font><br>' % (status, names[index])

            index = index + 1

        status = status + "</p>"
    return HttpResponse(status)

