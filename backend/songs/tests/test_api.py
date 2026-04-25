"""
Automated API tests (Django + DRF). Run: python manage.py test songs
"""
from __future__ import annotations

from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from songs.generation.factory import clear_runtime_generator_name
from songs.models import AIGenerationRequest, GenerationStatus, User

API = "/api"


class CleanCacheMixin:
    def setUp(self) -> None:
        super().setUp()
        cache.clear()
        clear_runtime_generator_name()

    def tearDown(self) -> None:
        cache.clear()
        clear_runtime_generator_name()
        super().tearDown()


class AuthConfigTests(CleanCacheMixin, APITestCase):
    def test_auth_config_empty_when_not_configured(self) -> None:
        with override_settings(GOOGLE_OAUTH_CLIENT_ID=""):
            r = self.client.get(f"{API}/auth/config/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json().get("google_client_id"), "")

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="testclient.apps.googleusercontent.com")
    def test_auth_config_returns_client_id(self) -> None:
        r = self.client.get(f"{API}/auth/config/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(
            r.json().get("google_client_id"), "testclient.apps.googleusercontent.com"
        )


class AuthGoogleTests(CleanCacheMixin, APITestCase):
    @override_settings(GOOGLE_OAUTH_CLIENT_ID="")
    def test_google_oauth_not_configured_returns_503(self) -> None:
        r = self.client.post(f"{API}/auth/google/", {"id_token": "x"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("not configured", r.json().get("detail", "").lower())

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="cid.apps.googleusercontent.com")
    def test_missing_id_token_returns_400(self) -> None:
        r = self.client.post(f"{API}/auth/google/", {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="cid.apps.googleusercontent.com")
    @mock.patch("songs.views.auth_google.id_token.verify_oauth2_token")
    def test_valid_id_token_returns_user_and_session(self, mock_verify) -> None:
        mock_verify.return_value = {
            "sub": "google-sub-123",
            "email": "a@example.com",
            "name": "Test User",
        }
        r = self.client.post(
            f"{API}/auth/google/",
            {"id_token": "mock-jwt"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        body = r.json()
        self.assertIn("session_token", body)
        self.assertTrue(body["session_token"])
        self.assertEqual(body.get("email"), "a@example.com")
        u = User.objects.get(google_id="google-sub-123")
        self.assertEqual(u.session_token, body["session_token"])


class UserGetOrCreateTests(CleanCacheMixin, APITestCase):
    @override_settings(ALLOW_DISPLAY_NAME_GET_OR_CREATE=False)
    def test_get_or_create_forbidden_by_default(self) -> None:
        r = self.client.post(
            f"{API}/users/get-or-create/",
            {"username": "api_tester"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(ALLOW_DISPLAY_NAME_GET_OR_CREATE=True)
    def test_get_or_create_creates_user_with_session(self) -> None:
        r = self.client.post(
            f"{API}/users/get-or-create/",
            {"username": "api_tester"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        body = r.json()
        self.assertIn("session_token", body)
        self.assertEqual(body["username"], "api_tester")
        u = User.objects.get(username="api_tester")
        self.assertTrue(u.session_token)


class UserSongsScopeTests(CleanCacheMixin, APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.u1 = User.objects.create(username="owner1", display_name="Owner1")
        cls.u2 = User.objects.create(username="owner2", display_name="Owner2")
        issue_token(cls.u1)
        issue_token(cls.u2)

    def test_cannot_list_other_users_songs_with_bearer(self) -> None:
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.u1.session_token}")
        r = client.get(f"{API}/users/{self.u2.pk}/songs/")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


def issue_token(user: User) -> None:
    from songs.utils_auth import issue_session_token

    issue_session_token(user)
    user.refresh_from_db()


class GenerationConfigTests(CleanCacheMixin, APITestCase):
    @override_settings(GENERATOR_STRATEGY="mock", SUNO_API_KEY="")
    def test_get_shows_mock_and_strategy_source(self) -> None:
        r = self.client.get(f"{API}/generation-config/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        j = r.json()
        self.assertEqual(j.get("generator_strategy"), "mock")
        self.assertIn("strategy_source", j)

    def test_post_invalid_strategy_returns_400(self) -> None:
        r = self.client.post(
            f"{API}/generation-config/",
            {"generator_strategy": "lunar"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(GENERATOR_STRATEGY="mock", SUNO_API_KEY="")
    def test_post_switch_to_mock(self) -> None:
        r = self.client.post(
            f"{API}/generation-config/",
            {"generator_strategy": "mock"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json().get("generator_strategy"), "mock")


@override_settings(ALLOW_DISPLAY_NAME_GET_OR_CREATE=True, GENERATOR_STRATEGY="mock")
class MockGenerationRunTests(CleanCacheMixin, APITestCase):
    """End-to-end: user → song → prompt → generation request → run (mock)."""

    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        r = self.client.post(
            f"{API}/users/get-or-create/", {"username": "gen_test"}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.content)
        self.assertIn("session_token", r.json())
        self.user_id = r.json()["id"]
        self.token = r.json()["session_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_full_mock_generation_completes(self) -> None:
        rs = self.client.post(
            f"{API}/songs/",
            {
                "user_id": self.user_id,
                "title": "Unit Test Song",
                "generation_status": "DRAFT",
                "is_draft": True,
            },
            format="json",
        )
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED, rs.content)
        song_id = rs.json()["id"]

        rp = self.client.post(
            f"{API}/song-prompts/",
            {
                "song_id": song_id,
                "title": "T",
                "occasion": "BIRTHDAY",
                "mood_and_tone": "HAPPY",
                "singer_tone": "NEUTRAL",
                "description": "",
            },
            format="json",
        )
        self.assertEqual(rp.status_code, status.HTTP_201_CREATED, rp.content)
        prompt_id = rp.json()["id"]

        rg = self.client.post(
            f"{API}/generation-requests/",
            {"prompt_id": prompt_id},
            format="json",
        )
        self.assertEqual(rg.status_code, status.HTTP_201_CREATED, rg.content)
        req_pk = rg.json()["id"]

        rr = self.client.post(
            f"{API}/generation-requests/{req_pk}/run/",
            {},
            format="json",
        )
        self.assertEqual(rr.status_code, status.HTTP_200_OK, rr.content)
        data = rr.json()
        self.assertEqual(data.get("status"), GenerationStatus.COMPLETED)
        ar = AIGenerationRequest.objects.get(pk=req_pk)
        self.assertTrue(ar.external_task_id.startswith("mock-"))
        self.assertIn("audio", (ar.prompt.song.audio_file_url or "").lower())


class ModelSanityTests(TestCase):
    def test_user_str(self) -> None:
        u = User.objects.create(username="u", display_name="D")
        self.assertIn("u", str(u))
