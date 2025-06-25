from adhocracy4.comments_async.api import CommentViewSet

# from adhocracy4.comments_async.serializers import ThreadListSerializer
# from adhocracy4.comments.serializers import ThreadSerializer


class CombinedCommentViewSet(CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
