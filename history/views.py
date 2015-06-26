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
from django.template import defaultfilters as filters

from django_evaluation.ldaptools import get_ldap_object

import json
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.model.db import UserDB
from evaluation_system.model.user import User
from evaluation_system.misc import utils

from evaluation_system.model.history.models import History, Result, ResultTag, HistoryTag
from django_evaluation import settings
from plugins.utils import ssh_call

from history.utils import FileDict, utf8SaveEncode, sendmail_to_follower, getCaption

from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.db.models import Q

import logging
from history.models import HistoryTag
import evaluation_system
from evaluation_system.model import user

from templatetags.resulttags import mask_uid


class history(DatatableView):
    model = History

    datatable_options = {
        'columns' : [('', 'checkbox', 'checkbox'),
                     ('Id', 'id'),
                     ('User', 'uid'),
                     ('Tool', 'tool'),
                     ('Caption', None, 'get_caption'),
		     #('Version', 'version'),
                     ('Timestamp', 'timestamp', helpers.format_date('%d.%m.%y %H:%M')),
                     ('Status', 'get_status_display'),
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
        plugin = self.request.GET.get('plugin', None)

        if status >= 0:
            objects = objects.filter(status=status)
     
        if flag >= 0:
            objects = objects.filter(flag=flag)
        else:
            objects = objects.filter(~Q(flag=History.Flag.deleted))

        if plugin:
            objects = objects.filter(tool=plugin)

        return objects

        # return History.objects.order_by('-id').filter(uid=user)
        # MyModel.objects.filter(user=self.request.user)

    def get_caption(self, instance, *args, **kwargs):
        (default_caption, user_caption) = getCaption(instance.id, self.request.user)
	if user_caption:
            caption = user_caption
        elif default_caption:
            caption = default_caption
        else:
            caption = ''#instance.tool
	return caption

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

        (default_caption, user_caption) = getCaption(instance.id, self.request.user)

        caption = ''

        if not user_caption is None:
            if default_caption is None:
                caption = escape(user_caption)
            elif user_caption != default_caption:
                caption = '%s<br>[%s]' % (escape(user_caption),
                                          escape(default_caption))
            else:
                caption = escape(user_caption)

        elif default_caption is not None:
            caption = escape(default_caption)


        config = '%s<br><br><table class="table-condensed">' % information
        
        # fill configuration
        try:
            # this is much faster than the routine config_dict.
            config_dict = json.loads(instance.configuration)
            for key, value in config_dict.items():
                text = escape(mask_uid(str(value), self.request.user.isGuest()))
                config = config + "<tr><td>%s</td><td>%s<td></tr>" % (key, text)
        except Exception, e:
            print "Tooltip error:", e
 
        config = config + "</table>"

        if caption:
            title = "title='%s<br><br>%s'" % (caption, config)
        else:
            title = "title='%s'" % (config,)

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
        second_button_style = 'class="btn btn-success btn-sm" style="width:80px;"'
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
            second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel" style="width:80px;"'

            second_button_href = 'onclick="cancelDialog.show(%i);"' % instance.id

            # disable button for manually started jobs
            if instance.slurm_output == '0':
                second_button_text = 'n/a'
                second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel disabled" style="width:80px;"'
                second_button_href = ''

            # disable button when its not the user's job
            if instance.uid != self.request.user:
                second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel disabled" style="width:80px;"'
                second_button_href = ''

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
 
        plugin = self.request.GET.get('plugin', None)

        ajax_url = ''

        if plugin:
            ajax_url = (self.request.path +
                        "?status={status}".format(status=status) +
                        "&flag={flag}".format(flag=flag) +
                        "&plugin={plugin}".format(plugin=plugin))
        else:
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
  
                # notify followers
                if int(flag) == int(History.Flag.deleted):
                    try:
                        name = '%s %s' % (request.user.first_name, request.user.last_name)
                 
                        subject = 'Deleted evaluation'
                        message = 'The evaluation %s you are following has been deleted by %s.\n' % (str(id), name)
                    
                        sendmail_to_follower(request, id, subject, message)
                    except Exception, e:
                        logging.error(e)
    
            except:
                changed -= 1
                
    retstr = ''

    if changed != len(ids):
        retstr = 'Changed %i of %i entries' % (changed, len(ids))

    return HttpResponse(retstr, content_type="text/plain")


@login_required
def followResult(request, history_id):
    retstr = 'Follow'
    
    history_object = get_object_or_404(History, id=history_id)


    # check if the user has the permission to access the result
    flag = history_object.flag
    guest = request.user.isGuest()
    
    
    if not guest and flag in [History.Flag.free,
                              History.Flag.public,
                              History.Flag.guest]:
    
        
        user = str(request.user)
        pm.followHistoryTag(history_object.id, user, 'Web page: follow')
        
        retstr = 'Unfollow'

    return HttpResponse(retstr, content_type="text/plain")

@login_required
def unfollowResult(request, history_id):
    '''
    This routine renders the unfolle view.
    When the get paramater "button" is given, only
    the strings "Follow" and "Unfollow" will be returned.
    This is used for the button in the result view.
    '''
    retstr = 'Unfollow'
    success = False
    
    history_object = get_object_or_404(History, id=history_id)


    user = str(request.user)
    try:
        pm.unfollowHistoryTag(history_object.id, user)
        retstr = 'Follow'
        success = True
    except:
        pass
      
    if request.GET.get('button', None):
        return HttpResponse(retstr, content_type="text/plain")

    else:
        return render(request, 'history/unfollow.html', {'success' : success,
                                                         'history_id' : history_id})




@login_required
def jobinfo(request, id):
    return results(request, id, True)

def results(request, id, show_output_only = False):
    from history.utils import pygtailwrapper
    
    
    #get history object
    history_object = get_object_or_404(History, id=id)
    print 'al'
    plugin = pm.getPluginInstance(history_object.tool)
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

            file_content = utf8SaveEncode(file_content)
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
    
    
    (default_caption, user_caption) = getCaption(id, request.user)
    
    if default_caption is None:
        default_caption = history_object.tool.upper()

    result_caption = default_caption
        
    if not user_caption is None:
        result_caption = user_caption

    htag_notes = None
    follow_string = 'Follow'


    historytag_objects = HistoryTag.objects.filter(history_id_id=id)

    try:
        htag_notes = historytag_objects.filter((Q(uid=request.user) & Q(type=HistoryTag.tagType.note_private)) | Q(type=HistoryTag.tagType.note_public)).order_by('id')

    except Exception, e:
	logging.error(e)

    try:
        follow = historytag_objects.filter(Q(uid=request.user) & Q(type=HistoryTag.tagType.follow))

        if len(follow) > 0:
            follow_string = 'Unfollow'

    except Exception, e:
	logging.error(e)

    return render(request, 'history/results.html', {'history_object': history_object,
                                                    'result_object' : result_object,
                                                    'result_caption' : result_caption,
                                                    'default_caption' : default_caption, 
                                                    'file_content' : file_content,
                                                    'collapse' : collapse,
                                                    'PREVIEW_URL' : settings.PREVIEW_URL,
                                                    'file_list' : file_tree ,
                                                    'documentation' : documentation,
                                                    'analyze_command' : analyze_command,
                                                    'api_repos' : api_repos,
                                                    'tool_repos' : tool_repos,
                                                    'api_version' : api_version,
                                                    'tool_version' : tool_version,
                                                    'notes' : htag_notes,
                                                    'follow' : follow_string,
						    'developer': plugin.tool_developer})
        
        
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
    else:
         # encode to utf8
         new_lines = utf8SaveEncode(new_lines)
    
    return HttpResponse(json.dumps(new_lines), content_type="application/json")
    
@login_required()
def generate_caption(request, id, type): 
    caption = request.POST['caption'].strip() 
    toolname = request.POST['tool'].strip().capitalize() 
 
    retval = pm.generateCaption(caption, toolname)
    

    # change type to integer
    type = int(type)

    if not request.user.isGuest():
        db = UserDB(request.user)

        caption_type = HistoryTag.tagType.caption
        user = str(request.user)

        if type == 2 and History.objects.get(id=id).uid == request.user:
            db.addHistoryTag(id, caption_type, retval)
        if type in [1,2]:
            # try to find an existing caption
            tag_id = None
            try:
                tag_obj = HistoryTag.objects.filter(history_id_id=id).filter(type=HistoryTag.tagType.caption)
                tag_id = tag_obj.filter(uid=user).order_by('-id')[0].id
            except:
                pass
            
            if tag_id:
                db.updateHistoryTag(tag_id, caption_type, retval, user)
            else:
                db.addHistoryTag(id, caption_type, retval, user)
        else:
            retval = '*' + retval
 
    else:
        retval = '*' + retval
 
    return HttpResponse(json.dumps(retval), content_type="application/json")    

@sensitive_post_parameters('password')
@login_required()
def cancelSlurmjob(request):

    from paramiko import AuthenticationException
    history_item = History.objects.get(pk=request.POST['id'])
    if history_item.status < 3:
        return HttpResponse(json.dumps('Job already finished'), content_type="application/json")
    
    slurm_id = history_item.slurmId() 

    try:
        result = ssh_call(username=request.user.username, password=request.POST['password'], command='bash -c "source /client/etc/profile.miklip > /dev/null; scancel -Q %s 2>&1;exit 0"' % (slurm_id,), hostnames=settings.SCHEDULER_HOSTS)
        #logging.debug(result[1].readlines())
        history_item.status=2
        history_item.save()
        return HttpResponse(json.dumps(result[2].readlines()), content_type="application/json")
    except AuthenticationException:
        return HttpResponse(json.dumps('wrong password'), content_type="application/json")    
    
@login_required()
def send_mail_to_developer(request):
    from templated_email import send_templated_mail
    
    text = request.POST.get('text',None)
    tool_name = request.POST.get('tool_name',None)
    
    tool = pm.getPluginInstance(tool_name)
    developer = tool.tool_developer
    
    user_info = get_ldap_object() 
    myinfo = user_info.get_user_info(str(request.user))
    myemail = myinfo[3]
    
    a=send_templated_mail(
        template_name='mail_to_developer',
        from_email=myemail,
        recipient_list=[developer['email']],
        context={
            'username':request.user.get_full_name(),
            'developer_name':developer['name'],
            'text':text,
            'tool_name': tool_name,
            'mail': myemail
        },
        # Optional:
        cc=[a[1] for a in settings.ADMINS],
        # bcc=['bcc@example.com'],
        headers={'Reply-To' : myemail},
        # template_prefix="my_emails/",
        # template_suffix="email",
    )
    return HttpResponse(True)
        
    
@login_required()
def sendMail(request):
    import base64
    import json

    def createText(names, user_text):
        text = ''
        
        if isinstance(names, list):
            text = 'Dear %s,\n\n' % ',\nDear '.join(names)
        else:
            text = 'Dear %s\n\n' % names

        text += 'you can access my new results from the MiKlip evaluation system\'s web page.\n'
        text += '%s\n\n' % url
        
        if user_text:
            text += 'Message from the user:\n%s\n\n' % user_text
            
        text += 'Best regards,\n%s %s\n\n\n' % (request.user.first_name, request.user.last_name)
        
        text += '--------------------------------------------------------------------------------\n'
        text += 'This email has been automatically generated by the web server of the\n'
        text += 'MiKlip evaluation system (www-miklip.dkrz.de)'
        
        return text
    
    def sendIt(myemail, name, toemail, subject, text):
        replyto = {'Reply-To' : myemail}
        from_email = myemail
    
        try:
            email = EmailMessage(subject,
                                 text,
                                 from_email,
                                 toemail,
                                 headers = replyto)
    
            email.send()
    
            status = 'Shared with %s\n' % (name,)
        except Exception, e:
            logging.error('EMAIL ERROR: ' + str(e))
            status = 'WARNING: Sharing with %s failed!\n' % name

        return status

    # return special response for guest users
    if request.user.isGuest():
        status = 'Normally, the selected recipients would get an email containing a link to this result,'
        status += 'but this feature is turned off for guest users.'
        return HttpResponse(status)

    action = request.POST['action']
    rec = request.POST['rec'].split(',')
    user_text = request.POST['text']
    one4all = request.POST.get('one4all', 'off')
    copy4me = request.POST.get('copy4me', 'off')
    
    # the one4all option will be automatically set, when only one recipient is in the list.
    if len(rec) == 1:
        one4all = "on"

    status = ""
    addresses = []
    names = []

    user_info = get_ldap_object() 


    myinfo = user_info.get_user_info(str(request.user))
    myemail = myinfo[3]
    myname = "%s %s" % (myinfo[2], myinfo[1])
    
    for uid in rec:
        info= user_info.get_user_info(uid)
        names.append("%s %s" % (info[2], info[1]))
        addresses.append(info[3])
        
    
    # only append the address, when the mail goes to multiple users
    if copy4me == 'on' and one4all == 'on':
        addresses.append(myemail)


    if action == 'results':
        url = request.POST['url']
        subject = '%s %s shares results with you' % (request.user.first_name, request.user.last_name)

        if one4all == 'on':
            text = createText(names, user_text)
            toname = ', '.join(names)
            status += sendIt(myemail, toname, addresses, subject, text)
        else:
            for index in range(len(addresses)):
                toemail = [addresses[index]]
                toname = names[index]
                text = createText(toname, user_text)
                status += sendIt(myemail, toname, toemail, subject, text)
   

            if copy4me == 'on':
                toemail = [myemail,]
                text = 'This is a copy of the email, which has been sent to:\n%s\n\n' % (', '.join(names),)
                text += createText(myname, user_text)
                status += sendIt(myemail, myname, toemail, subject, text)

    return HttpResponse(status)

@login_required
def result_comments(request, history_id):
    htag_notes = None

    try:
        historytag_objects = HistoryTag.objects.filter(history_id_id=history_id)
        htag_notes = historytag_objects.filter((Q(uid=request.user) &
                                                Q(type=HistoryTag.tagType.note_private)) |
                                               Q(type=HistoryTag.tagType.note_public)).order_by('-id')
    except HistoryTag.DoesNotExist:
        pass

    except:
        pass

    return render(request, 'history/comments.html', {'history_id' : history_id,
                                                     'notes' : htag_notes,})

@login_required()
def edit_htag(request, history_id, tag_id): 
    from django.template import defaultfilters as filters
    text = request.POST['text'].strip()
    type = int(request.POST['type'])

    allowed_types = [HistoryTag.tagType.note_public,
                     HistoryTag.tagType.note_private,
                     HistoryTag.tagType.note_deleted,]

    retval = ''

    if not request.user.isGuest() and type in allowed_types:
        user = request.user
        db = UserDB(user)

        if tag_id=='0':
            db.addHistoryTag(history_id, type, text, user)
            
        elif HistoryTag.objects.get(id=tag_id).uid == user:
            db.updateHistoryTag(tag_id, type, text, user.username)
            
        retval = filters.linebreaks(filters.escape(text))
 
        # notify followers
        name = '%s %s' % (request.user.first_name, request.user.last_name)
        url =request.build_absolute_uri(reverse('history:results', kwargs={'id': history_id}))
         
        if type==HistoryTag.tagType.note_public:
            if tag_id=='0':
                subject = 'New comment'
                message = '%s added new comment to the results of the evaluation %s\n' % (name, history_id)
                message += url
                
            else:
                subject = 'Edited comment'
                message = '%s edited comment %s beloning to the results of the evaluation %s\n' % (name, tag_id, history_id)
                message += url
            
            sendmail_to_follower(request, history_id, subject, message)
            

 
    return HttpResponse(json.dumps(retval), content_type="application/json")    


def count_notes(request, history_id, deleted): 
    count = 0

    history_tags = None

    if request.user.is_authenticated():
        try:
            history_tags = HistoryTag.objects.filter(history_id_id=history_id)
    
            count += history_tags.filter(type=HistoryTag.tagType.note_public).count()
            count += history_tags.filter(type=HistoryTag.tagType.note_private).filter(uid=request.user).count()
        except Exception, e:
            pass

    if int(deleted):
        try:
            count += history_tags.filter(type=HistoryTag.tagType.note_deleted).filter(uid=request.user).count()
        except:
            pass

    return HttpResponse(str(count), content_type="text/plain")    
