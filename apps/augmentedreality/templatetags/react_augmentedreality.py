import json

from django import template
from django.conf import settings
from django.utils.html import format_html

from apps.augmentedreality.serializers import SceneSerializer
from apps.topicprio.serializers import TopicSerializer

register = template.Library()


@register.simple_tag()
def react_augmentedreality_arc(topic):
    attributes = {
        "topic": TopicSerializer(topic).data,
        "scene": None,
    }

    if topic.scene:
        attributes["scene"] = SceneSerializer(topic.scene).data

    if hasattr(settings, "MINIO_DATA"):
        attributes["minioData"] = settings.MINIO_DATA

    return format_html(
        '<div data-arpas-widget="arc" ' 'data-attributes="{attributes}"></div>',
        attributes=json.dumps(attributes),
    )

@register.simple_tag()
def react_arc_viewer(topic):
    attributes = {
        "topic": TopicSerializer(topic).data,
        "scene": None,
    }

    if topic.scene:
        attributes["scene"] = SceneSerializer(topic.scene).data

    if hasattr(settings, "MINIO_DATA"):
        attributes["minioData"] = settings.MINIO_DATA

    if attributes["scene"]:
        return format_html(
            '<div data-arpas-widget="viewer" ' 'data-attributes="{attributes}"></div>',
            attributes=json.dumps(attributes),
        )
    else:
        return format_html("<div></div>")
