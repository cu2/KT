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


RECOMMENDED_FILMS = '''
SELECT f.*
FROM ktapp_film f
INNER JOIN ktapp_filmfilmrecommendation ffr ON ffr.film_1_id = {film_id} AND ffr.film_2_id = f.id
ORDER BY ffr.score DESC, f.number_of_ratings DESC
LIMIT 10
'''


RECOMMENDED_FILMS_LOGGED_IN = '''
SELECT f.*
FROM ktapp_film f
INNER JOIN ktapp_filmfilmrecommendation ffr ON ffr.film_1_id = {film_id} AND ffr.film_2_id = f.id
LEFT JOIN ktapp_vote v ON v.film_id = f.id AND v.user_id = {user_id}
WHERE v.id IS NULL
ORDER BY ffr.score DESC, f.number_of_ratings DESC
LIMIT 10
'''
