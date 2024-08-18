import datetime

from django.core.management.base import BaseCommand
from django.db import connection

from ktapp import models
from ktapp import utils as kt_utils


class Command(BaseCommand):
    help = 'Calculate Vapiti: eligible films, user weights'

    def handle(self, *args, **options):
        today = datetime.date.today()
        vapiti_year = kt_utils.get_app_config('vapiti_year')
        is_it_standard_period = today.year == vapiti_year
        is_it_extended_period = today.year == vapiti_year + 1 and today.month == 1 and today.day <= 31

        if is_it_standard_period or is_it_extended_period:
            self.mark_eligible_films(vapiti_year)
            self.calculate_vapiti_weights(vapiti_year)

    def mark_eligible_films(self, vapiti_year):
        self.stdout.write('Marking eligible films for {}...'.format(vapiti_year))

        models.Film.objects.filter(vapiti_year=vapiti_year).update(vapiti_year=None)

        film_ids = set()
        for film in models.Film.objects.filter(
            vapiti_year=None,
            main_premier_year=vapiti_year,
        ):
            film_ids.add(film.id)

        for film in models.Film.objects.filter(
            vapiti_year=None,
            main_premier_year=None,
            year=vapiti_year,
            number_of_ratings__gte=20,
            genre_cache_is_music_video=False,
            genre_cache_is_mini=False,
            genre_cache_is_short=False,
        ):
            film_ids.add(film.id)

        for film_id in film_ids:
            film = models.Film.objects.get(id=film_id)
            film.vapiti_year = vapiti_year
            film.save(update_fields=['vapiti_year'])

        self.stdout.write('{} films marked as eligible for {}.'.format(
            len(film_ids),
            vapiti_year,
        ))

    def calculate_vapiti_weights(self, vapiti_year):
        self.stdout.write('Calculating Vapiti weights...')
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE ktapp_ktuser u, (
                SELECT u.id,
                COUNT(1) AS number_of_ratings,
                COALESCE(SUM(f.vapiti_year={vapiti_year}), 0) AS number_of_vapiti_votes,
                COUNT(1) + 25 * COALESCE(SUM(f.vapiti_year={vapiti_year}), 0) AS vapiti_weight
                FROM ktapp_ktuser u
                LEFT JOIN ktapp_vote v ON v.user_id = u.id
                INNER JOIN ktapp_film f ON f.id = v.film_id
                GROUP BY u.id
            ) t
            SET u.number_of_ratings = COALESCE(t.number_of_ratings, 0),
                u.number_of_vapiti_votes = COALESCE(t.number_of_vapiti_votes, 0),
                u.vapiti_weight = COALESCE(t.vapiti_weight, 0)
            WHERE u.id = t.id;
        '''.format(vapiti_year=vapiti_year))
        self.stdout.write('Vapiti weights calculated.')
