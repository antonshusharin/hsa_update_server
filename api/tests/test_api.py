from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_200_OK
from rest_framework.test import APITestCase

from api.models import Release, ReleaseChannel

# Create your tests here.


class CustomTestCase(APITestCase):
    def setUp(self) -> None:
        user = get_user_model().objects.create_superuser("admin", None, "admin")
        self.client.force_authenticate(user)
        self.releases = []  # We need to keep track of any Release objects we create during tests, because post_delete might not be emitted and temporary files will be left in media root.

    def tearDown(self):
        for release in self.releases:
            release.delete()

    def create_fake_release(self, accessibility_version=100):
        release = Release.objects.create(
            hearthstone_version="30.0.0.203120",
            accessibility_version=accessibility_version,
            changelog="Something was added",
            file=SimpleUploadedFile("test.zip", b""),
        )
        self.releases.append(release)
        return release


class ReleaseChannelTestCase(CustomTestCase):
    def setUp(self):
        super().setUp()
        channel1 = ReleaseChannel.objects.create(
            name="testing", description="Recommended for experienced users"
        )  # noqa: F841
        channel2 = ReleaseChannel.objects.create(
            name="duos", description="Battlegrounds Duos beta test"
        )
        release = self.create_fake_release()
        channel2.releases.add(release)

    def test_create_release_channel(self):
        url = reverse("release-channels", kwargs={"version": "v1"})
        res = self.client.post(
            url, {"name": "stable", "description": "Recommended for all users"}
        )
        self.assertEqual(res.status_code, HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "stable")
        self.assertEqual(res.data["description"], "Recommended for all users")

    def test_list_release_channels(self):
        url = reverse("release-channels", kwargs={"version": "v1"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, HTTP_200_OK)
        data = res.data
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        channel1, channel2 = data
        self.assertEqual(channel1["name"], "testing")
        self.assertEqual(channel1["description"], "Recommended for experienced users")
        self.assertIsNone(channel1["latest_release"])
        self.assertEqual(channel2["name"], "duos")
        self.assertEqual(channel2["description"], "Battlegrounds Duos beta test")
        release = channel2["latest_release"]
        self.assertIsNotNone(release)
        self.assertEqual(release["hearthstone_version"], "30.0.0.203120")
        self.assertEqual(release["accessibility_version"], 100)
        self.assertEqual(release["changelog"], "Something was added")

    def test_add_release_to_channel(self):
        channel = ReleaseChannel.objects.get(name="testing")
        self.assertIsNone(channel.get_latest_release())
        release = self.create_fake_release(101)
        url = reverse(
            "release-channels-add-release-",
            kwargs={"version": "v1", "channel_name": "testing", "release_version": 101},
        )
        self.client.post(url)
        self.assertEqual(channel.get_latest_release(), release)

    def test_remove_release_from_channel(self):
        # Create a new channel and release specifically for this test
        channel = ReleaseChannel.objects.create(
            name="test_channel", description="Test Channel"
        )
        release = self.create_fake_release(102)
        channel.releases.add(release)

        # Verify the release is in the channel
        self.assertEqual(channel.get_latest_release(), release)

        # Remove the release
        url = reverse(
            "release-channels-remove-release",
            kwargs={
                "version": "v1",
                "channel_name": "test_channel",
                "release_version": release.accessibility_version,
            },
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

        # Verify the release has been removed
        channel.refresh_from_db()
        self.assertIsNone(channel.get_latest_release())

    def test_get_release_channel(self):
        ReleaseChannel.objects.get(name="testing")
        url = reverse(
            "release-channel-detail", kwargs={"version": "v1", "name": "testing"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["name"], "testing")
        self.assertEqual(
            response.data["description"], "Recommended for experienced users"
        )

    def test_delete_release_channel(self):
        ReleaseChannel.objects.create(
            name="to_delete", description="Channel to be deleted"
        )
        url = reverse(
            "release-channel-detail", kwargs={"version": "v1", "name": "to_delete"}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertFalse(ReleaseChannel.objects.filter(name="to_delete").exists())

    def test_update_release_channel(self):
        channel = ReleaseChannel.objects.create(
            name="update_test", description="Original description"
        )
        url = reverse(
            "release-channel-detail", kwargs={"version": "v1", "name": "update_test"}
        )
        new_description = "Updated description"
        response = self.client.patch(url, {"description": new_description})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["description"], new_description)
        channel.refresh_from_db()
        self.assertEqual(channel.description, new_description)

    def test_download_latest_release_from_channel(self):
        release = ReleaseChannel.objects.get(name="duos").get_latest_release()
        url = reverse(
            "download-latest-release-from-channel",
            kwargs={"version": "v1", "channel": "duos"},
        )
        response = self.client.get(url)
        self.assertRedirects(
            response, release.file.url, 302, fetch_redirect_response=False
        )


TEST_FILES_BASE = Path(__file__).resolve().parent / "files"


class ReleaseTestCase(CustomTestCase):
    def setUp(self):
        super().setUp()
        self.stable = ReleaseChannel.objects.create(
            name="stable", description="Recommended for all users"
        )

    def test_upload_release(self):
        self.assertIsNone(self.stable.get_latest_release())
        with open(TEST_FILES_BASE / "good_patch.zip", "rb") as f:
            res = self.upload_release("stable", f)

        self.assertEqual(res.status_code, HTTP_201_CREATED)
        data = res.data
        self.assertEqual(data["hearthstone_version"], "30.0.0.203120")
        self.assertEqual(data["accessibility_version"], 104)
        self.assertTrue(data["changelog"])
        self.assertIsNotNone(self.stable.get_latest_release())
        self.releases.append(self.stable.get_latest_release())

    def upload_release(self, channel, f):
        url = reverse("releases-upload", kwargs={"version": "v1", "channel": channel})
        return self.client.generic(
            "POST",
            url,
            f.read(),
            headers={
                "Content-Type": "application/zip",
                "Content-Disposition": "Attachment; filename=test.zip",
            },
        )
