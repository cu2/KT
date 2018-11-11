from django.test import TestCase

from ktapp import models


class MessageSendingTestCase(TestCase):

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
        models.KTUser.objects.create(
            id=3,
            username='u3',
            email='u3@example.com',
        )

    def test_send_message(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.Message.send_message(
            sent_by=u1,
            content='Test message',
            recipients={u2},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 2)
        message1, message2 = tuple(messages)
        self.assertEqual(message1.sent_by, u1)
        self.assertEqual(message2.sent_by, u1)
        self.assertEqual(message1.owned_by, u1)
        self.assertEqual(message2.owned_by, u2)
        self.assertTrue(message1.private)
        self.assertTrue(message2.private)
        self.assertEqual(message1.sent_to.count(), 1)
        self.assertEqual(message2.sent_to.count(), 1)
        self.assertEqual(message1.sent_to.all()[0], u2)
        self.assertEqual(message2.sent_to.all()[0], u2)
        self.assertEqual(u1.number_of_messages, 1)
        self.assertEqual(u2.number_of_messages, 1)
        self.assertEqual(u1.last_message_at, None)
        self.assertEqual(u2.last_message_at, message2.sent_at)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u2), 1)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u1), 1)

    def test_send_message_with_ignore(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        models.IgnoreUser.set(
            who=u2,
            whom=u1,
            ignore_pm=True,
        )
        models.Message.send_message(
            sent_by=u1,
            content='Test message',
            recipients={u2},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 1)
        message1 = messages[0]
        self.assertEqual(message1.sent_by, u1)
        self.assertEqual(message1.owned_by, u1)
        self.assertTrue(message1.private)
        self.assertEqual(message1.sent_to.count(), 1)
        self.assertEqual(message1.sent_to.all()[0], u2)
        self.assertEqual(u1.number_of_messages, 1)
        self.assertEqual(u2.number_of_messages, 0)
        self.assertEqual(u1.last_message_at, None)
        self.assertEqual(u2.last_message_at, None)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u2), 1)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u1), 0)

    def test_send_message_2_recipients(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        u3 = models.KTUser.objects.get(id=3)
        models.Message.send_message(
            sent_by=u1,
            content='Test message',
            recipients={u2, u3},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 3)
        message1, message2, message3 = tuple(messages)
        self.assertEqual(message1.sent_by, u1)
        self.assertEqual(message2.sent_by, u1)
        self.assertEqual(message3.sent_by, u1)
        self.assertEqual(message1.owned_by, u1)
        self.assertEqual(message2.owned_by, u2)
        self.assertEqual(message3.owned_by, u3)
        self.assertFalse(message1.private)
        self.assertFalse(message2.private)
        self.assertFalse(message3.private)
        self.assertEqual(message1.sent_to.count(), 2)
        self.assertEqual(message2.sent_to.count(), 2)
        self.assertEqual(message3.sent_to.count(), 2)
        self.assertListEqual(list(message1.sent_to.all()), [u2, u3])
        self.assertListEqual(list(message2.sent_to.all()), [u2, u3])
        self.assertListEqual(list(message3.sent_to.all()), [u2, u3])
        self.assertEqual(u1.number_of_messages, 1)
        self.assertEqual(u2.number_of_messages, 1)
        self.assertEqual(u3.number_of_messages, 1)
        self.assertEqual(u1.last_message_at, None)
        self.assertEqual(u2.last_message_at, message2.sent_at)
        self.assertEqual(u3.last_message_at, message3.sent_at)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u2), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u3), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u1), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u3), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u3, partner=u1), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u3, partner=u2), 0)

    def test_send_message_2_recipients_with_ignore(self):
        u1 = models.KTUser.objects.get(id=1)
        u2 = models.KTUser.objects.get(id=2)
        u3 = models.KTUser.objects.get(id=3)
        models.IgnoreUser.set(
            who=u2,
            whom=u1,
            ignore_pm=True,
        )
        models.Message.send_message(
            sent_by=u1,
            content='Test message',
            recipients={u2, u3},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 2)
        message1, message3 = tuple(messages)
        self.assertEqual(message1.sent_by, u1)
        self.assertEqual(message3.sent_by, u1)
        self.assertEqual(message1.owned_by, u1)
        self.assertEqual(message3.owned_by, u3)
        self.assertFalse(message1.private)
        self.assertFalse(message3.private)
        self.assertEqual(message1.sent_to.count(), 2)
        self.assertEqual(message3.sent_to.count(), 2)
        self.assertListEqual(list(message1.sent_to.all()), [u2, u3])
        self.assertListEqual(list(message3.sent_to.all()), [u2, u3])
        self.assertEqual(u1.number_of_messages, 1)
        self.assertEqual(u3.number_of_messages, 1)
        self.assertEqual(u1.last_message_at, None)
        self.assertEqual(u3.last_message_at, message3.sent_at)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u2), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u1, partner=u3), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u1), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u2, partner=u3), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u3, partner=u1), 0)
        self.assertEqual(models.MessageCountCache.get_count(owned_by=u3, partner=u2), 0)

    def test_send_system_message(self):
        u2 = models.KTUser.objects.get(id=2)
        models.Message.send_message(
            sent_by=None,
            content='Test message',
            recipients={u2},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 1)
        message2 = messages[0]
        self.assertEqual(message2.sent_by, None)
        self.assertEqual(message2.owned_by, u2)
        self.assertTrue(message2.private)
        self.assertEqual(message2.sent_to.count(), 1)
        self.assertEqual(message2.sent_to.all()[0], u2)
        self.assertEqual(u2.number_of_messages, 1)
        self.assertEqual(u2.last_message_at, message2.sent_at)

    def test_send_system_message_2_recipients(self):
        u2 = models.KTUser.objects.get(id=2)
        u3 = models.KTUser.objects.get(id=3)
        models.Message.send_message(
            sent_by=None,
            content='Test message',
            recipients={u2, u3},
        )
        messages = models.Message.objects.all()
        self.assertEqual(messages.count(), 2)
        message2, message3 = tuple(messages)
        self.assertEqual(message2.sent_by, None)
        self.assertEqual(message3.sent_by, None)
        self.assertEqual(message2.owned_by, u2)
        self.assertEqual(message3.owned_by, u3)
        self.assertFalse(message2.private)
        self.assertFalse(message3.private)
        self.assertEqual(message2.sent_to.count(), 2)
        self.assertEqual(message3.sent_to.count(), 2)
        self.assertListEqual(list(message2.sent_to.all()), [u2, u3])
        self.assertListEqual(list(message3.sent_to.all()), [u2, u3])
        self.assertEqual(u2.number_of_messages, 1)
        self.assertEqual(u3.number_of_messages, 1)
        self.assertEqual(u2.last_message_at, message2.sent_at)
        self.assertEqual(u3.last_message_at, message3.sent_at)
