# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model
# from user.models import User
# from form.models import Form, Process, Question, Category, Option, Answer
# import pytest
# from django.contrib.auth import get_user_model
# from graphene_django.utils.testing import graphql_query
# from .models import Form, Process, Question, Option

# User = get_user_model()

# class FormTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user', password='password')
#         self.client.force_authenticate(user=self.user)  

#     def test_form_creation(self):
#         """
#         Ensure we can create a form.
#         """
#         url = reverse('form-list')
#         data = {
#             'name': 'Test Form'
#         }
#         response = self.client.post(url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         form = Form.objects.get(name='Test Form')
#         self.assertEqual(Form.objects.count(), 1)
#         self.assertEqual(Form.objects.get().name, 'Test Form')
#         self.assertIsNotNone(form.url)
#         self.assertTrue(form.url.startswith('http'))


#     def test_private_form_requires_password(self):
#         """
#         Ensure private forms require a password.
#         """
#         url = reverse('form-list')  
#         data = {
#             'name': 'Private Form',
#             'is_private': True,  
#         }
#         response = self.client.post(url, data, format='json')

        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('non_field_errors', response.data)  
#         self.assertEqual(response.data['non_field_errors'][0], 'A password is required for private forms.')


#     def test_password_not_shown_in_retrieval(self):
#         """
#         Ensure password is not shown when retrieving a form.
#         """
#         form_data = {
#         'name': 'Private Test Form',
#         'is_private': True,
#         'password': '1234',  
#     }
#         url = reverse('form-list')
#         create_response = self.client.post(url, form_data, format='json')

        
#         self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
#         form_id = create_response.data['id']
#         retrieve_url = reverse('form-detail', args=[form_id])
#         response = self.client.get(f'{retrieve_url}?password=1234', format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertNotIn('password', response.data)

#     def test_only_creator_can_update_delete_form(self):
#         self.client.login(username='testuser', password='testpass')

#         # Create a form as 'testuser'
#         form_data = {
#             'name': 'Test Form'
#         }
#         form_response = self.client.post(reverse('form-list'), form_data, format='json')
#         self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)

#         # Log out and log in as another user
#         self.client.logout()
#         self.user1 = User.objects.create_user(username='user1', password='password1')
#         self.client.force_authenticate(user=self.user1)

#         # Try updating the form
#         update_data = {
#             'title': 'Updated Form Title',
#         }
#         update_response = self.client.put(reverse('form-detail', args=[form_response.data['id']]), update_data, format='json')
#         self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

#         # Try deleting the form
#         delete_response = self.client.delete(reverse('form-detail', args=[form_response.data['id']]))
#         self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)


# class ProcessTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user', password='password')
#         self.client.force_authenticate(user=self.user)  

#     def test_process_creation(self):
#         """
#         Ensure we can create a process.
#         """
#         form_data = {
#         'name': 'Test Form'
#         }
#         form_response = self.client.post(reverse('form-list'), form_data, format='json')
#         self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)
#         url = reverse('process-list')
#         process_data = {
#             'form': form_response.data['id'] 
#         }
#         response = self.client.post(url, process_data, processat='json')

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Process.objects.count(), 1)
        
#     def test_private_process_require_password(self):
        
#         # Create a private form
#         form_data = {
#             'name': 'Private Test Form',
#             'is_private': True,
#             'password': '1234',
#         }
#         form_response = self.client.post(reverse('form-list'), form_data, format='json')
#         self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)
        
#         process_data = {
#             'form': form_response.data['id'],
#             'is_private': True
#         }
#         process_response = self.client.post(reverse('process-list'), process_data, format='json')
#         self.assertEqual(process_response.status_code, status.HTTP_400_BAD_REQUEST)
 
#     def test_private_process_check_password(self):

#         form_data = {
#             'name': 'Public Form'
#         }
#         form_response = self.client.post(reverse('form-list'), form_data, format='json')
#         self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)

       
#         process_data = {
#             'form': form_response.data['id'],
#             'is_private': True,
#             'password': '1234',
#         }
#         process_response = self.client.post(reverse('process-list'), process_data, format='json')
#         self.assertEqual(process_response.status_code, status.HTTP_201_CREATED)

#         # 2. Try to retrieve the private process without providing a password
#         retrieve_process_url = reverse('process-detail', args=[process_response.data['id']])
#         retrieve_response = self.client.get(retrieve_process_url)
#         self.assertEqual(retrieve_response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertIn('detail', retrieve_response.data)
#         self.assertEqual(retrieve_response.data['detail'], 'This process is private. Please provide a password.')

#         # 3. Try to retrieve the private process with a wrong password
#         retrieve_response_wrong_password = self.client.get(retrieve_process_url, {'password': 'wrong_password'})
#         self.assertEqual(retrieve_response_wrong_password.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertIn('detail', retrieve_response_wrong_password.data)
#         self.assertEqual(retrieve_response_wrong_password.data['detail'], 'Incorrect password. Access denied.')

#         # 4. Retrieve the private process with the correct password
#         retrieve_response_with_password = self.client.get(retrieve_process_url, {'password': '1234'})
#         self.assertEqual(retrieve_response_with_password.status_code, status.HTTP_200_OK)

#         # Ensure that the password is not shown in the response
#         self.assertNotIn('password', retrieve_response_with_password.data)

#     def test_only_creator_can_update_delete_process(self):
#         form_data = {
#             'name': 'Test Form'
#         }
#         form_response = self.client.post(reverse('form-list'), form_data, format='json')
#         self.assertEqual(form_response.status_code, status.HTTP_201_CREATED)

#         process_data = {
#             'form': form_response.data['id']
#         }
#         process_response = self.client.post(reverse('process-list'), process_data, format='json')
#         self.assertEqual(process_response.status_code, status.HTTP_201_CREATED)

#         # Log out and log in as another user
#         self.client.logout()
#         self.user1 = User.objects.create_user(username='user1', password='password1')
#         self.client.force_authenticate(user=self.user1)

#         # Try updating the process
#         update_data = {
#             'name': 'Updated Process Name',
#         }
#         update_response = self.client.put(reverse('process-detail', args=[process_response.data['id']]), update_data, format='json')
#         self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)

#         # Try deleting the process
#         delete_response = self.client.delete(reverse('process-detail', args=[process_response.data['id']]))
#         self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        

# class QuestionTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user', password='pass')
#         self.client.force_authenticate(user=self.user) 

        
#         self.other_user = User.objects.create_user(username='otheruser', password='pass1')

#         self.form = Form.objects.create(name='Test Form', user=self.user, is_private=False)

#         self.process = Process.objects.create(form=self.form, order=1, user=self.user)

#     def test_question_creation(self):
#             """Ensure a question can be created"""
#             question_data = {
#                 'form': self.form.id,
#                 'process': self.process.id,
#                 'order': 1,
#                 'text': 'What is your name?',
#                 'type': 1
#             }
#             response = self.client.post(reverse('question-list'), question_data, format='json')
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertEqual(Question.objects.count(), 1)   


#     def test_unique_order_form_process_combination(self):
#         """Ensure the combination of order, form, and process is unique"""
#         Question.objects.create(form=self.form, process=self.process, order=1, text="First question", type=1, user=self.user)

#         question_data = {
#             'form': self.form.id,
#             'process': self.process.id,
#             'order': 1,  # Same order
#             'text': 'other question',
#             'type': 1
#         }
#         response = self.client.post(reverse('question-list'), question_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         self.assertEqual(response.data[0], 'The combination of form, process and order must be unique.')         


#     def test_only_creator_can_create_question(self):
#         """Ensure only the creator of the process can create questions for it"""
#         self.client.logout()
#         self.client.login(username='otheruser', password='pass1')

#         question_data = {
#             'form': self.form.id,
#             'process': self.process.id,
#             'order': 5,
#             'text': 'question by other user',
#             'type': 1
#         }
#         response = self.client.post(reverse('question-list'), question_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data[0], 'You do not have permission to add questions to this process.')    


# class CategoryTests(APITestCase):
#     def setUp(self):


#         # Create an admin user and a regular user
#         self.admin_user = User.objects.create_superuser(  
#             username='admin_user',  
#             email='admin@example.com',  
#             password='admin_pass'  
#         )  
#         self.normal_user = User.objects.create_user(
#             username='normal_user', password='normal_pass'
#         )

#         # Admin logs in
#         self.client.force_authenticate(user=self.admin_user) 

#     def test_admin_can_create_public_category(self):
#         """Test that an admin can create a public category"""
#         data = {
#             'name': 'Public Category', 
#             }
#         response = self.client.post(reverse('public-category-list'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         category = Category.objects.get(name='Public Category')
#         self.assertEqual(category.user, None)

#     def test_normal_user_creates_exclusive_category(self):
#         """Test that a normal user can create an exclusive category"""
#         self.client.logout()
#         self.client.force_authenticate(self.normal_user)

#         data = {'name': 'Exclusive Category', 'user': self.normal_user.id}
#         response = self.client.post(reverse('exclusive-category-list'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         category = Category.objects.get(name='Exclusive Category')
#         self.assertEqual(category.user, self.normal_user)

#     def test_normal_user_cannot_create_public_category(self):
#         """Test that a normal user cannot create a public category"""
#         self.client.logout()
#         self.client.force_authenticate(self.normal_user)

#         data = {'name': 'Invalid Public Category', 'user': None}
#         response = self.client.post(reverse('public-category-list'), data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_admin_can_retrieve_public_categories(self):
#         """Test that an admin can retrieve public categories"""
#         Category.objects.create(name='Public Category 1', user=None)
#         Category.objects.create(name='Public Category 2', user=None)

#         response = self.client.get(reverse('public-category-list'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)

#     def test_normal_user_can_retrieve_public_categories(self):
#         """Test that a normal user can retrieve public categories"""
#         self.client.logout()
#         self.client.login(username='normal_user', password='normal_pass')

#         Category.objects.create(name='Public Category 1', user=None)
#         Category.objects.create(name='Public Category 2', user=None)

#         response = self.client.get(reverse('public-category-list'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)

#     def test_normal_user_can_retrieve_exclusive_categories(self):
#         """Test that a normal user can retrieve their exclusive categories"""
#         self.client.logout()
#         self.client.force_authenticate(self.normal_user)

#         Category.objects.create(name='Exclusive Category 1', user=self.normal_user)
#         Category.objects.create(name='Exclusive Category 2', user=self.normal_user)

#         response = self.client.get(reverse('exclusive-category-list'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)

#     def test_admin_cannot_retrieve_exclusive_categories_of_others(self):
#         """Test that an admin cannot retrieve exclusive categories of normal users"""
#         Category.objects.create(name='Exclusive Category 1', user=self.normal_user)
#         Category.objects.create(name='Exclusive Category 2', user=self.normal_user)

#         response = self.client.get(reverse('exclusive-category-list'))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)

# class AnswerTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='testuser@example.com',
#             password='TestPassword123'
#         )
#         self.client.login(username='testuser', password='TestPassword123')
        
#         self.form = Form.objects.create(user=self.user, name='Sample Form')
#         self.question = Question.objects.create(
#             form=self.form, process=None, text='Sample Question', type=2, required=True
#         )
#         self.option1 = Option.objects.create(question=self.question, text='Option 1')
#         self.option2 = Option.objects.create(question=self.question, text='Option 2')
    
#     def test_submit_answer(self):
#         url = reverse('answer-submit-list')
#         data = {
#             'question': self.question.id,
#             'select': [self.option1.id],
#             'text': 'Sample answer text'
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Answer.objects.count(), 1)
#         self.assertEqual(Answer.objects.first().text, 'Sample answer text')
#     def test_get_answers(self):
#         # Submit an answer first
#         Answer.objects.create(
#             question=self.question,
#             user=self.user,
#             text='Sample answer text'
#         )
#         url = reverse('answer-submit-list') + f'?question_id={self.question.id}'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]['text'], 'Sample answer text')


# User = get_user_model()

# @pytest.mark.django_db
# def test_start_form(client):
#     # Set up test data
#     user = User.objects.create_user(username='testuser', password='password')
#     form = Form.objects.create(user=user, name='Test Form')
#     process = Process.objects.create(user=user, linear=False, order=1)
#     process.form.add(form)
#     question1 = Question.objects.create(
#         user=user,
#         process=process,
#         text="What's your name?",
#         type=1,  # Text question type
#         order=1,
#         required=True
#     )
#     question2 = Question.objects.create(
#         user=user,
#         process=process,
#         text="How old are you?",
#         type=1,  # Text question type
#         order=2,
#         required=True
#     )

#     # Perform the GraphQL query
#     response = graphql_query(
#         '''
#         mutation {
#             startForm(formId: "1") {
#                 processes {
#                     id
#                     name
#                     type
#                     questions {
#                         id
#                         text
#                     }
#                 }
#                 question {
#                     id
#                     text
#                 }
#             }
#         }
#         ''',
#         client=client,
#         user=user,
#     )

#     # Assert the response
#     content = response.json()
#     assert 'data' in content
#     assert 'startForm' in content['data']
#     assert 'processes' in content['data']['startForm']

# @pytest.mark.django_db
# def test_record_answer(client):
#     # Set up test data
#     user = User.objects.create_user(username='testuser', password='password')
#     form = Form.objects.create(user=user, name='Test Form')
#     process = Process.objects.create(user=user, linear=True, order=1)
#     process.form.add(form)
#     question = Question.objects.create(
#         user=user,
#         process=process,
#         text="What's your name?",
#         type=1,  # Text question type
#         order=1,
#         required=True
#     )

#     # Perform the GraphQL mutation
#     response = graphql_query(
#         '''
#         mutation {
#             recordAnswer(questionId: "1", answerText: "John Doe") {
#                 success
#             }
#         }
#         ''',
#         client=client,
#         user=user,
#     )

#     # Assert the response
#     content = response.json()
#     assert 'data' in content
#     assert content['data']['recordAnswer']['success'] is True
