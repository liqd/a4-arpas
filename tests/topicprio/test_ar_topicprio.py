# import os

import pytest
# from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

# from adhocracy4.comments import models as comments_models
# from adhocracy4.ratings import models as rating_models
# from adhocracy4.test.helpers import create_thumbnail
# from apps.topicprio import models as idea_models



# @pytest.mark.django_db
# def test_ar_user_create(
#     client, phase_factory, topic_factory
# ):
#     phase, module, project, topic = setup_phase(
#         phase_factory, topic_factory, phases.PrioritizePhase
#     )
#     topic.module.project.access = Access.PRIVATE
#     topic.module.project.save()
#     url = topic.get_absolute_url()
#     response = client.get(url)
#     assert response.status_code == 302
#     assert redirect_target(response) == "account_login"


# @pytest.mark.django_db
# def test_ar_user_create(
#     # comment_factory,
#     apiclient,
#     # phase_factory,
#     # idea_factory,
#     topic
#     # organisation_terms_of_use_factory,
# ):
#     # phase, _, _, idea = setup_phase(phase_factory, idea_factory, CollectPhase)
#     # comment = comment_factory(content_object=idea)
#     # organisation_terms_of_use_factory(
#     #     user=comment.creator,
#     #     organisation=comment.project.organisation,
#     #     has_agreed=True,
#     # )
#     breakpoint()
#     # apiclient.force_authenticate(user=comment.creator)
#     url = reverse(
#         "arpas-comments",
#         kwargs={
#             # "pk": comment.pk,
#             "content_type": topic.content_type.pk,
#             "object_pk": topic.object_pk,
#         },
#     )
#     data = {
#         "comment": "comment comment comment",
#         "agreed_terms_of_use": True,
#     }
#     with freeze_phase(phase):
#         response = apiclient.post(url, data, format="json")
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data["comment"] == "comment comment comment"
#         assert response.data["user_name"] == "AR comment"


@pytest.mark.django_db
def test_ar_variant_comment_create(
    apiclient,
    variant_factory,  # You'll need this factory
):
    # Create test data
    variant = variant_factory()
    
    # Get content type for Variant model
    content_type = ContentType.objects.get_for_model(Variant)
    
    # Authenticate the user
    # apiclient.force_authenticate(user=user)
    
    # Build URL - adjust "arpas-comments" to your actual URL name
    url = reverse(
        "arpas-comments",
        kwargs={
            "content_type": content_type.pk,
            "object_pk": variant.pk,
        },
    )
    
    # Test data
    data = {
        "comment": "Test comment on variant",
        "agreed_terms_of_use": True,
    }
    
    # Make the request
    response = apiclient.post(url, data, format="json")
    
    # Assertions
    assert response.status_code == status.HTTP_201_CREATED  # Or whatever your API returns
    assert response.data["comment"] == "Test comment on variant"
    assert response.data["user_name"] == "AR comment"
    
    # Verify comment was actually created
    # comment = Comment.objects.first()
    # assert comment is not None
    # assert comment.content_object == variant
    # assert comment.comment == "Test comment on variant"





# @pytest.mark.django_db
# def test_authenticated_user_can_edit_own_comment(
#     comment_factory,
#     apiclient,
#     phase_factory,
#     idea_factory,
#     organisation_terms_of_use_factory,
# ):
#     phase, _, _, idea = setup_phase(phase_factory, idea_factory, CollectPhase)
#     comment = comment_factory(content_object=idea)
#     organisation_terms_of_use_factory(
#         user=comment.creator,
#         organisation=comment.project.organisation,
#         has_agreed=True,
#     )

#     apiclient.force_authenticate(user=comment.creator)
#     url = reverse(
#         "comments-detail",
#         kwargs={
#             "pk": comment.pk,
#             "content_type": comment.content_type.pk,
#             "object_pk": comment.object_pk,
#         },
#     )
#     data = {"comment": "comment comment comment"}
#     with freeze_phase(phase):
#         response = apiclient.patch(url, data, format="json")
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data["comment"] == "comment comment comment"




