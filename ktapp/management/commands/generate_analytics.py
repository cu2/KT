from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Generate analytics'

    def add_arguments(self, parser):
        parser.add_argument('day')

    def handle(self, *args, **options):
        selected_day = options['day']
        cursor = connection.cursor()
        self.stdout.write('Generating analytics for {selected_day}...'.format(selected_day=selected_day))
        cursor.execute('''
            INSERT INTO ktapp_activeusercount
            (day, dau_count, wau_count, mau_count, new_count)
            SELECT
              '{selected_day}' AS day,
              SUM(status = 'dau') AS dau_count,
              SUM(status = 'wau') AS wau_count,
              SUM(status = 'mau') AS mau_count,
              SUM(status = 'new') AS new_count
            FROM (
              SELECT
                user_id,
                CASE
                  WHEN days_since_reg < 30 THEN 'new'
                  ELSE CASE
                    WHEN week_count >= 3 AND day_count >= 21 THEN 'dau'
                    WHEN week_count >= 3 AND day_count < 21 THEN 'wau'
                    WHEN week_count < 3 AND day_count >= 3 THEN 'mau'
                    ELSE 'inactive'
                  END
                END AS status
              FROM (
                SELECT
                  dau.user_id,
                  COUNT(DISTINCT dau.day) AS day_count,
                  COUNT(DISTINCT FLOOR(DATEDIFF('{selected_day}', dau.day)/7)) AS week_count,
                  DATEDIFF('{selected_day}', reg_date) AS days_since_reg
                FROM (
                  SELECT dau.day, dau.user_id, DATE(u.date_joined) AS reg_date
                  FROM ktapp_dailyactiveuser dau
                  INNER JOIN ktapp_ktuser u ON u.id = dau.user_id
                  WHERE dau.day BETWEEN DATE_SUB('{selected_day}', INTERVAL 27 DAY) AND '{selected_day}'
                ) dau
                GROUP BY dau.user_id
              ) t
              GROUP BY user_id
            ) t
        '''.format(selected_day=selected_day))
        self.stdout.write('Analytics generated.')
