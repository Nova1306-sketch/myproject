import os
import sqlite3
from datetime import datetime
from models import Client, Product, Order
import csv

DB_NAME = "shop.db"

# ===================== Удаление старой базы =====================
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("Старая база удалена")

# ===================== Инициализация базы =====================
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT
)
""")

cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    order_date TEXT,
    products TEXT,
    FOREIGN KEY(client_id) REFERENCES clients(id)
)
""")

conn.commit()
conn.close()

# ===================== ФУНКЦИИ КЛИЕНТОВ =====================
def add_client(client: Client):
    """
    Добавляет клиента в базу данных.

    Parameters
    ----------
    client : Client
        Экземпляр класса Client с данными о клиенте.

    Returns
    -------
    None
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
                   (client.name, client.email, client.phone, client.address))
    conn.commit()
    conn.close()


def get_clients():
    """
    Получает список всех клиентов из базы.

    Returns
    -------
    list of Client
        Список объектов Client, загруженных из базы данных.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, address FROM clients")
    rows = cursor.fetchall()
    conn.close()
    clients = []
    for row in rows:
        c = Client(row[1], row[2], row[3], row[4])
        c.id = row[0]
        clients.append(c)
    return clients

# ===================== ФУНКЦИИ ЗАКАЗОВ =====================
def add_order(order: Order):
    """
    Добавляет заказ в базу данных.

    Parameters
    ----------
    order : Order
        Экземпляр класса Order с информацией о заказе.

    Returns
    -------
    None
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients WHERE name=?", (order.client.name,))
    client_row = cursor.fetchone()
    if not client_row:
        conn.close()
        return
    client_id = client_row[0]
    products_text = ", ".join([f"{p.name}:{p.price}" for p in order.products])
    cursor.execute("INSERT INTO orders (client_id, order_date, products) VALUES (?, ?, ?)",
                   (client_id, order.order_date.strftime("%Y-%m-%d %H:%M:%S"), products_text))
    conn.commit()
    conn.close()


def get_orders():
    """
    Получает список всех заказов из базы.

    Returns
    -------
    list of tuple
        Список кортежей вида (id, client_name, order_date, products).
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT o.id, c.name, o.order_date, o.products
    FROM orders o
    JOIN clients c ON o.client_id = c.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ===================== ЭКСПОРТ / ИМПОРТ КЛИЕНТОВ =====================
def export_clients():
    """
    Экспортирует клиентов в CSV-файл `clients.csv`.

    Returns
    -------
    None
    """
    clients = get_clients()
    with open("clients.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "phone", "address"])
        for c in clients:
            writer.writerow([c.name, c.email, c.phone, c.address])
    print("Клиенты экспортированы в clients.csv")


def import_clients():
    """
    Импортирует клиентов из CSV-файла `clients.csv`.

    Returns
    -------
    None
    """
    try:
        with open("clients.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c = Client(row["name"], row["email"], row["phone"], row["address"])
                add_client(c)
        print("Клиенты импортированы из clients.csv")
    except FileNotFoundError:
        print("clients.csv не найден")

# ===================== ЭКСПОРТ / ИМПОРТ ЗАКАЗОВ =====================
def export_orders():
    """
    Экспортирует заказы в CSV-файл `orders.csv`.

    Returns
    -------
    None
    """
    orders = get_orders()
    with open("orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["client_name", "order_date", "products"])
        for o in orders:
            writer.writerow([o[1], o[2], o[3]])
    print("Заказы экспортированы в orders.csv")


def import_orders():
    """
    Импортирует заказы из CSV-файла `orders.csv`.

    Returns
    -------
    None
    """
    try:
        with open("orders.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                client_name = row["client_name"]
                order_date = row["order_date"]
                products_text = row["products"]
                client = next((c for c in get_clients() if c.name == client_name), None)
                if not client:
                    continue
                products = []
                for p in products_text.split(","):
                    if ":" not in p:
                        continue
                    name, price = p.split(":")
                    products.append(Product(name.strip(), float(price), "Разное"))
                order = Order(client, products, datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S"))
                add_order(order)
        print("Заказы импортированы из orders.csv")
    except FileNotFoundError:
        print("orders.csv не найден")
