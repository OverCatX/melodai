from django.db import models


class GenerationStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED   = "COMPLETED",   "Completed"
    FAILED      = "FAILED",      "Failed"
    DRAFT       = "DRAFT",       "Draft"


class Occasion(models.TextChoices):
    BIRTHDAY    = "BIRTHDAY",    "Birthday"
    WEDDING     = "WEDDING",     "Wedding"
    ANNIVERSARY = "ANNIVERSARY", "Anniversary"
    GRADUATION  = "GRADUATION",  "Graduation"
    GENERAL     = "GENERAL",     "General"


class MoodTone(models.TextChoices):
    HAPPY     = "HAPPY",     "Happy"
    SAD       = "SAD",       "Sad"
    ROMANTIC  = "ROMANTIC",  "Romantic"
    ENERGETIC = "ENERGETIC", "Energetic"
    CALM      = "CALM",      "Calm"


class SingerTone(models.TextChoices):
    MALE_DEEP    = "MALE_DEEP",    "Male Deep"
    MALE_LIGHT   = "MALE_LIGHT",   "Male Light"
    FEMALE_DEEP  = "FEMALE_DEEP",  "Female Deep"
    FEMALE_LIGHT = "FEMALE_LIGHT", "Female Light"
    NEUTRAL      = "NEUTRAL",      "Neutral"
