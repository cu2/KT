from django.test import TestCase

from ktapp import models


class IgnoreUserTestCase(TestCase):

    def setUp(self):
        models.KTUser.objects.create(
            id=1,
            username='u1',
            email='u1@example.com',
        )
        models.KTUser.objects.create(
            id=2,
            username='u2',
            email='u2@example.com',
        )

    def test_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertFalse(ignore_pm)
        self.assertFalse(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 0)

    def test_set_pm_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=True)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertTrue(ignore_pm)
        self.assertFalse(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 1)

    def test_set_comment_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_comment=True)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertFalse(ignore_pm)
        self.assertTrue(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 1)

    def test_set_both_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=True, ignore_comment=True)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertTrue(ignore_pm)
        self.assertTrue(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 1)

    def test_set_neither_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertFalse(ignore_pm)
        self.assertFalse(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 0)

    def test_set_both_and_reset_pm_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=True, ignore_comment=True)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=False)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertFalse(ignore_pm)
        self.assertTrue(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 1)

    def test_set_both_and_reset_both_and_get(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=True, ignore_comment=True)
        models.IgnoreUser.set(who=u1, whom=u2, ignore_pm=False, ignore_comment=False)
        ignore_pm, ignore_comment = models.IgnoreUser.get(who=u1, whom=u2)
        self.assertFalse(ignore_pm)
        self.assertFalse(ignore_comment)
        self.assertEqual(models.IgnoreUser.objects.filter(who=u1, whom=u2).count(), 0)
