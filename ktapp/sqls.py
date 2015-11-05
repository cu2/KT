SIMILARITY = '''
SELECT
  uur.number_of_ratings,
  ROUND(1.0 * (
  100 * uur.number_of_ratings_11 +
   85 * uur.number_of_ratings_12 +
   50 * uur.number_of_ratings_13 +
   15 * uur.number_of_ratings_14 +
    0 * uur.number_of_ratings_15 +
   85 * uur.number_of_ratings_21 +
  100 * uur.number_of_ratings_22 +
   65 * uur.number_of_ratings_23 +
   30 * uur.number_of_ratings_24 +
   15 * uur.number_of_ratings_25 +
   50 * uur.number_of_ratings_31 +
   65 * uur.number_of_ratings_32 +
  100 * uur.number_of_ratings_33 +
   65 * uur.number_of_ratings_34 +
   50 * uur.number_of_ratings_35 +
   15 * uur.number_of_ratings_41 +
   30 * uur.number_of_ratings_42 +
   65 * uur.number_of_ratings_43 +
  100 * uur.number_of_ratings_44 +
   85 * uur.number_of_ratings_45 +
    0 * uur.number_of_ratings_51 +
   15 * uur.number_of_ratings_52 +
   50 * uur.number_of_ratings_53 +
   85 * uur.number_of_ratings_54 +
  100 * uur.number_of_ratings_55
  ) / uur.number_of_ratings) AS sim
FROM ktapp_useruserrating uur
WHERE uur.user_1_id = %s AND uur.user_2_id = %s AND uur.keyword_id IS NULL
'''


SIMILARITY_PER_GENRE = '''
SELECT
  uur.number_of_ratings,
  ROUND(1.0 * (
  100 * uur.number_of_ratings_11 +
   85 * uur.number_of_ratings_12 +
   50 * uur.number_of_ratings_13 +
   15 * uur.number_of_ratings_14 +
    0 * uur.number_of_ratings_15 +
   85 * uur.number_of_ratings_21 +
  100 * uur.number_of_ratings_22 +
   65 * uur.number_of_ratings_23 +
   30 * uur.number_of_ratings_24 +
   15 * uur.number_of_ratings_25 +
   50 * uur.number_of_ratings_31 +
   65 * uur.number_of_ratings_32 +
  100 * uur.number_of_ratings_33 +
   65 * uur.number_of_ratings_34 +
   50 * uur.number_of_ratings_35 +
   15 * uur.number_of_ratings_41 +
   30 * uur.number_of_ratings_42 +
   65 * uur.number_of_ratings_43 +
  100 * uur.number_of_ratings_44 +
   85 * uur.number_of_ratings_45 +
    0 * uur.number_of_ratings_51 +
   15 * uur.number_of_ratings_52 +
   50 * uur.number_of_ratings_53 +
   85 * uur.number_of_ratings_54 +
  100 * uur.number_of_ratings_55
  ) / uur.number_of_ratings) AS sim,
  k.id, k.name, k.slug_cache
FROM ktapp_useruserrating uur
INNER JOIN ktapp_keyword k ON k.id = uur.keyword_id
WHERE uur.user_1_id = %s AND uur.user_2_id = %s
ORDER BY sim DESC
'''
