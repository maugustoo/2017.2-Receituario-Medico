from django.test import TestCase
from user.models import HealthProfessional
from chat.models import Message
from chat.views import ViewMessageHealthProfessional


class TestViewMessageHealthProfessional(TestCase):

    def setUp(self):
        self.view = ViewMessageHealthProfessional()

        self.user = HealthProfessional.objects.create(name='test',
                                                      email='teste@test.com')
        # Create Message.

        self.message = Message()
        self.message.text = "meu texto"
        self.message.subject = "Assunto"
        self.message.user_from = self.user
        self.message.user_to = self.user
        self.message.pk = '1'
        self.message.save()

        self.view.object = self.message
        self.view.user = self.user

    def test_chat_get_success_url_true(self):
        self.assertEqual(self.view.get_success_url(), '/pt-br/chat/view_message_health_professional/1')

    def test_chat_get_succes_url_false(self):
        self.message.pk = '2'
        self.assertNotEqual(self.view.get_success_url(), '/pt-br/chat/view_message_health_professional/1')
