from django.db import models


class MoodTone(models.TextChoices):
    HAPPY = "HAPPY", "Happy"
    SAD = "SAD", "Sad"
    ROMANTIC = "ROMANTIC", "Romantic"
    ENERGETIC = "ENERGETIC", "Energetic"
    CALM = "CALM", "Calm"
