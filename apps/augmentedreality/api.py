from guest_user.mixins import AllowGuestUserMixin

from adhocracy4.comments_async.api import CommentViewSet
from adhocracy4.ratings.api import RatingViewSet


class CombinedRatingViewSet(AllowGuestUserMixin, RatingViewSet):
    http_method_names = ["post", "put", "patch", "delete", "head", "options"]


class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
