import matplotlib.pyplot as plt
from collections import Counter
from db import get_clients, get_orders
from datetime import datetime
import networkx as nx


def top_clients_by_orders():
    """
    Определяет топ-5 клиентов по числу заказов.

    Returns
    -------
    list of tuple
        Список из 5 кортежей вида (имя_клиента, количество_заказов).
    """
    orders = get_orders()
    client_names = [row[1] for row in orders]  # row[1] — имя клиента
    counter = Counter(client_names)
    top5 = counter.most_common(5)
    print("Топ 5 клиентов по числу заказов:")
    for i, (name, count) in enumerate(top5, 1):
        print(f"{i}. {name} — {count} заказов")
    return top5


def plot_orders_over_time():
    """
    Строит график динамики заказов по датам.

    Returns
    -------
    None
        Функция отображает график, но не возвращает значения.
    """
    orders = get_orders()
    dates = [datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S").date() for row in orders]  # row[2] — дата
    counter = Counter(dates)
    sorted_dates = sorted(counter.items())
    x = [d[0] for d in sorted_dates]
    y = [d[1] for d in sorted_dates]

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker="o")
    plt.title("Динамика количества заказов по датам")
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def top_products():
    """
    Определяет топ-5 наиболее часто заказываемых товаров.

    Returns
    -------
    list of tuple
        Список из 5 кортежей вида (название_товара, количество_заказов).
    """
    orders = get_orders()
    product_list = []
    for row in orders:
        products_text = row[3]  # row[3] — "Ноутбук:75000, Мышь:1500"
        products = [p.split(":")[0] for p in products_text.split(", ")]
        product_list.extend(products)
    counter = Counter(product_list)
    top5 = counter.most_common(5)
    print("Топ 5 товаров по количеству заказов:")
    for i, (name, count) in enumerate(top5, 1):
        print(f"{i}. {name} — {count} раз")
    return top5


def client_graph():
    """
    Строит граф связей клиентов по общим товарам.

    Returns
    -------
    None
        Функция отображает граф, но не возвращает значения.
    """
    orders = get_orders()
    product_to_clients = {}
    for row in orders:
        client_name = row[1]
        products_text = row[3]
        products = [p.split(":")[0] for p in products_text.split(", ")]
        for p in products:
            if p not in product_to_clients:
                product_to_clients[p] = set()
            product_to_clients[p].add(client_name)

    G = nx.Graph()
    for clients in product_to_clients.values():
        clients = list(clients)
        for i in range(len(clients)):
            for j in range(i + 1, len(clients)):
                G.add_edge(clients[i], clients[j])

    plt.figure(figsize=(8, 8))
    nx.draw(G, with_labels=True, node_color='skyblue', edge_color='gray', node_size=2000, font_size=10)
    plt.title("Граф связей клиентов по общим товарам")
    plt.show()
