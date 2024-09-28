from rest_framework import serializers
from .models import Release, ReleaseChannel


class ReleaseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ["accessibility_version", "hearthstone_version"]


class ReleaseFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = [
            "hearthstone_version",
            "accessibility_version",
            "changelog",
            "upload_time",
            "url",
        ]

    url = serializers.URLField(source="file.url")


class ReleaseChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseChannel
        fields = ["name", "description", "latest_release"]

    latest_release = ReleaseFullSerializer(source="get_latest_release", read_only=True)
