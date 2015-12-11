from django import forms
from externaluser.models import ExternalUser
import hashlib
import os
from base64 import urlsafe_b64encode as encode
import re


class ExternalUserForm(forms.ModelForm):
    
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = ExternalUser
        fields = ['email', 'username', 'first_name', 'last_name',
                  'institute', 'password', 'confirm_password']
        
    def validate_characters(self, value):
        if not re.match(r'^[A-Za-z0-9_-]+$', value):
            raise forms.ValidationError('"Sorry , you can only have alphanumeric, _ or -')
        
    def clean_username(self):
        value = self.cleaned_data['username']
        self.validate_characters(value)
        return value.lower()
    
    def clean_first_name(self):
        value = self.cleaned_data['first_name']
        self.validate_characters(value)
        return value
    
    def clean_last_name(self):
        value = self.cleaned_data['last_name']
        self.validate_characters(value)
        return value
    
    def clean(self):
        pw1 = self.cleaned_data.get('password')
        pw2 = self.cleaned_data.get('confirm_password')
        
        if pw1 and pw1 != pw2:
            self.add_error('password', forms.ValidationError("Passwords don't match"))
            self.add_error('confirm_password', forms.ValidationError("Passwords don't match"))
        
        self.cleaned_data['password'] = self.make_secret(pw1)
        
        return forms.ModelForm.clean(self)

    def make_secret(self, password):
        """
        Encodes the given password as a base64 SSHA hash+salt buffer
        """
        salt = os.urandom(4)
    
        # hash the password and append the salt
        sha = hashlib.sha1(password)
        sha.update(salt)
    
        # create a base64 encoded string of the concatenated digest + salt
        digest_salt_b64 = '{}{}'.format(sha.digest(), salt).encode('base64').strip()
    
        # now tag the digest above with the {SSHA} tag
        tagged_digest_salt = '{{SSHA}}{}'.format(digest_salt_b64)
        return tagged_digest_salt
    
#     def clean_password(self):
#         pw = self.cleaned_data['password']
#         return self.hash_password(pw)
#     
#     def clean_confirm_password(self):
#         pw = self.cleaned_data['confirm_password']
#         return self.hash_password(pw)
    