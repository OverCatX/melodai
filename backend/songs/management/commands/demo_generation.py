import uuid

from django.core.management.base import BaseCommand

from songs.generation import get_song_generator_strategy
from songs.generation.service import run_generation
from songs.models import (
    AIGenerationRequest,
    GenerationStatus,
    MoodTone,
    Occasion,
    SingerTone,
    Song,
    SongPrompt,
    User,
)


class Command(BaseCommand):
    help = (
        "Create a User + Song + SongPrompt + AIGenerationRequest, then run the active "
        "generator strategy (mock or suno from GENERATOR_STRATEGY / runtime override)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-run",
            action="store_true",
            help="Only print which strategy is active; do not create data or call run.",
        )

    def handle(self, *args, **options):
        strategy = get_song_generator_strategy()
        self.stdout.write(
            self.style.NOTICE(f"Active strategy: {strategy.__class__.__name__}")
        )

        if options["skip_run"]:
            return

        suffix = uuid.uuid4().hex[:8]
        user = User.objects.create(
            username=f"demo_gen_{suffix}",
            display_name="Demo Gen",
        )
        song = Song.objects.create(
            user=user,
            title="Strategy Demo Song",
            generation_status=GenerationStatus.DRAFT,
        )
        prompt = SongPrompt.objects.create(
            song=song,
            title="Demo Prompt",
            occasion=Occasion.GENERAL,
            mood_and_tone=MoodTone.CALM,
            singer_tone=SingerTone.NEUTRAL,
            description="Demo prompt for strategy run.",
        )
        req = AIGenerationRequest.objects.create(
            prompt=prompt, status=GenerationStatus.IN_PROGRESS
        )

        run_generation(req)
        req.refresh_from_db()
        song.refresh_from_db()

        self.stdout.write(f"request_id={req.request_id}")
        self.stdout.write(f"external_task_id={req.external_task_id!r}")
        self.stdout.write(f"external_status={req.external_status!r}")
        self.stdout.write(f"ai_status={req.status}")
        self.stdout.write(f"song.generation_status={song.generation_status}")
        self.stdout.write(f"song.audio_file_url={song.audio_file_url!r}")
