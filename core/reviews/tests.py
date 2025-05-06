from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from consumers.models import Consumer
from merchants.models import Merchant
from offers.models import Offer
from orders.models import Order
from .models import Review
import datetime

User = get_user_model()

class ReviewAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='marjestro',
            email='admin@example.com',
            password='adminpass',
            first_name='Admin',
            last_name='User',
            role='administrator'
        )
        self.merchant_user = User.objects.create_user(
            username='marjestromerchant',
            email='merchant@example.com',
            password='merchantpass',
            first_name='Merchant',
            last_name='User',
            role='merchant'
        )
        self.consumer_user = User.objects.create_user(
            username='marjestromconsumer',
            email='consumer@example.com',
            password='consumerpass',
            first_name='Consumer',
            last_name='User',
            role='consumer'
        )
        self.other_consumer_user = User.objects.create_user(
            username='marjestrootherconsumer',
            email='otherconsumer@example.com',
            password='otherpass',
            first_name='Other',
            last_name='Consumer',
            role='consumer'
        )

        # Create related models with all required fields
        self.merchant = Merchant.objects.create(
            user=self.merchant_user,
            business_name="Test Merchant",
            business_type="Restaurant",
            address="123 Test St",
            description="Test description",
            phone="1234567890",
            pickup_hours="9-5",
            is_verified=True
        )
        
        self.consumer = Consumer.objects.create(
            user=self.consumer_user,
            delivery_address="456 Consumer Ave",
            food_preferences="Vegetarian",
            purchase_history=""
        )
        
        self.other_consumer = Consumer.objects.create(
            user=self.other_consumer_user,
            delivery_address="789 Other St",
            food_preferences="Vegan",
            purchase_history=""
        )

        # Create test offers with all required fields
        today = datetime.date.today()
        self.offer1 = Offer.objects.create(
            merchant=self.merchant,
            title="Test Offer 1",
            description="Description 1",
            price=10.00,
            available_quantity=100,
            start_date=today,
            end_date=today + datetime.timedelta(days=7),
            status='available'
        )
        self.offer2 = Offer.objects.create(
            merchant=self.merchant,
            title="Test Offer 2",
            description="Description 2",
            price=20.00,
            available_quantity=50,
            start_date=today,
            end_date=today + datetime.timedelta(days=7),
            status='available'
        )

        # Create test orders
        self.order1 = Order.objects.create(
            consumer=self.consumer,
            offer=self.offer1,
            quantity=2,
            total_price=20.00,
            status='completed'
        )
        self.order2 = Order.objects.create(
            consumer=self.consumer,
            offer=self.offer2,
            quantity=3,
            total_price=60.00,
            status='completed'
        )
        self.order3 = Order.objects.create(
            consumer=self.other_consumer,
            offer=self.offer1,
            quantity=1,
            total_price=10.00,
            status='completed'
        )

        # Create test reviews
        self.review1 = Review.objects.create(
            order=self.order1,
            rating=5,
            comment='Excellent service'
        )
        self.review2 = Review.objects.create(
            order=self.order2,
            rating=3,
            comment='Average experience'
        )
        self.review3 = Review.objects.create(
            order=self.order3,
            rating=4,
            comment='Good overall'
        )

        # API client
        self.client = APIClient()

    # Update the filtering tests to use user_id instead of id
    def test_filter_reviews_by_merchant(self):
        """Test filtering reviews by merchant"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('review_list_create')
        response = self.client.get(url, {'merchant': self.merchant.user_id})  # Use user_id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)

    def test_filter_reviews_by_consumer(self):
        """Test filtering reviews by consumer"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('review_list_create')
        response = self.client.get(url, {'consumer': self.consumer.user_id})  # Use user_id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

    # Update the permission tests to check the correct status codes
    def test_cannot_create_review_for_pending_order(self):
        """Test that reviews can't be created for non-completed orders"""
        pending_order = Order.objects.create(
            consumer=self.consumer,
            offer=self.offer1,
            quantity=1,
            total_price=10.00,
            status='pending'
        )
        
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_list_create')
        data = {
            'order': pending_order.id,
            'rating': 4,
            'comment': 'Should fail'
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_consumer_can_see_own_reviews(self):
        """Test that consumers can see their own reviews"""
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_list_reviews_unauthenticated(self):
        """Test that unauthenticated users cannot list reviews"""
        url = reverse('review_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reviews_authenticated(self):
        """Test that authenticated users can list reviews"""
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)

    # Review Creation Tests
    def test_create_review_for_own_order(self):
        """Test that consumer can create review for their own completed order"""
        # Create a new completed order for the consumer
        new_order = Order.objects.create(
            consumer=self.consumer,
            offer=self.offer1,
            quantity=1,
            total_price=10.00,
            status='completed'
        )
        
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_list_create')
        data = {
            'order': new_order.id,
            'rating': 4,
            'comment': 'New review'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(Review.objects.count(), 4)

    def test_cannot_create_review_for_pending_order(self):
        """Test that reviews can't be created for non-completed orders"""
        pending_order = Order.objects.create(
            consumer=self.consumer,
            offer=self.offer1,
            quantity=1,
            total_price=10.00,
            status='pending'
        )
        
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_list_create')
        data = {
            'order': pending_order.id,
            'rating': 4,
            'comment': 'Should fail'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_cannot_create_review_for_other_users_order(self):
        """Test that users can't create reviews for orders that aren't theirs"""
        self.client.force_authenticate(user=self.other_consumer_user)
        url = reverse('review_list_create')
        data = {
            'order': self.order1.id,  # order1 belongs to consumer_user
            'rating': 1,
            'comment': 'Malicious review'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Review Permissions Tests
    def test_merchant_cannot_create_review(self):
        """Test that merchants can't create reviews"""
        self.client.force_authenticate(user=self.merchant_user)
        url = reverse('review_list_create')
        data = {
            'order': self.order1.id,
            'rating': 4,
            'comment': 'Merchant review attempt'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_review_for_any_order(self):
        """Test that admin can create reviews for any order"""
        new_order = Order.objects.create(
            consumer=self.other_consumer,
            offer=self.offer1,
            quantity=1,
            total_price=10.00,
            status='completed'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('review_list_create')
        data = {
            'order': new_order.id,
            'rating': 2,
            'comment': 'Admin review'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    # Review Retrieval Tests
    def test_consumer_can_see_own_reviews(self):
        """Test that consumers can see their own reviews"""
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.review1.id)

    def test_consumer_cannot_see_other_users_reviews(self):
        """Test that consumers can't see other users' reviews"""
        self.client.force_authenticate(user=self.other_consumer_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_merchant_can_see_reviews_for_their_offers(self):
        """Test that merchants can see reviews for their offers"""
        self.client.force_authenticate(user=self.merchant_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.review1.id)

    # Review Update/Delete Tests
    def test_consumer_can_update_own_review(self):
        """Test that consumers can update their own reviews"""
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        data = {
            'rating': 2,
            'comment': 'Updated review'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review1.refresh_from_db()
        self.assertEqual(self.review1.rating, 2)
        self.assertEqual(self.review1.comment, 'Updated review')

    def test_consumer_cannot_update_other_users_reviews(self):
        """Test that consumers can't update other users' reviews"""
        self.client.force_authenticate(user=self.other_consumer_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        data = {
            'rating': 1,
            'comment': 'Malicious update'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_merchant_cannot_update_reviews(self):
        """Test that merchants can't update reviews"""
        self.client.force_authenticate(user=self.merchant_user)
        url = reverse('review_detail', kwargs={'pk': self.review1.id})
        data = {
            'rating': 1,
            'comment': 'Merchant update attempt'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Order-Specific Review Tests
    def test_get_review_for_own_order(self):
        """Test that consumers can get reviews for their own orders"""
        self.client.force_authenticate(user=self.consumer_user)
        url = reverse('order_review', kwargs={'order_id': self.order1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.review1.id)

    def test_get_review_for_other_users_order(self):
        """Test that consumers can't get reviews for other users' orders"""
        self.client.force_authenticate(user=self.other_consumer_user)
        url = reverse('order_review', kwargs={'order_id': self.order1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_merchant_can_get_review_for_their_offer_order(self):
        """Test that merchants can get reviews for orders of their offers"""
        self.client.force_authenticate(user=self.merchant_user)
        url = reverse('order_review', kwargs={'order_id': self.order1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.review1.id)

