from PyQt6.QtWidgets import *
from cartWindow import CartWindow
from PyQt6.QtGui import *


class ShopWindow(QMainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.setWindowTitle("Витрина")
        self.setGeometry(100, 100, 800, 600)
        self.user_id = user_id
        self.db = db
        self.cart_window = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Cart button
        cart_action = QAction('Открыть корзину', self)
        cart_action.triggered.connect(self.show_cart)
        toolbar.addAction(cart_action)

        # Input fields
        input_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Наименование")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Цена")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Количество")
        self.add_to_cart_btn = QPushButton('Положить в корзину')
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.price_input)
        input_layout.addWidget(self.quantity_input)
        input_layout.addWidget(self.add_to_cart_btn)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Добавить товар")
        add_button.clicked.connect(self.add_product)

        update_button = QPushButton("Обновить товар")
        update_button.clicked.connect(self.update_product)

        delete_button = QPushButton("Удалить товар")
        delete_button.clicked.connect(self.delete_product)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Наименование", "Цена", "Количество"])
        self.table.clicked.connect(self.table_clicked)

        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        self.load_products()

    def load_products(self):
        self.db.connect_to_db()
        self.db.cursor.execute("SELECT * FROM products")
        products = self.db.cursor.fetchall()
        self.db.close_connection()

        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_product(self):
        self.db.connect_to_db()
        try:
            name = self.name_input.text()
            price = float(self.price_input.text())
            quantity = int(self.quantity_input.text())
            if (price > 0 and quantity > 0):
                self.db.cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                                       (name, price, quantity))
                self.db.conn.commit()

                self.load_products()
                self.clear_inputs()
            else:
                QMessageBox.warning(self, "Error", "Пожалуйста, введите корректные значения")
        except ValueError:
            QMessageBox.warning(self, "Error", "Пожалуйста, введите корректные значения")
        self.db.close_connection()

    def update_product(self):
        self.db.connect_to_db()
        try:
            selected_row = self.table.currentRow()
            if selected_row >= 0:
                product_id = int(self.table.item(selected_row, 0).text())
                name = self.name_input.text()
                price = float(self.price_input.text())
                quantity = int(self.quantity_input.text())
                if (price > 0 and quantity > 0 ):
                    self.db.cursor.execute("""
                        UPDATE products 
                        SET name=?, price=?, quantity=?
                        WHERE id=?
                    """, (name, price, quantity, product_id))
                    self.db.conn.commit()

                    self.load_products()
                    self.clear_inputs()
                else:
                    QMessageBox.warning(self, "Error", "Пожалуйста, введите корректные значения")
        except ValueError:
            QMessageBox.warning(self, "Error", "Пожалуйста, введите корректные значения")
        self.db.close_connection()

    def delete_product(self):
        self.db.connect_to_db()
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            product_id = int(self.table.item(selected_row, 0).text())

            self.db.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.db.conn.commit()

            self.load_products()
            self.clear_inputs()

        self.db.close_connection()

    def show_cart(self):
        self.cart_window = CartWindow(self.db, self.user_id, self)
        self.cart_window.show()

    def add_to_cart(self):
        self.db.connect_to_db()
        selected_row = self.table.currentRow()

        if selected_row >= 0:
            product_id = int(self.table.item(selected_row, 0).text())

            # Проверяем текущее количество товара в корзине пользователя
            self.db.cursor.execute('''SELECT c.quantity 
                                 FROM cart c
                                 LEFT JOIN products p ON p.id = c.product_id
                                 WHERE c.user_id = ? AND c.product_id = ?''', (self.user_id, product_id))
            cart_quantity = self.db.cursor.fetchone()

            self.db.cursor.execute('SELECT quantity FROM products WHERE id = ' + str(product_id))
            product_quantity = self.db.cursor.fetchone()

            try:
                if cart_quantity[0] < product_quantity[0]:
                    self.db.cursor.execute(f'''UPDATE cart 
                                                SET quantity = quantity + 1
                                                WHERE product_id = {product_id}''')
                    self.db.conn.commit()

                    QMessageBox.information(self, 'Success', 'Товар добавлен в корзину!')
                else:
                    QMessageBox.information(self, 'Error',
                                            'Достигнуто максисмальное количество товара в корзине')
            except TypeError:
                if cart_quantity is None:
                    self.db.cursor.execute('''INSERT INTO cart (user_id, product_id, quantity)
                                                                    VALUES (?, ?, 1)''', (self.user_id, product_id))
                    self.db.conn.commit()

                    QMessageBox.information(self, 'Success', 'Товар добавлен в корзину!')
                else:
                    QMessageBox.information(self, 'Error', 'Возникла ошибка')
            self.load_products()
            self.clear_inputs()

        self.db.close_connection()

    def table_clicked(self):
        selected_row = self.table.currentRow()
        self.name_input.setText(self.table.item(selected_row, 1).text())
        self.price_input.setText(self.table.item(selected_row, 2).text())
        self.quantity_input.setText(self.table.item(selected_row, 3).text())

    def clear_inputs(self):
        self.name_input.clear()
        self.price_input.clear()
        self.quantity_input.clear()
