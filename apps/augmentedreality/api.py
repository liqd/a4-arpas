from django.contrib.contenttypes.models import ContentType
from guest_user.mixins import AllowGuestUserMixin

from adhocracy4.comments.models import Comment
from adhocracy4.comments_async.api import CommentViewSet
from adhocracy4.ratings.api import RatingViewSet

from .models import Scene
from .models import Variant


class CombinedRatingViewSet(AllowGuestUserMixin, RatingViewSet):
    http_method_names = ["post", "put", "patch", "delete", "head", "options"]


class CombinedCommentViewSet(AllowGuestUserMixin, CommentViewSet):
    def get_queryset(self):
        # First get the normal comments of the topic
        topic_comments = super().get_queryset()

        if self.content_type.model == "topic":
            # Get the scene of the topic
            scene = Scene.objects.filter(
                content_type_id=self.content_type_id,  # Correction here
                object_id=self.object_pk,
            ).first()

            if scene:
                # Get all objects of the scene
                scene_variants = Variant.objects.filter(
                    object__scene=scene
                ).values_list("id", flat=True)
                # Get the comments of the variants
                variant_content_type = ContentType.objects.get_for_model(Variant)
                variant_comments = (
                    Comment.objects.filter(
                        object_pk__in=scene_variants,
                        content_type_id=variant_content_type.id,
                    )
                    .annotate_positive_rating_count()
                    .annotate_negative_rating_count()
                )

                # For list action only top-level comments
                if self.action == "list":
                    child_comment_content_type_id = ContentType.objects.get_for_model(
                        Comment
                    )
                    variant_comments = variant_comments.exclude(
                        content_type_id=child_comment_content_type_id
                    )

                # Combine and sort by creation date
                return (topic_comments | variant_comments).order_by("-created")

        return topic_comments
