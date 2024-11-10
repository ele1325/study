import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox

class HelloWorldApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 設定視窗大小和標題
        self.setWindowTitle('Hello World App')
        self.setGeometry(100, 100, 300, 200)

        # 創建按鈕
        self.button = QPushButton('Hello, World!', self)
        self.button.clicked.connect(self.show_message)
        self.button.resize(self.button.sizeHint())
        self.button.move(100, 80)

    def show_message(self):
        # 顯示訊息框
        QMessageBox.information(self, 'Message', 'Hello, World!')

def main():
    app = QApplication(sys.argv)
    ex = HelloWorldApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
