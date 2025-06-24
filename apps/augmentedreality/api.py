<<<<<<< HEAD
from adhocracy4.comments_async.api import CommentViewSet

=======
from django.contrib.contenttypes.models import ContentType
from guest_user.mixins import AllowGuestUserMixin

from adhocracy4.comments.models import Comment
from adhocracy4.comments_async.api import CommentViewSet

from .models import Scene
from .models import Variant

# from adhocracy4.comments.serializers import ThreadSerializer

>>>>>>> 0bd46281 (Add guest user created on non auth comment)

class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
