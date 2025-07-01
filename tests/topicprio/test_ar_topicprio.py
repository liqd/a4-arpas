import pytest
from django.contrib.contenttypes.models import ContentType

from apps.augmentedreality.models import ARObject  # Adjust import path as needed
from apps.augmentedreality.models import Scene
from apps.augmentedreality.models import Variant
from apps.topicprio.models import Topic
from tests.topicprio.factories import TopicFactory


@pytest.mark.django_db
def test_comment_creation_with_valid_content_type(apiclient, admin):
    from rest_framework.permissions import AllowAny

    from apps.augmentedreality.api import CombinedCommentViewSet

    # TODO: Need to redo this permissions after done
    # original_permissions = CombinedCommentViewSet.permission_classes
    CombinedCommentViewSet.permission_classes = [AllowAny]

    # Create a Topic (or whatever your Scene's item should be)
    # topic = Topic.objects.create(name="Test Topic", creator=admin)
    topic = TopicFactory()

    # Create ContentType for the item
    content_type = ContentType.objects.get_for_model(Topic)

    # Create Scene with valid item
    scene = Scene.objects.create(
        content_type=content_type, object_id=topic.id  # Link to the actual item
    )

    # Create ARObject with scene
    ar_object = ARObject.objects.create(scene=scene)

    # Create Variant
    variant = Variant.objects.create(ar_object=ar_object, name="Test Variant")

    # 3. Verify relationships
    print(f"Variant -> ARObject: {variant.ar_object}")
    print(f"ARObject -> Scene: {ar_object.scene}")
    print(f"Scene -> Item: {scene.item}")  # Should be your Topic
    print(f"Item -> Project: {scene.item.project}")  # Should exist

    # 4. Make request
    variant_content_type = ContentType.objects.get_for_model(Variant)
    url = f"/api/contenttypes/{variant_content_type.id}/objects/{variant.id}/arpas-comments/"
    response = apiclient.post(
        url, {"comment": "Test comment", "agreed_terms_of_use": True}, format="json"
    )

    assert response.status_code == 201
    assert response.data["comment"] == "Test comment"
    assert response.data["user_name"] == "AR comment"
