from django.contrib import admin
from ktapp.models import Film, Vote, Comment, Topic, Poll


class FilmAdmin(admin.ModelAdmin):
    list_display = ['orig_title', 'other_titles', 'year', 'avg_rating']
    search_fields = ['orig_title', 'other_titles', 'year']


admin.site.register(Film, FilmAdmin)
# admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(Topic)
admin.site.register(Poll)
