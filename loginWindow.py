from PyQt6.QtWidgets import *
from shopWindow import ShopWindow
import sqlite3


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.user_id = None

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.register)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setLayout(layout)
        self.setWindowTitle("Авторизация")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.db.connect_to_db()
        self.db.cursor.execute('''SELECT * FROM users WHERE username=? AND password=?''', (username, password))
        user = self.db.cursor.fetchone()

        if user:
            self.user_id = user[0]
            self.user_id = user[0]
            self.shop_window = ShopWindow(self.db, self.user_id)

            self.shop_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Некорректные данные")

        self.db.close_connection()

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.db.connect_to_db()
        try:
            self.db.cursor.execute('''INSERT INTO users (username, password)
                            VALUES (?, ?)''', (username, password))
            self.db.conn.commit()
            QMessageBox.information(self, "Success", "Регистрация успешна")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Введено некорректное значение")

        self.db.close_connection()
