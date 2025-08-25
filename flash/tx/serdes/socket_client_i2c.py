import socket
import time
import threading

class SocketClientI2C:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        self.connect()
        
    def connect(self):
        while True:
            try:
                # 創建一個 socket 物件
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # 連接伺服器
                self.client_socket.connect((self.host, self.port))
                self.connected = True
                print("Connected to server")
                break
            except ConnectionRefusedError:
                # 伺服器未啟動，等待 5 秒後重新連線
                print("Connection refused, retrying in 5 seconds...")
                time.sleep(5)
    
    def receive_message(self):
        while self.connected:
            try:
                # 接收伺服器回傳的消息
                data = self.client_socket.recv(1024)
                if data:
                    print("Received from server:", data.decode('utf-8'))
                else:
                    # 如果接收到空数据，说明连接已关闭
                    print("Server closed connection")
                    self.connected = False
                    self.connect()
            except ConnectionResetError:
                # 伺服器斷線，等待 5 秒後重新連線
                print("Connection reset by peer, retrying in 5 seconds...")
                self.connected = False
                time.sleep(5)
                # 重新連接伺服器
                self.connect()
            except Exception as e:
                print("Error receiving message:", e)
                self.connected = False
                self.connect()
    
    def send_message(self, message):
        try:
            if self.connected:
                # 發送消息給伺服器
                self.client_socket.send(message.encode('utf-8'))
        except ConnectionResetError:
            # 伺服器斷線，等待 5 秒後重新連線
            print("Connection reset by peer, retrying in 5 seconds...")
            self.connected = False
            time.sleep(5)
            # 重新連接伺服器
            self.connect()
            # 重新發送消息
            self.send_message(message)

    def write(self, addr, data):
        # 將 addr 和 data 組成一個封包發送
        packet = bytes([addr]) + data
        self.client_socket.sendall(packet)

    def read(self, addr, data, size):
        # 發送讀取請求
        packet = bytes([addr]) + data
        self.client_socket.sendall(packet)
        return self.client_socket.recv(size)
    
    def close(self):
        # 關閉客戶端連接
        self.connected = False
        if self.client_socket:
            self.client_socket.close()
    
    def run(self):
        # 接收伺服器回傳的消息
        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.daemon = True
        receive_thread.start()
        
        while True:
            # 讀取用戶輸入的消息
            message = input("Enter message: ")
            if message.lower() == 'quit':
                break
            # 發送消息給伺服器
            self.send_message(message)
        
        self.close()

if __name__ == "__main__":
    # 創建 SocketClientI2C 物件
    client = SocketClientI2C('localhost', 27015)
    # 執行 SocketClientI2C
    client.run()
