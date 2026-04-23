from django.db import models

from .user import User
from .song import Song


class Library(models.Model):
    """
    A User owns exactly one Library (1..1).
    A Library contains zero or more Songs (0..*).
    filterCriteria is optional ([0..1] in the domain model).
    totalCount reflects the number of songs currently in the library.
    """

    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name="library")
    songs           = models.ManyToManyField(Song, blank=True, related_name="libraries")
    filter_criteria = models.CharField(max_length=500, blank=True)  # optional [0..1]
    total_count     = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "libraries"

    def __str__(self):
        return f"{self.user.display_name}'s Library"

    def sync_total_count(self):
        self.total_count = self.songs.count()
        self.save(update_fields=["total_count"])
