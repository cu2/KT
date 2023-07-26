from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Calculate user contribution'

    def handle(self, *args, **options):
        self.cursor = connection.cursor()
        self.stdout.write('Calculating user contribution...')
        self.cursor.execute('''
        TRUNCATE ktapp_usercontribution
        ''')
        self.cursor.execute('''
        INSERT INTO ktapp_usercontribution
        (ktuser_ptr_id, {count_str}, {rank_str})
        SELECT id, {zero_str}, {zero_str}
        FROM ktapp_ktuser
        ORDER BY id
        '''.format(
            count_str=bulk_interpolate('count_{item}', ', '),
            rank_str=bulk_interpolate('rank_{item}', ', '),
            zero_str=bulk_interpolate('0', ', '),
        ))
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
        WHERE {count_str} = 0
        '''.format(
            count_str=bulk_interpolate('count_{item}', ' + ')
        ))
        self.cursor.execute('''
        UPDATE ktapp_usercontribution uc, (
            SELECT {max_str}
            FROM ktapp_usercontribution
        ) t
        SET {set_str}
        '''.format(
            max_str=bulk_interpolate('MAX(count_{item}) AS max_{item}', ', '),
            set_str=bulk_interpolate('rank_{item} = 1000 - IF(max_{item} > 0, count_{item} / max_{item} * 1000, 0)', ', '),
        ))
        self.stdout.write('User contribution calculated.')

    def calculate_metric(self, metric_name, table_name=None):
        if table_name is None:
            table_name = metric_name
        self.cursor.execute('''
        UPDATE ktapp_usercontribution uc, (
            SELECT created_by_id AS user_id, COUNT(1) AS cnt
            FROM ktapp_{table_name}
            GROUP BY created_by_id
        ) t
        SET uc.count_{metric_name} = t.cnt
        WHERE uc.ktuser_ptr_id = t.user_id
        '''.format(
            metric_name=metric_name,
            table_name=table_name,
        ))


def bulk_interpolate(template, separator):
    return separator.join([
        template.format(item=item)
        for item in ['film', 'role', 'keyword', 'picture', 'trivia', 'quote', 'review', 'link', 'biography', 'poll', 'usertoplist']
    ])
