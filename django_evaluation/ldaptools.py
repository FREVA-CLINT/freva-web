import ldap

import settings
from exceptions import ValueError
from django.core.cache import cache, get_cache
from django.core.exceptions import ImproperlyConfigured
import importlib
from abc import ABCMeta, abstractmethod
import grp
import pwd


class LdapUserInformation(object):
    __metaclass__ = ABCMeta
    _con = None
    miklip_user = []
    user_info = []
    user_info_dict = {}   
 
    def _connect_to_ldap(self):
        """
        Establish ldap connection, use django settings
        """
        if self._con:
            return self._con
        # whenever a CA_CERTDIR is set use it.
        try:
            ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, settings.CA_CERT_DIR)
        except:
            pass
        LDAP_SERVERS = settings.AUTH_LDAP_SERVER_URI.split(",")
        SERVER = LDAP_SERVERS.pop()
        con = None
        connected_to = None
        # try any LDAP server in list
        while SERVER:
            try:
                con = ldap.initialize(SERVER)
                connected_to = SERVER
                SERVER = None
            except:
                SERVER = LDAP_SERVERS.pop()
                if not SERVER:
                    raise

        # bind with the simple user
        try:
            con.simple_bind_s(settings.LDAP_USER_DN, settings.LDAP_USER_PW)
        except (ValueError, AttributeError):
            con.simple_bind_s()
        self._con = con
        return self._con

    @abstractmethod
    def load_from_ldap(self):
        pass

    def get_user_info(self, uid=None):
        """
        Returns the user info and loads it whenever necessary
        """
        if not self.user_info:
            get_cache('default')
            self.user_info = cache.get('LDAP_user_info')

            if not self.user_info:
                self.load_from_ldap()
                cache.set('LDAP_user_info', self.user_info, 3600)
        if uid:
            if not self.user_info_dict:
                get_cache('default')
                self.user_info_dict = cache.get('LDAP_user_info_dict')
                if not self.user_info_dict:
                    self.user_info_dict = {}
                    for user in self.user_info:
                        self.user_info_dict[user[0]] = user
                    cache.set('LDAP_user_info_dict', self.user_info_dict, 3600)
            return self.user_info_dict.get(uid, None)
        else:
            return self.user_info

    @property
    def connection(self):
        return self._connect_to_ldap()

    def __del__(self, *args, **kwargs):
        self._con.unbind_s()


class FUUserInformation(LdapUserInformation):

    def load_from_ldap(self):
        # search all users belonging
        con = self.connection
        res = con.search_s(settings.LDAP_GROUP_BASE,
                          ldap.SCOPE_SUBTREE,
                          'objectClass=account'
                          )

        self.miklip_user = []
        user_info = []
        user_list = res

        # fill the users list
        for user in user_list:
            uid = user[1]['uid'][0]
            name = user[1]['cn'][0].split(' ')
            try:
                prename = name[1]
            except:
                prename = ''
            try: 
                lastname = name[0]
            except:
                lastname = ''
            mail = user[1].get('mail', None)
            gecos = user[1].get('gecos', None)

            if mail:
                email = mail
                user_info.append((uid, prename, lastname, email))
            elif gecos:
                tmp = gecos[0].split(',')
                for val in tmp:
                    if '@' in val:
                        email = val
                        user_info.append((uid, prename, lastname, email))
                        break

        self.user_info = sorted(user_info, key=lambda tup: tup[1])
        return self.user_info


class MiklipUserInformation(LdapUserInformation):
    """
    A class to access additional LDAP information using the
    agent user and no binding with the logged in user
    """       
    ldap_keys = ['sn', 'givenName', 'uid', 'mail', 'mailForwardingAddress']    

    def load_from_ldap(self):
        """
        Loads the miklip user ids and the info belonging to the user
        """
        con = self.connection
        res = con.search_s(settings.LDAP_GROUP_BASE,
                          ldap.SCOPE_SUBTREE,
                          attrlist=['memberUid'],
                          filterstr=settings.LDAP_MIKLIP_GROUP_FILTER)
        self.miklip_user = []
        user_info = []
        user_list = res[0][1]['memberUid']
             
        # fill the users list
        for user in user_list:
            # look up the user entries in the LDAP System
            res = con.search_s(settings.LDAP_USER_BASE,
                              ldap.SCOPE_SUBTREE,
                              attrlist=self.ldap_keys,
                              filterstr='uid=%s' % user)
            
            mail = res[0][1].get('mail', None)
            forward = res[0][1].get('mailForwardingAddress', None)
            
            if forward:
                user_info.append((user,
                                  ' '.join(res[0][1]['sn']),
                                  ' '.join(res[0][1].get('givenName', '')),
                                  forward[-1],))
            elif mail:
                user_info.append((user,
                                  ' '.join(res[0][1]['sn']),
                                  ' '.join(res[0][1].get('givenName', '')),
                                  mail[-1],))
        self.user_info = sorted(user_info, key=lambda tup: tup[1])
        return self.user_info


class UCARUserInformation(LdapUserInformation):

    def load_from_ldap(self):
        info = grp.getgrnam('freva')
        users = info.gr_mem
        user_info = []
        for user in users:
            tmp = pwd.getpwnam(user)
            name = tmp.pw_gecos.split(' ')
            user_info.append((user, name[1], name[0], '%s@ucar.edu' % user))                
        self.user_info = sorted(user_info, key=lambda tup: tup[1])
        return self.user_info


def get_ldap_object():
    """
    Returns an instance of the ldap class specified in django settings
    """
    try:
        parts = settings.LDAP_MODEL.split('.')
        model_name = parts[-1]
        module = '.'.join(parts[:-1])
    except (ValueError, AttributeError):
        raise ImproperlyConfigured('LDAP_MODEL must be of the form '
                                   '"module.model_name" (i.e. django_evaluation.ldaptools.MiklipUserInformation')
    m = importlib.import_module(module)
    return getattr(m, model_name)()

# This is for backward compatibility
miklip_user_information = get_ldap_object
