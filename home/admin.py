from django.contrib import admin
from .models import Player, Score, Question

# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("crewid", "crew_name", "father", "emp_code", "mobile_no","score","category")
    search_fields = ("crewid", "crew_name", "emp_code", "mobile_no")
    fields = ("crewid", "crew_name", "father", "emp_code", "mobile_no")
@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player_crew_name', 'player_crewid', 'total_score','created_at')
    search_fields = ('player__crew_name', 'player__crewid')
    list_filter = ('created_at',)
    def player_crew_name(self, obj):
        return obj.player.crew_name
    player_crew_name.short_description = "Player Name"

    def player_crewid(self, obj):
        return obj.player.crewid
    player_crewid.short_description = "CMS ID"

    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = "Score"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_eng","question_hin", "category", "score", "special_note", "created_at")
    list_filter = ("category", "score")
    search_fields = ("question_eng","question_hin", "special_note")
    ordering = ("-created_at",)

