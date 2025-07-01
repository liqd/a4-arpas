import factory
from django.contrib.gis.geos import Point


from adhocracy4.test import factories as a4_factories
from apps.topicprio import models
from apps.augmentedreality.models import Variant, ARObject  # Adjust import path as needed


class ARObjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ARObject
    
    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    scene = factory.SubFactory(a4_factories.ItemFactory)  # Adjust based on your scene relationship


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    module = factory.SubFactory(a4_factories.ModuleFactory)

# @pytest.fixture
# def variant_factory(db):
#     def factory(**kwargs):
#         from myapp.models import Variant, ARObject
#         ar_object = ARObject.objects.create()  # Or use a factory
#         return Variant.objects.create(ar_object=ar_object, **kwargs)
#     return factory


class VariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Variant
        django_get_or_create = ('name',)  # Optional: prevents duplicates by name

    creator = factory.SubFactory(a4_factories.USER_FACTORY)
    ar_object = factory.SubFactory(ARObjectFactory)
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    mesh_id = factory.Faker('uuid4')
    
    # Default PointField values
    offset_position = Point(0, 0, 0)
    offset_rotation = Point(0, 0, 0)
    offset_scale = Point(0, 0, 0)
    weight = 0