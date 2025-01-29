from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .responce_data import * 
User = get_user_model()

class AuthTests(APITestCase):
    def __init__(self, *args, **kwargs):
        self.data = [
            {"email_or_phone": "+995579008787"},
            {"password": "TestPass123!"},
            {"password2": "TestPass123!"},
            {"email_or_phone": "testuser@user.com"},
            {"email_or_phone": "testuseruser.com"},
            {"email_or_phone": "995579008787"},
            {"password2": "TestPass13!"},
            ]
        super(AuthTests, self).__init__(*args, **kwargs)
    
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
        

    def test_registration_with_no_information(self):
        """Test that a user cannot register without providing any information."""
        data = {}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, no_data_registration)

    def test_registration_with_only_email(self):
        """Test that a user cannot register with only email address."""
        data = {**self.data[3]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, only_email_provided_registration)

    def test_registration_with_only_email_and_password(self):
        """Test that a user cannot register with only email and one password."""
        data = {**self.data[3], **self.data[1]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, only_email_and_password_provided_registration)
    
    def test_registration_with_only_email_and_password2(self):
        """Test that a user cannot register with only email and one password2."""
        data = {**self.data[3], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, only_email_and_password2_provided_registration)
    
    def test_registration_with_only_passwords(self):
        """Test that a user cannot register with only passwords."""
        data = {**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, only_passwords_provided_registration)

    def test_registration_with_Phone(self):
        """Test that a user can register with an phone number."""
        data = {**self.data[0],**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(email_or_phone=data["email_or_phone"]).exists()
        self.assertTrue(user_exists, "User was not created in the database.")

    def test_validating_email(self):
        """Test that a user cannot register with an invalid email or phone number."""
        data = {**self.data[4],**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, invalid_email_registration)
    
    def test_validating_phone(self):
        """Test that a user cannot register with an invalid email or phone number."""
        data = {**self.data[5],**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, invalid_email_registration)

    def test_password_missmatch(self):
        """Test that a user cannot register if passwords do not match."""
        data = {**self.data[0],**self.data[1], **self.data[6]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, password_missmatch)

    def test_successful_registration_with_phone(self):
        """Test that a user can register successfully with phone."""
        data = {**self.data[0],**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(email_or_phone=data["email_or_phone"]).exists()
        self.assertTrue(user_exists, "User was not created in the database.")

    def test_successful_registration_with_email(self):
        """Test that a user can register successfully with email."""
        data = {**self.data[3],**self.data[1], **self.data[2]}
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(email_or_phone=data["email_or_phone"]).exists()
        self.assertTrue(user_exists, "User was not created in the database.")