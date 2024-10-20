# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from form.models import Form, Question, Option, Answer

class AnswerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123'
        )
        self.client.login(username='testuser', password='TestPassword123')
        
        self.form = Form.objects.create(user=self.user, name='Sample Form')
        self.question = Question.objects.create(
            form=self.form, process=None, text='Sample Question', type=2, required=True
        )
        self.option1 = Option.objects.create(question=self.question, text='Option 1')
        self.option2 = Option.objects.create(question=self.question, text='Option 2')
    
    def test_submit_answer(self):
        url = reverse('answer-submit-list')
        data = {
            'question': self.question.id,
            'select': [self.option1.id],
            'text': 'Sample answer text'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(Answer.objects.first().text, 'Sample answer text')
    def test_get_answers(self):
        # Submit an answer first
        Answer.objects.create(
            question=self.question,
            user=self.user,
            text='Sample answer text'
        )
        url = reverse('answer-submit-list') + f'?question_id={self.question.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Sample answer text')
