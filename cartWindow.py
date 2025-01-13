from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from checkoutWindow import CheckoutWindow


class CartWindow(QWidget):
    def __init__(self, db, user_id, shop_window):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.init_ui()
        self.shop_window = shop_window

    def init_ui(self):
        self.setWindowTitle('Корзина')
        self.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout()

        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(['Наименование', 'Цена', 'Количество', 'Итог', ''])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Total amount label
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(self.total_label)

        checkout_btn = QPushButton('Сформировать заказ')
        checkout_btn.clicked.connect(self.show_checkout)

        layout.addWidget(self.cart_table)
        layout.addWidget(total_widget)
        layout.addWidget(checkout_btn)

        self.setLayout(layout)
        self.load_cart()

    def calculate_total(self):
        self.db.connect_to_db()
        self.db.cursor.execute('''
            SELECT SUM(p.price * c.quantity) as total
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (self.user_id,))

        total = self.db.cursor.fetchone()[0]
        self.db.close_connection()
        total = total if total else 0
        self.total_label.setText(f'ИТОГО: {total:.2f}')
        return total

    def load_cart(self):
        self.db.connect_to_db()
        self.db.cursor.execute('''
            SELECT c.id, p.name, p.price, c.quantity, (p.price * c.quantity) as total, 
            p.quantity as stock_qty, p.id as product_id
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
            GROUP BY p.name
        ''', (self.user_id,))

        cart_items = self.db.cursor.fetchall()
        self.db.close_connection()

        self.cart_table.setRowCount(len(cart_items))
        for row, item in enumerate(cart_items):
            cart_id, name, price, quantity, total, stock_qty, product_id = item

            # Name
            self.cart_table.setItem(row, 0, QTableWidgetItem(name))

            # Price
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{price:.2f}"))

            # Quantity
            quantity_widget = QWidget()
            quantity_layout = QHBoxLayout(quantity_widget)
            quantity_layout.setContentsMargins(0, 0, 0, 0)

            decrease_btn = QPushButton("-")
            quantity_label = QLabel(str(quantity))
            increase_btn = QPushButton("+")

            decrease_btn.setFixedWidth(30)
            increase_btn.setFixedWidth(30)

            quantity_layout.addWidget(decrease_btn)
            quantity_layout.addWidget(quantity_label)
            quantity_layout.addWidget(increase_btn)

            # Store references to avoid garbage collection
            quantity_widget.quantity_label = quantity_label
            quantity_widget.cart_id = cart_id
            quantity_widget.product_id = product_id
            quantity_widget.current_quantity = quantity
            quantity_widget.stock_qty = stock_qty

            decrease_btn.clicked.connect(lambda checked, w=quantity_widget: self.decrease_quantity(w))
            increase_btn.clicked.connect(lambda checked, w=quantity_widget: self.increase_quantity(w))

            self.cart_table.setCellWidget(row, 2, quantity_widget)

            # Total
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}"))

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            delete_btn = QPushButton('Убрать')
            delete_btn.clicked.connect(lambda checked, x=cart_id: self.delete_item(x))

            actions_layout.addWidget(delete_btn)
            self.cart_table.setCellWidget(row, 4, actions_widget)
        self.calculate_total()

    def decrease_quantity(self, widget):
        if widget.current_quantity > 1:
            widget.current_quantity -= 1
            widget.quantity_label.setText(str(widget.current_quantity))
            self.update_quantity(widget.cart_id, widget.current_quantity)

    def increase_quantity(self, widget):
        if widget.current_quantity < widget.stock_qty:
            widget.current_quantity += 1
            widget.quantity_label.setText(str(widget.current_quantity))
            self.update_quantity(widget.cart_id, widget.current_quantity)

    def update_quantity(self, item_id, quantity):
        self.db.connect_to_db()
        self.db.cursor.execute('UPDATE cart SET quantity=? WHERE id=?', (quantity, item_id))
        self.db.conn.commit()
        self.db.close_connection()

        self.load_cart()

    def delete_item(self, item_id):
        reply = QMessageBox.question(self, 'Delete Item',
                                     'Подтвердите удаление товара из корзины',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.db.connect_to_db()
            self.db.cursor.execute('DELETE FROM cart WHERE id=?', (item_id,))
            self.db.conn.commit()
            self.db.close_connection()
            self.load_cart()

    def show_checkout(self):
        if self.cart_table.rowCount() > 0:
            self.checkout_window = CheckoutWindow(self.db, self.user_id, self, self.shop_window)
            self.checkout_window.show()
            self.shop_window.load_products()
            self.close()

        else:
            QMessageBox.warning(self, 'Error', 'Корзина пуста')


            