import asyncio
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from kubernetes.client.exceptions import ApiException

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
    read_task = None
    write_task = None

    try:
        shell = connect_pod_exec(
            namespace,
            pod,
        )

        await websocket.send_text(
            "Connected to pod shell\r\n"
        )

        read_task = asyncio.create_task(
            read_pod_output(
                websocket,
                shell,
            )
        )

        write_task = asyncio.create_task(
            write_pod_input(
                websocket,
                shell,
            )
        )

        done, pending = await asyncio.wait(
            {read_task, write_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(
            *pending,
            return_exceptions=True,
        )

        for task in done:
            exception = task.exception()

            if exception is not None:
                raise exception

    except WebSocketDisconnect:
        pass

    except ApiException as e:
        status = getattr(e, "status", None)

        if status == 404:
            message = (
                f"\r\nERROR: Pod '{pod}' not found "
                f"in namespace '{namespace}'.\r\n"
            )
        elif status == 403:
            message = (
                "\r\nERROR: Access denied (403).\r\n"
            )
        else:
            message = (
                f"\r\nERROR: Kubernetes API error "
                f"({status}): {e.reason}\r\n"
            )

        try:
            await websocket.send_text(message)
        except Exception:
            pass

    except Exception as e:
        traceback.print_exc()

        try:
            await websocket.send_text(
                f"\r\nERROR: {type(e).__name__}: {e}\r\n"
            )
        except Exception:
            pass

    finally:
        if read_task and not read_task.done():
            read_task.cancel()

        if write_task and not write_task.done():
            write_task.cancel()

        tasks = [
            task
            for task in (read_task, write_task)
            if task is not None
        ]

        if tasks:
            await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

        if shell:
            shell.close()
