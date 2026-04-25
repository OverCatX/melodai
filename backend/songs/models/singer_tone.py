from django.db import models


class SingerTone(models.TextChoices):
    MALE_DEEP = "MALE_DEEP", "Male Deep"
    MALE_LIGHT = "MALE_LIGHT", "Male Light"
    FEMALE_DEEP = "FEMALE_DEEP", "Female Deep"
    FEMALE_LIGHT = "FEMALE_LIGHT", "Female Light"
    NEUTRAL = "NEUTRAL", "Neutral"
