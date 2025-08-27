from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    crewid = models.CharField(max_length=50, unique=True)
    crew_name = models.CharField(max_length=100)
    father = models.CharField(max_length=100, blank=True, null=True)
    emp_code = models.CharField(max_length=50, blank=True, null=True)
    mobile_no= models.CharField(max_length=15)
    score = models.IntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    special_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.crewid} ({self.crew_name})"

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.crew_name} - {self.total_score}"
