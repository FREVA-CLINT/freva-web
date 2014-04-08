import ldap

from django.http import Http404
from django_auth_ldap.config import LDAPGroupType
import settings
from exceptions import ValueError
import re

class LDAPNisGroupType(LDAPGroupType):
    """
    This class provides group verification via LDAP at
    the DKRZ architecture based on NIS
    """

    def __init__(self, name_attr='cn'):
        """
        This constructor calls the constructor of the parent class only
        """
        super(LDAPNisGroupType, self).__init__(name_attr)

    def user_groups(self, ldap_user, group_search):
        """
        Overrides LDAPGroupType.user_groups
        ldap_user represents the user and has the following three
        properties:

        dn: the distinguished name
        attrs: a dictionary of LDAP attributes (with lists of values)
        connection: an LDAPObject that has been bound with credentials

        This is the primitive method in the API and must be implemented.

        ATTENTION: Here we restrict all LDAP groups to the Django groups.
        So, we can use LDAP_AUTH_MIRROR_GROUPS without introducing
        non-relevant groups.
        """
        from django.contrib.auth.models import Group

        result = []

        SEARCH_BASE = 'ou=netgroup,o=ldap,o=root'
        uid = str(ldap_user.attrs['uid'][0])
        ldap_filter='(nisNetgroupTriple=\(,%s,\))' % uid
        attrs = ['cn']

        s = ldap_user.connection.search_s( SEARCH_BASE, ldap.SCOPE_SUBTREE,
                                           ldap_filter,
                                           attrs)

        for entry in s:
            result.append(entry[1]['cn'][0])

        django_groups = []
        for g in Group.objects.all():
            django_groups.append(g.name)

        intersection = list(set(result).intersection(set(django_groups)))
        return intersection

    def is_member(self, ldap_user, group_dn):
        """
        This method is an optimization for determining group membership without
        loading all of the user's groups. Subclasses that are able to do this
        may return True or False. ldap_user is as above. group_dn is the
        distinguished name of the group in question.

        The base implementation returns None, which means we don't have enough
        information. The caller will have to call user_groups() instead and look
        for group_dn in the results.
        """

        SEARCH_BASE = 'ou=netgroup,o=ldap,o=root'
        uid = str(ldap_user.attrs['uid'][0])
        ldap_filter='(&(nisNetgroupTriple=\(,%s,\))(cn=%s))' % (uid, group_dn)
        attrs = ['cn']

        try:
            s = ldap_user.connection.search_s( SEARCH_BASE,
                                               ldap.SCOPE_SUBTREE,
                                               ldap_filter,
                                               attrs)
        except Exception, e:
            raise Http404, str(e)


        return len(s) > 0

    def group_name_from_info(self, group_info):

        result = []
        django_groups = []

        return group_info
    

class miklip_user_information:
    """
    A class to access additional LDAP information using the
    agent user and no binding with the logged in user
    """
    
    def __init__(self):
        self.ldap_keys = ['sn', 'givenName', 'uid', 'mail']
        self.miklip_user = []
        self.user_info = []
       
    def load_from_ldap(self):
        """
        Loads the miklip user ids and the info belonging to the user
        """
        
        # whenever a CA_CERTDIR is set use it.
        try:
            ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, settings.CA_CERT_DIR)
        except:
            pass
        
        LDAP_SERVERS = settings.AUTH_LDAP_SERVER_URI[:]
        
        SERVER = LDAP_SERVERS.pop()
        
        con = None
        connected_to = None
        
        # try any LDAP server in list
        while(SERVER):
            try:
                con = ldap.initialize(SERVER)
                connected_to = SERVER
                SERVER = None
            except:
                SERVER = LDAP_SERVERS.pop()
                if not SERVER:
                    raise
         
        # bind with the simple DKRZ user
        con.simple_bind_s(settings.LDAP_USER_DN, settings.LDAP_USER_PW)
        
        # search all users belonging 
        res= con.search_s(settings.LDAP_GROUP_BASE,
                          ldap.SCOPE_SUBTREE,
                          attrlist=['nisnetgrouptriple'],
                          filterstr=settings.LDAP_MIKLIP_GROUP_FILTER)
        
        self.miklip_user = []
        self.user_info = []
        user_list = res[1]['cn']

        nisnetgrouptriple_pattern = "^\(,.*,\)$"
        nisnetgrouptriple_re = re.compile(nisnetgrouptriple_pattern)
        
             
        # fill the users list
        for user in user_list:
            uid = None
            if nisnetgrouptriple_re.match(user):
                uid = user[2:-2]
                self.miklip_user.append(uid)
            else:
                raise ValueError('NisNetGroupTriple has not the expected pattern')
            
        
            # look up the user entries in the LDAP System
            res= con.search_s(settings.LDAP_USER_BASE,
                              ldap.SCOPE_SUBTREE,
                              attrlist=self.ldap_keys,
                              filterstr='uid=%s' % uid)
            
            self.user_info.append((uid,
                                   res[1]['sn'],
                                   res[1]['givenName'],
                                   res[1]['mail'],))
            
            
        # gracefully close the connection
        con.unbind_s()
            
        return self.user_info
    
    def get_user_info(self):
        """
        Returns the user info and loads it whenever necessary
        """
        if not self.user_info:
            self.load_from_ldap()
            
        return self.user_info

