import evaluation_system.api.plugin_manager as pm
from django.views.decorators.debug import sensitive_variables
from django.http import Http404

import paramiko
import logging

def get_plugin_or_404(plugin_name,user=None):
    
    try:
        return pm.getPluginInstance(plugin_name,user)
    except SyntaxError:
        raise 
    except:
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
    
    return (stdin, stdout, stderr)
