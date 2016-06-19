from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Calculate number of followers'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        self.stdout.write('Calculating number of followers...')
        cursor.execute('''
        UPDATE ktapp_ktuser u, (
            SELECT u.id, COALESCE(t.follower_count, 0) AS follower_count
            FROM ktapp_ktuser u
            LEFT JOIN (
                SELECT f.whom_id, COUNT(1) AS follower_count
                FROM ktapp_follow f
                INNER JOIN ktapp_ktuser u
                ON u.id = f.who_id
                WHERE u.core_member = 1
                GROUP BY f.whom_id
            ) t
            ON t.whom_id = u.id
            GROUP BY u.id
        ) tt
        SET u.number_of_followers = tt.follower_count
        WHERE tt.id = u.id
        ''')
        cursor.execute('''
        SELECT number_of_followers
        FROM ktapp_ktuser
        WHERE is_active = 1
        ORDER BY number_of_followers DESC
        LIMIT 99, 1
        ''')
        number_of_followers_limit = int(cursor.fetchone()[0])
        self.stdout.write('Opinion leadership limit = %d' % number_of_followers_limit)
        cursor.execute('''
        UPDATE ktapp_ktuser
        SET opinion_leader = CASE
            WHEN is_active = 1 AND number_of_followers >= {number_of_followers_limit} THEN 1
            ELSE 0
        END
        '''.format(number_of_followers_limit=number_of_followers_limit))
        self.stdout.write('Number of followers calculated.')
