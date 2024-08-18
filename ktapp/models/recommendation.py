from django.db import models, connection


class Recommendation(models.Model):
    film = models.ForeignKey('Film')
    user = models.ForeignKey('KTUser')
    fav_number_of_ratings = models.PositiveIntegerField(default=0)
    fav_average_rating = models.DecimalField(default=None, max_digits=2, decimal_places=1, blank=True, null=True)

    class Meta:
        unique_together = ['film', 'user']

    @classmethod
    def recalculate_fav_for_user_and_user(cls, who, whom):
        cursor = connection.cursor()
        cursor.execute('''SELECT COUNT(1) FROM ktapp_vote WHERE user_id = %s''', [whom.id])
        vote_count = cursor.fetchone()[0]
        # If the new fav user has many votes, it's faster to regenerate all recommendations.
        if vote_count > 5000:
            regenerate_all_recommendations(who)
        else:
            regenerate_some_recommendations(who, whom)

    @classmethod
    def recalculate_fav_for_users_and_film(cls, users, film):
        user_ids = ','.join([unicode(u.id) for u in users])
        if user_ids:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM ktapp_recommendation WHERE user_id IN (%s) AND film_id = %s' % (user_ids, film.id))
            cursor.execute('''
                INSERT INTO ktapp_recommendation (user_id, film_id, fav_number_of_ratings, fav_average_rating)
                SELECT
                  f.who_id AS user_id,
                  v.film_id AS film_id,
                  COUNT(v.rating) AS fav_number_of_ratings,
                  CAST(AVG(v.rating) AS DECIMAL(2, 1)) AS fav_average_rating
                FROM ktapp_follow f
                INNER JOIN ktapp_vote v ON v.user_id = f.whom_id
                WHERE f.who_id IN (%s) AND v.film_id = %s
                GROUP BY
                  f.who_id,
                  v.film_id
            ''' % (user_ids, film.id))


class FilmFilmRecommendation(models.Model):
    film_1 = models.ForeignKey('Film', related_name='film_1')
    film_2 = models.ForeignKey('Film', related_name='film_2')
    last_calculated_at = models.DateTimeField()
    score = models.IntegerField(default=0)


class UserUserRating(models.Model):
    user_1 = models.ForeignKey('KTUser', related_name='user_1')
    user_2 = models.ForeignKey('KTUser', related_name='user_2')
    keyword = models.ForeignKey('Keyword', blank=True, null=True)
    last_calculated_at = models.DateTimeField()
    number_of_ratings = models.IntegerField(default=0)
    similarity = models.PositiveSmallIntegerField(blank=True, null=True)
    # TODO: unique index on user_1, user_2, keyword


def regenerate_all_recommendations(who):
    cursor = connection.cursor()
    cursor.execute('''
        DELETE FROM ktapp_recommendation WHERE user_id = %s
    ''', [who.id])
    cursor.execute('''
        INSERT INTO ktapp_recommendation (user_id, film_id, fav_number_of_ratings, fav_average_rating)
        SELECT
            f.who_id AS user_id,
            v.film_id AS film_id,
            COUNT(v.rating) AS fav_number_of_ratings,
            CAST(AVG(v.rating) AS DECIMAL(2, 1)) AS fav_average_rating
        FROM ktapp_follow f
        INNER JOIN ktapp_vote v ON v.user_id = f.whom_id
        WHERE f.who_id = %s
        GROUP BY
            f.who_id,
            v.film_id
    ''', [who.id])


def regenerate_some_recommendations(who, whom):
    cursor = connection.cursor()
    cursor.execute('''
        DELETE FROM ktapp_recommendation WHERE user_id = %s AND film_id IN (
            SELECT film_id FROM ktapp_vote WHERE user_id = %s
        )
    ''', [who.id, whom.id])
    cursor.execute('''
        INSERT INTO ktapp_recommendation (user_id, film_id, fav_number_of_ratings, fav_average_rating)
        SELECT
            f.who_id AS user_id,
            v.film_id AS film_id,
            COUNT(v.rating) AS fav_number_of_ratings,
            CAST(AVG(v.rating) AS DECIMAL(2, 1)) AS fav_average_rating
        FROM ktapp_follow f
        INNER JOIN ktapp_vote v ON v.user_id = f.whom_id
        WHERE f.who_id = %s AND v.film_id IN (
            SELECT film_id FROM ktapp_vote WHERE user_id = %s
        )
        GROUP BY
            f.who_id,
            v.film_id
    ''', [who.id, whom.id])
