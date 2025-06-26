from adhocracy4.api import routers as a4routers

from .api import CombinedCommentViewSet

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r"arpas_comments", CombinedCommentViewSet, basename="arpas_comments")

urlpatterns = ct_router.urls
