import ldap

import settings
from exceptions import ValueError
from django.core.cache import cache, get_cache
import re
   

class miklip_user_information:
    """
    A class to access additional LDAP information using the
    agent user and no binding with the logged in user
    """
    
    def __init__(self):
        self.ldap_keys = ['sn', 'givenName', 'uid', 'mail', 'mailForwardingAddress']
        self.miklip_user = []
        self.user_info = []
        self.user_info_dict = {}
       
    def load_from_ldap(self):
        """
        Loads the miklip user ids and the info belonging to the user
        """
        
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
        user_info = []
        user_list = res[0][1]['nisnetgrouptriple']

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
            
            mail = res[0][1].get('mail', None)
            forward = res[0][1].get('mailForwardingAddress', None)
            
            if forward:
                user_info.append((uid,
                                  ' '.join(res[0][1]['sn']),
                                  ' '.join(res[0][1].get('givenName', '')),
                                  forward[-1],))
                
            elif mail:
                user_info.append((uid,
                                  ' '.join(res[0][1]['sn']),
                                  ' '.join(res[0][1].get('givenName', '')),
                                  mail[-1],))
            
            
        self.user_info = sorted(user_info, key=lambda tup: tup[1]);
        # gracefully close the connection
        con.unbind_s()
            
        return self.user_info
    
    def get_user_info(self, uid = None):
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



