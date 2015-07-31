from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Refresh film ratings cache'

    def handle(self, *args, **options):
        self.stdout.write('Refreshing ratings cache...')
        cursor = connection.cursor()
        sql = '''
        UPDATE ktapp_film f, (
            SELECT f.id,
            COALESCE(SUM(v.rating=1), 0) AS r1,
            COALESCE(SUM(v.rating=2), 0) AS r2,
            COALESCE(SUM(v.rating=3), 0) AS r3,
            COALESCE(SUM(v.rating=4), 0) AS r4,
            COALESCE(SUM(v.rating=5), 0) AS r5
            FROM ktapp_film f
            LEFT JOIN ktapp_vote v ON v.film_id = f.id
            INNER JOIN ktapp_ktuser u ON u.id = v.user_id AND u.core_member = 1
            GROUP BY f.id
        ) t
        SET f.number_of_ratings_1 = t.r1,
            f.number_of_ratings_2 = t.r2,
            f.number_of_ratings_3 = t.r3,
            f.number_of_ratings_4 = t.r4,
            f.number_of_ratings_5 = t.r5,
            f.number_of_ratings = t.r1 + t.r2 + t.r3 + t.r4 + t.r5,
            f.average_rating = CASE
              WHEN t.r1 + t.r2 + t.r3 + t.r4 + t.r5 < 10 THEN NULL
              ELSE CAST((1.0 * t.r1 + 2.0 * t.r2 + 3.0 * t.r3 + 4.0 * t.r4 + 5.0 * t.r5) / (t.r1 + t.r2 + t.r3 + t.r4 + t.r5) AS DECIMAL(2, 1))
            END
        WHERE f.id = t.id
        '''
        cursor.execute(sql)
        self.stdout.write('Ratings cache refreshed.')
