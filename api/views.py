import zipfile

from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from knox.views import LoginView
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Release, ReleaseChannel
from api.patch_utils import parse_changelog, parse_manifest
from api.serializers import ReleaseChannelSerializer, ReleaseFullSerializer

# Create your views here.


class Login(LoginView):
    authentication_classes = [BasicAuthentication]

    def post(self, request, version=None, format=None):
        return super().post(request, format)


class GetOrDeleteRelease(RetrieveDestroyAPIView):
    queryset = Release.objects.all()
    serializer_class = ReleaseFullSerializer


class GetLatestRelease(RetrieveAPIView):
    serializer_class = ReleaseFullSerializer

    def get_object(self):
        try:
            return Release.objects.latest()
        except Release.DoesNotExist:
            raise NotFound()


class UploadRelease(APIView):
    check_version = True
    parser_classes = [FileUploadParser]

    def post(self, request, format=None, channel="", **kwargs):
        try:
            release_channel = ReleaseChannel.objects.get(name=channel)
        except ReleaseChannel.DoesNotExist:
            raise NotFound(f"No release channel named {channel}")
        f = request.data["file"]
        if not zipfile.is_zipfile(f):
            raise ValidationError("A valid ZIP file is required.")
        z = zipfile.ZipFile(f, "r", zipfile.ZIP_DEFLATED)
        hearthstone_version, accessibility_version = parse_manifest(z)
        changelog = parse_changelog(z)
        release, created = Release.objects.get_or_create(
            {"hearthstone_version": hearthstone_version},
            accessibility_version=accessibility_version,
        )
        if self.check_version and not created:
            raise ValidationError("Release already exists")
        release.file = f
        release.changelog = changelog
        release.save()
        release_channel.releases.add(release)
        return Response(status=201, data=ReleaseFullSerializer(release).data)


class ListOrCreateReleaseChannels(ListCreateAPIView):
    queryset = ReleaseChannel.objects.all()
    serializer_class = ReleaseChannelSerializer

    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AddReleaseToChannel(APIView):
    def post(
        self, request, format=None, channel_name=None, release_version=None, **kwargs
    ):
        try:
            channel = ReleaseChannel.objects.get(name=channel_name)
        except ReleaseChannel.DoesNotExist:
            raise NotFound(f"No release channel named {channel_name}")
        try:
            release = Release.objects.get(accessibility_version=release_version)
        except Release.DoesNotExist:
            raise NotFound(f"No release with version {release_version}")
        channel.releases.add(release)
        return Response(status=204)


class RemoveReleaseFromChannel(APIView):
    def delete(
        self, request, format=None, channel_name=None, release_version=None, **kwargs
    ):
        try:
            channel = ReleaseChannel.objects.get(name=channel_name)
        except ReleaseChannel.DoesNotExist:
            raise NotFound(f"No release channel named {channel_name}")
        try:
            release = Release.objects.get(accessibility_version=release_version)
        except Release.DoesNotExist:
            raise NotFound(f"No release with version {release_version}")
        channel.releases.remove(release)
        return Response(status=204)


class GetUpdateOrDeleteReleaseChannel(RetrieveUpdateDestroyAPIView):
    queryset = ReleaseChannel.objects.all()
    serializer_class = ReleaseChannelSerializer
    lookup_field = "name"


class DownloadLatestReleaseFromChannel(APIView):
    def get(self, request,  channel, version=None, format=None):
        release_channel = get_object_or_404(ReleaseChannel, name=channel)
        if latest_release := release_channel.get_latest_release():
            return redirect(latest_release.file.url, permanent=False)
        raise NotFound(f"Channel {channel} has no releases")
