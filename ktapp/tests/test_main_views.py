from django.conf import settings
from django.urls import reverse

from ktapp import models
from . import utils as test_utils


class IndexTestCase(test_utils.SimpleViewTestCase):
    @classmethod
    def setup_test_data(cls):
        cls.user2 = test_utils.create_test_user("user2")
        cls.film = models.Film.objects.create(orig_title="film", year=1999)
        cls.topic = models.Topic.objects.create(title="topic")
        if settings.VAPITI_TOPIC_ID:
            models.Topic.objects.create(id=settings.VAPITI_TOPIC_ID, title="Vapiti-topic")
        cls.comment1 = test_utils.create_test_comment(1, cls.test_user, film=cls.film)
        cls.comment2 = test_utils.create_test_comment(2, cls.user2, film=cls.film)
        cls.comment3 = test_utils.create_test_comment(3, cls.test_user, film=cls.film)
        cls.comment4 = test_utils.create_test_comment(4, cls.user2, topic=cls.topic)

    @classmethod
    def get_url(cls):
        return reverse("index")

    def common_assertions(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ktapp/index.html")
        self.assertEqual(len(response.context["buzz_comments"]), 2)
        self.assertEqual(
            list(response.context["buzz_comments"]),
            [self.comment4, self.comment3],
        )


class FilmMainTestCase(test_utils.SimpleViewTestCase):
    @classmethod
    def setup_test_data(cls):
        cls.user2 = test_utils.create_test_user("user2")
        cls.film = models.Film.objects.create(orig_title="film", year=1999)
        cls.vote = models.Vote.objects.create(
            user=cls.test_user, film=cls.film, rating=5
        )
        cls.vote2 = models.Vote.objects.create(user=cls.user2, film=cls.film, rating=3)

    @classmethod
    def get_url(cls):
        return reverse("film_main", args=[cls.film.id, cls.film.slug_cache])

    def common_assertions(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ktapp/film_subpages/film_main.html")
        self.assertEqual(response.context["film"], self.film)
        self.assertEqual(len(response.context["votes"]), 5)
        number_of_ratings_3, (special_votes_3, normal_votes_3) = response.context[
            "votes"
        ][2]
        self.assertEqual(number_of_ratings_3, 0)
        self.assertEqual(special_votes_3, [])
        self.assertEqual(normal_votes_3, [self.vote2])

    def anonymous_assertions(self, response):
        self.assertEqual(response.context["your_rating"], 0)
        number_of_ratings_5, (special_votes_5, normal_votes_5) = response.context[
            "votes"
        ][0]
        self.assertEqual(number_of_ratings_5, 0)
        self.assertEqual(special_votes_5, [])
        self.assertEqual(normal_votes_5, [self.vote])

    def logged_in_assertions(self, response):
        self.assertEqual(response.context["your_rating"], self.vote.rating)
        number_of_ratings_5, (special_votes_5, normal_votes_5) = response.context[
            "votes"
        ][0]
        self.assertEqual(number_of_ratings_5, 0)
        self.assertEqual(special_votes_5, [self.vote])
        self.assertEqual(normal_votes_5, [])


class FilmCommentsTestCase(test_utils.SimpleViewTestCase):
    @classmethod
    def setup_test_data(cls):
        cls.user2 = test_utils.create_test_user("user2")
        cls.film = models.Film.objects.create(orig_title="film", year=1999)
        cls.other_film = models.Film.objects.create(orig_title="other_film", year=1999)
        cls.vote = models.Vote.objects.create(
            user=cls.test_user, film=cls.film, rating=5
        )
        cls.comment1 = test_utils.create_test_comment(1, cls.user2, film=cls.film)
        cls.comment2 = test_utils.create_test_comment(2, cls.test_user, film=cls.film)
        cls.comment3 = test_utils.create_test_comment(3, cls.user2, film=cls.film)
        cls.other_comment = test_utils.create_test_comment(
            4, cls.test_user, film=cls.other_film
        )
        models.Notification.objects.create(
            target_user=cls.test_user,
            notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT,
            film=cls.film,
            comment=cls.comment3,
        )

    @classmethod
    def get_url(cls):
        return reverse("film_comments", args=[cls.film.id, cls.film.slug_cache])

    def common_assertions(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ktapp/film_subpages/film_comments.html")
        self.assertEqual(response.context["film"], self.film)
        self.assertEqual(
            list(response.context["comments"]),
            [
                self.comment3,
                self.comment2,
                self.comment1,
            ],
        )

    def anonymous_assertions(self, response):
        self.assertEqual(response.context["your_rating"], 0)

    def logged_in_assertions(self, response):
        self.assertEqual(response.context["your_rating"], self.vote.rating)
        self.assertTrue(response.context["comments"][0].notified)


class ListOfTopicsTestCase(test_utils.SimpleViewTestCase):
    @classmethod
    def setup_test_data(cls):
        cls.user2 = test_utils.create_test_user("user2")
        cls.film = models.Film.objects.create(orig_title="film", year=1999)
        cls.topic1 = models.Topic.objects.create(title="topic1")
        cls.topic2 = models.Topic.objects.create(title="topic2")
        cls.topic3 = models.Topic.objects.create(title="topic3")
        cls.comment1 = test_utils.create_test_comment(1, cls.test_user, film=cls.film)
        cls.comment2 = test_utils.create_test_comment(2, cls.user2, topic=cls.topic1)
        cls.comment3 = test_utils.create_test_comment(
            3, cls.test_user, topic=cls.topic1
        )
        cls.comment4 = test_utils.create_test_comment(4, cls.user2, topic=cls.topic2)

    @classmethod
    def get_url(cls):
        return reverse("list_of_topics")

    def common_assertions(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ktapp/list_of_topics.html")
        self.assertEqual(len(response.context["topics"]), 3)
        self.assertEqual(
            list(response.context["topics"]), [self.topic2, self.topic1, self.topic3]
        )
        self.assertEqual(response.context["topics"][0].number_of_comments, 1)
        self.assertEqual(response.context["topics"][1].number_of_comments, 2)
        self.assertEqual(response.context["topics"][2].number_of_comments, 0)
        self.assertEqual(response.context["topics"][0].last_comment, self.comment4)
        self.assertEqual(response.context["topics"][1].last_comment, self.comment3)
        self.assertIsNone(response.context["topics"][2].last_comment)


class ForumTestCase(test_utils.SimpleViewTestCase):
    @classmethod
    def setup_test_data(cls):
        cls.user2 = test_utils.create_test_user("user2")
        cls.topic = models.Topic.objects.create(title="topic")
        cls.other_topic = models.Topic.objects.create(title="other_topic")
        cls.comment1 = test_utils.create_test_comment(1, cls.user2, topic=cls.topic)
        cls.comment2 = test_utils.create_test_comment(2, cls.test_user, topic=cls.topic)
        cls.comment3 = test_utils.create_test_comment(3, cls.user2, topic=cls.topic)
        cls.other_comment = test_utils.create_test_comment(
            4, cls.test_user, topic=cls.other_topic
        )
        models.Notification.objects.create(
            target_user=cls.test_user,
            notification_type=models.Notification.NOTIFICATION_TYPE_COMMENT,
            topic=cls.topic,
            comment=cls.comment3,
        )

    @classmethod
    def get_url(cls):
        return reverse("forum", args=[cls.topic.id, cls.topic.slug_cache])

    def common_assertions(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ktapp/forum.html")
        self.assertEqual(response.context["topic"], self.topic)
        self.assertEqual(
            list(response.context["comments"]),
            [
                self.comment3,
                self.comment2,
                self.comment1,
            ],
        )

    def logged_in_assertions(self, response):
        self.assertTrue(response.context["comments"][0].notified)
