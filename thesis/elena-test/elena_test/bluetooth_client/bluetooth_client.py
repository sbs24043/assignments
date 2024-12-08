import bluetooth

class BluetoothManager:
    def __init__(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = 1

    def discover_devices(self):
        print("Searching for devices...")
        devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
        print("Found {} devices.".format(len(devices)))
        for addr, name in devices:
            print("  {} - {}".format(addr, name))
        return devices

    def pair_device(self, addr):
        # Note: Pairing is typically handled by the OS, not directly via PyBluez.
        # This is a placeholder for the pairing process.
        print(f"Pairing with device {addr}...")
        # Perform pairing steps here if necessary
        print(f"Paired with device {addr}.")

    def connect(self, addr):
        print(f"Connecting to {addr} on port {self.port}...")
        self.sock.connect((addr, self.port))
        print("Connected.")

    def send_data(self, data: str):
        print(f"Sending data: {data}")
        self.sock.send(data)
        print("Data sent.")

    def receive_data(self, buf_size: int = 1024) -> str:
        print("Receiving data...")
        data = self.sock.recv(buf_size)
        print(f"Data received: {data}")
        return data

    def close_connection(self):
        print("Closing connection...")
        self.sock.close()
        print("Connection closed.")

# Example usage
if __name__ == "__main__":
    bt_manager = BluetoothManager()
    devices = bt_manager.discover_devices()
    if devices:
        addr, name = devices[0]
        bt_manager.pair_device(addr)
        bt_manager.connect(addr)
        bt_manager.send_data("Hello, Bluetooth!")
        response = bt_manager.receive_data()
        print(f"Response: {response}")
        bt_manager.close_connection()