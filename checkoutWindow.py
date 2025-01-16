from PyQt6.QtWidgets import *
from message import Message


class CheckoutWindow(QWidget):
    def __init__(self, db, user_id, cart_window, shop_window):
        super().__init__()
        self.address_input = None
        self.email_input = None
        self.username_input = None
        self.db = db
        self.user_id = user_id
        self.init_ui()
        self.status = True
        self.cart_window = cart_window
        self.shop_window = shop_window

    def init_ui(self):
        self.setWindowTitle("Создание заказа")
        self.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ваше имя")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e-mail")
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Адрес")

        submit_btn = QPushButton("Подтвердить заказ")
        submit_btn.clicked.connect(self.submit_order)

        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.address_input)
        layout.addWidget(submit_btn)

        self.setLayout(layout)

    def submit_order(self):
        name = self.username_input.text()
        email = self.email_input.text()
        address = self.address_input.text()
        if not all([name, email, address]):
            QMessageBox.warning(self, 'Error', 'Please fill in all fields')
            return
        else:
            self.create_message(name, email, address)

            self.update_products_quantity()    # Обновляем количества продуктов в Products
            self.shop_window.load_products()   # Обновляем окно с Витриной Products
            self.db.connect_to_db()
            self.db.cursor.execute('DELETE FROM cart WHERE user_id = ?', (self.user_id,))    # Чистим корзину
            self.db.conn.commit()
            self.db.close_connection()

            QMessageBox.information(self, 'Success', 'Order placed successfully!')
            self.close()                       # Закрываем окно с формой

    def create_message(self, username, email, address):
        self.db.connect_to_db()
        self.db.cursor.execute(f'''
                    SELECT c.id, p.name, p.price, c.quantity, (p.price * c.quantity) as total, 
                    p.quantity as stock_qty, p.id as product_id
                    FROM cart c
                    JOIN products p ON c.product_id = p.id
                    WHERE c.user_id = {self.user_id}
                    GROUP BY p.name
                    ''')

        cart_items = self.db.cursor.fetchall()
        self.db.close_connection()

        self.db.connect_to_db()
        self.db.cursor.execute(f'''
                                SELECT SUM(p.price*c.quantity)
                                FROM cart c
                                JOIN products p ON c.product_id = p.id
                                WHERE c.user_id = {self.user_id} 
                                GROUP BY c.user_id
                                ''')

        total_sum = self.db.cursor.fetchall()[0]
        self.db.close_connection()

        tax_string = "<table>"
        for row, item in enumerate(cart_items):
            cart_id, name, price, quantity, total, stock_qty, product_id = item
            tax_string += name.ljust(30, '.') + "х" + str(quantity).ljust(10, '.') + str(total)
            tax_string += "<br>"

        subject = 'Информация по вашему заказу из Пиццерии!'
        body = (f'Добрый день, {username}! <br> '
                f'Ваш заказ был успешно сформирован!<br>'
                f'Адрес для доставки: {address} <br>'
                f'Сумма заказа: {total_sum[0]} <br>'
                f'Ваш выбор: <br>'
                f'{tax_string}')
        to_recip = [email]

        msg = Message(subject=subject, body=body, to_recip=to_recip)

        msg.show()

    def update_products_quantity(self):
        self.db.connect_to_db()
        try:
            self.db.cursor.execute('BEGIN TRANSACTION')
            self.db.cursor.execute(f"""
                    UPDATE products
                    SET quantity = (
                        SELECT products.quantity - cart.quantity
                        FROM cart
                        WHERE cart.product_id = products.id
                        AND cart.user_id = {self.user_id}
                    )
                    WHERE id IN (
                        SELECT product_id 
                        FROM cart 
                        WHERE user_id = {self.user_id}
                    );
                """)

            self.db.conn.commit()

        except Exception as e:
            self.db.conn.rollback()
            raise e

        finally:
            self.db.close_connection()
            self.cart_window.load_cart()
