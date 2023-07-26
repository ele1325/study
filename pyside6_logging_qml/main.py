import logging
import sys
from PySide6.QtCore import QObject, QUrl, Signal, Slot, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlApplicationEngine

# 自定義的 QObject 類別，用於發送信號
class LogEmitter(QObject): #信號只能宣告在繼承QObject的class裡，不然無法獨立emit
    logChanged = Signal(str)

#    @Slot(str)
#    def log(self, message):
#        self.logChanged.emit(message)

# 註冊emitter, 將logging訊息轉給emitter發送，才會傳到UI
class UiHandler(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter #註冊一個emitter

    def emit(self, record): #此為log handler的emit，勿與signal的emit混淆
        msg = self.format(record) #record即為log訊息，其他py檔呼叫logging.xxx("")都會傳來這裡
#        self.emitter.log(msg)
        self.emitter.logChanged.emit(msg)

# 建立 LogEmitter 實例
log_emitter = LogEmitter()
ui_handler = UiHandler(log_emitter)
# 初始化 logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger().addHandler(ui_handler)

# 建立 QGuiApplication 實例
app = QGuiApplication()
# 載入 QML 檔案
engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("logEmitter", log_emitter)  # 使用contextProperty

engine.load(QUrl.fromLocalFile('main.qml'))
def log_test():
    logging.warning("test111")

# 使用QTimer每秒觸發一次log_test函數
timer = QTimer()
timer.timeout.connect(log_test)
timer.start(1000)  # 1000毫秒 = 1秒


# 顯示 UI
if not engine.rootObjects():
    sys.exit(-1)
sys.exit(app.exec())
