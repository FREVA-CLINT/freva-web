from django.db import models
from model_utils.models import StatusModel
from model_utils import Choices


class ExternalUser(StatusModel):
    
    STATUS = Choices(
        ('pending', 'pending'), ('approved_by_freva', 'approved_by_freva'),
        ('account_created', 'account_created'), ('active', 'active'),
        ('inactive', 'inactive')
    )
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    institute = models.CharField(max_length=255)
    password = models.CharField(max_length=255)