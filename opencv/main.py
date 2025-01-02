import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine

def main():
    app = QGuiApplication(sys.argv)
    
    # 使用 QQmlApplicationEngine 加載 QML 文件
    engine = QQmlApplicationEngine()
    engine.load(QUrl("main.qml"))
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
