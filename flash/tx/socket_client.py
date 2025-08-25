
import socket

class DPS150SocketClient:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port

    def send_command(self, command: str) -> str:
        try:
            with socket.create_connection((self.host, self.port), timeout=2) as s:
                s.sendall(command.encode())
                response = s.recv(1024)
                return response.decode()
        except Exception as e:
            return f"[ERROR] {e}"

    def set_voltage(self, value: float) -> str:
        return self.send_command(f"SET_VOLTAGE:{value}")

    def set_current(self, value: float) -> str:
        return self.send_command(f"SET_CURRENT:{value}")

    def output_on(self) -> str:
        return self.send_command("OUTPUT_ON")

    def output_off(self) -> str:
        return self.send_command("OUTPUT_OFF")

    def get_status(self) -> str:
        return self.send_command("STATUS")
