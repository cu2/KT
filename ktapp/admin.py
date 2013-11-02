from django.contrib import admin
from ktapp.models import Film, Vote, Comment, Topic, Poll, Quote, Trivia, \
    Artist, FilmArtistRelationship, Keyword, FilmKeywordRelationship


class FilmArtistInline(admin.TabularInline):
    model = FilmArtistRelationship


class FilmKeywordInline(admin.TabularInline):
    model = FilmKeywordRelationship


class FilmAdmin(admin.ModelAdmin):
    list_display = ['orig_title', 'other_titles', 'year', 'avg_rating', 'num_rating']
    search_fields = ['orig_title', 'other_titles', 'year']
    fields = ['orig_title', 'other_titles', 'year', 'plot_summary']
    inlines = [FilmArtistInline, FilmKeywordInline]


class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_by', 'created_at', 'domain', 'film', 'topic', 'poll']


class FilmUserTextContentAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_by', 'created_at', 'film']


admin.site.register(Film, FilmAdmin)
# admin.site.register(Vote)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Topic)
admin.site.register(Poll)
admin.site.register(Quote, FilmUserTextContentAdmin)
admin.site.register(Trivia, FilmUserTextContentAdmin)
admin.site.register(Artist)
admin.site.register(Keyword)
