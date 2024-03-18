from django.db import models
from django.contrib.auth.models import User
import uuid

GENRES = (
    ("Action", "action"),
    ("Drama", "drama"),
    ("Thriller", "thriller"),
    ("Family", "family"),
    ("Romance", "romance"),
    ("Science Fiction", "science_fiction"),
    ("Mystery", "Mystery"),
    ("Comedy", "comedy"),
    ("Horror", "horror"),
)


class Movies(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    genres = models.TextField(blank=True)
    uuid = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.title} - {self.uuid}"


class Collection(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField(Movies, blank=True)
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")

    def __str__(self) -> str:
        return f"{self.title}"
