from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Option, Question, Process, Form, User, Category, Answer
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
import graphene
from .schema import Query
from django.core.exceptions import ValidationError
from django.db import IntegrityError


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


class CategoryTests(APITestCase):
    def setUp(self):


        
        self.admin_user = User.objects.create_superuser(  
            username='admin_user',  
            email='admin@example.com',  
            password='admin_pass'  
        )  
        self.normal_user = User.objects.create_user(
            username='normal_user', password='normal_pass'
        )

        # Admin logs in
        self.client.force_authenticate(user=self.admin_user) 

    def test_admin_can_create_public_category(self):
        """Test that an admin can create a public category"""
        data = {
            'name': 'Public Category', 
            }
        response = self.client.post(reverse('public-category-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(name='Public Category')
        self.assertEqual(category.user, None)

    def test_normal_user_creates_exclusive_category(self):
        """Test that a normal user can create an exclusive category"""
        self.client.logout()
        self.client.force_authenticate(self.normal_user)

        data = {'name': 'Exclusive Category', 'user': self.normal_user.id}
        response = self.client.post(reverse('exclusive-category-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(name='Exclusive Category')
        self.assertEqual(category.user, self.normal_user)

    def test_normal_user_cannot_create_public_category(self):
        """Test that a normal user cannot create a public category"""
        self.client.logout()
        self.client.force_authenticate(self.normal_user)

        data = {'name': 'Invalid Public Category', 'user': None}
        response = self.client.post(reverse('public-category-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_retrieve_public_categories(self):
        """Test that an admin can retrieve public categories"""
        Category.objects.create(name='Public Category 1', user=None)
        Category.objects.create(name='Public Category 2', user=None)

        response = self.client.get(reverse('public-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_normal_user_can_retrieve_public_categories(self):
        """Test that a normal user can retrieve public categories"""
        self.client.logout()
        self.client.login(username='normal_user', password='normal_pass')

        Category.objects.create(name='Public Category 1', user=None)
        Category.objects.create(name='Public Category 2', user=None)

        response = self.client.get(reverse('public-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_normal_user_can_retrieve_exclusive_categories(self):
        """Test that a normal user can retrieve their exclusive categories"""
        self.client.logout()
        self.client.force_authenticate(self.normal_user)

        Category.objects.create(name='Exclusive Category 1', user=self.normal_user)
        Category.objects.create(name='Exclusive Category 2', user=self.normal_user)

        response = self.client.get(reverse('exclusive-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_cannot_retrieve_exclusive_categories_of_others(self):
        """Test that an admin cannot retrieve exclusive categories of normal users"""
        Category.objects.create(name='Exclusive Category 1', user=self.normal_user)
        Category.objects.create(name='Exclusive Category 2', user=self.normal_user)

        response = self.client.get(reverse('exclusive-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

User = get_user_model()

class FormProcessQuestionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        
        # Create categories and forms
        self.category = Category.objects.create(user=self.user, name="General", description="General category")
        self.form_linear = Form.objects.create(user=self.user, name="Linear Form", category=self.category, linear=True)
        
        # Create processes and questions for the form
        self.process1 = Process.objects.create(user=self.user, category=self.category)
        self.process2 = Process.objects.create(user=self.user, category=self.category)
        self.form_linear.order = [self.process1.id, self.process2.id]
        self.form_linear.save()

        self.question1 = Question.objects.create(user=self.user, text="First question?", type=1, required=True)
        self.question2 = Question.objects.create(user=self.user, text="Second question?", type=1, required=True)
        self.process1.order = [self.question1.id, self.question2.id]
        self.process1.save()

    def test_unique_answer_per_form_per_user(self):
        """
        Test that a user cannot submit multiple answers to the same question within the same form.
        """
        Answer.objects.create(user=self.user, question=self.question1, form=self.form_linear, text="First answer to question 1")
        
        # Attempt to create a duplicate answer
        with self.assertRaises(IntegrityError):
            Answer.objects.create(user=self.user, question=self.question1, form=self.form_linear, text="Duplicate answer")

    def test_free_form_answer_submission(self):
        """
        In a free form, any question should be answerable regardless of order.
        """
        Answer.objects.create(user=self.user, question=self.question1, form=self.form_linear, text="Answer to question in free form")
        Answer.objects.create(user=self.user, question=self.question2, form=self.form_linear, text="Answer to another question in free form")


    def test_answer_submission_non_linear_form(self):
        """
        Test that answers in a non-linear form can be submitted in any order.
        """
        self.form_linear.linear = False
        self.form_linear.save()
        
       
        answer2 = Answer.objects.create(user=self.user, question=self.question2, form=self.form_linear, text="Answer to question 2")
        self.assertIsNotNone(answer2)
        
        
        answer1 = Answer.objects.create(user=self.user, question=self.question1, form=self.form_linear, text="Answer to question 1")
        self.assertIsNotNone(answer1)

    def test_text_only_answer_for_text_question(self):
        """
        Test that only the text field is accepted for text-type questions.
        """
        with self.assertRaises(ValidationError):
            Answer.objects.create(user=self.user, question=self.question1, form=self.form_linear, option=self.option)
        
    


from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.testcases import JSONWebTokenTestCase

class FormProcessQuestionTests(JSONWebTokenTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.client.authenticate(self.user)
        
        
        self.category = Category.objects.create(user=self.user, name="General", description="General category")
        self.form_linear = Form.objects.create(user=self.user, name="Linear Form", category=self.category, linear=True)
        self.process1 = Process.objects.create(user=self.user, category=self.category)
        self.process2 = Process.objects.create(user=self.user, category=self.category)
        self.form_linear.order = [self.process1.id, self.process2.id]
        self.form_linear.save()

        self.question1 = Question.objects.create(user=self.user, text="First question?", type=1, required=True)
        self.question2 = Question.objects.create(user=self.user, text="Second question?", type=1, required=True)
        self.process1.order = [self.question1.id, self.question2.id]
        self.process1.save()

    def test_answer_submission_order_linear_form(self):
        """
        Test that answers in a linear form must be submitted in order.
        """
        
        response = self.client.execute(
            '''
            mutation($input: AnswerInput!) {
                submitAnswer(input: $input) {
                    answer {
                        text
                    }
                }
            }
            ''',
            variables={'input': {'questionId': str(self.question2.id), 'text': "Attempt to answer out of order", 'formId': str(self.form_linear.id)}}
        )

        
        self.assertIsNotNone(response.errors)
        self.assertIn("Answer previous questions in order first.", response.errors[0].message)
        
        
        response = self.client.execute(
            '''
            mutation($input: AnswerInput!) {
                submitAnswer(input: $input) {
                    answer {
                        text
                    }
                }
            }
            ''',
            variables={'input': {'questionId': str(self.question1.id), 'text': "Answer to question 1", 'formId': str(self.form_linear.id)}}
        )

        self.assertIsNone(response.errors)  
