from rest_framework import serializers

from util.minio_client import minio_client

from . import models


class VariantSerializer(serializers.ModelSerializer):
    offset_position = serializers.SerializerMethodField()
    offset_scale = serializers.SerializerMethodField()
    offset_rotation = serializers.SerializerMethodField()
    mesh_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Variant
        fields = (
            "id",
            "name",
            "description",
            "mesh_id",
            "mesh_url",
            "offset_position",
            "offset_scale",
            "offset_rotation",
            "weight",
        )

    def get_offset_position(self, obj):
        return list(obj.offset_position.tuple)

    def get_offset_scale(self, obj):
        return list(obj.offset_scale.tuple)

    def get_offset_rotation(self, obj):
        return list(obj.offset_rotation.tuple)

    def get_mesh_url(self, obj):
        return minio_client.get_presigned_url(obj.mesh_id)


class ObjectSerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True)
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = models.Object
        fields = ("id", "name", "coordinates", "qr_id", "variants")

    def get_coordinates(self, obj):
        return list(obj.coordinates.tuple)


class SceneSerializer(serializers.ModelSerializer):
    objects = ObjectSerializer(source="object_set", many=True)

    class Meta:
        model = models.Scene
        fields = ("id", "objects", "object_id", "content_type")
