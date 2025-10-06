"""
WebSocket connection manager for real-time updates
"""
# Standard library imports
import json

# Third-party imports
import redis.asyncio as aioredis
from fastapi import WebSocket

# Local application imports
from app.core.config import settings


class ConnectionManager:
    """
    Manages WebSocket connections and Redis pub/sub for real-time updates
    """

    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = {}
        self.redis_client: aioredis.Redis = None

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """
        Accept WebSocket connection and track it

        Args:
            websocket: The WebSocket connection
            user_id: The user ID for this connection
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"WebSocket connected for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        """
        Remove connection when client disconnects

        Args:
            websocket: The WebSocket connection to remove
            user_id: The user ID for this connection
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """
        Send message to all connections for a user

        Args:
            user_id: The user ID to send the message to
            message: The message to send
        """
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to connection: {e}")
                    disconnected.add(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

    async def get_redis_client(self) -> aioredis.Redis:
        """
        Get or create Redis client for pub/sub operations

        Returns:
            Redis client instance
        """
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
        return self.redis_client

    async def broadcast_document_update(self, document_id: int, user_id: int, status: dict) -> None:
        """
        Broadcast document status update to user's connections

        Args:
            document_id: The document ID that was updated
            user_id: The user ID to notify
            status: The status information to broadcast
        """
        message = {
            "type": "document_update",
            "document_id": document_id,
            "status": status
        }
        await self.send_to_user(user_id, message)

    async def close_all_connections(self) -> None:
        """
        Close all active WebSocket connections
        """
        for user_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                try:
                    await connection.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")
            del self.active_connections[user_id]

        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None


# Global connection manager instance
connection_manager = ConnectionManager()


async def notify_document_update(
    document_id: int, user_id: int, processed: bool, error: str = None
) -> None:
    """
    Publish document status update to Redis pub/sub

    Call this from Celery tasks when processing completes/fails

    Args:
        document_id: The document ID that was updated
        user_id: The user ID to notify
        processed: Whether the document was successfully processed
        error: Error message if processing failed
    """
    try:
        redis = await aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

        message = {
            "type": "document_update",
            "document_id": document_id,
            "status": {"processed": processed, "processing_error": error},
        }

        channel = f"document_updates:{user_id}"
        await redis.publish(channel, json.dumps(message))
        await redis.close()

        print(f"Published update for document {document_id} to channel {channel}")

    except Exception as e:
        print(f"Error publishing to Redis: {e}")
