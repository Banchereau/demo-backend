import threading

import websocket


ws = websocket.create_connection(
    "ws://127.0.0.1:8000/exec/default/web-7fdc5fd5c-wskdw"
)


def receiver():
    while True:
        try:
            data = ws.recv()
            print("\n" + data)
            print("> ", end="", flush=True)

        except Exception:
            break


threading.Thread(
    target=receiver,
    daemon=True,
).start()


while True:
    command = input("> ")

    ws.send(
        command + "\n"
    )
