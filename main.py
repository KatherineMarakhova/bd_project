import sys
from PyQt6.QtWidgets import *
from database import Database
from loginWindow import LoginWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db_name = "shop.db"
    db = Database(db_name)
    window = LoginWindow(db)
    window.show()
    sys.exit(app.exec())
