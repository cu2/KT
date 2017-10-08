from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth.views import logout
from django.views.generic.base import RedirectView
from rest_framework import routers

from ktapp.views import web_views, api_views
from ktapp.views.web import user_profile as user_profile_views
from ktapp.views.web import post as post_views
from ktapp.views.web import film as film_views
from ktapp.views.web import user as user_views


# API urls

router = routers.DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'films', api_views.FilmViewSet)
router.register(r'keywords', api_views.KeywordViewSet)
router.register(r'artists', api_views.ArtistViewSet)
router.register(r'sequels', api_views.SequelViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # custom api endpoints:
    url(r'^api/autocomplete/search/$', api_views.search, name='api_search'),
    url(r'^api/autocomplete/users/$', api_views.get_users, name='get_users'),
    url(r'^api/autocomplete/artists/$', api_views.get_artists, name='get_artists'),
    url(r'^api/autocomplete/keywords/$', api_views.get_keywords, name='get_keywords'),
    url(r'^api/autocomplete/films/$', api_views.get_films, name='get_films'),
    url(r'^api/autocomplete/sequels/$', api_views.get_sequels, name='get_sequels'),
    url(r'^api/autocomplete/awards/$', api_views.get_awards, name='get_awards'),
    url(r'^api/autocomplete/vapiti_films/$', api_views.get_vapiti_films, name='get_vapiti_films'),
    url(r'^api/autocomplete/vapiti_artists/$', api_views.get_vapiti_artists, name='get_vapiti_artists'),
    url(r'^api/buzz/$', api_views.buzz, name='buzz'),
    url(r'^api/comment_page/(?P<domain>[^/]*)/(?P<id>\d+)/$', api_views.comment_page, name='comment_page'),
]


# Web urls (should be Hungarian SEO compliant)

urlpatterns += [
    url(r'^$', web_views.index, name='index'),

    url(r'^keres/$', web_views.search, name='search'),
    url(r'^osszetett_kereso/$', web_views.browse, name='browse'),
    url(r'^bemutatok/evfordulok/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/$', web_views.premier_anniversaries, name='premier_anniversaries'),
    url(r'^bemutatok/(?P<year>\d+)/$', web_views.premiers_in_a_year, name='premiers_in_a_year'),
    url(r'^bemutatok/$', web_views.premiers, name='premiers'),
    url(r'^top_filmek/$', web_views.top_films, name='top_films'),
    url(r'^napok_filmjei/$', web_views.films_of_past_days, name='films_of_past_days'),

    url(r'^folytatasok/$', web_views.sequels, name='sequels'),
    url(r'^folytatas/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.sequel, name='sequel'),

    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/velemenyek/$', film_views.film_comments, name='film_comments'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/idezetek/$', film_views.film_quotes, name='film_quotes'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/erdekessegek/$', film_views.film_trivias, name='film_trivias'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kulcsszavak/$', film_views.film_keywords, name='film_keywords'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/cikkek/$', film_views.film_articles, name='film_articles'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/cikkek/(?P<review_id>\d+)$', film_views.film_article, name='film_article'),

    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/elemzesek/$', RedirectView.as_view(pattern_name='film_articles')),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/elemzesek/(?P<review_id>\d+)$', RedirectView.as_view(pattern_name='film_article')),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/dijak/$', film_views.film_awards, name='film_awards'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/linkek/$', RedirectView.as_view(pattern_name='film_articles')),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kepek/$', film_views.film_pictures, name='film_pictures'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)/kepek/(?P<picture_id>\d+)$', film_views.film_picture, name='film_picture'),
    url(r'^film/(?P<id>\d+)/(?P<film_slug>[^/]*)$', film_views.film_main, name='film_main'),

    url(r'^szavaz$', post_views.vote, name='vote'),
    url(r'^kivan$', post_views.wish, name='wish'),
    url(r'^kommentel$', post_views.new_comment, name='new_comment'),
    url(r'^szerk_komment$', post_views.edit_comment, name='edit_comment'),
    url(r'^uj_idezet$', post_views.new_quote, name='new_quote'),
    url(r'^szerk_idezet$', post_views.edit_quote, name='edit_quote'),
    url(r'^torol_idezet$', post_views.delete_quote, name='delete_quote'),
    url(r'^uj_erdekesseg$', post_views.new_trivia, name='new_trivia'),
    url(r'^szerk_erdekesseg$', post_views.edit_trivia, name='edit_trivia'),
    url(r'^torol_erdekesseg$', post_views.delete_trivia, name='delete_trivia'),
    url(r'^uj_kep$', post_views.new_picture, name='new_picture'),
    url(r'^szerk_kep$', post_views.edit_picture, name='edit_picture'),
    url(r'^foplakat$', post_views.set_main_poster, name='set_main_poster'),
    url(r'^torol_kep$', post_views.delete_picture, name='delete_picture'),

    url(r'^uj_film$', film_views.new_film, name='new_film'),
    url(r'^szerk_film$', post_views.edit_film, name='edit_film'),
    url(r'^szerk_sztori$', post_views.edit_plot, name='edit_plot'),
    url(r'^szerk_bemutatok$', post_views.edit_premiers, name='edit_premiers'),
    url(r'^szerk_kulcsszavak$', post_views.edit_keywords, name='edit_keywords'),
    url(r'^szerk_folytatasok$', post_views.edit_sequels, name='edit_sequels'),
    url(r'^szerk_iszdb$', post_views.edit_iszdb, name='edit_iszdb'),
    url(r'^uj_dij$', post_views.new_award, name='new_award'),
    url(r'^torol_dij$', post_views.delete_award, name='delete_award'),
    url(r'^offba$', post_views.move_to_off, name='move_to_off'),

    url(r'^uj_link$', post_views.new_link, name='new_link'),
    url(r'^szerk_link$', post_views.edit_link, name='edit_link'),
    url(r'^bekuldott_linkek/$', web_views.suggested_links, name='suggested_links'),
    url(r'^bekuld_link$', post_views.suggest_link, name='suggest_link'),
    url(r'^link_elfogadasa$', post_views.accept_link, name='accept_link'),
    url(r'^link_elutasitasa$', post_views.reject_link, name='reject_link'),
    url(r'^cikkek/$', web_views.articles, name='articles'),
    url(r'^linkek/$', RedirectView.as_view(pattern_name='articles')),

    url(r'^bekuldott_filmek/$', film_views.suggested_films, name='suggested_films'),
    url(r'^bekuld_film$', film_views.suggest_film, name='suggest_film'),
    url(r'^film_elfogadasa$', post_views.accept_film, name='accept_film'),
    url(r'^film_elutasitasa$', post_views.reject_film, name='reject_film'),

    url(r'^uj_elemzes$', post_views.new_review, name='new_review'),
    url(r'^bekuldott_elemzesek/$', web_views.suggested_reviews, name='suggested_reviews'),
    url(r'^bekuldott_portrek/$', web_views.suggested_bios, name='suggested_bios'),
    url(r'^elemzes_elfogadasa$', post_views.approve_review, name='approve_review'),
    url(r'^elemzes_elutasitasa$', post_views.disapprove_review, name='disapprove_review'),
    url(r'^elemzes_torlese$', post_views.delete_review, name='delete_review'),

    url(r'^valtozasok/$', web_views.changes, name='changes'),
    url(r'^hianyos_filmek/$', film_views.films_with_missing_data, name='films_with_missing_data'),
    url(r'^hianyos_muveszek/$', web_views.artists_with_missing_data, name='artists_with_missing_data'),
    url(r'^analytics/$', web_views.analytics, name='analytics'),
    url(r'^logs/$', web_views.view_logs, name='view_logs'),

    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)/kepek/$', web_views.artist_pictures, name='artist_pictures'),
    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)/kepek/(?P<picture_id>\d+)$', web_views.artist_picture, name='artist_picture'),
    url(r'^muvesz/(?P<id>\d+)/(?P<name_slug>[^/]*)$', web_views.artist_main, name='artist'),
    url(r'^szereplo/(?P<id>\d+)/(?P<name_slug>[^/]*)$', web_views.role, name='role'),
    url(r'^uj_szereplo$', post_views.new_role, name='new_role'),
    url(r'^szerk_szereplok$', post_views.edit_roles, name='edit_roles'),
    url(r'^szerk_szereplo$', post_views.edit_role, name='edit_role'),
    url(r'^torol_szereplo$', post_views.delete_role, name='delete_role'),
    url(r'^osszevon_muvesz$', post_views.merge_artist, name='merge_artist'),
    url(r'^fokep$', post_views.set_main_picture, name='set_main_picture'),
    url(r'^kepkivagas/(?P<id>\d+)/$', web_views.crop_picture, name='crop_picture'),
    url(r'^jovahagy_foszereplok$', post_views.confirm_main_roles, name='confirm_main_roles'),

    url(r'^forum/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.forum, name='forum'),
    url(r'^forum/$', web_views.list_of_topics, name='list_of_topics'),
    url(r'^uj_topik$', post_views.new_topic, name='new_topic'),
    url(r'^lezar$', post_views.close_topic, name='close_topic'),
    url(r'^rejtett_mod$', post_views.set_topic_game_mode, name='set_topic_game_mode'),
    url(r'^legfrissebb_kommentek/$', web_views.latest_comments, name='latest_comments'),
    url(r'^kedvencek/$', web_views.favourites, name='favourites'),
    url(r'^hasonlok/$', web_views.similar_users, name='similar_users'),
    url(r'^jofejek/$', web_views.contributors, name='contributors'),
    url(r'^mindenki/$', web_views.everybody, name='everybody'),
    url(r'^ertesitesek/$', web_views.notifications, name='notifications'),

    url(r'^felhasznaloi_toplista/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.usertoplist, name='usertoplist'),
    url(r'^felhasznaloi_toplistak/$', web_views.usertoplists, name='usertoplists'),
    url(r'^uj_felhasznaloi_toplista$', web_views.new_usertoplist, name='new_usertoplist'),
    url(r'^torol_felhasznaloi_toplista$', post_views.delete_usertoplist, name='delete_usertoplist'),

    url(r'^kozkerdes/(?P<id>\d+)/(?P<title_slug>[^/]*)$', web_views.poll, name='poll'),
    url(r'^kozkerdesek/$', web_views.polls, name='polls'),
    url(r'^kozkerdesre_szavaz$', post_views.poll_vote, name='poll_vote'),
    url(r'^kozkerdest_archival', post_views.poll_archive, name='poll_archive'),
    url(r'^kozkerdest_aktival', post_views.poll_activate, name='poll_activate'),
    url(r'^kozkerdest_tamogat', post_views.poll_support, name='poll_support'),
    url(r'^kozkerdest_torol', post_views.poll_delete, name='poll_delete'),
    url(r'^uj_kozkerdes', post_views.new_poll, name='new_poll'),

    url(r'^elemzesek/$', RedirectView.as_view(pattern_name='articles')),
    url(r'^portrek/$', RedirectView.as_view(url='/cikkek/?t=muveszek')),
    url(r'^kepek/$', web_views.latest_pictures, name='latest_pictures'),
    url(r'^idezetek/$', web_views.latest_quotes, name='latest_quotes'),
    url(r'^erdekessegek/$', web_views.latest_trivias, name='latest_trivias'),
    url(r'^dijak/$', web_views.awards, name='awards'),

    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/izles/(?P<domain>rendezok|mufajok|orszagok|korszakok)/$', user_profile_views.user_taste, name='user_taste'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/filmek/$', user_profile_views.user_films, name='user_films'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/kommentek/$', user_profile_views.user_comments, name='user_comments'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/kivansagok/$', user_profile_views.user_wishlist, name='user_wishlist'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/toplistak/$', user_profile_views.user_toplists, name='user_toplists'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/irasok/$', user_profile_views.user_articles, name='user_articles'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/aktivitas/$', user_profile_views.user_activity, name='user_activity'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)/uzenetek/$', user_profile_views.user_messages, name='user_messages'),
    url(r'^user/(?P<id>\d+)/(?P<name_slug>[^/]*)$', user_profile_views.user_profile, name='user_profile'),
    url(r'^szerk_profil/$', user_profile_views.edit_profile, name='edit_profile'),
    url(r'^egyeni_beallitasok/$', user_views.user_settings, name='user_settings'),
    url(r'^szerk_facebook$', post_views.edit_share_on_facebook, name='edit_share_on_facebook'),

    url(r'^jelszo_modositasa$', user_views.change_password, name='change_password'),
    url(r'^bejelentkezes$', user_views.custom_login, name='login'),
    url(r'^kijelentkezes$', logout, name='logout'),
    url(r'^regisztracio$', user_views.registration, name='registration'),
    url(r'^email_ellenorzes/(?P<token>.*)$', user_views.verify_email, name='verify_email'),
    url(r'^jelszo_reset/(?P<token>.*)$', user_views.reset_password, name='reset_password'),
    url(r'^hirlevel_leiratkozas/(?P<user_id>\d+)/(?P<token>.*)/$', user_views.unsubscribe_from_campaigns, name='unsubscribe_from_campaigns'),

    url(r'^uzik/$', user_views.messages, name='messages'),
    url(r'^uj_uzenet$', user_views.new_message, name='new_message'),
    url(r'^torol_uzenet$', post_views.delete_message, name='delete_message'),

    url(r'^uj_kedvenc$', post_views.follow, name='follow'),
    url(r'^torol_kedvenc$', post_views.unfollow, name='unfollow'),

    url(r'^kitilt$', post_views.ban_user, name='ban_user'),

    url(r'^email_header.jpg$', web_views.email_header, name='email_header'),
    url(r'^click/$', web_views.click, name='click'),
    url(r'^impresszum/$', web_views.impressum, name='impressum'),
    url(r'^rolunk/$', web_views.about_page, name='about_page'),
    url(r'^szabalyzat/$', web_views.rulez, name='rulez'),
    url(r'^feketelista/$', web_views.blacklist, name='blacklist'),
    url(r'^kassza/$', web_views.finance, name='finance'),
    url(r'^bezar_banner$', post_views.close_banner, name='close_banner'),
    url(r'^url/$', web_views.link_click, name='link_click'),

    url(r'^vapiti/$', web_views.vapiti_general, name='vapiti_general'),
    url(r'^arany_vapiti/$', web_views.vapiti_gold, name='vapiti_gold'),
    url(r'^arany_vapiti/masodik_fordulo/$', web_views.vapiti_gold_2, name='vapiti_gold_2'),
    url(r'^arany_vapiti/gyoztesek/$', web_views.vapiti_gold_winners, name='vapiti_gold_winners'),
    url(r'^ezust_vapiti/(?P<gender>ferfi|noi)/$', web_views.vapiti_silver, name='vapiti_silver'),
    url(r'^ezust_vapiti/masodik_fordulo/(?P<gender>ferfi|noi)/$', web_views.vapiti_silver_2, name='vapiti_silver_2'),
    url(r'^ezust_vapiti/gyoztesek/(?P<gender>ferfi|noi)/$', web_views.vapiti_silver_winners, name='vapiti_silver_winners'),
    url(r'^jelol_vapiti$', post_views.vote_vapiti, name='vote_vapiti'),

    # legacy redirects:
    url(r'^[^.]*.php$', web_views.old_url, name='old_url'),  # old php urls
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/filmek/$', RedirectView.as_view(pattern_name='user_films')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/kommentek/$', RedirectView.as_view(pattern_name='user_comments')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/kivansagok/$', RedirectView.as_view(pattern_name='user_wishlist')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)/uzenetek/$', RedirectView.as_view(pattern_name='user_messages')),
    url(r'^tag/(?P<id>\d+)/(?P<name_slug>[^/]*)$', RedirectView.as_view(pattern_name='user_profile')),
    url(r'^bongeszes/$', RedirectView.as_view(pattern_name='browse')),
]


# Static

if settings.DEBUG:  # in production webserver should serve these
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
