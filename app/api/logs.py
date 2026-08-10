import asyncio

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.services.logs import get_pod_logs, stream_pod_logs


router = APIRouter()


@router.get("/pods/{namespace}/{pod}/logs")
def pod_logs(
    namespace: str,
    pod: str,
    tail: int = 200,
    timestamps: bool = False,
    previous: bool = False,
    container: str | None = None,
):
    try:
        return get_pod_logs(
            namespace=namespace,
            pod=pod,
            tail_lines=tail,
            timestamps=timestamps,
            previous=previous,
            container=container,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.websocket("/logs/{namespace}/{pod}")
async def pod_logs_stream(
    websocket: WebSocket,
    namespace: str,
    pod: str,
    tail: int = 20,
    timestamps: bool = False,
    previous: bool = False,
    container: str | None = None,
):
    await websocket.accept()

    response = None
    stream = None

    try:
        response = stream_pod_logs(
            namespace=namespace,
            pod=pod,
            tail_lines=tail,
            timestamps=timestamps,
            previous=previous,
            container=container,
        )

        stream = response.stream(
            amt=1024,
            decode_content=False,
        )

        while True:
            chunk = await asyncio.to_thread(
                next,
                stream,
                None,
            )

            if chunk is None:
                break

            if isinstance(chunk, bytes):
                chunk = chunk.decode(
                    "utf-8",
                    errors="replace",
                )

            await websocket.send_text(chunk)

    except WebSocketDisconnect:
        pass

    except HTTPException as e:
        try:
            await websocket.send_json(
                {
                    "error": e.detail,
                    "status": e.status_code,
                }
            )
        except Exception:
            pass

    except Exception as e:
        try:
            await websocket.send_json(
                {
                    "error": str(e),
                    "status": 500,
                }
            )
        except Exception:
            pass

    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass

        try:
            await websocket.close()
        except Exception:
            pass
