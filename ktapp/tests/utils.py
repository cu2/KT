import datetime
import logging

from django.test import TestCase

from ktapp import models


class SimpleViewTestCase(TestCase):
    @classmethod
    def setup_test_data(cls):
        pass  # implement in subclass, if needed

    @classmethod
    def get_url(cls):
        raise NotImplementedError

    def common_assertions(self, response):
        pass  # implement in subclass, if needed

    def anonymous_assertions(self, response):
        pass  # implement in subclass, if needed

    def logged_in_assertions(self, response):
        pass  # implement in subclass, if needed

    @classmethod
    def setUpTestData(cls):
        cls.test_user = create_test_user("test_user")
        cls.setup_test_data()
        cls.url = cls.get_url()

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.common_assertions(response)
        self.anonymous_assertions(response)

    def test_logged_in(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        self.common_assertions(response)
        self.logged_in_assertions(response)


def create_test_user(name):
    return models.KTUser.objects.create(username=name, email=name)


def create_test_comment(when, user, film=None, topic=None, poll=None):
    if film:
        domain = models.Comment.DOMAIN_FILM
    elif topic:
        domain = models.Comment.DOMAIN_TOPIC
    elif poll:
        domain = models.Comment.DOMAIN_POLL
    else:
        raise Exception("Either film or topic or poll must be set")
    comment = models.Comment.objects.create(
        domain=domain,
        film=film,
        topic=topic,
        poll=poll,
        created_by=user,
        created_at=datetime.datetime.now() + datetime.timedelta(seconds=when),
        content="Test comment #{} to {} by {}".format(when, film, user),
    )
    comment.save(domain=comment.domain_object)
    return comment
