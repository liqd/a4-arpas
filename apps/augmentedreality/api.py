<<<<<<< HEAD
from adhocracy4.comments_async.api import CommentViewSet

=======
from django.contrib.contenttypes.models import ContentType
from guest_user.mixins import AllowGuestUserMixin

from adhocracy4.comments.models import Comment
from adhocracy4.comments_async.api import CommentViewSet
from adhocracy4.ratings.api import RatingViewSet

from .models import Scene
from .models import Variant


class CombinedRatingViewSet(AllowGuestUserMixin, RatingViewSet):
    http_method_names = ["post", "put", "patch", "delete", "head", "options"]

>>>>>>> 0bd46281 (Add guest user created on non auth comment)

class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
