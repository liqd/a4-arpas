from django.db import models

from adhocracy4.comments.models import Comment


class ARComment(Comment):
    fromAR = models.BooleanField(default=False)
