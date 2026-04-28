from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    SongViewSet,
    LibraryViewSet,
    SongPromptViewSet,
    AIGenerationRequestViewSet,
    SharedSongViewSet,
    PlaybackSessionViewSet,
    DraftViewSet,
)
from .views.auth_google import (
    auth_config,
    auth_google,
    auth_google_callback,
    auth_google_login,
)
from .views.generation_config import generation_config

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("songs", SongViewSet, basename="song")
router.register("libraries", LibraryViewSet, basename="library")
router.register("song-prompts", SongPromptViewSet, basename="song-prompt")
router.register(
    "generation-requests", AIGenerationRequestViewSet, basename="generation-request"
)
router.register("shared-songs", SharedSongViewSet, basename="shared-song")
router.register(
    "playback-sessions", PlaybackSessionViewSet, basename="playback-session"
)
router.register("drafts", DraftViewSet, basename="draft")

urlpatterns = [
    path("auth/config/", auth_config, name="auth-config"),
    path("auth/google/login/", auth_google_login, name="auth-google-login"),
    path(
        "auth/google/callback/",
        auth_google_callback,
        name="auth-google-callback",
    ),
    path("auth/google/", auth_google, name="auth-google"),
    path("generation-config/", generation_config, name="generation-config"),
] + router.urls
