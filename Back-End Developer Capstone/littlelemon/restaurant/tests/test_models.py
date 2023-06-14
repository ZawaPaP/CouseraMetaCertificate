from django.test import TestCase
from ..models import Menu

class MenuTest(TestCase):
    def test_menu_representation(self):
        # Create a new instance of the Menu model
        menu = Menu.objects.create(title='Pizza', price=9.99, inventory=10)

        # Compare the string representation of the menu object with the anticipated value
        self.assertEqual(str(menu), 'Pizza : 9.99')