"""
Management command: python manage.py seed

Populates the database with realistic sample data covering every
domain entity so that CRUD operations can be demonstrated immediately.
Safe to run multiple times (clears existing data first).
"""

from django.core.management.base import BaseCommand
from songs.models import (
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


class Command(BaseCommand):
    help = "Seed the database with sample domain data"

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        for Model in [
            AIGenerationRequest,
            SharedSong,
            Draft,
            SongPrompt,
            Library,
            Song,
            PlaybackSession,
            User,
        ]:
            Model.objects.all().delete()

        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        alice = User.objects.create(
            google_id="google_alice_001",
            email="alice@example.com",
            display_name="Alice Nguyen",
            session_token="tok_alice_abc",
        )
        bob = User.objects.create(
            google_id="google_bob_002",
            email="bob@example.com",
            display_name="Bob Smith",
            session_token="tok_bob_xyz",
        )
        self.stdout.write(f"  Created users: {alice}, {bob}")

        # ------------------------------------------------------------------
        # PlaybackSession
        # ------------------------------------------------------------------
        session = PlaybackSession.objects.create(
            current_position=47.3,
            loop_start=10.0,
            loop_end=60.0,
            equalizer_settings="bass=+3,treble=-1",
        )
        self.stdout.write(f"  Created playback session: {session}")

        # ------------------------------------------------------------------
        # Songs
        # ------------------------------------------------------------------
        song_completed = Song.objects.create(
            user=alice,
            title="Happy Birthday to You",
            audio_file_url="https://cdn.aisong.example.com/audio/song_001.mp3",
            generation_status=GenerationStatus.COMPLETED,
            is_draft=False,
            is_favorite=True,
            share_link="https://aisong.example.com/s/abc123",
            playback_session=session,
        )
        song_draft = Song.objects.create(
            user=alice,
            title="Our Wedding Song",
            generation_status=GenerationStatus.DRAFT,
            is_draft=True,
        )
        song_bob = Song.objects.create(
            user=bob,
            title="Graduation Day",
            audio_file_url="https://cdn.aisong.example.com/audio/song_003.mp3",
            generation_status=GenerationStatus.COMPLETED,
            is_draft=False,
        )
        self.stdout.write(
            f"  Created songs: {song_completed}, {song_draft}, {song_bob}"
        )

        # ------------------------------------------------------------------
        # Libraries
        # ------------------------------------------------------------------
        alice_lib = Library.objects.create(
            user=alice, filter_criteria="is_favorite=true"
        )
        alice_lib.songs.add(song_completed, song_draft)
        alice_lib.sync_total_count()

        bob_lib = Library.objects.create(user=bob)
        bob_lib.songs.add(song_bob)
        bob_lib.sync_total_count()
        self.stdout.write(f"  Created libraries: {alice_lib}, {bob_lib}")

        # ------------------------------------------------------------------
        # SongPrompts
        # ------------------------------------------------------------------
        prompt_completed = SongPrompt.objects.create(
            song=song_completed,
            title="Birthday song for my best friend",
            occasion=Occasion.BIRTHDAY,
            mood_and_tone=MoodTone.HAPPY,
            singer_tone=SingerTone.FEMALE_LIGHT,
            description="A cheerful birthday song with upbeat melody.",
        )
        prompt_draft = SongPrompt.objects.create(
            song=song_draft,
            title="Romantic wedding ballad",
            occasion=Occasion.WEDDING,
            mood_and_tone=MoodTone.ROMANTIC,
            singer_tone=SingerTone.MALE_DEEP,
            description="A slow, emotional ballad for the first dance.",
        )
        prompt_bob = SongPrompt.objects.create(
            song=song_bob,
            title="Energetic graduation anthem",
            occasion=Occasion.GRADUATION,
            mood_and_tone=MoodTone.ENERGETIC,
            singer_tone=SingerTone.NEUTRAL,
            description="Celebratory and motivational.",
        )
        self.stdout.write(
            f"  Created prompts: {prompt_completed}, {prompt_draft}, {prompt_bob}"
        )

        # ------------------------------------------------------------------
        # AIGenerationRequests
        # ------------------------------------------------------------------
        AIGenerationRequest.objects.create(
            prompt=prompt_completed,
            status=GenerationStatus.COMPLETED,
        )
        AIGenerationRequest.objects.create(
            prompt=prompt_draft,
            status=GenerationStatus.IN_PROGRESS,
        )
        AIGenerationRequest.objects.create(
            prompt=prompt_bob,
            status=GenerationStatus.COMPLETED,
        )
        self.stdout.write("  Created AI generation requests")

        # ------------------------------------------------------------------
        # SharedSong
        # ------------------------------------------------------------------
        SharedSong.objects.create(
            song=song_completed,
            share_link="https://aisong.example.com/share/happy-bday-alice",
            accessible_by_guest=True,
        )
        self.stdout.write("  Created shared song")

        # ------------------------------------------------------------------
        # Drafts
        # ------------------------------------------------------------------
        Draft.objects.create(
            song=song_draft,
            is_submitted=False,
            retention_policy="30_DAYS",
        )
        Draft.objects.create(
            song=song_draft,
            is_submitted=False,
            retention_policy="30_DAYS",
        )
        self.stdout.write("  Created drafts")

        self.stdout.write(self.style.SUCCESS("\nSeed complete. Summary:"))
        self.stdout.write(f"  Users:               {User.objects.count()}")
        self.stdout.write(f"  Songs:               {Song.objects.count()}")
        self.stdout.write(f"  Libraries:           {Library.objects.count()}")
        self.stdout.write(f"  SongPrompts:         {SongPrompt.objects.count()}")
        self.stdout.write(
            f"  GenerationRequests:  {AIGenerationRequest.objects.count()}"
        )
        self.stdout.write(f"  SharedSongs:         {SharedSong.objects.count()}")
        self.stdout.write(f"  PlaybackSessions:    {PlaybackSession.objects.count()}")
        self.stdout.write(f"  Drafts:              {Draft.objects.count()}")
