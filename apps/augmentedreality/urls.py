from adhocracy4.api import routers as a4routers

from .api import CombinedCommentViewSet
from .api import CombinedRatingViewSet

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r"arpas-comments", CombinedCommentViewSet, basename="arpas-comments")
ct_router.register(r"arpas-ratings", CombinedRatingViewSet, basename="arpas-ratings")

urlpatterns = ct_router.urls
