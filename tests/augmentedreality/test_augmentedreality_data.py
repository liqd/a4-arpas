import json

import pytest
from django.contrib.contenttypes.models import ContentType

from adhocracy4.comments.models import Comment
from adhocracy4.ratings.models import Rating
from apps.augmentedreality.models import Variant
from apps.augmentedreality.templatetags.react_augmentedreality import (
    react_augmentedreality_arc,
)
from tests.augmentedreality.factories import VariantFactory
from tests.factories import UserFactory
from tests.topicprio.factories import TopicFactory


@pytest.mark.django_db
def test_react_augmentedreality_arc_variant_content_type_id():
    topic = TopicFactory()

    # Call template-tag directly
    rendered_html = react_augmentedreality_arc(topic)

    # Extract the data-attributes attribute
    import re

    match = re.search(r'data-attributes="([^"]+)"', rendered_html)
    assert match, "data-attributes attribute not found"
    data_attributes = match.group(1)
    # Reverse HTML-escaping
    data_attributes = data_attributes.replace("&quot;", '"')
    attributes = json.loads(data_attributes)

    variant_content_type_id = ContentType.objects.get_for_model(Variant).id
    assert attributes["topic"]["variant_content_type_id"] == variant_content_type_id


@pytest.mark.django_db
def test_variant_comments_and_ratings():
    # Create user and base objects
    variant = VariantFactory()
    user = UserFactory()
    # Create comment
    comment = Comment.objects.create(
        content_object=variant, comment="Test comment", creator=user
    )
    # Create rating
    rating = Rating.objects.create(content_object=variant, value=1, creator=user)

    # Access via GenericRelation
    comments = list(variant.comments.all())
    ratings = list(variant.ratings.all())

    assert len(comments) == 1
    assert comments[0] == comment
    assert len(ratings) == 1
    assert ratings[0] == rating
    # Reverse check
    assert comment.content_object == variant
    assert rating.content_object == variant
