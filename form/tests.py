from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Option, Question, Process, Form, User
from django.urls import reverse
from rest_framework import status

class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

class OptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_create_option(self):
        response = self.client.post('/options/', {'text': 'Option 1'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Option.objects.filter(text='Option 1').exists())


class QuestionAPITests(UserTestCase):
    def setUp(self):
        super().setUp()
        self.option = Option.objects.create(user=self.user, text='Option 1')

    def test_create_question(self):
        response = self.client.post(reverse('questions-list'), {
            'text': 'Question 1',
            'type': 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Question.objects.filter(text='Question 1').exists())

    def test_order_field_not_empty_for_checkbox_or_test(self):
        response = self.client.post(reverse('questions-list'), {
            'text': 'Checkbox Question',
            'type': 2,
            'order': []
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn('order', response.data)

    def test_can_only_add_own_questions(self):
        another_user = User.objects.create_user(username='anotheruser', password='anotherpass')
        self.client.logout()
        self.client.force_authenticate(user=another_user)
        response = self.client.post(reverse('questions-list'), {
            'text': 'Question from Another User',
            'type': 2,
            'order': [self.option.id]
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_field_empty_for_text_questions(self):
        response = self.client.post(reverse('questions-list'), {
            'text': 'Question from Another User',
            'type': 1,
            'order': [self.option.id]
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class ProcessAPITests(UserTestCase):
    def setUp(self):
        super().setUp()
        self.question = Question.objects.create(user=self.user, text='Question 1', type=1)

    def test_create_process(self):
        response = self.client.post(reverse('processes-list'), {
            'order': [self.question.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_field_not_empty(self):
        response = self.client.post(reverse('processes-list'), {
            'order': []
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_only_add_own_questions(self):
        another_user = User.objects.create_user(username='anotheruser', password='anotherpass')
        self.client.logout()
        self.client.force_authenticate(user=another_user)
        response = self.client.post(reverse('processes-list'), {
            'order': [self.question.id],
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FormAPITests(UserTestCase):
    def setUp(self):
        super().setUp()
        self.process = Process.objects.create(user=self.user, order=[1])

    def test_create_form(self):
        response = self.client.post(reverse('form-list'), {
            'name': 'Form 1',
            'order': [self.process.id],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Form.objects.filter(name='Form 1').exists())

    def test_order_field_not_empty(self):
        response = self.client.post(reverse('form-list'), {
            'name': 'Form 2',
            'order': []
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_can_only_add_public_or_own_processes(self):
        private_process = Process.objects.create(user=self.user, is_private=True, order=[1])
        another_user = User.objects.create_user(username='anotheruser', password='anotherpass')
        self.client.logout()
        self.client.force_authenticate(user=another_user)
        
        
        response = self.client.post(reverse('form-list'), {
            'name': 'Form with Process from Another User',
            'order': [private_process.id],
            'is_private': False,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_private_form_requires_password(self):
        response = self.client.post(reverse('form-list'), {
            'name': 'Private Form',
            'order': [self.process.id],
            'is_private': True,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)  
        self.assertEqual(response.data['non_field_errors'][0], 'A password is required for private forms.')
