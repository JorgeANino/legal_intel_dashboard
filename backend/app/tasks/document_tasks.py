"""
Document processing Celery tasks with retry logic
"""
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.document_parser import DocumentParser
from app.services.metadata_extractor import MetadataExtractor
from app.services.embedding_service import EmbeddingService
from app.models.document import Document, DocumentMetadata, DocumentChunk
from sqlalchemy import select


@celery_app.task(
    name="app.tasks.document_tasks.process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 30},
    retry_backoff=True,
    retry_jitter=True
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
    import asyncio
    from app.core.logging_config import logger
    
    try:
        logger.info(f"Starting document processing", extra={"document_id": document_id})
        asyncio.run(_process_document(document_id))
        logger.info(f"Document processing completed", extra={"document_id": document_id})
    except Exception as exc:
        logger.error(
            f"Document processing failed", 
            extra={
                "document_id": document_id,
                "error": str(exc),
                "retry_count": self.request.retries
            }
        )
        raise


async def _process_document(document_id: int):
    """Async implementation of document processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get document
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if not document:
                print(f"Document {document_id} not found")
                return
            
            # Parse document
            parser = DocumentParser()
            raw_text, page_count = parser.parse_document(
                document.file_path,
                document.file_type
            )
            
            # Update document with extracted text
            document.raw_text = raw_text
            document.page_count = page_count
            
            # Extract metadata
            extractor = MetadataExtractor()
            metadata_dict = await extractor.extract_metadata(raw_text, document.filename)
            
            # Create metadata record
            metadata = DocumentMetadata(
                document_id=document.id,
                agreement_type=metadata_dict.get("agreement_type"),
                governing_law=metadata_dict.get("governing_law"),
                jurisdiction=metadata_dict.get("jurisdiction"),
                geography=metadata_dict.get("geography"),
                industry=metadata_dict.get("industry"),
                parties=metadata_dict.get("parties"),
                effective_date=metadata_dict.get("effective_date"),
                expiration_date=metadata_dict.get("expiration_date"),
                contract_value=metadata_dict.get("contract_value"),
                currency=metadata_dict.get("currency"),
                key_terms=metadata_dict.get("key_terms"),
                confidence_score=metadata_dict.get("confidence_score", 0.5)
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
                        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                            chunk = DocumentChunk(
                                document_id=document.id,
                                chunk_index=idx,
                                chunk_text=chunk_text,
                                chunk_size=len(chunk_text),
                                embedding=embedding
                            )
                            db.add(chunk)
                        
                        print(f"✅ Generated {len(embeddings)} embeddings for document {document_id}")
                except Exception as e:
                    print(f"⚠️  Warning: Failed to generate embeddings: {e}")
                    # Don't fail the entire task if embeddings fail
            else:
                print(f"ℹ️  Embeddings not available (no API key)")
            
            # Mark as processed
            document.processed = True
            
            await db.commit()
            
            print(f"✅ Successfully processed document {document_id}")
            
        except Exception as e:
            print(f"❌ Error processing document {document_id}: {e}")
            if document:
                document.processing_error = str(e)
                document.processed = False
                await db.commit()
            raise

