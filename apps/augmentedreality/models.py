from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import models

from adhocracy4.comments.models import Comment
from adhocracy4.models import query
from adhocracy4.modules.models import Item
from adhocracy4.ratings.models import Rating


def validate_item_content_type(content_type):
    """Validator to ensure only Item models can be stored in Scene"""
    try:
        model_class = content_type.model_class()
        if not model_class or not issubclass(model_class, Item):
            raise ValidationError(
                f"Scene can only be associated with Item models, not {content_type.model_class().__name__}"
            )
    except (AttributeError, ImportError):
        raise ValidationError("Invalid content type")


class Scene(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="scenes"
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = (("content_type", "object_id"),)

    def clean(self):
        super().clean()
        if self.content_type_id:
            validate_item_content_type(self.content_type)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.item.name:
            return f"Scene {self.item.name}"
        return f"Scene in {self.item.project.name}"


class ARObject(models.Model):
    name = models.CharField(max_length=255)
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name="arobjects")
    coordinates = PointField(dim=3, default=Point(0, 0, 0), srid=0)
    qr_id = models.CharField(max_length=255)

    def __str__(self):
        return f"ARObject: {self.name}"


class VariantQuerySet(query.RateableQuerySet):
    pass


class Variant(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    mesh_id = models.CharField(max_length=512)
    offset_position = PointField(dim=3, default=Point(0, 0, 0), srid=0)
    offset_rotation = PointField(dim=3, default=Point(0, 0, 0), srid=0)
    offset_scale = PointField(dim=3, default=Point(0, 0, 0), srid=0)
    weight = models.PositiveIntegerField(default=0)
    ar_object = models.ForeignKey(
        ARObject, on_delete=models.CASCADE, related_name="variants"
    )

    ratings = GenericRelation(
        Rating, related_query_name="topic", object_id_field="object_pk"
    )
    comments = GenericRelation(
        Comment, related_query_name="topic", object_id_field="object_pk"
    )

    objects = VariantQuerySet.as_manager()

    class Meta:
        ordering = ["weight"]

    def __str__(self):
        return f"Variant: {self.name}"

    @property
    def project(self):
        """Get the project through the relationship: Variant -> ARObject -> Scene -> item -> project"""
        return self.ar_object.scene.item.project

    @property
    def module(self):
        """Get the module through the relationship: Variant -> ARObject -> Scene -> item -> module"""
        return self.ar_object.scene.item.module
