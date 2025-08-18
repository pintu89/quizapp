from django.contrib import admin
from .models import Player, Score

# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('cms_id', 'name', 'pf_no')

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'player_cms_id', 'total_score', 'created_at')

    def player_name(self, obj):
        return obj.player.name
    player_name.short_description = "Player Name"

    def player_cms_id(self, obj):
        return obj.player.cms_id
    player_cms_id.short_description = "CMS ID"

    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = "Score"
