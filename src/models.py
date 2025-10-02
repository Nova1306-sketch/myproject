"""
models.py
=========

Модуль содержит классы предметной области:
- Person (базовый класс для человека)
- Client (клиент с контактными данными и заказами)
- Product (товар)
- Order (заказ клиента)

Все классы используют объектно-ориентированный подход с инкапсуляцией,
наследованием и полиморфизмом.
"""

from __future__ import annotations
from datetime import datetime
import re
from typing import List


class Person:
    """
    Базовый класс для человека.

    Parameters
    ----------
    name : str
        Имя человека
    email : str
        Email
    phone : str
        Телефон
    """

    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone

    def is_valid_email(self) -> bool:
        """
        Проверка корректности email.

        Returns
        -------
        bool
            True, если email корректный, иначе False.
        """
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.email) is not None

    def is_valid_phone(self) -> bool:
        """
        Проверка корректности телефона.

        Returns
        -------
        bool
            True, если телефон корректный, иначе False.
        """
        return re.match(r"^\+?\d{7,15}$", self.phone) is not None

    def __str__(self) -> str:
        return f"{self.name} ({self.email}, {self.phone})"


class Client(Person):
    """
    Класс клиента с адресом и заказами.

    Parameters
    ----------
    name : str
        Имя клиента
    email : str
        Email клиента
    phone : str
        Телефон клиента
    address : str
        Адрес клиента

    Attributes
    ----------
    orders : list of Order
        Список заказов клиента
    """

    def __init__(self, name: str, email: str, phone: str, address: str):
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            raise ValueError(f"Неверный email: {email}")
        if not re.match(r"^\+?\d{7,15}$", phone):
            raise ValueError(f"Неверный телефон: {phone}")
        super().__init__(name, email, phone)
        self.address = address
        self.orders: List[Order] = []

    def add_order(self, order: Order) -> None:
        """
        Добавление заказа клиенту.

        Parameters
        ----------
        order : Order
            Объект заказа
        """
        self.orders.append(order)

    def total_spent(self) -> float:
        """
        Общая сумма всех заказов клиента.

        Returns
        -------
        float
            Сумма всех заказов
        """
        return sum(order.total_price for order in self.orders)

    def __str__(self) -> str:
        return f"Client: {self.name}, Orders: {len(self.orders)}"


class Product:
    """
    Класс товара.

    Parameters
    ----------
    name : str
        Название товара
    price : float
        Цена товара
    category : str
        Категория товара
    """

    def __init__(self, name: str, price: float, category: str):
        self.name = name
        self.price = price
        self.category = category

    def __str__(self) -> str:
        return f"Product: {self.name} ({self.category}) - {self.price:.2f} руб."


class Order:
    """
    Класс заказа клиента.

    Parameters
    ----------
    client : Client
        Клиент, сделавший заказ
    products : list of Product
        Список товаров в заказе
    order_date : datetime, optional
        Дата заказа (по умолчанию текущая)
    """

    def __init__(self, client: Client, products: List[Product], order_date: datetime = None):
        self.client = client
        self.products = products
        self.order_date = order_date or datetime.now()
        client.add_order(self)

    @property
    def total_price(self) -> float:
        """
        Общая стоимость заказа.

        Returns
        -------
        float
            Сумма всех товаров в заказе
        """
        return sum(p.price for p in self.products)

    def __str__(self) -> str:
        product_list = ", ".join(p.name for p in self.products)
        return (f"Order for {self.client.name} on {self.order_date.date()} "
                f"({len(self.products)} items: {product_list}) "
                f"Total: {self.total_price:.2f} руб.")
