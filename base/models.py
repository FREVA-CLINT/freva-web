from django.contrib.auth.models import User

def isGuest(self):
   groups = self.groups.filter(name='Guest')
   return len(groups) > 0

User.add_to_class('isGuest',isGuest)

