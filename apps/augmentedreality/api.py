from adhocracy4.comments_async.api import CommentViewSet


class CombinedCommentViewSet(CommentViewSet):
    def get_queryset(self):
        comments = super().get_queryset()
        return comments
