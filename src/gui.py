import tkinter as tk
from tkinter import ttk, messagebox
from models import Client, Product, Order
import db
from analysis import top_clients_by_orders, plot_orders_over_time, top_products, client_graph

def start_gui():
    # ====================== ГЛАВНОЕ ОКНО ======================
    root = tk.Tk()
    root.title("Система учета заказов")
    root.geometry("1000x650")

    tab_control = ttk.Notebook(root)

    # ====================== КЛИЕНТЫ ======================
    clients_tab = ttk.Frame(tab_control)
    tab_control.add(clients_tab, text="Клиенты")

    tk.Label(clients_tab, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
    tk.Label(clients_tab, text="Email:").grid(row=1, column=0, padx=5, pady=5)
    tk.Label(clients_tab, text="Телефон:").grid(row=2, column=0, padx=5, pady=5)
    tk.Label(clients_tab, text="Адрес:").grid(row=3, column=0, padx=5, pady=5)

    name_entry = tk.Entry(clients_tab)
    email_entry = tk.Entry(clients_tab)
    phone_entry = tk.Entry(clients_tab)
    address_entry = tk.Entry(clients_tab)

    name_entry.grid(row=0, column=1, padx=5, pady=5)
    email_entry.grid(row=1, column=1, padx=5, pady=5)
    phone_entry.grid(row=2, column=1, padx=5, pady=5)
    address_entry.grid(row=3, column=1, padx=5, pady=5)

    clients_listbox = tk.Listbox(clients_tab, width=80)
    clients_listbox.grid(row=0, column=2, rowspan=4, padx=10, pady=5)

    def refresh_clients():
        clients_listbox.delete(0, tk.END)
        for c in db.get_clients():
            clients_listbox.insert(tk.END, f"{c.name}, {c.email}, {c.phone}, {c.address}")
        # Обновляем список в Заказах
        clients_combo['values'] = [c.name for c in db.get_clients()]

    def add_client_gui():
        name = name_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()
        address = address_entry.get()
        if not (name and email and phone):
            messagebox.showerror("Ошибка", "Имя, Email и Телефон обязательны")
            return
        c = Client(name, email, phone, address)
        db.add_client(c)
        refresh_clients()
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)

    tk.Button(clients_tab, text="Добавить клиента", command=add_client_gui).grid(row=4, column=0, columnspan=2, pady=10)

    # ====================== ЗАКАЗЫ ======================
    orders_tab = ttk.Frame(tab_control)
    tab_control.add(orders_tab, text="Заказы")

    tk.Label(orders_tab, text="Выбрать клиента:").grid(row=0, column=0, padx=5, pady=5)
    clients_combo = ttk.Combobox(orders_tab, values=[c.name for c in db.get_clients()])
    clients_combo.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(orders_tab, text="Товары (через запятую, цена через ':')").grid(row=1, column=0, padx=5, pady=5)
    products_entry = tk.Entry(orders_tab, width=50)
    products_entry.grid(row=1, column=1, padx=5, pady=5)

    orders_listbox = tk.Listbox(orders_tab, width=100)
    orders_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def calculate_total(products_text: str) -> float:
        try:
            return sum(float(p.split(":")[1].strip()) for p in products_text.split(","))
        except:
            return 0.0

    def refresh_orders(sort_by=None):
        """
        sort_by: None, 'date', 'total'
        """
        orders_listbox.delete(0, tk.END)
        orders = db.get_orders()  # [(id, client_name, order_date, products_text), ...]

        # Добавим total_price для каждого заказа
        orders_with_total = []
        for o in orders:
            total = calculate_total(o[3])
            orders_with_total.append((o[0], o[1], o[2], o[3], total))

        # Сортировка
        if sort_by == 'date':
            orders_with_total.sort(key=lambda x: x[2])
        elif sort_by == 'total':
            orders_with_total.sort(key=lambda x: x[4], reverse=True)

        for o in orders_with_total:
            orders_listbox.insert(tk.END, f"{o[1]} | {o[2]} | {o[3]} | {o[4]:.2f} руб.")

    def add_order_gui():
        client_name = clients_combo.get()
        products_text = products_entry.get()
        if not client_name or not products_text:
            messagebox.showerror("Ошибка", "Выберите клиента и введите товары")
            return
        try:
            products = []
            for p in products_text.split(","):
                if ":" not in p:
                    raise ValueError
                name, price = p.split(":")
                price = float(price.strip())
                products.append(Product(name.strip(), price, ""))

            # Найдем клиента
            client = next((c for c in db.get_clients() if c.name == client_name), None)
            if client is None:
                messagebox.showerror("Ошибка", f"Клиент {client_name} не найден")
                return

            order = Order(client, products)
            db.add_order(order)
            refresh_orders()
            products_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Неправильный формат: 'Товар:цена, ...'")

    # Кнопки сортировки
    tk.Button(orders_tab, text="Сортировать по дате", command=lambda: refresh_orders('date')).grid(row=3, column=0, pady=5)
    tk.Button(orders_tab, text="Сортировать по сумме", command=lambda: refresh_orders('total')).grid(row=3, column=1, pady=5)
    tk.Button(orders_tab, text="Добавить заказ", command=add_order_gui).grid(row=4, column=0, columnspan=2, pady=10)

    # ====================== АНАЛИЗ / ИМПОРТ/ЭКСПОРТ ======================
    import_tab = ttk.Frame(tab_control)
    tab_control.add(import_tab, text="Анализ / Импорт/Экспорт")

    # Квадраты для Топ 5
    top_clients_box = tk.Listbox(import_tab, width=50, height=10)
    top_clients_box.pack(padx=10, pady=5)
    top_products_box = tk.Listbox(import_tab, width=50, height=10)
    top_products_box.pack(padx=10, pady=5)

    def show_top_clients():
        top_clients_box.delete(0, tk.END)
        for i, (name, count) in enumerate(top_clients_by_orders(), 1):
            top_clients_box.insert(tk.END, f"{i}. {name} — {count} заказов")

    def show_top_products():
        top_products_box.delete(0, tk.END)
        for i, (name, count) in enumerate(top_products(), 1):
            top_products_box.insert(tk.END, f"{i}. {name} — {count} раз")

    tk.Button(import_tab, text="Показать Топ 5 клиентов", command=show_top_clients).pack(pady=5)
    tk.Button(import_tab, text="Показать Топ 5 товаров", command=show_top_products).pack(pady=5)
    tk.Button(import_tab, text="График динамики заказов (сайт)", command=plot_orders_over_time).pack(pady=5)
    tk.Button(import_tab, text="Граф связей клиентов (сайт)", command=client_graph).pack(pady=5)
    tk.Button(import_tab, text="Экспорт клиентов в CSV", command=db.export_clients).pack(pady=5)
    tk.Button(import_tab, text="Импорт клиентов из CSV", command=lambda: [db.import_clients(), refresh_clients()]).pack(pady=5)
    tk.Button(import_tab, text="Экспорт заказов в CSV", command=db.export_orders).pack(pady=5)
    tk.Button(import_tab, text="Импорт заказов из CSV", command=lambda: [db.import_orders(), refresh_orders()]).pack(pady=5)

    tab_control.pack(expand=1, fill="both")
    refresh_clients()
    refresh_orders()

    root.mainloop()
