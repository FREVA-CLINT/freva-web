import evaluation_system.api.plugin_manager as pm
from evaluation_system.misc import config
from django.views.decorators.debug import sensitive_variables
from django.http import Http404
from django.conf import settings
import paramiko
import logging
from os import stat
from pwd import getpwuid


def find_owner(filename):
    """
    Return the owner of a file or directory
    """
    return getpwuid(stat(filename).st_uid).pw_name


def get_scheduler_hosts(user):
    if user.groups.filter(
        name=config.get('external_group', 'noexternalgroupset')
    ).exists():
        try:
            return settings.SCHEDULER_HOSTS_EXTERNAL
        except AttributeError:
            return settings.SCHEDULER_HOSTS
    else:
        return settings.SCHEDULER_HOSTS


def get_plugin_or_404(plugin_name, user=None, user_name=None):

    try:
        if user:
            user_name = user.getName()
        return pm.getPluginInstance(plugin_name, user, user_name)
    except SyntaxError:
        raise 
    except:
        raise
        raise Http404
    

@sensitive_variables('password')    
def ssh_call(username, password, command, hostnames=['127.0.0.1']):
    """
    executes a command under the given user on a remote machine.
    :param username: login name
    :param password: password
    :param command: the command to be executed
    :param hostnames: list of _hostnames default: ['127.0.0.1']
    :return: triple of FileChannels (stdin, stdout, stderr) to read
            the stdout stdout.getlines()
    """
    
    _hostnames = hostnames[:]
    hostname = _hostnames.pop()
    sentto = hostname
    
    while hostname:
        try:
            # create the ssh client
            ssh = paramiko.SSHClient()

            # except remote key anyways
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname,
                        username=username,
                        password=password,
                        look_for_keys=False)
            
            # nullify the hostname to exit the loop
            hostname = None
        except paramiko.SSHException:
            # on exception try the next server
            logging.error('SSH connection to %s failed' % sentto)

            if _hostnames:
                hostname = _hostnames.pop()
                sentto = hostname
            else:
                raise
            
    (stdin, stdout, stderr) = ssh.exec_command(command=command)

    logging.debug("sent command '%s' to '%s'" % (command, sentto))

    # poll until executed command has finished
    stdout.channel.recv_exit_status()
    
    # close the connection
    ssh.close()
    
    return stdin, stdout, stderr
