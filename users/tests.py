from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            password='password123',
            email='testuser@example.com'
        )

    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')

        self.assertFalse(self.user.image)

    def test_user_str_mathod(self):
        self.assertEqual(str(self.user), 'testuser')
