from adhocracy4.comments.serializers import CommentSerializer

from .models import ARComment


class ARCommentSerializer(CommentSerializer):

    class Meta:
        model = ARComment
        fields = "__all__"
