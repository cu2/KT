import datetime

from django.core.management.base import BaseCommand
from django.db import connection

from ktapp import models


MINIMUM_YEAR = 1920


class Command(BaseCommand):
    help = 'Update profile segments'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        today = datetime.date.today()
        this_year = today.year

        self.stdout.write('Updating segments...')
        # self.update_global_segment(cursor)
        # for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE):
        #     self.update_keyword_segment(cursor, 'genre', keyword.id)
        # self.update_segment_all(cursor, 'genre')
        # for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY):
        #     self.update_keyword_segment(cursor, 'country', keyword.id)
        # self.update_segment_all(cursor, 'country')
        # for year in range(MINIMUM_YEAR - 10, this_year, 10):
        #     self.update_year_segment(cursor, year)
        # self.update_segment_all(cursor, 'year')
        # self.stdout.write('Updated segments.')

        self.stdout.write('Updating usersegments...')
        # cursor.execute('''
        #     TRUNCATE ktapp_userprofilesegment
        # ''')
        # self.update_global_usersegment(cursor)
        # for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE):
        #     self.update_keyword_usersegment(cursor, 'genre', keyword.id)
        # self.update_usersegment_all(cursor, 'genre')
        # for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY):
        #     self.update_keyword_usersegment(cursor, 'country', keyword.id)
        # self.update_usersegment_all(cursor, 'country')
        # for year in range(MINIMUM_YEAR - 10, this_year, 10):
        #     self.update_year_usersegment(cursor, year)
        # self.update_usersegment_all(cursor, 'year')
        self.stdout.write('Updated usersegments.')

        self.stdout.write('Updating scores...')
        # cursor.execute('''
        #     UPDATE ktapp_userprofilesegment ups
        #     INNER JOIN ktapp_profilesegment ps
        #     SET ups.score = ROUND(100.0 * ups.ratio_of_films / ps.ratio_of_films - 100.0)
        #     WHERE
        #       ps.id = ups.segment_id
        # ''')
        self.stdout.write('Updated scores.')

    def update_global_segment(self, cursor):
        self.stdout.write('Global segment...')
        segment, _ = models.ProfileSegment.objects.get_or_create(dimension='', segment=0)
        cursor.execute('''
            SELECT ROUND(1.0 / SUM(POW(1.0 * f.number_of_ratings / sf.sum_of_number_of_ratings, 2))) AS effective_number
            FROM ktapp_film f
            INNER JOIN (
                SELECT SUM(number_of_ratings) AS sum_of_number_of_ratings FROM ktapp_film
            ) sf
        ''')
        segment.effective_number_of_films = int(cursor.fetchone()[0])
        segment.ratio_of_films = 10000
        segment.save()

    def update_global_usersegment(self, cursor):
        self.stdout.write('Global usersegment...')
        segment = models.ProfileSegment.objects.get(dimension='', segment=0)
        cursor.execute('''
            DELETE FROM ktapp_userprofilesegment
            WHERE segment_id = {segment_id}
        '''.format(segment_id=segment.id))
        cursor.execute('''
            INSERT INTO ktapp_userprofilesegment (user_id, segment_id, number_of_votes, relative_number_of_votes, ratio_of_films, score)
            SELECT id, {segment_id}, number_of_ratings, ROUND(10000.0 * number_of_ratings / {effective_number_of_films}), 10000, 0
            FROM ktapp_ktuser
        '''.format(
            segment_id=segment.id,
            effective_number_of_films=segment.effective_number_of_films,
        ))

    def update_keyword_segment(self, cursor, dimension, keyword_id):
        self.stdout.write('Keyword segment %s:%s...' % (dimension, keyword_id))
        if dimension == 'genre':
            dim_field = 'number_of_genres'
        elif dimension == 'country':
            dim_field = 'number_of_countries'
        else:
            return
        cursor.execute('''
            SELECT COALESCE(ROUND(1.0 / SUM(POW(1.0 * f.weighted_number_of_ratings / sf.sum_of_weighted_number_of_ratings, 2))), 0) AS effective_number
            FROM (SELECT 1.0 * f.number_of_ratings / f.{dim_field} AS weighted_number_of_ratings FROM ktapp_film f INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = f.id AND fk.keyword_id = {keyword_id}) f
            INNER JOIN (
                SELECT SUM(1.0 * f.number_of_ratings / f.{dim_field}) AS sum_of_weighted_number_of_ratings FROM (SELECT f.number_of_ratings, f.{dim_field} FROM ktapp_film f INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = f.id AND fk.keyword_id = {keyword_id}) f
            ) sf
        '''.format(
            keyword_id=keyword_id,
            dim_field=dim_field,
        ))
        effective_number_of_films = int(cursor.fetchone()[0])
        if effective_number_of_films >= 20:
            segment, _ = models.ProfileSegment.objects.get_or_create(dimension=dimension, segment=keyword_id)
            segment.effective_number_of_films = effective_number_of_films
            segment.save()
            return segment
        return None

    def update_keyword_usersegment(self, cursor, dimension, keyword_id):
        try:
            segment = models.ProfileSegment.objects.get(dimension=dimension, segment=keyword_id)
        except models.ProfileSegment.DoesNotExist:
            return
        self.stdout.write('Keyword usersegment %s:%s...' % (dimension, keyword_id))
        if dimension == 'genre':
            dim_field = 'number_of_genres'
        elif dimension == 'country':
            dim_field = 'number_of_countries'
        else:
            return
        cursor.execute('''
            DELETE FROM ktapp_userprofilesegment
            WHERE segment_id = {segment_id}
        '''.format(segment_id=segment.id))
        cursor.execute('''
            INSERT INTO ktapp_userprofilesegment (user_id, segment_id, number_of_votes, relative_number_of_votes, ratio_of_films, score)
            SELECT id, {segment_id}, ROUND(weighted_number_of_ratings), ROUND(10000.0 * weighted_number_of_ratings / {effective_number_of_films}), 10000, 0
            FROM (
                SELECT u.id, SUM(1.0 / f.{dim_field}) AS weighted_number_of_ratings
                FROM ktapp_ktuser u
                INNER JOIN ktapp_vote v ON v.user_id = u.id
                INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = v.film_id AND fk.keyword_id = {keyword_id}
                INNER JOIN ktapp_film f ON f.id = v.film_id
                GROUP BY u.id
            ) uu
        '''.format(
            segment_id=segment.id,
            keyword_id=keyword_id,
            effective_number_of_films=segment.effective_number_of_films,
            dim_field=dim_field,
        ))

    def update_year_segment(self, cursor, year):
        self.stdout.write('Year segment %s...' % year)
        cursor.execute('''
            SELECT ROUND(1.0 / SUM(POW(1.0 * f.number_of_ratings / sf.sum_of_number_of_ratings, 2))) AS effective_number
            FROM (SELECT number_of_ratings FROM ktapp_film WHERE year BETWEEN {min_year} AND {max_year}) f
            INNER JOIN (
                SELECT SUM(number_of_ratings) AS sum_of_number_of_ratings FROM ktapp_film WHERE year BETWEEN {min_year} AND {max_year}
            ) sf
        '''.format(
            min_year=1800 if year < MINIMUM_YEAR else year,
            max_year=MINIMUM_YEAR - 1 if year < MINIMUM_YEAR else year + 9,
        ))
        effective_number_of_films = int(cursor.fetchone()[0])
        if effective_number_of_films >= 20:
            segment, _ = models.ProfileSegment.objects.get_or_create(dimension='year', segment=year)
            segment.effective_number_of_films = effective_number_of_films
            segment.save()
            return segment
        return None

    def update_year_usersegment(self, cursor, year):
        try:
            segment = models.ProfileSegment.objects.get(dimension='year', segment=year)
        except models.ProfileSegment.DoesNotExist:
            return
        self.stdout.write('Year usersegment %s...' % year)
        cursor.execute('''
            DELETE FROM ktapp_userprofilesegment
            WHERE segment_id = {segment_id}
        '''.format(segment_id=segment.id))
        cursor.execute('''
            INSERT INTO ktapp_userprofilesegment (user_id, segment_id, number_of_votes, relative_number_of_votes, ratio_of_films, score)
            SELECT id, {segment_id}, ROUND(weighted_number_of_ratings), ROUND(10000.0 * weighted_number_of_ratings / {effective_number_of_films}), 10000, 0
            FROM (
                SELECT u.id, COUNT(1) AS weighted_number_of_ratings
                FROM ktapp_ktuser u
                INNER JOIN ktapp_vote v ON v.user_id = u.id
                INNER JOIN ktapp_film f ON f.id = v.film_id AND f.year BETWEEN {min_year} AND {max_year}
                GROUP BY u.id
            ) uu
        '''.format(
            segment_id=segment.id,
            min_year=1800 if year < MINIMUM_YEAR else year,
            max_year=MINIMUM_YEAR - 1 if year < MINIMUM_YEAR else year + 9,
            effective_number_of_films=segment.effective_number_of_films,
        ))

    def update_segment_all(self, cursor, dimension):
        self.stdout.write('Segment %s:all...' % dimension)
        cursor.execute('''
            UPDATE ktapp_profilesegment ps
            INNER JOIN (
                SELECT ps.id, ps.effective_number_of_films
                FROM ktapp_profilesegment ps
                WHERE ps.dimension = '{dimension}'
            ) detailed_ps
            INNER JOIN (
                SELECT SUM(ps.effective_number_of_films) AS effective_number_of_films
                FROM ktapp_profilesegment ps
                WHERE ps.dimension = '{dimension}'
            ) sum_ps
            SET ps.ratio_of_films = ROUND(10000.0 * detailed_ps.effective_number_of_films / sum_ps.effective_number_of_films)
            WHERE
              detailed_ps.id = ps.id
        '''.format(dimension=dimension))

    def update_usersegment_all(self, cursor, dimension):
        self.stdout.write('Usersegment %s:all...' % dimension)
        cursor.execute('''
            UPDATE ktapp_userprofilesegment ups
            INNER JOIN (
                SELECT ups.user_id, ups.segment_id, ups.number_of_votes
                FROM ktapp_userprofilesegment ups
                INNER JOIN ktapp_profilesegment ps
                ON ps.id = ups.segment_id AND ps.dimension = '{dimension}'
            ) detailed_ups
            INNER JOIN (
                SELECT ups.user_id, SUM(ups.number_of_votes) AS number_of_votes
                FROM ktapp_userprofilesegment ups
                INNER JOIN ktapp_profilesegment ps
                ON ps.id = ups.segment_id AND ps.dimension = '{dimension}'
                GROUP BY ups.user_id
            ) sum_ups
            SET ups.ratio_of_films = ROUND(10000.0 * detailed_ups.number_of_votes / sum_ups.number_of_votes)
            WHERE
              detailed_ups.user_id = ups.user_id
              AND detailed_ups.segment_id = ups.segment_id
              AND sum_ups.user_id = ups.user_id
              AND sum_ups.number_of_votes > 0
        '''.format(dimension=dimension))
