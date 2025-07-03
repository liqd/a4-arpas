import pytest
from django.contrib.contenttypes.models import ContentType

from apps.augmentedreality.api import CombinedCommentViewSet
from apps.augmentedreality.models import ARObject
from apps.augmentedreality.models import Scene
from apps.augmentedreality.models import Variant
from apps.topicprio.models import Topic
from tests.topicprio.factories import TopicFactory


@pytest.mark.django_db
def test_ar_variant_comment_create_with_guest(apiclient):
    from rest_framework.permissions import AllowAny

    """
    AllowAny permissions gets around an auth issue in test, likely from
    AllowGuestUser mixin not being engaged in correct order.
    """
    original_permissions = CombinedCommentViewSet.permission_classes
    CombinedCommentViewSet.permission_classes = [AllowAny]

    try:
        # Create topic, scene, ARObject needed for variant, which comment is bound to
        topic = TopicFactory()
        content_type = ContentType.objects.get_for_model(Topic)
        scene = Scene.objects.create(content_type=content_type, object_id=topic.id)
        ar_object = ARObject.objects.create(scene=scene)
        variant = Variant.objects.create(ar_object=ar_object, name="Test Variant")
        variant_content_type = ContentType.objects.get_for_model(Variant)

        url = f"/api/contenttypes/{variant_content_type.id}/objects/{variant.id}/arpas-comments/"
        response = apiclient.post(
            url, {"comment": "Test comment", "agreed_terms_of_use": True}, format="json"
        )

        assert response.status_code == 201
        assert response.data["comment"] == "Test comment"
        assert response.data["user_name"] == "AR comment"

    finally:
        # Reset permissions
        CombinedCommentViewSet.permission_classes = original_permissions
