from django.contrib import admin
from StiCazzi.models import TvShow, TvShowVote

class TvShowAdmin(admin.ModelAdmin):
    pass
admin.site.register(TvShow, TvShowAdmin)

class TvShowVoteAdmin(admin.ModelAdmin):
    pass
admin.site.register(TvShowVote, TvShowVoteAdmin)