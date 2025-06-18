from django.contrib.contenttypes.models import ContentType

from adhocracy4.comments.models import Comment
from adhocracy4.comments_async.api import CommentViewSet

from .models import Scene
from .models import Variant

# from adhocracy4.comments_async.serializers import ThreadListSerializer
# from adhocracy4.comments.serializers import ThreadSerializer


class CombinedCommentViewSet(CommentViewSet):
    def get_queryset(self):
        # First get the normal comments of the topic
        comments = super().get_queryset()
        if self.content_type.model == "topic":
            comments = self.get_variant_comments(comments)
        if self.content_type.model == "variant":
            comments = self.get_topic_comments(comments)
        return comments

    def get_variant_comments(self, topic_comments):
        # Get the scene of the topic
        scene = Scene.objects.filter(
            content_type_id=self.content_type_id,  # Correction here
            object_id=self.object_pk,
        ).first()
        print(scene)

        if scene:
            # print("Scene " + str(scene) + " " + str(scene.pk))
            # Get all objects of the scene
            scene_variants = Variant.objects.filter(object__scene=scene).values_list(
                "id", flat=True
            )
            print(scene_variants)
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
                variant_comments = self.exclude_child_comments(variant_comments)

            # Combine and sort by creation date
            return (topic_comments | variant_comments).order_by("-created")
        return topic_comments

    def get_topic_comments(self, variant_comments):
        # Get the variant object
        variant = Variant.objects.get(pk=self.object_pk)

        # Get the scene through the variant's object
        scene = variant.object.scene

        if scene:
            # Get the topic (item) from the scene
            topic = scene.item

            # Get the content type for the topic
            topic_content_type = ContentType.objects.get_for_model(topic)

            # Get the comments of the topic
            topic_comments = (
                Comment.objects.filter(
                    object_pk=topic.pk,
                    content_type_id=topic_content_type.id,
                )
                .annotate_positive_rating_count()
                .annotate_negative_rating_count()
            )

            # For list action only top-level comments
            if self.action == "list":
                topic_comments = self.exclude_child_comments(topic_comments)

            # Combine and sort by creation date
            return (variant_comments | topic_comments).order_by("-created")

        return variant_comments

    def exclude_child_comments(self, comments):
        child_comment_content_type_id = ContentType.objects.get_for_model(Comment)
        return comments.exclude(content_type_id=child_comment_content_type_id)
