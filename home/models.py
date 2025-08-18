from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cms_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    pf_no = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.pf_no})"

class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name} - {self.total_score}"
