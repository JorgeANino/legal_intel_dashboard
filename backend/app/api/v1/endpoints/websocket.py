"""
WebSocket endpoint for real-time document processing updates
"""
# Standard library imports
import asyncio
import json

# Third-party imports
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

# Local application imports
from app.core.websocket_manager import connection_manager


router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time document processing updates

    Client receives messages when document processing status changes:
    {
        "type": "document_update",
        "document_id": 123,
        "status": {
            "processed": true,
            "processing_error": null
        }
    }
    """
    await connection_manager.connect(websocket, user_id)
    pubsub = None

    try:
        # Subscribe to Redis pub/sub for this user
        redis = await connection_manager.get_redis_client()
        pubsub = redis.pubsub()
        channel_name = f"document_updates:{user_id}"
        await pubsub.subscribe(channel_name)

        print(f"Subscribed to {channel_name}")

        # Listen for Redis messages and forward to WebSocket
        async def listen_redis():
            """Listen for Redis pub/sub messages"""
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            # Check if WebSocket is still connected before sending
                            if websocket.client_state == WebSocketState.CONNECTED:
                                data = json.loads(message["data"])
                                await websocket.send_json(data)
                            else:
                                break
                        except Exception as e:
                            print(f"Error processing Redis message: {e}")
                            break
            except Exception as e:
                print(f"Redis listener error: {e}")

        # Listen for client messages (to detect disconnects)
        async def listen_client():
            """Listen for client messages to detect disconnections"""
            try:
                while True:
                    # Wait for any message from client (or disconnect)
                    await websocket.receive_text()
            except WebSocketDisconnect:
                print(f"Client disconnected: user {user_id}")
            except Exception as e:
                print(f"Client listener error: {e}")

        # Run both listeners concurrently
        await asyncio.gather(listen_redis(), listen_client(), return_exceptions=True)

    except WebSocketDisconnect:
        print(f"Client disconnected: user {user_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket, user_id)
        if pubsub:
            try:
                await pubsub.unsubscribe(channel_name)
                await pubsub.close()
            except Exception:
                pass
