import datetime
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Calculate user contribution'

    def handle(self, *args, **options):
        self.cursor = connection.cursor()
        self.stdout.write('Calculating user contribution...')
        self.year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        SELECT COUNT(1) FROM ktapp_ktuser
        ''')
        number_of_users = int(self.cursor.fetchone()[0])
        self.cursor.execute('''
        TRUNCATE ktapp_usercontribution
        ''')
        self.cursor.execute('''
        INSERT INTO ktapp_usercontribution
        (ktuser_ptr_id,
        count_film, count_role, count_keyword, count_picture, count_trivia, count_quote, count_review, count_link, count_biography, count_poll, count_usertoplist,
        rank_film, rank_role, rank_keyword, rank_picture, rank_trivia, rank_quote, rank_review, rank_link, rank_biography, rank_poll, rank_usertoplist)
        SELECT id,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}, {number_of_users}
        FROM ktapp_ktuser
        ORDER BY id
        '''.format(number_of_users=number_of_users))
        self.calculate_metric('film')
        self.calculate_metric('role', 'filmartistrelationship')
        self.calculate_metric('keyword', 'filmkeywordrelationship')
        self.calculate_metric('picture')
        self.calculate_metric('trivia')
        self.calculate_metric('quote')
        self.calculate_metric('review')
        self.calculate_metric('link')
        self.calculate_metric('biography')
        self.calculate_metric('poll')
        self.calculate_metric('usertoplist')
        self.cursor.execute('''
        DELETE FROM ktapp_usercontribution
        WHERE count_film + count_role + count_keyword + count_picture + count_trivia + count_quote + count_review + count_link + count_biography + count_poll + count_usertoplist = 0
        ''')
        self.stdout.write('User contribution calculated.')

    def calculate_metric(self, metric_name, table_name=None):
        if table_name is None:
            table_name = metric_name
        self.cursor.execute('''
        UPDATE ktapp_usercontribution uc, (
            SELECT user_id, cnt, @rank := @rank + 1 as rank
            FROM (
                SELECT created_by_id AS user_id, COUNT(1) AS cnt
                FROM ktapp_{table_name}
                WHERE created_at >= '{year_ago}'
                GROUP BY created_by_id
                ORDER BY COUNT(1) DESC, created_by_id DESC
            ) ttt,
            (SELECT @rank := 0) r
        ) t
        SET uc.count_{metric_name} = t.cnt, uc.rank_{metric_name} = t.rank
        WHERE uc.ktuser_ptr_id = t.user_id
        '''.format(
            metric_name=metric_name,
            table_name=table_name,
            year_ago=self.year_ago,
        ))
