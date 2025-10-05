"""
Embedding service for generating and managing document embeddings
"""
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings


class EmbeddingService:
    """Service for generating embeddings for semantic search"""
    
    def __init__(self):
        """Initialize embedding model"""
        self.embeddings = None
        self.dimension = 1536  # Default OpenAI dimension
        
        # Initialize embeddings (OpenAI preferred for consistency)
        if settings.OPENAI_API_KEY:
            try:
                self.embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",  # Cost-effective, 1536 dimensions
                    api_key=settings.OPENAI_API_KEY
                )
                self.dimension = 1536
            except Exception as e:
                print(f"Failed to initialize OpenAI embeddings: {e}")
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Characters per chunk
            chunk_overlap=200,  # Overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Full document text
            
        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not self.embeddings:
            raise ValueError("Embeddings not initialized. Please provide API key.")
        
        if not text or len(text.strip()) == 0:
            # Return zero vector for empty text
            return [0.0] * self.dimension
        
        try:
            # Generate embedding
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector on error
            return [0.0] * self.dimension
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.embeddings:
            raise ValueError("Embeddings not initialized. Please provide API key.")
        
        if not texts:
            return []
        
        # Filter out empty texts
        non_empty_texts = [t for t in texts if t and len(t.strip()) > 0]
        
        if not non_empty_texts:
            return [[0.0] * self.dimension] * len(texts)
        
        try:
            # Batch generate embeddings (more efficient)
            embeddings = await self.embeddings.aembed_documents(non_empty_texts)
            return embeddings
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Return zero vectors on error
            return [[0.0] * self.dimension] * len(non_empty_texts)
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.embeddings is not None

