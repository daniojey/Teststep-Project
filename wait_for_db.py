import socket
import time
import sys

def wait_for_db(host, port, timeout=30):
    """Ожидает подключения к указанному хосту и порту."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Database is ready on {host}:{port}")
                return
        except (socket.timeout, socket.error) as e:
            if time.time() - start_time > timeout:
                print(f"Timeout exceeded while waiting for {host}:{port}")
                sys.exit(1)
            print(f"Waiting for database at {host}:{port}... {e}")
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python wait_for_db.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    wait_for_db(host, port)

    # Выполнение переданной команды
    command = sys.argv[3:]
    if command:
        import subprocess
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command)