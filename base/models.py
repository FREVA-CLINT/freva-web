from datetime import datetime

from django.db import models


class UIMessages(models.Model):
    message = models.TextField()
    date = models.DateTimeField(default=datetime.now)
    resolved = models.BooleanField(default=False)
