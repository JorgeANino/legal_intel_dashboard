"""
WebSocket endpoint for real-time document processing updates
"""
# Standard library imports
import json

# Third-party imports
import redis.asyncio as aioredis
# Local application imports
from app.core.config import settings
from app.core.websocket_manager import connection_manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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

    try:
        # Subscribe to Redis pub/sub for this user
        redis = await connection_manager.get_redis_client()
        pubsub = redis.pubsub()
        channel_name = f"document_updates:{user_id}"
        await pubsub.subscribe(channel_name)

        print(f"📡 Subscribed to {channel_name}")

        # Listen for Redis messages and forward to WebSocket
        async def listen_redis():
            """Listen for Redis pub/sub messages"""
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await websocket.send_json(data)
                    except Exception as e:
                        print(f"Error processing Redis message: {e}")

        # Keep connection alive and listen
        await listen_redis()

    except WebSocketDisconnect:
        print(f"Client disconnected: user {user_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket, user_id)
        try:
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()
        except Exception:
            pass


