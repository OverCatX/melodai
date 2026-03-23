"""
Tests for the songs app.
"""

from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from .models import (
    GenerationStatus,
    Occasion,
    MoodTone,
    SingerTone,
    User,
    Song,
    Library,
    SongPrompt,
    AIGenerationRequest,
    SharedSong,
    PlaybackSession,
    Draft,
)


def make_user(email="test@example.com", display_name="Test User"):
    return User.objects.create(
        google_id=f"google_{email}",
        email=email,
        display_name=display_name,
        session_token="tok123",
    )


def make_song(user, title="My Song"):
    return Song.objects.create(
        user=user,
        title=title,
        generation_status=GenerationStatus.DRAFT,
    )


def make_prompt(song):
    return SongPrompt.objects.create(
        song=song,
        title="A Birthday Song",
        occasion=Occasion.BIRTHDAY,
        mood_and_tone=MoodTone.HAPPY,
        singer_tone=SingerTone.FEMALE_LIGHT,
        description="For my best friend.",
    )


class EnumerationTests(TestCase):

    def test_generation_status_values(self):
        expected = {"IN_PROGRESS", "COMPLETED", "FAILED", "DRAFT"}
        actual = {c.value for c in GenerationStatus}
        self.assertEqual(actual, expected)

    def test_occasion_values(self):
        expected = {"BIRTHDAY", "WEDDING", "ANNIVERSARY", "GRADUATION", "GENERAL"}
        self.assertEqual({c.value for c in Occasion}, expected)

    def test_mood_tone_values(self):
        expected = {"HAPPY", "SAD", "ROMANTIC", "ENERGETIC", "CALM"}
        self.assertEqual({c.value for c in MoodTone}, expected)

    def test_singer_tone_values(self):
        expected = {"MALE_DEEP", "MALE_LIGHT", "FEMALE_DEEP", "FEMALE_LIGHT", "NEUTRAL"}
        self.assertEqual({c.value for c in SingerTone}, expected)


class UserTests(TestCase):

    def test_create_user(self):
        user = make_user()
        self.assertIsNotNone(user.pk)
        self.assertIsNotNone(user.user_id)

    def test_user_email_unique(self):
        make_user(email="same@example.com")
        with self.assertRaises(IntegrityError):
            make_user(email="same@example.com")

    def test_user_google_id_unique(self):
        User.objects.create(google_id="gid1", email="a@x.com", display_name="A")
        with self.assertRaises(IntegrityError):
            User.objects.create(google_id="gid1", email="b@x.com", display_name="B")

    def test_update_user(self):
        user = make_user()
        user.display_name = "Updated Name"
        user.save()
        self.assertEqual(User.objects.get(pk=user.pk).display_name, "Updated Name")

    def test_delete_user_cascades_songs(self):
        user = make_user()
        make_song(user)
        user.delete()
        self.assertEqual(Song.objects.count(), 0)


class SongTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_create_song(self):
        song = make_song(self.user)
        self.assertEqual(song.generation_status, GenerationStatus.DRAFT)
        self.assertTrue(song.is_draft)
        self.assertFalse(song.is_favorite)

    def test_song_share_link_optional(self):
        song = make_song(self.user)
        self.assertEqual(song.share_link, "")

    def test_song_audio_url_optional(self):
        song = make_song(self.user)
        self.assertEqual(song.audio_file_url, "")

    def test_update_generation_status(self):
        song = make_song(self.user)
        song.generation_status = GenerationStatus.COMPLETED
        song.is_draft = False
        song.save()
        refreshed = Song.objects.get(pk=song.pk)
        self.assertEqual(refreshed.generation_status, GenerationStatus.COMPLETED)
        self.assertFalse(refreshed.is_draft)

    def test_delete_song(self):
        song = make_song(self.user)
        song_pk = song.pk
        song.delete()
        self.assertFalse(Song.objects.filter(pk=song_pk).exists())


class LibraryTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_create_library(self):
        lib = Library.objects.create(user=self.user)
        self.assertEqual(lib.user, self.user)
        self.assertEqual(lib.total_count, 0)

    def test_user_library_one_to_one(self):
        Library.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            Library.objects.create(user=self.user)

    def test_library_contains_songs(self):
        lib = Library.objects.create(user=self.user)
        song1 = make_song(self.user, "Song A")
        song2 = make_song(self.user, "Song B")
        lib.songs.add(song1, song2)
        self.assertEqual(lib.songs.count(), 2)

    def test_sync_total_count(self):
        lib = Library.objects.create(user=self.user)
        lib.songs.add(make_song(self.user, "S1"), make_song(self.user, "S2"))
        lib.sync_total_count()
        self.assertEqual(Library.objects.get(pk=lib.pk).total_count, 2)

    def test_library_filter_criteria_optional(self):
        lib = Library.objects.create(user=self.user)
        self.assertEqual(lib.filter_criteria, "")

    def test_delete_user_cascades_library(self):
        Library.objects.create(user=self.user)
        self.user.delete()
        self.assertEqual(Library.objects.count(), 0)


class SongPromptTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.song = make_song(self.user)

    def test_create_prompt(self):
        prompt = make_prompt(self.song)
        self.assertEqual(prompt.song, self.song)
        self.assertEqual(prompt.occasion, Occasion.BIRTHDAY)

    def test_prompt_song_one_to_one(self):
        make_prompt(self.song)
        with self.assertRaises(IntegrityError):
            SongPrompt.objects.create(
                song=self.song,
                title="Duplicate",
                occasion=Occasion.GENERAL,
                mood_and_tone=MoodTone.CALM,
                singer_tone=SingerTone.NEUTRAL,
            )

    def test_delete_song_cascades_prompt(self):
        make_prompt(self.song)
        self.song.delete()
        self.assertEqual(SongPrompt.objects.count(), 0)

    def test_reverse_accessor(self):
        make_prompt(self.song)
        self.assertTrue(hasattr(self.song, "prompt"))
        self.assertEqual(self.song.prompt.occasion, Occasion.BIRTHDAY)


class AIGenerationRequestTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.song = make_song(self.user)
        self.prompt = make_prompt(self.song)

    def test_create_request(self):
        req = AIGenerationRequest.objects.create(prompt=self.prompt)
        self.assertEqual(req.status, GenerationStatus.IN_PROGRESS)
        self.assertEqual(req.error_message, "")

    def test_request_prompt_one_to_one(self):
        AIGenerationRequest.objects.create(prompt=self.prompt)
        with self.assertRaises(IntegrityError):
            AIGenerationRequest.objects.create(prompt=self.prompt)

    def test_error_message_optional(self):
        req = AIGenerationRequest.objects.create(prompt=self.prompt)
        self.assertEqual(req.error_message, "")

    def test_status_transitions(self):
        req = AIGenerationRequest.objects.create(prompt=self.prompt)
        req.status = GenerationStatus.FAILED
        req.error_message = "Timeout from AI service"
        req.save()
        refreshed = AIGenerationRequest.objects.get(pk=req.pk)
        self.assertEqual(refreshed.status, GenerationStatus.FAILED)
        self.assertIn("Timeout", refreshed.error_message)

    def test_delete_prompt_cascades_request(self):
        AIGenerationRequest.objects.create(prompt=self.prompt)
        self.prompt.delete()
        self.assertEqual(AIGenerationRequest.objects.count(), 0)


class SharedSongTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.song = make_song(self.user)

    def test_create_shared_song(self):
        shared = SharedSong.objects.create(
            song=self.song,
            share_link="https://aisong.example.com/share/abc123",
        )
        self.assertFalse(shared.accessible_by_guest)
        self.assertIsNotNone(shared.shared_at)

    def test_song_shared_song_one_to_one(self):
        SharedSong.objects.create(song=self.song, share_link="https://example.com/1")
        with self.assertRaises(IntegrityError):
            SharedSong.objects.create(
                song=self.song, share_link="https://example.com/2"
            )

    def test_share_link_unique(self):
        song2 = make_song(self.user, "Other Song")
        SharedSong.objects.create(song=self.song, share_link="https://example.com/same")
        with self.assertRaises(IntegrityError):
            SharedSong.objects.create(song=song2, share_link="https://example.com/same")

    def test_delete_song_cascades_shared_song(self):
        SharedSong.objects.create(song=self.song, share_link="https://example.com/x")
        self.song.delete()
        self.assertEqual(SharedSong.objects.count(), 0)


class PlaybackSessionTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_create_session(self):
        session = PlaybackSession.objects.create(current_position=42.5)
        self.assertIsNotNone(session.session_id)
        self.assertIsNone(session.loop_start)
        self.assertIsNone(session.loop_end)

    def test_loop_boundaries_optional(self):
        session = PlaybackSession.objects.create(
            current_position=10.0,
            loop_start=5.0,
            loop_end=30.0,
        )
        self.assertEqual(session.loop_start, 5.0)
        self.assertEqual(session.loop_end, 30.0)

    def test_song_linked_to_session(self):
        session = PlaybackSession.objects.create(current_position=0.0)
        song = Song.objects.create(
            user=self.user,
            title="Playing Now",
            playback_session=session,
        )
        self.assertEqual(song.playback_session, session)
        self.assertEqual(session.songs.count(), 1)

    def test_delete_session_nullifies_song_reference(self):
        session = PlaybackSession.objects.create(current_position=0.0)
        song = Song.objects.create(
            user=self.user, title="Track", playback_session=session
        )
        session.delete()
        song.refresh_from_db()
        self.assertIsNone(song.playback_session)


class DraftTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.song = make_song(self.user)

    def test_create_draft(self):
        draft = Draft.objects.create(song=self.song, retention_policy="30_DAYS")
        self.assertFalse(draft.is_submitted)
        self.assertEqual(draft.retention_policy, "30_DAYS")

    def test_multiple_drafts_per_song(self):
        Draft.objects.create(song=self.song)
        Draft.objects.create(song=self.song)
        self.assertEqual(Draft.objects.filter(song=self.song).count(), 2)

    def test_draft_submission(self):
        draft = Draft.objects.create(song=self.song)
        draft.is_submitted = True
        draft.save()
        self.assertTrue(Draft.objects.get(pk=draft.pk).is_submitted)

    def test_delete_song_cascades_drafts(self):
        Draft.objects.create(song=self.song)
        Draft.objects.create(song=self.song)
        self.song.delete()
        self.assertEqual(Draft.objects.count(), 0)
