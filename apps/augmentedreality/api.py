from guest_user.mixins import AllowGuestUserMixin
from guest_user.models import is_guest_user

from adhocracy4.api.permissions import ViewSetRulesPermission
from adhocracy4.comments_async.api import CommentViewSet
from adhocracy4.ratings.api import RatingViewSet


# TODO: Move this permission to A4, if this is becoming permanent
class AllowGuestCommentPermission(ViewSetRulesPermission):
    def has_permission(self, request, view):
        # Allow guest users for POST (create) requests
        if request.method == "POST" and is_guest_user(request.user):
            return True

        # For all other cases, use the normal permission logic
        return super().has_permission(request, view)


class CombinedRatingViewSet(AllowGuestUserMixin, RatingViewSet):
    http_method_names = ["post", "patch"]


class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    permission_classes = [AllowGuestCommentPermission]

    def get_queryset(self):
        comments = super().get_queryset()
        return comments
