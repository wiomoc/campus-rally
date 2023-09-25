from datetime import datetime
from typing import Optional

from django.contrib import admin
from django.db import models

class Group(models.Model):
    public_id: str = models.CharField(max_length=30, unique=True)
    track_id: str = models.CharField(max_length=30)
    current_element_id: str = models.CharField(max_length=30)
    starting_element_id: str = models.CharField(max_length=30)

    def __str__(self):
        return self.public_id


class TrackElementGroupAnswer(models.Model):
    element_id: str = models.CharField(max_length=30, db_index=True)
    group: Group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_finished: datetime = models.DateTimeField(auto_now_add=True)
    answer: Optional[str] = models.TextField()
    hint_used: bool = models.BooleanField(default=False)
    score: Optional[int] = models.IntegerField(null=True)


    def __str__(self):
        return f"{self.group.public_id} - {self.element_id}"