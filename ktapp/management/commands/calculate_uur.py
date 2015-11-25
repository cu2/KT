import datetime

from django.core.management.base import BaseCommand
from django.db import connection


DELETE_SQL_TEMPLATE = '''
DELETE FROM ktapp_useruserrating WHERE user_1_id = %s
'''


INSERT_SQL_TEMPLATE = '''
INSERT INTO ktapp_useruserrating (
  user_1_id, user_2_id, keyword_id,
  number_of_ratings,
  similarity,
  last_calculated_at
)
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


INSERT_SQL_TEMPLATE_W_KEYWORD = '''
INSERT INTO ktapp_useruserrating (
  user_1_id, user_2_id, keyword_id,
  number_of_ratings,
  similarity,
  last_calculated_at
)
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

    def handle(self, *args, **options):
        if len(args) < 1:
            return
        user_id = int(args[0])
        self.stdout.write('Refreshing user-user recommendation for user %s...' % user_id)
        cursor = connection.cursor()
        now = datetime.datetime.now()
        cursor.execute(DELETE_SQL_TEMPLATE, (user_id,))
        print 'Generic...'
        cursor.execute(INSERT_SQL_TEMPLATE, (now, user_id))
        print 'Keyword...'
        cursor.execute(INSERT_SQL_TEMPLATE_W_KEYWORD, (now, user_id))
        connection.commit()
        print 'Done in %s sec.' % (datetime.datetime.now() - now).total_seconds()
        self.stdout.write('Refreshed user-user recommendation.')
