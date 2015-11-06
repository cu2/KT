SIMILARITY = '''
SELECT
  uur.number_of_ratings,
  uur.similarity AS sim
FROM ktapp_useruserrating uur
WHERE uur.user_1_id = %s AND uur.user_2_id = %s AND uur.keyword_id IS NULL
'''


SIMILARITY_PER_GENRE = '''
SELECT
  uur.number_of_ratings,
  uur.similarity AS sim,
  k.id, k.name, k.slug_cache
FROM ktapp_useruserrating uur
INNER JOIN ktapp_keyword k ON k.id = uur.keyword_id
WHERE uur.user_1_id = %s AND uur.user_2_id = %s
ORDER BY sim DESC
'''


SIMILAR_USERS = '''
SELECT
  uur.number_of_ratings,
  uur.similarity AS sim,
  u.id, u.username, u.slug_cache
FROM ktapp_useruserrating uur
INNER JOIN ktapp_ktuser u ON u.id = uur.user_2_id
WHERE uur.user_1_id = %s AND uur.user_2_id != %s
AND uur.number_of_ratings >= %s
AND uur.keyword_id IS NULL
ORDER BY sim DESC, uur.number_of_ratings DESC, u.username, u.id
'''


SIMILAR_USERS_PER_GENRE = '''
SELECT
  uur.number_of_ratings,
  uur.similarity AS sim,
  u.id, u.username, u.slug_cache
FROM ktapp_useruserrating uur
INNER JOIN ktapp_ktuser u ON u.id = uur.user_2_id
WHERE uur.user_1_id = %s AND uur.user_2_id != %s
AND uur.number_of_ratings >= %s
AND uur.keyword_id = %s
ORDER BY sim DESC, uur.number_of_ratings DESC, u.username, u.id
'''
