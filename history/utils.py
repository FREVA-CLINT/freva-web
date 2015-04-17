import os

from evaluation_system.misc import utils
from models import History, HistoryTag
from django_evaluation import settings
# from contrib.comments.views.moderation import delete


def getCaption(history_id, user):
    """    
    This function returns a tuple with default and user caption
    :type history_id: int
    :param history_id: the id of the history record
    :type user: user object
    :param user: the user to get individual captions

    """
    
    default_caption = None
    user_caption = None
    
    caption_objects = None
    defaultcaption_object = None
    usercaption_object = None
    historytag_objects = None

    try:
        historytag_objects = HistoryTag.objects.filter(history_id_id=history_id)
        caption_objects = historytag_objects.filter(type=HistoryTag.tagType.caption) 
    except HistoryTag.DoesNotExist:
        pass
    
    
    # check for a user defined caption
    if caption_objects:
        try:
            usercaption_object = caption_objects.filter(uid=user)
        except:
            pass
        try:
            defaultcaption_object = caption_objects.filter(uid=None)
        except:
            pass
    
    
    if usercaption_object:
        user_caption = usercaption_object.order_by('-id')[0].text

    if defaultcaption_object:
        default_caption = defaultcaption_object.order_by('-id')[0].text
        
    return (default_caption, user_caption)
  

def pygtailwrapper(id, restart = False):
    """
    This function return the pygtail result for the slurm file
    specified in the history
    """
    from pygtail import Pygtail

    history_object = History.objects.get(id=id)
    full_file_name = history_object.slurm_output
        
    # path for the offset file
    utils.supermakedirs(settings.TAIL_TMP_DIR, 0777)
    
    file_name = os.path.basename(full_file_name)
    
    # offset file
    offset_file_name = os.path.join(settings.TAIL_TMP_DIR, file_name)
    offset_file_name = offset_file_name + '.offset'
    
    if restart and os.path.isfile(offset_file_name):
        os.remove(offset_file_name)
    
    
    return Pygtail(full_file_name, offset_file=offset_file_name)    

class FileDict(dict):
    """
    This class ease the browsing through a bunch of files in several directories.
    """
    def _add_file(self, split_path, value):
        if len(split_path)==1:
            self[split_path[0]] = value
        else:
            fdict = self.get(split_path[0], None)

            if not isinstance(fdict, FileDict):
                fdict = FileDict()
                     
            self[split_path[0]] = fdict._add_file(split_path[1:], value)
        return self
    def add_file(self, str_to_file, value=None):
        """
        Adds a file to the directory structure and assigns a value to it.
        :type str_to_file: string
        :param str_to_file: The path of a file
        :type value: arbitrary
        :param value: A value which can be assigned to the file (the path is a useful choice)
        """
        split_path = []
        # create a list of directories      
        while str_to_file:
            (str_to_file, head) = os.path.split(str_to_file)
            last_char = ''
            if not head:
                last_char = str_to_file[-1]
                (str_to_file, head) = os.path.split(str_to_file[:-1])

            split_path.append(head + last_char)

        self._add_file(split_path[::-1], value)
        
    def compressed_copy(self):
        """
        Returns a copy where single sub-directories are joined to their parents 
        """
        fdcopy = FileDict()
        
        for k in self.keys():
            fdict = self[k]
            if isinstance(fdict, FileDict):
                fdict = fdict.compressed_copy()
                
                if len(fdict) == 1:
                    k2, v2 = fdict.popitem()
                    # create a compressed key
                    newkey = os.path.join(k, k2)
                    fdcopy[newkey] = v2
                else:
                    fdcopy[k] = fdict
            else:
                fdcopy[k] = fdict
        return fdcopy

    def uncompress_single_files(self):
        """
        Single files will end as one entry containing the whole path.
        This routing splits up this path. Browsing will be more convenient.
        """
        for k in self.keys():
            entry = self[k]
            if isinstance(entry, FileDict):
                entry.uncompress_single_files()
            else:
                (head, tail) = os.path.split(k)
                if tail and head:
                    self.pop(k)
                    subdict = FileDict()
                    subdict.add_file(tail, entry)
                    self[head]=subdict
    
    def get_list(self):
        """
        Returns a nested list of the tree object. 
        """
        ret =[]
        
        for item in self.items():
            ret.append(item[0])
            if isinstance(item[1], FileDict):
                ret.append(item[1].get_list())
        
        return ret
        
def utf8SaveEncode(str_or_list):
    """
    Encodes a string or a list of strings in UTF8
    :type str_or_list: string or list
    :param str_or_list: variable to encode
    """
    
    def strEncode(ascii):
        """
        Encodes a string in UTF8 and standadizes error handling
        :type str: string
        :param str: variable to encode
        """
        return unicode(ascii, errors='replace')
    
    retval = None
    if isinstance(str, basestring):
        retval = strEncode(str_or_list)
        
    else:
        retval = [ strEncode(ascii) for ascii in str_or_list ]
        
    return retval
        

def sendmail_to_follower(request, history_id, subject, message):
    '''
    sends a mail to all follower of the result, except the django user
    :type request: the request object
    :param request: the standard request object
    :type history_id: int
    :param history_id: the id of the history record
    :type subject: string
    :param subject: the subject of the mail
    :type message: string
    :param message: the mesaage
    '''
    from django.core.urlresolvers import reverse
    from django.core.mail import EmailMessage
    from django_evaluation.ldaptools import get_ldap_object

    follower = HistoryTag.objects.filter(history_id_id=history_id).filter(type=HistoryTag.tagType.follow)
    
    follower = follower.order_by('uid')


    addresses = []
    names = []

    user_info = get_ldap_object() 

    prev_uid = None

    url = request.build_absolute_uri(reverse('history:unfollow', kwargs={'history_id': history_id}))

    text = message

    text += '\n\n--------------------------------------------------------------------------------\n'
    text += 'This email has been automatically generated by the web server of the\n'
    text += 'MiKlip evaluation system (www-miklip.dkrz.de)\n\n'
    text += 'To unfollow the notifications for this result, please follow the link below.\n'
    text += url

    from_email = request.user.email
    to_email = []
    subject = '[evaluation system]  %s' % subject
        

    replyto = {'Reply-To' : 'do_not_reply@www-miklip.de'}

    for user in follower:
        uid = str(user.uid)

        if uid != prev_uid and user.uid != request.user:
            info= user_info.get_user_info(uid)
            addresses.append(info[3])
        prev_uid = uid



        for addr in addresses:

            to_email.append(addr)

    email = EmailMessage(subject,
                         text,
                         from_email,
                         to_email,
                         headers = replyto)

    email.send()
            
