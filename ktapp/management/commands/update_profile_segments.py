from django.core.management.base import BaseCommand
from django.db import connection

from ktapp import models


class Command(BaseCommand):
    help = 'Update profile segments'

    def handle(self, *args, **options):
        cursor = connection.cursor()

        self.stdout.write('Updating segments...')
        self.update_global_segment(cursor)
        for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE):
            self.update_keyword_segment(cursor, 'genre', keyword.id)
        cursor.execute('''
            UPDATE ktapp_profilesegment ps
            INNER JOIN (
                SELECT ps.id, ps.effective_number_of_films
                FROM ktapp_profilesegment ps
                WHERE ps.dimension = 'genre'
            ) detailed_ps
            INNER JOIN (
                SELECT SUM(ps.effective_number_of_films) AS effective_number_of_films
                FROM ktapp_profilesegment ps
                WHERE ps.dimension = 'genre'
            ) sum_ps
            SET ps.ratio_of_films = ROUND(10000.0 * detailed_ps.effective_number_of_films / sum_ps.effective_number_of_films)
            WHERE
              detailed_ps.id = ps.id
        ''')
        self.stdout.write('Updated segments.')

        self.stdout.write('Updating usersegments...')
        cursor.execute('''
            TRUNCATE ktapp_userprofilesegment
        ''')
        self.update_global_usersegment(cursor)
        for keyword in models.Keyword.objects.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE):
            self.update_keyword_usersegment(cursor, 'genre', keyword.id)
        cursor.execute('''
            UPDATE ktapp_userprofilesegment ups
            INNER JOIN (
                SELECT ups.user_id, ups.segment_id, ups.number_of_votes
                FROM ktapp_userprofilesegment ups
                INNER JOIN ktapp_profilesegment ps
                ON ps.id = ups.segment_id AND ps.dimension = 'genre'
            ) detailed_ups
            INNER JOIN (
                SELECT ups.user_id, SUM(ups.number_of_votes) AS number_of_votes
                FROM ktapp_userprofilesegment ups
                INNER JOIN ktapp_profilesegment ps
                ON ps.id = ups.segment_id AND ps.dimension = 'genre'
                GROUP BY ups.user_id
            ) sum_ups
            SET ups.ratio_of_films = ROUND(10000.0 * detailed_ups.number_of_votes / sum_ups.number_of_votes)
            WHERE
              detailed_ups.user_id = ups.user_id
              AND detailed_ups.segment_id = ups.segment_id
              AND sum_ups.user_id = ups.user_id
              AND sum_ups.number_of_votes > 0
        ''')
        cursor.execute('''
            UPDATE ktapp_userprofilesegment ups
            INNER JOIN ktapp_profilesegment ps
            SET ups.score = ROUND(100.0 * ups.ratio_of_films / ps.ratio_of_films - 100.0)
            WHERE
              ps.id = ups.segment_id
        ''')
        self.stdout.write('Updated usersegments.')

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
        segment, _ = models.ProfileSegment.objects.get_or_create(dimension=dimension, segment=keyword_id)
        cursor.execute('''
            SELECT ROUND(1.0 / SUM(POW(1.0 * f.weighted_number_of_ratings / sf.sum_of_weighted_number_of_ratings, 2))) AS effective_number
            FROM (SELECT 1.0 * f.number_of_ratings / f.number_of_genres AS weighted_number_of_ratings FROM ktapp_film f INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = f.id AND fk.keyword_id = {keyword_id}) f
            INNER JOIN (
                SELECT SUM(1.0 * f.number_of_ratings / f.number_of_genres) AS sum_of_weighted_number_of_ratings FROM (SELECT f.number_of_ratings, f.number_of_genres FROM ktapp_film f INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = f.id AND fk.keyword_id = {keyword_id}) f
            ) sf
        '''.format(keyword_id=keyword_id))
        segment.effective_number_of_films = int(cursor.fetchone()[0])
        segment.save()

    def update_keyword_usersegment(self, cursor, dimension, keyword_id):
        self.stdout.write('Keyword usersegment %s:%s...' % (dimension, keyword_id))
        segment = models.ProfileSegment.objects.get(dimension=dimension, segment=keyword_id)
        cursor.execute('''
            DELETE FROM ktapp_userprofilesegment
            WHERE segment_id = {segment_id}
        '''.format(segment_id=segment.id))
        cursor.execute('''
            INSERT INTO ktapp_userprofilesegment (user_id, segment_id, number_of_votes, relative_number_of_votes, ratio_of_films, score)
            SELECT id, {segment_id}, ROUND(weighted_number_of_ratings), ROUND(10000.0 * weighted_number_of_ratings / {effective_number_of_films}), 10000, 0
            FROM (
                SELECT u.id, SUM(1.0 / f.number_of_genres) AS weighted_number_of_ratings
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
        ))
