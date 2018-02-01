import datetime

from django.core.management.base import BaseCommand
from django.db import connection

from ktapp import models


INSERT_SQL_TEMPLATE_1 = '''
INSERT INTO ktapp_useruserrating (
  user_1_id, user_2_id, keyword_id,
  number_of_ratings,
  similarity,
  last_calculated_at
)
VALUES(%s, %s, %s, %s, %s, %s)
'''


INSERT_SQL_TEMPLATE_2 = '''
INSERT INTO ktapp_useruserrating (
  user_2_id, user_1_id, keyword_id,
  number_of_ratings,
  similarity,
  last_calculated_at
)
VALUES(%s, %s, %s, %s, %s, %s)
'''


GENERIC_SIMILARITY_TEMPLATE = '''
SELECT
  user_1_id, user_2_id, keyword_id,
  number_of_ratings,
  ROUND(1.0 * (
  100 * number_of_ratings_11 +
   85 * number_of_ratings_12 +
   50 * number_of_ratings_13 +
   15 * number_of_ratings_14 +
    0 * number_of_ratings_15 +
   85 * number_of_ratings_21 +
  100 * number_of_ratings_22 +
   65 * number_of_ratings_23 +
   30 * number_of_ratings_24 +
   15 * number_of_ratings_25 +
   50 * number_of_ratings_31 +
   65 * number_of_ratings_32 +
  100 * number_of_ratings_33 +
   65 * number_of_ratings_34 +
   50 * number_of_ratings_35 +
   15 * number_of_ratings_41 +
   30 * number_of_ratings_42 +
   65 * number_of_ratings_43 +
  100 * number_of_ratings_44 +
   85 * number_of_ratings_45 +
    0 * number_of_ratings_51 +
   15 * number_of_ratings_52 +
   50 * number_of_ratings_53 +
   85 * number_of_ratings_54 +
  100 * number_of_ratings_55
  ) / number_of_ratings) AS similarity,
  %s AS last_calculated_at
FROM (
SELECT
  v1.user_id AS user_1_id, v2.user_id AS user_2_id, NULL AS keyword_id,
  COUNT(1) AS number_of_ratings,
  SUM(v1.rating = 1 AND v2.rating = 1) AS number_of_ratings_11,
  SUM(v1.rating = 1 AND v2.rating = 2) AS number_of_ratings_12,
  SUM(v1.rating = 1 AND v2.rating = 3) AS number_of_ratings_13,
  SUM(v1.rating = 1 AND v2.rating = 4) AS number_of_ratings_14,
  SUM(v1.rating = 1 AND v2.rating = 5) AS number_of_ratings_15,
  SUM(v1.rating = 2 AND v2.rating = 1) AS number_of_ratings_21,
  SUM(v1.rating = 2 AND v2.rating = 2) AS number_of_ratings_22,
  SUM(v1.rating = 2 AND v2.rating = 3) AS number_of_ratings_23,
  SUM(v1.rating = 2 AND v2.rating = 4) AS number_of_ratings_24,
  SUM(v1.rating = 2 AND v2.rating = 5) AS number_of_ratings_25,
  SUM(v1.rating = 3 AND v2.rating = 1) AS number_of_ratings_31,
  SUM(v1.rating = 3 AND v2.rating = 2) AS number_of_ratings_32,
  SUM(v1.rating = 3 AND v2.rating = 3) AS number_of_ratings_33,
  SUM(v1.rating = 3 AND v2.rating = 4) AS number_of_ratings_34,
  SUM(v1.rating = 3 AND v2.rating = 5) AS number_of_ratings_35,
  SUM(v1.rating = 4 AND v2.rating = 1) AS number_of_ratings_41,
  SUM(v1.rating = 4 AND v2.rating = 2) AS number_of_ratings_42,
  SUM(v1.rating = 4 AND v2.rating = 3) AS number_of_ratings_43,
  SUM(v1.rating = 4 AND v2.rating = 4) AS number_of_ratings_44,
  SUM(v1.rating = 4 AND v2.rating = 5) AS number_of_ratings_45,
  SUM(v1.rating = 5 AND v2.rating = 1) AS number_of_ratings_51,
  SUM(v1.rating = 5 AND v2.rating = 2) AS number_of_ratings_52,
  SUM(v1.rating = 5 AND v2.rating = 3) AS number_of_ratings_53,
  SUM(v1.rating = 5 AND v2.rating = 4) AS number_of_ratings_54,
  SUM(v1.rating = 5 AND v2.rating = 5) AS number_of_ratings_55
FROM ktapp_vote v1
INNER JOIN ktapp_vote v2 ON v2.film_id = v1.film_id
WHERE v1.user_id = %s
GROUP BY v1.user_id, v2.user_id
HAVING COUNT(1) >= 50
) t
'''


KEYWORD_SIMILARITY_TEMPLATE = '''
SELECT
  user_1_id, user_2_id, keyword_id,
  number_of_ratings,
  ROUND(1.0 * (
  100 * number_of_ratings_11 +
   85 * number_of_ratings_12 +
   50 * number_of_ratings_13 +
   15 * number_of_ratings_14 +
    0 * number_of_ratings_15 +
   85 * number_of_ratings_21 +
  100 * number_of_ratings_22 +
   65 * number_of_ratings_23 +
   30 * number_of_ratings_24 +
   15 * number_of_ratings_25 +
   50 * number_of_ratings_31 +
   65 * number_of_ratings_32 +
  100 * number_of_ratings_33 +
   65 * number_of_ratings_34 +
   50 * number_of_ratings_35 +
   15 * number_of_ratings_41 +
   30 * number_of_ratings_42 +
   65 * number_of_ratings_43 +
  100 * number_of_ratings_44 +
   85 * number_of_ratings_45 +
    0 * number_of_ratings_51 +
   15 * number_of_ratings_52 +
   50 * number_of_ratings_53 +
   85 * number_of_ratings_54 +
  100 * number_of_ratings_55
  ) / number_of_ratings) AS similarity,
  %s AS last_calculated_at
FROM (
SELECT
  v1.user_id AS user_1_id, v2.user_id AS user_2_id, fk.keyword_id AS keyword_id,
  COUNT(1) AS number_of_ratings,
  SUM(v1.rating = 1 AND v2.rating = 1) AS number_of_ratings_11,
  SUM(v1.rating = 1 AND v2.rating = 2) AS number_of_ratings_12,
  SUM(v1.rating = 1 AND v2.rating = 3) AS number_of_ratings_13,
  SUM(v1.rating = 1 AND v2.rating = 4) AS number_of_ratings_14,
  SUM(v1.rating = 1 AND v2.rating = 5) AS number_of_ratings_15,
  SUM(v1.rating = 2 AND v2.rating = 1) AS number_of_ratings_21,
  SUM(v1.rating = 2 AND v2.rating = 2) AS number_of_ratings_22,
  SUM(v1.rating = 2 AND v2.rating = 3) AS number_of_ratings_23,
  SUM(v1.rating = 2 AND v2.rating = 4) AS number_of_ratings_24,
  SUM(v1.rating = 2 AND v2.rating = 5) AS number_of_ratings_25,
  SUM(v1.rating = 3 AND v2.rating = 1) AS number_of_ratings_31,
  SUM(v1.rating = 3 AND v2.rating = 2) AS number_of_ratings_32,
  SUM(v1.rating = 3 AND v2.rating = 3) AS number_of_ratings_33,
  SUM(v1.rating = 3 AND v2.rating = 4) AS number_of_ratings_34,
  SUM(v1.rating = 3 AND v2.rating = 5) AS number_of_ratings_35,
  SUM(v1.rating = 4 AND v2.rating = 1) AS number_of_ratings_41,
  SUM(v1.rating = 4 AND v2.rating = 2) AS number_of_ratings_42,
  SUM(v1.rating = 4 AND v2.rating = 3) AS number_of_ratings_43,
  SUM(v1.rating = 4 AND v2.rating = 4) AS number_of_ratings_44,
  SUM(v1.rating = 4 AND v2.rating = 5) AS number_of_ratings_45,
  SUM(v1.rating = 5 AND v2.rating = 1) AS number_of_ratings_51,
  SUM(v1.rating = 5 AND v2.rating = 2) AS number_of_ratings_52,
  SUM(v1.rating = 5 AND v2.rating = 3) AS number_of_ratings_53,
  SUM(v1.rating = 5 AND v2.rating = 4) AS number_of_ratings_54,
  SUM(v1.rating = 5 AND v2.rating = 5) AS number_of_ratings_55
FROM ktapp_vote v1
INNER JOIN ktapp_vote v2 ON v2.film_id = v1.film_id
INNER JOIN ktapp_filmkeywordrelationship fk ON fk.film_id = v1.film_id
WHERE v1.user_id = %s
AND fk.keyword_id IN (3,27,29,32,39,54,55,56,62,76,95,107,112,120,171,174,212,250,314,332,368,612,674,954,1229,1264,1265,1323,1672,4150)
GROUP BY v1.user_id, v2.user_id, fk.keyword_id
HAVING COUNT(1) >= 30
) t
'''


class Command(BaseCommand):
    help = 'Calculate user-user recommendation'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='*', type=int)

    def calculate_uur(self, user_id):
        self.stdout.write('Refreshing user-user recommendation for user %d...' % user_id)
        now = datetime.datetime.now()

        self.stdout.write('Calculating generic...')
        benchmark_now = datetime.datetime.now()
        self.cursor.execute(GENERIC_SIMILARITY_TEMPLATE, (now, user_id))
        general_similarity = [row for row in self.cursor.fetchall()]
        self.stdout.write('Calculated in %d sec.' % (datetime.datetime.now() - benchmark_now).total_seconds())
        self.stdout.write('Updating generic...')
        benchmark_now = datetime.datetime.now()
        self.cursor.execute('''DELETE FROM ktapp_useruserrating WHERE user_1_id = %d AND keyword_id IS NULL''' % user_id)
        self.cursor.execute('''DELETE FROM ktapp_useruserrating WHERE user_2_id = %d AND keyword_id IS NULL''' % user_id)
        for row in general_similarity:
            self.cursor.execute(INSERT_SQL_TEMPLATE_1, row)
            if row[0] != row[1]:
                self.cursor.execute(INSERT_SQL_TEMPLATE_2, row)
        self.stdout.write('Updated in %d sec.' % (datetime.datetime.now() - benchmark_now).total_seconds())

        self.stdout.write('Calculating keyword...')
        benchmark_now = datetime.datetime.now()
        self.cursor.execute(KEYWORD_SIMILARITY_TEMPLATE, (now, user_id))
        general_similarity = [row for row in self.cursor.fetchall()]
        self.stdout.write('Calculated in %d sec.' % (datetime.datetime.now() - benchmark_now).total_seconds())
        self.stdout.write('Updating keyword...')
        benchmark_now = datetime.datetime.now()
        self.cursor.execute('''DELETE FROM ktapp_useruserrating WHERE user_1_id = %d AND keyword_id IS NOT NULL''' % user_id)
        self.cursor.execute('''DELETE FROM ktapp_useruserrating WHERE user_2_id = %d AND keyword_id IS NOT NULL''' % user_id)
        for row in general_similarity:
            self.cursor.execute(INSERT_SQL_TEMPLATE_1, row)
            if row[0] != row[1]:
                self.cursor.execute(INSERT_SQL_TEMPLATE_2, row)
        self.stdout.write('Updated in %d sec.' % (datetime.datetime.now() - benchmark_now).total_seconds())

        connection.commit()
        u = models.KTUser.objects.get(id=user_id)
        u.last_uur_calculation_at = now
        u.save()
        self.stdout.write('Refreshed user-user recommendation for user %d in %f sec.' % (
            user_id,
            (datetime.datetime.now() - now).total_seconds(),
        ))

    def handle(self, *args, **options):
        self.cursor = connection.cursor()
        if options['user_id']:
            for user_id in options['user_id']:
                self.calculate_uur(user_id)
        else:
            a_year_ago = datetime.date.today() - datetime.timedelta(days=365)
            a_month_ago = datetime.date.today() - datetime.timedelta(days=30)
            try:
                if random.random() < 0.5:
                    # relatively new users: less than a year
                    # selected_user_id = models.KTUser.objects.filter(last_activity_at__gte=a_month_ago, date_joined__gte=a_year_ago, number_of_ratings__gte=50).only('id').order_by('?')[0].id
                    selected_user_id = models.KTUser.objects.filter(last_uur_calculation_at=None, last_activity_at__gte=a_month_ago, date_joined__gte=a_year_ago, number_of_ratings__gte=50).only('id').order_by('?')[0].id
                else:
                    # relatively old users
                    # selected_user_id = models.KTUser.objects.filter(last_activity_at__gte=a_month_ago, date_joined__lt=a_year_ago, number_of_ratings__gte=100).only('id').order_by('?')[0].id
                    selected_user_id = models.KTUser.objects.filter(last_uur_calculation_at=None, last_activity_at__gte=a_month_ago, date_joined__lt=a_year_ago, number_of_ratings__gte=100).only('id').order_by('?')[0].id
            except Exception:
                return
            self.calculate_uur(selected_user_id)
