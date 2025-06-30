import factory
from django.contrib.contenttypes.models import ContentType

from apps.augmentedreality.models import ARObject
from apps.augmentedreality.models import Scene
from apps.augmentedreality.models import Variant
from apps.topicprio.models import Topic
from tests.topicprio.factories import TopicFactory


class SceneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Scene

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(Topic)

    @factory.lazy_attribute
    def object_id(self):
        topic = TopicFactory()
        return topic.pk


class ARObjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ARObject

    name = factory.Sequence(lambda n: f"ARObjekt{n}")
    scene = factory.SubFactory(SceneFactory)
    coordinates = "POINT(0 0 0)"
    qr_id = factory.Sequence(lambda n: f"qr{n}")


class VariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Variant

    name = factory.Sequence(lambda n: f"Variante{n}")
    mesh_id = factory.Sequence(lambda n: f"mesh{n}")
    ar_object = factory.SubFactory(ARObjectFactory)
    offset_position = "POINT(0 0 0)"
    offset_rotation = "POINT(0 0 0)"
    offset_scale = "POINT(0 0 0)"
    weight = 0
