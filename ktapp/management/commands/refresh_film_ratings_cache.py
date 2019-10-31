from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Refresh film and artist ratings cache'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        self.stdout.write('Refreshing ratings cache...')
        self.stdout.write('Films...')
        cursor.execute('''
        UPDATE ktapp_film f, (
            SELECT f.id,
            COALESCE(SUM(v.rating=1), 0) AS r1,
            COALESCE(SUM(v.rating=2), 0) AS r2,
            COALESCE(SUM(v.rating=3), 0) AS r3,
            COALESCE(SUM(v.rating=4), 0) AS r4,
            COALESCE(SUM(v.rating=5), 0) AS r5
            FROM ktapp_film f
            LEFT JOIN (
                SELECT v.film_id, v.rating
                FROM ktapp_vote v
                INNER JOIN ktapp_ktuser u ON u.id = v.user_id AND u.core_member = 1
            ) v ON v.film_id = f.id
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
        ''')
        self.stdout.write('Artists...')
        cursor.execute('''
        UPDATE ktapp_artist a, (
            SELECT a.id,
            COUNT(DISTINCT f.id) AS film_count,
            COALESCE(SUM(f.number_of_ratings_1), 0) AS r1,
            COALESCE(SUM(f.number_of_ratings_2), 0) AS r2,
            COALESCE(SUM(f.number_of_ratings_3), 0) AS r3,
            COALESCE(SUM(f.number_of_ratings_4), 0) AS r4,
            COALESCE(SUM(f.number_of_ratings_5), 0) AS r5
            FROM ktapp_artist a
            INNER JOIN ktapp_filmartistrelationship fa ON fa.artist_id = a.id
            INNER JOIN ktapp_film f ON f.id = fa.film_id
            GROUP BY a.id
        ) t
        SET a.number_of_films = t.film_count,
            a.number_of_ratings = t.r1 + t.r2 + t.r3 + t.r4 + t.r5,
            a.average_rating = CASE
              WHEN t.r1 + t.r2 + t.r3 + t.r4 + t.r5 < 10 THEN NULL
              ELSE CAST((1.0 * t.r1 + 2.0 * t.r2 + 3.0 * t.r3 + 4.0 * t.r4 + 5.0 * t.r5) / (t.r1 + t.r2 + t.r3 + t.r4 + t.r5) AS DECIMAL(2, 1))
            END
        WHERE a.id = t.id
        ''')
        self.stdout.write('Artists as actors...')
        cursor.execute('''
        UPDATE ktapp_artist a, (
            SELECT a.id,
            COUNT(DISTINCT f.id) AS film_count,
            COALESCE(SUM(f.number_of_ratings_1), 0) AS r1,
            COALESCE(SUM(f.number_of_ratings_2), 0) AS r2,
            COALESCE(SUM(f.number_of_ratings_3), 0) AS r3,
            COALESCE(SUM(f.number_of_ratings_4), 0) AS r4,
            COALESCE(SUM(f.number_of_ratings_5), 0) AS r5
            FROM ktapp_artist a
            INNER JOIN ktapp_filmartistrelationship fa ON fa.artist_id = a.id AND fa.role_type = 'A'
            INNER JOIN ktapp_film f ON f.id = fa.film_id
            GROUP BY a.id
        ) t
        SET a.number_of_films_as_actor = t.film_count,
            a.number_of_ratings_as_actor = t.r1 + t.r2 + t.r3 + t.r4 + t.r5,
            a.average_rating_as_actor = CASE
              WHEN t.r1 + t.r2 + t.r3 + t.r4 + t.r5 < 10 THEN NULL
              ELSE CAST((1.0 * t.r1 + 2.0 * t.r2 + 3.0 * t.r3 + 4.0 * t.r4 + 5.0 * t.r5) / (t.r1 + t.r2 + t.r3 + t.r4 + t.r5) AS DECIMAL(2, 1))
            END
        WHERE a.id = t.id
        ''')
        self.stdout.write('Artists as directors...')
        cursor.execute('''
        UPDATE ktapp_artist a, (
            SELECT a.id,
            COUNT(DISTINCT f.id) AS film_count,
            COALESCE(SUM(f.number_of_ratings_1), 0) AS r1,
            COALESCE(SUM(f.number_of_ratings_2), 0) AS r2,
            COALESCE(SUM(f.number_of_ratings_3), 0) AS r3,
            COALESCE(SUM(f.number_of_ratings_4), 0) AS r4,
            COALESCE(SUM(f.number_of_ratings_5), 0) AS r5
            FROM ktapp_artist a
            INNER JOIN ktapp_filmartistrelationship fa ON fa.artist_id = a.id AND fa.role_type = 'D'
            INNER JOIN ktapp_film f ON f.id = fa.film_id
            GROUP BY a.id
        ) t
        SET a.number_of_films_as_director = t.film_count,
            a.number_of_ratings_as_director = t.r1 + t.r2 + t.r3 + t.r4 + t.r5,
            a.average_rating_as_director = CASE
              WHEN t.r1 + t.r2 + t.r3 + t.r4 + t.r5 < 10 THEN NULL
              ELSE CAST((1.0 * t.r1 + 2.0 * t.r2 + 3.0 * t.r3 + 4.0 * t.r4 + 5.0 * t.r5) / (t.r1 + t.r2 + t.r3 + t.r4 + t.r5) AS DECIMAL(2, 1))
            END
        WHERE a.id = t.id
        ''')
        self.stdout.write('Ratings cache refreshed.')
