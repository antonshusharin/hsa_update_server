from django.urls import path
from . import views

urlpatterns = [
    path("login", views.Login.as_view(), name="api-login"),
    path("releases/latest", views.GetLatestRelease.as_view(), name="releases-latest"),
    path(
        "releases/upload/<channel>",
        views.UploadRelease.as_view(),
        name="releases-upload",
    ),
    path("releases/<pk>", views.GetOrDeleteRelease.as_view(), name="releases"),
    path(
        "release-channels",
        views.ListOrCreateReleaseChannels.as_view(),
        name="release-channels",
    ),
    path(
        "release-channels/<str:name>",
        views.GetUpdateOrDeleteReleaseChannel.as_view(),
        name="release-channel-detail",
    ),
    path(
        "release-channels/<channel_name>/add-release/<int:release_version>",
        views.AddReleaseToChannel.as_view(),
        name="release-channels-add-release-",
    ),
    path(
        "release-channels/<channel_name>/remove-release/<int:release_version>",
        views.RemoveReleaseFromChannel.as_view(),
        name="release-channels-remove-release",
    ),
]
