from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models

from adhocracy4.comments.models import Comment
from adhocracy4.models import query
from adhocracy4.ratings.models import Rating


class Scene(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = (("content_type", "object_id"),)

    def __str__(self):
        if self.item.name:
            return f"Scene {self.item.name}"
        return f"Scene in {self.item.project.name}"


class Object(models.Model):
    name = models.CharField(max_length=255)
    scene = models.ForeignKey(
        Scene, on_delete=models.CASCADE, related_name="object_set"
    )
    coordinates = PointField(dim=3, default=Point(0, 0, 0), srid=0)
    qr_id = models.CharField(max_length=255)

    def __str__(self):
        return f"Object: {self.name}"


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
    object = models.ForeignKey(
        Object, on_delete=models.CASCADE, related_name="variants"
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
        """Get the project through the relationship: Variant -> Object -> Scene -> item -> project"""
        return self.object.scene.item.project

    @property
    def module(self):
        """Get the module through the relationship: Variant -> Object -> Scene -> item -> module"""
        return self.object.scene.item.module
