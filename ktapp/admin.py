from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from ktapp import models
from ktapp import forms as kt_forms


class FilmArtistInline(admin.TabularInline):
    model = models.FilmArtistRelationship


class FilmKeywordInline(admin.TabularInline):
    model = models.FilmKeywordRelationship


class FilmSequelInline(admin.TabularInline):
    model = models.FilmSequelRelationship


class FilmPremierInline(admin.TabularInline):
    model = models.Premier


class FilmAdmin(admin.ModelAdmin):
    def view_link(self):
        return '<a href="%s">%s</a>' % (reverse("film_main", args=(self.pk, self.orig_title)), self.orig_title)
    view_link.allow_tags = True
    list_display = ['orig_title', 'second_title', 'year', 'avg_rating', 'num_rating', view_link]
    search_fields = ['orig_title', 'second_title', 'year']
    fields = ['orig_title', 'second_title', 'third_title', 'year', 'plot_summary',
              'main_premier', 'main_premier_year',
              'imdb_link', 'porthu_link', 'wikipedia_link_en', 'wikipedia_link_hu']
    inlines = [FilmArtistInline, FilmKeywordInline, FilmSequelInline, FilmPremierInline]


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


class PictureAdmin(admin.ModelAdmin):
    list_display = ['img', 'width', 'height', 'film', 'picture_type']


class PollChoiceAdmin(admin.ModelAdmin):
    list_display = ['poll', 'serial_number', 'choice', 'number_of_votes']


class KTUserAdmin(UserAdmin):
    form = kt_forms.UserChangeForm
    add_form = kt_forms.UserCreationForm

    list_display = ('username', 'email', 'gender', 'location', 'year_of_birth', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('gender', 'location', 'year_of_birth')}),
        ('Permissions', {'fields': ('is_staff',)}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'gender', 'location', 'year_of_birth', 'password1', 'password2')
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ()


admin.site.register(models.Film, FilmAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Topic)
admin.site.register(models.Poll)
admin.site.register(models.PollChoice, PollChoiceAdmin)
admin.site.register(models.PollVote)
admin.site.register(models.Quote, FilmUserTextContentAdmin)
admin.site.register(models.Trivia, FilmUserTextContentAdmin)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Artist)
admin.site.register(models.Keyword)
admin.site.register(models.Award, AwardAdmin)
admin.site.register(models.Link, LinkAdmin)
admin.site.register(models.LinkSite)
admin.site.register(models.Sequel)
admin.site.register(models.Premier)
admin.site.register(models.PremierType)
admin.site.register(models.Picture, PictureAdmin)
admin.site.register(models.Wishlist)
admin.site.register(models.TVChannel)
admin.site.register(models.TVFilm)
admin.site.register(models.UserToplist)
admin.site.register(models.UserToplistItem)

admin.site.register(models.KTUser, KTUserAdmin)
admin.site.unregister(Group)

# these probably shouldn't be in admin:
# admin.site.register(models.Message)
# admin.site.register(models.Vote)
