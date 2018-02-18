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


VAPITI_WINNER_GOLD = '''
SELECT v.film_id, f.orig_title, SUM(u.vapiti_weight) AS sum_vapiti_weight, COUNT(distinct u.id) AS user_count, f.number_of_ratings, f.average_rating
FROM ktapp_vapitivote v
INNER JOIN ktapp_ktuser u ON u.id = v.user_id
INNER JOIN ktapp_film f ON f.id = v.film_id
WHERE u.core_member=1
AND v.year = %s
AND v.vapiti_round = 2
AND v.vapiti_type = 'G'
GROUP BY v.film_id
ORDER BY user_count DESC, sum_vapiti_weight DESC
LIMIT 1
'''


VAPITI_WINNER_SILVER_FEMALE = '''
SELECT r.id, a.name, f.orig_title, SUM(u.vapiti_weight) AS sum_vapiti_weight, COUNT(distinct u.id) AS user_count, f.number_of_ratings, f.average_rating
FROM ktapp_vapitivote v
INNER JOIN ktapp_ktuser u ON u.id = v.user_id
INNER JOIN ktapp_film f ON f.id = v.film_id
INNER JOIN ktapp_artist a ON a.id = v.artist_id
INNER JOIN ktapp_filmartistrelationship r ON r.film_id = v.film_id AND r.artist_id = v.artist_id
WHERE u.core_member=1
AND v.year = %s
AND v.vapiti_round = 2
AND v.vapiti_type = 'F'
GROUP BY f.id, a.id
ORDER BY user_count DESC, sum_vapiti_weight DESC
LIMIT 1
'''


VAPITI_WINNER_SILVER_MALE = '''
SELECT r.id, a.name, f.orig_title, SUM(u.vapiti_weight) AS sum_vapiti_weight, COUNT(distinct u.id) AS user_count, f.number_of_ratings, f.average_rating
FROM ktapp_vapitivote v
INNER JOIN ktapp_ktuser u ON u.id = v.user_id
INNER JOIN ktapp_film f ON f.id = v.film_id
INNER JOIN ktapp_artist a ON a.id = v.artist_id
INNER JOIN ktapp_filmartistrelationship r ON r.film_id = v.film_id AND r.artist_id = v.artist_id
WHERE u.core_member=1
AND v.year = %s
AND v.vapiti_round = 2
AND v.vapiti_type = 'M'
GROUP BY f.id, a.id
ORDER BY user_count DESC, sum_vapiti_weight DESC
LIMIT 1
'''
