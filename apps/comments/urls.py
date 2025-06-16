from adhocracy4.api import routers as a4routers

from .api import ARCommentViewSet

ct_router = a4routers.ContentTypeDefaultRouter()
ct_router.register(r"ar_comments", ARCommentViewSet, basename="comments")

urlpatterns = ct_router.urls
