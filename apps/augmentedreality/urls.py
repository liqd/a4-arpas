from adhocracy4.api import routers as a4routers

from .api import CombinedCommentViewSet
from .api import CombinedRatingViewSet

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r"arpas_comments", CombinedCommentViewSet, basename="arpas_comments")
ct_router.register(r"arpas_ratings", CombinedRatingViewSet, basename="arpas_ratings")

urlpatterns = ct_router.urls
