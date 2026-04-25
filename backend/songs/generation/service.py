from __future__ import annotations

from django.db import transaction

from ..models import AIGenerationRequest, GenerationStatus, SongPrompt
from .factory import get_song_generator_strategy
from .song_generation_request import SongGenerationRequest


def build_prompt_text(prompt: SongPrompt) -> str:
    parts = [
        f"Title: {prompt.title}",
        f"Occasion: {prompt.get_occasion_display()}",
        f"Mood: {prompt.get_mood_and_tone_display()}",
        f"Voice: {prompt.get_singer_tone_display()}",
    ]
    if prompt.description:
        parts.append(prompt.description)
    return ". ".join(parts)


def _style_hint(prompt: SongPrompt) -> str:
    return f"{prompt.get_mood_and_tone_display()} / {prompt.get_occasion_display()}"


@transaction.atomic
def run_generation(ai_request: AIGenerationRequest) -> AIGenerationRequest:
    """
    Execute the configured strategy and persist outcomes on Song + AIGenerationRequest.
    """
    if ai_request.status == GenerationStatus.COMPLETED:
        raise ValueError("This generation request is already completed.")

    prompt = ai_request.prompt
    song = prompt.song

    strategy = get_song_generator_strategy()
    gen_req = SongGenerationRequest(
        internal_request_uuid=ai_request.request_id,
        title=prompt.title,
        prompt_text=build_prompt_text(prompt),
        style_hint=_style_hint(prompt),
    )
    result = strategy.generate(gen_req)

    ai_request.external_task_id = result.external_task_id or ""
    ai_request.external_status = result.external_status or ""

    if not result.success:
        ai_request.status = GenerationStatus.FAILED
        ai_request.error_message = result.error_message or "Generation failed."
        ai_request.save(
            update_fields=["external_task_id", "external_status", "status", "error_message"]
        )
        song.generation_status = GenerationStatus.FAILED
        song.save(update_fields=["generation_status"])
        return ai_request

    if result.completed and result.audio_url:
        song.audio_file_url = result.audio_url
        song.generation_status = GenerationStatus.COMPLETED
        song.is_draft = False
        song.save(update_fields=["audio_file_url", "generation_status", "is_draft"])

        ai_request.status = GenerationStatus.COMPLETED
        ai_request.error_message = ""
        ai_request.save(
            update_fields=["external_task_id", "external_status", "status", "error_message"]
        )
        return ai_request

    # Async path (e.g. Suno task created — still generating)
    ai_request.status = GenerationStatus.IN_PROGRESS
    ai_request.error_message = ""
    ai_request.save(
        update_fields=["external_task_id", "external_status", "status", "error_message"]
    )

    song.generation_status = GenerationStatus.IN_PROGRESS
    song.is_draft = False
    song.save(update_fields=["generation_status", "is_draft"])

    return ai_request


@transaction.atomic
def refresh_generation_status(ai_request: AIGenerationRequest) -> AIGenerationRequest:
    """Poll provider status (Suno record-info). Mock returns immediately complete."""
    if ai_request.status == GenerationStatus.COMPLETED:
        raise ValueError("This generation request is already completed.")
    if not ai_request.external_task_id:
        raise ValueError("No external task id; run generation first.")

    strategy = get_song_generator_strategy()
    result = strategy.fetch_status(ai_request.external_task_id)

    ai_request.external_status = result.external_status or ""

    if not result.success:
        ai_request.status = GenerationStatus.FAILED
        ai_request.error_message = result.error_message or "Generation failed."
        ai_request.save(
            update_fields=["external_status", "status", "error_message"]
        )
        song = ai_request.prompt.song
        song.generation_status = GenerationStatus.FAILED
        song.save(update_fields=["generation_status"])
        return ai_request

    if result.completed and result.audio_url:
        song = ai_request.prompt.song
        song.audio_file_url = result.audio_url
        song.generation_status = GenerationStatus.COMPLETED
        song.is_draft = False
        song.save(update_fields=["audio_file_url", "generation_status", "is_draft"])

        ai_request.status = GenerationStatus.COMPLETED
        ai_request.error_message = ""
        ai_request.save(update_fields=["external_status", "status", "error_message"])
        return ai_request

    # Still processing (PENDING / TEXT_SUCCESS / FIRST_SUCCESS) or finished without URL
    ai_request.status = GenerationStatus.IN_PROGRESS
    ai_request.error_message = ""
    ai_request.save(update_fields=["external_status", "status", "error_message"])

    # Ensure the song status is also updated to IN_PROGRESS so it's not stuck as DRAFT in library
    song = ai_request.prompt.song
    if song.generation_status != GenerationStatus.IN_PROGRESS:
        song.generation_status = GenerationStatus.IN_PROGRESS
        song.is_draft = False
        song.save(update_fields=["generation_status", "is_draft"])

    return ai_request
