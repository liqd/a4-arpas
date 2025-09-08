from drf_spectacular.utils import extend_schema
from guest_user.mixins import AllowGuestUserMixin

from adhocracy4.comments_async.api import CommentViewSet
from adhocracy4.ratings.api import RatingViewSet


class CombinedRatingViewSet(AllowGuestUserMixin, RatingViewSet):
    http_method_names = ["post", "patch"]

    @extend_schema(
        summary="Create or update an ARPAS rating",
        description="""
        Create a new rating or update an existing one for ARPAS objects (variants, comments, etc.).

        Rating Values:
        1: Like (positive rating)
        -1: Dislike (negative rating)
        0: Remove rating (neutral)

        Note: Users can only have one rating per object.
        """,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
