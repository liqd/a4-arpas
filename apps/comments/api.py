from django.contrib.contenttypes.models import ContentType

from adhocracy4.comments_async.api import CommentViewSet
from apps.comments.models import ARComment
from apps.comments.serializers import ARCommentSerializer

# from adhocracy4.comments_async.serializers import ThreadListSerializer
# from adhocracy4.comments.serializers import ThreadSerializer


class ARCommentViewSet(CommentViewSet):
    serializer_class = ARCommentSerializer

    def get_serializer_class(self):
        return ARCommentSerializer

    def get_queryset(self):
        child_comment_content_type_id = ContentType.objects.get_for_model(ARComment)
        comments = (
            ARComment.objects.filter(object_pk=self.object_pk)
            .filter(content_type_id=self.content_type.pk)
            .annotate_positive_rating_count()
            .annotate_negative_rating_count()
        )
        if self.action == "list":
            return comments.exclude(
                content_type_id=child_comment_content_type_id
            ).order_by("-created")
        return comments
