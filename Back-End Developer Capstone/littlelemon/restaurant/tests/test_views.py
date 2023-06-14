from rest_framework.test import APITestCase
from restaurant.models import Menu
from restaurant.serializers import MenuSerializer

class MenuViewTest(APITestCase):
    def setUp(self):
        self.menu1 = Menu.objects.create(title='Pizza', price=9.99, inventory=10)
        self.menu2 = Menu.objects.create(title='Burger', price=5.99, inventory=15)
        self.menu3 = Menu.objects.create(title='Salad', price=7.99, inventory=8)

    def test_getall(self):
        response = self.client.get('/restaurant/menu/')
        print(response.data)

        expected_data = MenuSerializer(Menu.objects.all(), many=True).data
        self.assertEqual(response.data, expected_data)