from django.contrib import admin
from ktapp.models import Film, Vote


class FilmAdmin(admin.ModelAdmin):
    list_display = ['orig_title', 'other_titles', 'year', 'avg_rating']
    search_fields = ['orig_title', 'other_titles', 'year']


admin.site.register(Film, FilmAdmin)
# admin.site.register(Vote)
