from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        # Optional: Create any initial data you want in the DB before each test
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_details_url = reverse('user-details')
        self.change_details_url = reverse('change-details')
        self.verify_email_url = reverse('verify-email')

        # A sample user (if you want to test login for an existing user)
        self.existing_user = User.objects.create_user(
            email_or_phone='existing@example.com',
            password='SomeStrongP@ssw0rd'
        )

    def test_registration_with_email(self):
        """Test that a user can register with an email address."""
        data = {
            "email_or_phone": "testuser@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!"
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the user is actually created
        user_exists = User.objects.filter(email_or_phone="testuser@example.com").exists()
        self.assertTrue(user_exists, "User was not created in the database.")