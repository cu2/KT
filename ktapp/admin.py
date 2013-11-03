from django.contrib import admin
from ktapp.models import Film, Vote, Comment, Topic, Poll, Quote, Trivia, Review, \
    Artist, FilmArtistRelationship, Keyword, FilmKeywordRelationship, Award, \
    Link, LinkSite


class FilmArtistInline(admin.TabularInline):
    model = FilmArtistRelationship


class FilmKeywordInline(admin.TabularInline):
    model = FilmKeywordRelationship


class FilmAdmin(admin.ModelAdmin):
    list_display = ['orig_title', 'other_titles', 'year', 'avg_rating', 'num_rating']
    search_fields = ['orig_title', 'other_titles', 'year']
    fields = ['orig_title', 'other_titles', 'year', 'plot_summary',
              'imdb_link', 'porthu_link', 'wikipedia_link_en', 'wikipedia_link_hu']
    inlines = [FilmArtistInline, FilmKeywordInline]


class CommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_by', 'created_at', 'domain', 'film', 'topic', 'poll']


class FilmUserTextContentAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_by', 'created_at', 'film']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'created_by', 'created_at', 'film']


class AwardAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'category', 'film', 'artist']


class LinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'film']


admin.site.register(Film, FilmAdmin)
# admin.site.register(Vote)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Topic)
admin.site.register(Poll)
admin.site.register(Quote, FilmUserTextContentAdmin)
admin.site.register(Trivia, FilmUserTextContentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Artist)
admin.site.register(Keyword)
admin.site.register(Award, AwardAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(LinkSite)
