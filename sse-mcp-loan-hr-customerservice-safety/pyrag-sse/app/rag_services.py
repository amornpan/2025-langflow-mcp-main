"""
RAG Services initialization and management
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Global service instances
embedding_service: Optional[object] = None
storage_service: Optional[object] = None

def initialize_services(embedding_svc, storage_svc):
    """Initialize global service instances
    
    Args:
        embedding_svc: Embedding service instance
        storage_svc: Storage service instance
    """
    global embedding_service, storage_service
    embedding_service = embedding_svc
    storage_service = storage_svc
    
    # Also update mcp_server services
    import app.mcp_server as mcp
    mcp.embedding_service = embedding_svc
    mcp.storage_service = storage_svc
    
    logger.info("RAG services initialized in app modules")

def get_embedding_service():
    """Get the embedding service instance"""
    return embedding_service

def get_storage_service():
    """Get the storage service instance"""
    return storage_service
