import unittest
from datetime import datetime
from models import Client, Product, Order
from analysis import top_clients_by_orders, top_products
import db

class TestModels(unittest.TestCase):

    def setUp(self):
        """Создание тестовых данных"""
        # Клиенты
        self.client1 = Client("Иван", "ivan@mail.com", "+79001234567", "ул. Ленина, 1")
        self.client2 = Client("Петр", "petr@mail.com", "+79007654321", "ул. Пушкина, 5")
        
        # Товары
        self.product1 = Product("Ноутбук", 75000, "Электроника")
        self.product2 = Product("Мышь", 1500, "Электроника")
        self.product3 = Product("Книга", 500, "Книги")
        
        # Заказы
        self.order1 = Order(self.client1, [self.product1, self.product2])
        self.order2 = Order(self.client1, [self.product3])
        self.order3 = Order(self.client2, [self.product1])
        
        # Добавление в базу (SQLite)
        db.add_client(self.client1)
        db.add_client(self.client2)
        db.add_order(self.order1)
        db.add_order(self.order2)
        db.add_order(self.order3)

    def test_total_spent(self):
        self.assertEqual(self.client1.total_spent(), 75000 + 1500 + 500)
        self.assertEqual(self.client2.total_spent(), 75000)

    def test_order_total_price(self):
        self.assertEqual(self.order1.total_price, 75000 + 1500)
        self.assertEqual(self.order2.total_price, 500)

    def test_client_str(self):
        self.assertIn("Client: Иван", str(self.client1))
        self.assertIn("Orders: 2", str(self.client1))

    def test_product_str(self):
        self.assertEqual(str(self.product1), "Product: Ноутбук (Электроника) - 75000.00 руб.")

class TestAnalysis(unittest.TestCase):

    def test_top_clients_by_orders(self):
        top_clients = top_clients_by_orders()
        self.assertEqual(top_clients[0][0], "Иван")  # Иван сделал больше заказов

    def test_top_products(self):
        top = top_products()
        names = [name for name, count in top]
        self.assertIn("Ноутбук", names)
        self.assertIn("Мышь", names)

if __name__ == "__main__":
    unittest.main()
