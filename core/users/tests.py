from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import json

class UserTests(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            role='administrator'
        )
        
        self.merchant_user = User.objects.create_user(
            email='merchant@example.com',
            username='merchant',
            password='merchantpass123',
            role='merchant'
        )
        
        self.consumer_user = User.objects.create_user(
            email='consumer@example.com',
            username='consumer',
            password='consumerpass123',
            role='consumer'
        )
        
        # URLs
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_list_url = reverse('all-users')
        self.token_refresh_url = reverse('token_refresh')
        
    def test_register_user_success(self):
        """
        Ensure we can register a new user with valid data.
        """
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'role': 'consumer',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'User created successfully')
        self.assertEqual(User.objects.count(), 4)  # 3 from setUp + 1 new
        
    def test_register_user_invalid_data(self):
        """
        Ensure registration fails with invalid data.
        """
        # Missing required field (password)
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'role': 'consumer'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'User registration failed')
        self.assertIn('password', response.data['errors'])
        
    def test_register_duplicate_email(self):
        """
        Ensure registration fails with duplicate email.
        """
        data = {
            'email': 'consumer@example.com',  # Already exists
            'username': 'newuser',
            'password': 'testpass123',
            'role': 'consumer'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['errors'])
        
    def test_login_success(self):
        """
        Ensure users can login with valid credentials.
        """
        data = {
            'email': 'consumer@example.com',
            'password': 'consumerpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        
    def test_login_invalid_credentials(self):
        """
        Ensure login fails with invalid credentials.
        """
        # Wrong password
        data = {
            'email': 'consumer@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Login failed')
        
    def test_token_refresh(self):
        """
        Ensure token refresh works with valid refresh token.
        """
        # First login to get tokens
        login_data = {
            'email': 'consumer@example.com',
            'password': 'consumerpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['data']['refresh']
        
        # Then refresh
        refresh_data = {
            'refresh': refresh_token
        }
        refresh_response = self.client.post(self.token_refresh_url, refresh_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        
    def test_user_list_authenticated(self):
        """
        Ensure authenticated users can access the user list.
        """
        # First login
        login_data = {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Then access user list with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)  # 3 users from setUp
        
    def test_user_list_unauthenticated(self):
        """
        Ensure unauthenticated users cannot access the user list.
        """
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_detail_retrieve(self):
        """
        Ensure authenticated users can retrieve user details.
        """
        # First login
        login_data = {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Then access user detail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.consumer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'consumer@example.com')
        
    def test_user_detail_update(self):
        """
        Ensure users can update their own details.
        """
        # First login
        login_data = {
            'email': 'merchant@example.com',
            'password': 'merchantpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Then update user detail
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.merchant_user.id})
        update_data = {
            'username': 'Updated',
            'email': self.merchant_user.email,  # Include original email
            'role': self.merchant_user.role    # Include original role
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'User updated successfully')
        
        # Verify update
        updated_user = User.objects.get(id=self.merchant_user.id)
        self.assertEqual(updated_user.username, 'Updated')

        # Test PATCH (partial update)
        patch_data = {
            'username': 'PartiallyUpdated'
        }
        response = self.client.patch(url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify partial update
        updated_user.refresh_from_db()
        self.assertEqual(updated_user.username, 'PartiallyUpdated')
        self.assertEqual(updated_user.email, 'merchant@example.com')
        
    def test_user_can_delete_own_account(self):
        """
        Ensure users can delete their own accounts.
        """
        # First login as merchant
        login_data = {
            'email': 'merchant@example.com',
            'password': 'merchantpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Then delete own account
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.merchant_user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(response.data['success'])
        
      
    def test_user_profile_picture_upload(self):
        # Login first
        login_response = self.client.post(self.login_url, {
            'email': self.merchant_user.email,
            'password': 'merchantpass123'
        }, format='json')
        access_token = login_response.data['data']['access']
        
        # Prepare test image
        test_image = SimpleUploadedFile(
            "test.jpg", 
            b"file_content", 
            content_type="image/jpeg"
        )
        
        # Make request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.merchant_user.id})
        response = self.client.patch(url, {'profile_picture': test_image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_role_based_access_control(self):
        """
        Ensure role-based access control works as expected.
        """
        # Test consumer trying to access another user's data
        login_data = {
            'email': 'consumer@example.com',
            'password': 'consumerpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Try to update another user's profile (should fail)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.merchant_user.id})
        update_data = {'address': 'Unauthorized update'}
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_account(self):
        # First login as admin
        login_data = {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Verify admin role
        admin = User.objects.get(email='admin@example.com')
        self.assertEqual(admin.role, 'administrator')  # Add this check
        
        # Then try deletion
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.consumer_user.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(response.data['success'])

    def test_user_cannot_delete_other_users_accounts(self):
        """
        Ensure users cannot delete other users' accounts.
        """
        # First login as consumer
        login_data = {
            'email': 'consumer@example.com',
            'password': 'consumerpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['data']['access']
        
        # Try to delete merchant's account (should fail)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = reverse('user-detail', kwargs={'pk': self.merchant_user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify merchant account still exists
        merchant = User.objects.get(id=self.merchant_user.id)
        self.assertIsNotNone(merchant)