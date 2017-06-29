from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.flatpages.models import FlatPage
from django.utils.html import escape
from datatableview import helpers
from datatableview.views import XEditableDatatableView
from datatableview.utils import get_datatable_structure

from django_evaluation.ldaptools import get_ldap_object

import json
import os

import evaluation_system.api.plugin_manager as pm
from evaluation_system.model.db import UserDB
from evaluation_system.misc import config

from evaluation_system.model.history.models import History, ResultTag
from django_evaluation import settings
from plugins.utils import ssh_call, get_scheduler_hosts

from history.utils import FileDict, utf8SaveEncode, sendmail_to_follower

from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage
from django.db.models import Q
from django.core.urlresolvers import reverse

import logging
from history.models import HistoryTag

from templatetags.resulttags import mask_uid


class HistoryTable(XEditableDatatableView):
    model = History

    datatable_options = {
        'columns': [
            ('', 'checkbox', 'checkbox'),
            ('Id', 'id'),
            ('User', 'uid'),
            ('Plugin', 'tool'),
            ('Caption', 'caption', helpers.make_xeditable()),
            # the timestamp year search bug is fixed in django-datatable-view==0.8.3
            ('Timestamp', 'timestamp', helpers.format_date('%d.%m.%y %H:%M')),
            ('Status', 'get_status_display'),
            ('Info', 'configuration', 'info_button')
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

    def checkbox(self, instance, *args, **kwargs):
        id = "cb_%i" % instance.id
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
            button_text = 'Info'

        try:
            url = reverse('history:jobinfo', args=[instance.id])
            href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))

        tooltip_style = "data-toggle='tooltip' data-placement='left'"

        caption = instance.caption if instance.caption else ''

        config = '%s<br><br><table class="table-condensed blacktable">' % information
        
        # fill configuration
        try:
            # this is much faster than the routine config_dict.
            config_dict = json.loads(instance.configuration)
            for key, value in config_dict.items():
                text = escape(mask_uid(str(value), self.request.user.isGuest()))
                config += '<tr class="blacktable"><td class="blacktable">%s</td><td class="blacktable">%s<td></tr>' \
                          % (key, text)
        except Exception, e:
            print "Tooltip error:", e
 
        config += "</table>"

        if caption:
            title = "title='%s<br><br>%s'" % (caption, config)
        else:
            title = "title='%s'" % (config,)

        info_button = "<a %s %s %s %s style='width:35px; padding-left:5px'>%s</a>" % (
                css_class, href, tooltip_style, title, button_text)

        result_text = 'Results'
        style = "class='btn btn-success btn-sm' style='width:70px'"

        try:
            url = reverse('history:results', args=[instance.id])
            href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))
        
        second_button_text = 'Edit Config'
        second_button_style = 'class="btn btn-success btn-sm" style="width:70px; padding-left:3px;"'

        try:
            url = reverse('plugins:setup', args=[instance.tool, instance.id])
            second_button_href = "href='%s'" % url
        except Exception, e:
            return escape(str(e))

        if instance.status in [instance.processStatus.finished_no_output,
                               instance.processStatus.broken,
                               instance.processStatus.not_scheduled]:
            result_text = 'Report'

        elif instance.status in [instance.processStatus.scheduled,
                                 instance.processStatus.running]:
            result_text = 'Progress'
            second_button_text = 'Cancel Job'
            second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel" style="width:70px; padding-left:3px;"'

            second_button_href = 'onclick="cancelDialog.show(%i);"' % instance.id

            # disable button for manually started jobs
            if instance.slurm_output == '0':
                second_button_text = 'n/a'
                second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel disabled" style="width:70px; padding-left:3px;"'
                second_button_href = ''

            # disable button when its not the user's job
            if instance.uid != self.request.user:
                second_button_style = 'class="btn btn-danger btn-sm mybtn-cancel disabled" style="width:70px; padding-left:3px;"'
                second_button_href = ''

        result_button = "<a  %s %s>%s</a>" % (style, href, result_text)

        second_button = "<a %s %s>%s</a>" % (second_button_style,
                                             second_button_href,
                                             second_button_text,)

        return '%s\n%s\n%s' % (result_button, second_button, info_button)

    template_name = 'history/history_list.html'

    def get_datatable(self):
        """
        Customized implementation of the structure getter.  The custom argument ``type`` is managed
        by us, and is used in the context and GET parameters to control which table we return.
        """

        datatable_options = self.get_datatable_options()

        status = int(self.request.GET.get('status', -1))

        flag = int(self.request.GET.get('flag', -1))
 
        plugin = self.request.GET.get('plugin', None)

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
        context = super(HistoryTable, self).get_context_data(**kwargs)

        flag = int(self.request.GET.get('flag', -1))
        status = int(self.request.GET.get('status', -1))
        uid = self.kwargs.get('uid', self.request.user)

        context['STATUS_CHOICES'] = History.STATUS_CHOICES
        context['flag'] = flag
        context['status'] = status
        context['uid'] = uid

        return context


@login_required
def change_flag(request):
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
            # TODO: Exception too broad!
            except:
                changed -= 1
                
    retstr = ''
    if changed != len(ids):
        retstr = 'Changed %i of %i entries' % (changed, len(ids))

    return HttpResponse(retstr, content_type="text/plain")


@login_required
def follow_result(request, history_id):
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
def unfollow_result(request, history_id):
    """
    This routine renders the unfollow view.
    When the get parameter "button" is given, only
    the strings "Follow" and "Unfollow" will be returned.
    This is used for the button in the result view.
    """
    retstr = 'Unfollow'
    success = False
    
    history_object = get_object_or_404(History, id=history_id)

    user = str(request.user)
    try:
        pm.unfollowHistoryTag(history_object.id, user)
        retstr = 'Follow'
        success = True
    # Todo: Exception too broad!
    except:
        pass
      
    if request.GET.get('button', None):
        return HttpResponse(retstr, content_type="text/plain")
    else:
        return render(request, 'history/unfollow.html', {'success': success,
                                                         'history_id': history_id})


@login_required
def jobinfo(request, id):
    return results(request, id, True)


def results(request, id, show_output_only=False):
    from history.utils import pygtailwrapper

    # get history object
    history_object = get_object_or_404(History, id=id)
    try:
        plugin = pm.getPluginInstance(history_object.tool,
                                      user_name=request.user.username)
        developer = plugin.tool_developer
    # TODO: Exception too broad!
    except:
        developer = None
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
            elif not (request.user.has_perm('history.results_view_others') and flag in [History.Flag.public,
                                                                                        History.Flag.shared,
                                                                                        History.Flag.guest]):
                raise PermissionDenied
    if not request.user.is_authenticated():
        request.user.isGuest = True


    try:
        documentation = FlatPage.objects.get(title__iexact=history_object.tool)
    except FlatPage.DoesNotExist:
        documentation = None
    try:
        logging.debug(history_object.uid.email)
    # TODO: Exception too broad!
    except:
        pass

    try:
        analyze_command = pm.getCommandString(int(id))
    except Exception, e:
        logging.debug(e)
    analyze_command = pm.getCommandString(int(id))

    history_object = History.objects.get(id=id)
    file_content = []

    # ensure that this process has been started with slurm
    if history_object.slurm_output == '0':
        file_content = ['This job has been started manually.', 'No further information is available.']
        
    else:
        # for a read-protected directory this will fail
        try:
            for line in pygtailwrapper(id, restart=True):
                file_content.append(line)
            file_content = utf8SaveEncode(file_content)
        except IOError:
            file_content = ['WARNING:',
                            'This is not the content of the file \'' + history_object.slurm_output + '\'.',
                            'Probably, your home directory denies read access to the file.',
                            'In this case the results will be shown after the tool has finished.',
                            'You can view the tool\'s progress in a terminal with the command',
                            'tail -f ' + history_object.slurm_output]
            
            # make sure that the file exists
            try:
                if not os.path.isfile(history_object.slurm_output):
                    file_content = ['Can not locate the slurm file \'%s\'' % history_object.slurm_output]
            except IOError:
                pass

    # init result object
    result_object = -1
    file_tree = None

    collapse = []
    
    if history_object.status in [History.processStatus.finished, History.processStatus.finished_no_output]:
        result_object = history_object.result_set.filter(~Q(preview_file='')).order_by('output_file')
        
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
        if len(file_tree) == 0:
            collapse.append('output')
    else:
        collapse.append('output')

    if show_output_only:
        collapse = ['output']

    # repository stuff
    try:
        repos = history_object.version_details.repository
    except ObjectDoesNotExist:
        repos = 'Not available;Not available'
    tool_repos = repos.split(';')[0]
    api_repos = repos.split(';')[1]
    try:
        tool_version = history_object.version_details.internal_version_tool
        api_version = history_object.version_details.internal_version_api
    except ObjectDoesNotExist:
        tool_version = 'Not available'
        api_version = 'Not available'
    result_caption = history_object.caption
    if result_caption is None:
        result_caption = history_object.tool.upper()

    htag_notes = None
    follow_string = 'Follow'

    historytag_objects = HistoryTag.objects.filter(history_id_id=id)

    try:
        htag_notes = historytag_objects.filter(
            (Q(uid=request.user) & Q(type=HistoryTag.tagType.note_private)) | Q(type=HistoryTag.tagType.note_public)
        ).order_by('id')

    except Exception, e:
        logging.error(e)

    try:
        follow = historytag_objects.filter(Q(uid=request.user) & Q(type=HistoryTag.tagType.follow))

        if len(follow) > 0:
            follow_string = 'Unfollow'

    except Exception, e:
        logging.error(e)

    return render(request, 'history/results.html', {'history_object': history_object,
                                                    'result_object': result_object,
                                                    'result_caption': result_caption,
                                                    'file_content': file_content,
                                                    'collapse': collapse,
                                                    'PREVIEW_URL': settings.PREVIEW_URL,
                                                    'file_list': file_tree,
                                                    'documentation': documentation,
                                                    'analyze_command': analyze_command,
                                                    'api_repos': api_repos,
                                                    'tool_repos': tool_repos,
                                                    'api_version': api_version,
                                                    'tool_version': tool_version,
                                                    'notes': htag_notes,
                                                    'follow': follow_string,
                                                    'developer': developer})


@login_required()
def tail_file(request, id):
    from history.utils import pygtailwrapper

    history_object = get_object_or_404(History, id=id)
    new_lines = list()
    
    try: 
        for lines in pygtailwrapper(id):
            line = lines.replace('\n', '<br/>')
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
    tool_name = request.POST['tool'].strip().capitalize()
 
    retval = pm.generateCaption(caption, tool_name)
    
    if not request.user.isGuest():
        
        hist = History.objects.get(id=id)
        if hist.uid == request.user:
            hist.caption = retval
            hist.save()
        else:
            retval = '*' + retval
 
    else:
        retval = '*' + retval
 
    return HttpResponse(json.dumps(retval), content_type="application/json")    


@sensitive_post_parameters('password')
@login_required()
def cancel_slurmjob(request):

    from paramiko import AuthenticationException
    history_item = History.objects.get(pk=request.POST['id'])
    if history_item.status < 3:
        return HttpResponse(json.dumps('Job already finished'), content_type="application/json")
    
    slurm_id = history_item.slurmId() 

    try:
        host_names = get_scheduler_hosts(request.user)
        source_machine = settings.LOAD_MODULE
        result = ssh_call(
            username=request.user.username, password=request.POST['password'],
            command='bash -c "%s module load slurm; scancel -Q %s;exit 0"' % (source_machine, slurm_id,),
            hostnames=host_names
        )
        history_item.status = 2
        history_item.save()
        return HttpResponse(json.dumps(result[2].readlines()), content_type="application/json")
    except AuthenticationException:
        return HttpResponse(json.dumps('wrong password'), content_type="application/json")    


@login_required()
def send_mail_to_developer(request):
    from templated_email import send_templated_mail
    
    text = request.POST.get('text', None)
    tool_name = request.POST.get('tool_name', None)
    
    tool = pm.getPluginInstance(tool_name, user_name=request.user.username)
    developer = tool.tool_developer
    
    user_info = get_ldap_object() 
    myinfo = user_info.get_user_info(str(request.user))
    try:
        my_email = myinfo[3]
        username = request.user.get_full_name()
    # TODO: Exception too broad!
    except:
        my_email = settings.SERVER_EMAIL
        username = 'guest'   
    send_templated_mail(
        template_name='mail_to_developer',
        from_email=my_email,
        recipient_list=[developer['email']],
        context={
            'username': username,
            'developer_name': developer['name'],
            'text': text,
            'tool_name': tool_name,
            'mail': my_email,
            'project': config.get('project_name'),
            'website': config.get('project_website')
        },
        cc=[a[1] for a in settings.ADMINS],
        headers={'Reply-To': my_email},
    )
    return HttpResponse(True)
        
    
@login_required()
def send_share_email(request):

    def create_text(names, user_text):
        text = ''
        
        if isinstance(names, list):
            text = 'Dear %s,\n\n' % ',\nDear '.join(names)
        else:
            text = 'Dear %s\n\n' % names

        text += 'you can access my new results from Freva\'s web page.\n'
        text += '%s\n\n' % url
        
        if user_text:
            text += 'Message from the user:\n%s\n\n' % user_text
            
        text += 'Best regards,\n%s %s\n\n\n' % (request.user.first_name, request.user.last_name)
        
        text += '--------------------------------------------------------------------------------\n'
        project = config.get('project_name')
        website = config.get('project_website')
        text += 'This email has been automatically generated by the web server of the\n'
        text += '%s evaluation system (%s)' % (project, website)
        
        return text
    
    def send_it(myemail, name, toemail, subject, text):
        replyto = {'Reply-To': myemail}
        from_email = myemail
    
        try:
            email = EmailMessage(subject,
                                 text,
                                 from_email,
                                 toemail,
                                 headers=replyto)
    
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
        info = user_info.get_user_info(uid)
        names.append("%s %s" % (info[2], info[1]))
        addresses.append(info[3])

    # only append the address, when the mail goes to multiple users
    if copy4me == 'on' and one4all == 'on':
        addresses.append(myemail)

    if action == 'results':
        url = request.POST['url']
        subject = '%s %s shares results with you' % (request.user.first_name, request.user.last_name)

        if one4all == 'on':
            text = create_text(names, user_text)
            toname = ', '.join(names)
            status += send_it(myemail, toname, addresses, subject, text)
        else:
            for index in range(len(addresses)):
                toemail = [addresses[index]]
                toname = names[index]
                text = create_text(toname, user_text)
                status += send_it(myemail, toname, toemail, subject, text)

            if copy4me == 'on':
                toemail = [myemail]
                text = 'This is a copy of the email, which has been sent to:\n%s\n\n' % (', '.join(names),)
                text += create_text(myname, user_text)
                status += send_it(myemail, myname, toemail, subject, text)

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

    return render(request, 'history/comments.html', {'history_id': history_id,
                                                     'notes': htag_notes})


@login_required()
def edit_htag(request, history_id, tag_id): 
    from django.template import defaultfilters as filters
    text = request.POST['text'].strip()
    type = int(request.POST['type'])

    allowed_types = [HistoryTag.tagType.note_public,
                     HistoryTag.tagType.note_private,
                     HistoryTag.tagType.note_deleted]

    retval = ''

    if not request.user.isGuest() and type in allowed_types:
        user = request.user
        db = UserDB(user)

        if tag_id == '0':
            db.addHistoryTag(history_id, type, text, user)
            
        elif HistoryTag.objects.get(id=tag_id).uid == user:
            db.updateHistoryTag(tag_id, type, text, user.username)
            
        retval = filters.linebreaks(filters.escape(text))
 
        # notify followers
        name = '%s %s' % (request.user.first_name, request.user.last_name)
        url = request.build_absolute_uri(reverse('history:results', kwargs={'id': history_id}))
         
        if type == HistoryTag.tagType.note_public:
            if tag_id == '0':
                subject = 'New comment'
                message = '%s added new comment to the results of the evaluation %s\n' % (name, history_id)
                message += url
                
            else:
                subject = 'Edited comment'
                message = '%s edited comment %s belonging to the results of the evaluation %s\n' % (
                    name, tag_id, history_id)
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
        # TODO: Exception too broad!
        except Exception, e:
            pass

    if int(deleted):
        try:
            count += history_tags.filter(type=HistoryTag.tagType.note_deleted).filter(uid=request.user).count()
        # TODO: Exception too broad!
        except:
            pass

    return HttpResponse(str(count), content_type="text/plain")    


@login_required()
def result_browser(request):
    return render(request, 'plugins/list.html', {'title': 'Result Browser'})