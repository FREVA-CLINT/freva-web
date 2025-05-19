from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User
from django.db import models


class UIMessages(models.Model):
    message = models.TextField()
    date = models.DateTimeField(default=datetime.now)
    resolved = models.BooleanField(default=False)
