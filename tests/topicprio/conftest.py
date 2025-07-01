from pytest_factoryboy import register

from . import factories as topicprio

register(topicprio.TopicFactory)
register(topicprio.ARObjectFactory)
register(topicprio.VariantFactory)
