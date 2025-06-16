import json

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

from apps.augmentedreality.models import Variant
from apps.augmentedreality.serializers import SceneSerializer
from apps.topicprio.serializers import TopicSerializer

register = template.Library()


@register.simple_tag()
def react_augmentedreality_arc(topic):
    attributes = {
        "topic": TopicSerializer(topic).data,
        "scene": None,
    }

    variant_content_type_id = ContentType.objects.get_for_model(Variant).id
    attributes["topic"]["variant_content_type_id"] = variant_content_type_id

    if topic.scene:
        attributes["scene"] = SceneSerializer(topic.scene).data

    return format_html(
        '<div data-arpas-widget="arc" ' 'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )
