import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.pod_exec import connect_pod_exec


router = APIRouter(
    prefix="/exec",
    tags=["exec"],
)


async def read_pod_output(
    websocket: WebSocket,
    shell,
):
    while True:
        await asyncio.sleep(0.05)

        if not shell.is_open():
            break

        shell.update(timeout=0)

        if shell.peek_stdout():
            output = shell.read_stdout()

            if output:
                await websocket.send_text(output)

        if shell.peek_stderr():
            error = shell.read_stderr()

            if error:
                await websocket.send_text(error)


async def write_pod_input(
    websocket: WebSocket,
    shell,
):
    while True:
        data = await websocket.receive_text()

        if not shell.is_open():
            break

        shell.write_stdin(data)


@router.websocket("/{namespace}/{pod}")
async def exec_pod(
    websocket: WebSocket,
    namespace: str,
    pod: str,
):
    await websocket.accept()

    shell = None

    try:
        shell = connect_pod_exec(
            namespace,
            pod,
        )

        await websocket.send_text(
            "Connected to pod shell\r\n"
        )

        await asyncio.gather(
            read_pod_output(
                websocket,
                shell,
            ),
            write_pod_input(
                websocket,
                shell,
            ),
        )

    except WebSocketDisconnect:
        pass

    except Exception as e:
        try:
            await websocket.send_text(
                f"\r\nERROR: {e}\r\n"
            )
        except Exception:
            pass

    finally:
        if shell:
            shell.close()
