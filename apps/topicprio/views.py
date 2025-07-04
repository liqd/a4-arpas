from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from adhocracy4.categories import filters as category_filters
from adhocracy4.dashboard import mixins
from adhocracy4.exports.views import DashboardExportView
from adhocracy4.filters import filters as a4_filters
from adhocracy4.filters import views as filter_views
from adhocracy4.filters import widgets as filters_widgets
from adhocracy4.filters.filters import FreeTextFilter
from adhocracy4.projects.mixins import DisplayProjectOrModuleMixin
from adhocracy4.projects.mixins import ProjectMixin
from apps.contrib.widgets import AplusOrderingWidget
from apps.ideas import views as idea_views

from . import forms
from . import models


class FreeTextFilterWidget(filters_widgets.FreeTextFilterWidget):
    label = _("Search")


class TopicFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {"ordering": "name"}
    category = category_filters.CategoryFilter()
    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=(
            ("name", _("Alphabetical")),
            ("-positive_rating_count", _("Most popular")),
            ("-comment_count", _("Most commented")),
        ),
        widget=AplusOrderingWidget,
    )
    search = FreeTextFilter(widget=FreeTextFilterWidget, fields=["name"])

    class Meta:
        model = models.Topic
        fields = ["search", "category"]


class TopicListView(idea_views.AbstractIdeaListView, DisplayProjectOrModuleMixin):
    model = models.Topic
    filter_set = TopicFilterSet


class TopicDetailView(idea_views.AbstractIdeaDetailView):
    model = models.Topic
    queryset = (
        models.Topic.objects.annotate_positive_rating_count()
        .annotate_negative_rating_count()
        .prefetch_related("_scene__arobjects__variants")
    )
    permission_required = "a4_candy_topicprio.view_topic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["variant_object"] = self.get_variant_object()
        return context

    # Get the first Variant of the topic to start with
    def get_variant_object(self):
        if self.object and self.object.scene:
            first_ar_object = self.object.scene.arobjects.first()
            if first_ar_object:
                first_variant = (
                    first_ar_object.variants.order_by("pk")
                    .annotate_positive_rating_count()
                    .annotate_negative_rating_count()
                    .first()
                )
                if first_variant:
                    return first_variant
        return self.object


class TopicCreateFilterSet(a4_filters.DefaultsFilterSet):
    defaults = {"ordering": "name"}

    category = category_filters.CategoryFilter()

    ordering = a4_filters.DynamicChoicesOrderingFilter(
        choices=(("name", _("Alphabetical")),), widget=AplusOrderingWidget
    )

    class Meta:
        model = models.Topic
        fields = ["category"]


class TopicListDashboardView(
    ProjectMixin,
    mixins.DashboardBaseMixin,
    mixins.DashboardComponentMixin,
    filter_views.FilteredListView,
):
    model = models.Topic
    template_name = "a4_candy_topicprio/topic_dashboard_list.html"
    filter_set = TopicCreateFilterSet
    permission_required = "a4projects.change_project"

    def get_queryset(self):
        return super().get_queryset().filter(module=self.module)

    def get_permission_object(self):
        return self.project


class TopicCreateView(
    mixins.DashboardBaseMixin,
    mixins.DashboardComponentMixin,
    mixins.DashboardComponentFormSignalMixin,
    idea_views.AbstractIdeaCreateView,
):
    model = models.Topic
    form_class = forms.TopicForm
    permission_required = "a4_candy_topicprio.add_topic"
    template_name = "a4_candy_topicprio/topic_create_form.html"

    def get_success_url(self):
        return reverse(
            "a4dashboard:topic-list",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )

    def get_permission_object(self):
        return self.module


class TopicUpdateView(
    mixins.DashboardBaseMixin,
    mixins.DashboardComponentMixin,
    mixins.DashboardComponentFormSignalMixin,
    idea_views.AbstractIdeaUpdateView,
):
    model = models.Topic
    form_class = forms.TopicForm
    permission_required = "a4_candy_topicprio.change_topic"
    template_name = "a4_candy_topicprio/topic_update_form.html"

    @property
    def organisation(self):
        return self.project.organisation

    def get_success_url(self):
        return reverse(
            "a4dashboard:topic-list",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )

    def get_permission_object(self):
        return self.get_object()


class TopicDeleteView(
    mixins.DashboardBaseMixin,
    mixins.DashboardComponentMixin,
    mixins.DashboardComponentFormSignalMixin,
    idea_views.AbstractIdeaDeleteView,
):
    model = models.Topic
    success_message = _("The topic has been deleted")
    permission_required = "a4_candy_topicprio.change_topic"
    template_name = "a4_candy_topicprio/topic_confirm_delete.html"

    @property
    def organisation(self):
        return self.project.organisation

    def get_success_url(self):
        return reverse(
            "a4dashboard:topic-list",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )

    def get_permission_object(self):
        return self.get_object()


class TopicDashboardExportView(DashboardExportView):
    template_name = "a4exports/export_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["export"] = reverse(
            "a4dashboard:topic-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        context["comment_export"] = reverse(
            "a4dashboard:topic-comment-export",
            kwargs={
                "organisation_slug": self.module.project.organisation.slug,
                "module_slug": self.module.slug,
            },
        )
        return context
