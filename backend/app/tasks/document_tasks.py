"""
Document processing Celery tasks with retry logic
"""
# Standard library imports
import asyncio
from datetime import date, datetime

# Third-party imports
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal, engine
from app.core.logging_config import logger

# Local application imports
from app.core.websocket_manager import notify_document_update
from app.models.document import Document, DocumentChunk, DocumentMetadata
from app.services.document_parser import DocumentParser
from app.services.embedding_service import EmbeddingService
from app.services.metadata_extractor import MetadataExtractor


def parse_date(date_str: str | None) -> date | None:
    """
    Parse date string to Python date object

    Supports formats: YYYY-MM-DD, YYYY/MM/DD, DD-MM-YYYY, DD/MM/YYYY
    """
    if not date_str or not isinstance(date_str, str):
        return None

    formats = [
        "%Y-%m-%d",  # 2024-03-22
        "%Y/%m/%d",  # 2024/03/22
        "%d-%m-%Y",  # 22-03-2024
        "%d/%m/%Y",  # 22/03/2024
        "%B %d, %Y",  # March 22, 2024
        "%d %B %Y",  # 22 March 2024
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue

    # If no format works, return None
    return None


@celery_app.task(
    name="app.tasks.document_tasks.process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 30},
    retry_backoff=True,
    retry_jitter=True,
)
def process_document_task(self, document_id: int):
    """
    Background task to process uploaded document:
    1. Extract text
    2. Extract metadata
    3. Create embeddings (optional)

    Features:
    - Automatic retry on failure (3 attempts)
    - Exponential backoff with jitter
    - Error logging and tracking
    """
    try:
        logger.info("Starting document processing", extra={"document_id": document_id})

        # Create a fresh event loop for this task to avoid loop conflicts
        # in Celery's fork pool workers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_process_document(document_id))
        finally:
            # Dispose of the connection pool to prevent event loop conflicts
            # This ensures connections don't get reused across different event loops
            loop.run_until_complete(engine.dispose())

            # Clean up the loop to prevent resource leaks
            loop.close()
            asyncio.set_event_loop(None)

        logger.info("Document processing completed", extra={"document_id": document_id})
    except Exception as exc:
        logger.error(
            "Document processing failed",
            extra={
                "document_id": document_id,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
        )
        raise


async def _process_document(document_id: int):
    """Async implementation of document processing"""
    async with AsyncSessionLocal() as db:
        document = None  # Initialize to avoid UnboundLocalError
        try:
            # Get document
            result = await db.execute(select(Document).where(Document.id == document_id))
            document = result.scalar_one_or_none()

            if not document:
                print(f"Document {document_id} not found")
                return

            # Parse document
            parser = DocumentParser()
            raw_text, page_count = parser.parse_document(document.file_path, document.file_type)

            # Update document with extracted text
            document.raw_text = raw_text
            document.page_count = page_count

            # Extract metadata
            extractor = MetadataExtractor()
            metadata_dict = await extractor.extract_metadata(raw_text, document.filename)

            # Create metadata record (parse dates from strings)
            metadata = DocumentMetadata(
                document_id=document.id,
                agreement_type=metadata_dict.get("agreement_type"),
                governing_law=metadata_dict.get("governing_law"),
                jurisdiction=metadata_dict.get("jurisdiction"),
                geography=metadata_dict.get("geography"),
                industry=metadata_dict.get("industry"),
                parties=metadata_dict.get("parties"),
                effective_date=parse_date(metadata_dict.get("effective_date")),
                expiration_date=parse_date(metadata_dict.get("expiration_date")),
                contract_value=metadata_dict.get("contract_value"),
                currency=metadata_dict.get("currency"),
                key_terms=metadata_dict.get("key_terms"),
                confidence_score=metadata_dict.get("confidence_score", 0.5),
            )

            db.add(metadata)

            # Generate embeddings for semantic search
            embedding_service = EmbeddingService()
            if embedding_service.is_available():
                try:
                    # Chunk the document text
                    chunks = embedding_service.chunk_text(raw_text)
                    print(f"Created {len(chunks)} chunks for document {document_id}")

                    if chunks:
                        # Generate embeddings for all chunks (batch processing)
                        embeddings = await embedding_service.generate_embeddings_batch(chunks)

                        # Store chunks with embeddings
                        for idx, (chunk_text, embedding) in enumerate(
                            zip(chunks, embeddings, strict=False)
                        ):
                            chunk = DocumentChunk(
                                document_id=document.id,
                                chunk_index=idx,
                                chunk_text=chunk_text,
                                chunk_size=len(chunk_text),
                                embedding=embedding,
                            )
                            db.add(chunk)

                        print(
                            f"Generated {len(embeddings)} embeddings for document {document_id}"
                        )
                except Exception as e:
                    print(f"Warning: Failed to generate embeddings: {e}")
                    # Don't fail the entire task if embeddings fail
            else:
                print("INFO: Embeddings not available (no API key)")

            # Mark as processed
            document.processed = True

            await db.commit()

            print(f"Successfully processed document {document_id}")

            # Notify WebSocket clients
            await notify_document_update(document_id, document.user_id, processed=True)

        except Exception as e:
            print(f"ERROR: Error processing document {document_id}: {e}")
            await db.rollback()  # Rollback failed transaction

            # Save error state in a new transaction
            user_id_for_notification = None
            try:
                # Re-fetch document to attach to new transaction
                result = await db.execute(select(Document).where(Document.id == document_id))
                error_doc = result.scalar_one_or_none()

                if error_doc:
                    error_doc.processing_error = str(e)
                    error_doc.processed = False
                    user_id_for_notification = error_doc.user_id
                    await db.commit()
                    print(f"💾 Saved error state for document {document_id}")

                    # Notify WebSocket clients about failure
                    await notify_document_update(
                        document_id, user_id_for_notification, processed=False, error=str(e)
                    )
            except Exception as commit_error:
                print(f"WARNING: Could not save error state: {commit_error}")
                await db.rollback()

            raise
