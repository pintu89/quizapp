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

class Question(models.Model):
    CATEGORY_CHOICES = [
        ("OPS1","Option 1"),
        ("OPS2", "Option 2"),
        ("OPS3", "Option 3"),
        ("OPS4", "OPtion 4"),
        ("OPS5", "Option 5")
    ]
    question_eng = models.TextField()
    question_hin = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="OPS1")
    score = models.PositiveBigIntegerField(default=0)
    special_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    option_a_eng = models.CharField(max_length=255, blank=True, null=True)
    option_a_hin = models.CharField(max_length=255, blank=True, null=True)
    option_b_eng = models.CharField(max_length=255, blank=True, null=True)
    option_b_hin = models.CharField(max_length=255, blank=True, null=True)
    option_c_eng = models.CharField(max_length=255, blank=True, null=True)
    option_c_hin = models.CharField(max_length=255, blank=True, null=True)
    option_d_eng = models.CharField(max_length=255, blank=True, null=True)
    option_d_hin = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "Option A"),
            ("B", "Option B"),
            ("C", "Option C"),
            ("D", "Option D"),
        ],
        blank=True,
        null=True
    )
    def __str__(self):
        return f"Question: {self.question_eng[:80]}|Q(HI): {self.question_hin[:80]}...({self.category})"

class PlayerAnswer(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='player_answers')
    selected_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'question')