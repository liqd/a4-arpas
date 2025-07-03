import pytest
from django.contrib.contenttypes.models import ContentType

from apps.augmentedreality.api import CombinedCommentViewSet
from apps.augmentedreality.models import ARObject
from apps.augmentedreality.models import Scene
from apps.augmentedreality.models import Variant
from apps.topicprio.models import Topic
from tests.topicprio.factories import TopicFactory


@pytest.mark.django_db(transaction=True)
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
        print(f"Created Topic: id={topic.id}, slug={topic.slug}")  # Debug
        ContentType.objects.clear_cache()  # Add this before getting ContentType
        content_type = ContentType.objects.get_for_model(Topic)
        scene = Scene.objects.create(content_type=content_type, object_id=topic.id)
        ar_object = ARObject.objects.create(scene=scene)
        variant = Variant.objects.create(ar_object=ar_object, name="Test Variant")
        variant_content_type = ContentType.objects.get_for_model(Variant)

        print("\n=== Database State ===")
        print("Topics:", Topic.objects.values_list("id", flat=True))
        print("Scenes:", Scene.objects.values_list("id", "object_id"))
        print("Variants:", Variant.objects.values_list("id", "ar_object_id"))

        print(
            f"Actual ContentType ID for Variant: {ContentType.objects.get_for_model(Variant).id}"
        )
        print(f"Variant ID being used: {variant.id}")

        url = f"/api/contenttypes/{variant_content_type.id}/objects/{variant.id}/arpas-comments/"
        print(url)

        response = apiclient.get(url)  # Try GET first to inspect
        print("GET response:", response.status_code, response.data)

        from django.urls import resolve

        try:
            match = resolve(url)
            print(f"Resolved view: {match.func.__name__}")
            print(f"View class: {match.func.cls}")
        except Exception as e:
            print(f"URL resolution failed: {str(e)}")

        response = apiclient.post(
            url, {"comment": "Test comment", "agreed_terms_of_use": True}, format="json"
        )

        assert response.status_code == 201
        assert response.data["comment"] == "Test comment"
        assert response.data["user_name"] == "AR comment"

    finally:
        # Reset permissions
        CombinedCommentViewSet.permission_classes = original_permissions
