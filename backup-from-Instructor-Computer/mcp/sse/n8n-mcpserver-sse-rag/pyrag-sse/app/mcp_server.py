"""
MCP Server implementation with SSE transport for PyRAGDoc
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

# Import PyRAGDoc modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyragdoc.config import load_config
from pyragdoc.core.embedding import create_embedding_service
from pyragdoc.core.storage import create_storage_service
from pyragdoc.core.processors.pdf import PDFProcessor
from pyragdoc.core.processors.text import TextProcessor
from pyragdoc.utils.logging import setup_logging, get_logger

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp_server = FastMCP("pyragdoc-sse-server")

# Initialize SSE transport
sse_transport = SseServerTransport("/messages")

# Global services - will be initialized by main.py
embedding_service = None
storage_service = None

# MCP Resources
@mcp_server.resource(uri="rag://sources")
async def get_sources_resource() -> str:
    """List all documentation sources in the database"""
    try:
        sources = await storage_service.list_sources()
        return json.dumps(sources, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp_server.resource(uri="rag://stats")
async def get_stats_resource() -> str:
    """Get statistics about the RAG database"""
    try:
        # This is a placeholder - implement actual stats gathering
        stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "embedding_dimension": 768,
            "storage_type": "qdrant"
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

# MCP Tools
@mcp_server.tool()
async def add_documentation(url: str) -> str:
    """Add documentation from a URL to the RAG database
    
    Args:
        url: URL of the documentation to fetch
    """
    try:
        # This is a placeholder - implement URL fetching and processing
        logger.info(f"Adding documentation from URL: {url}")
        
        # TODO: Implement URL fetching
        # 1. Fetch content from URL
        # 2. Detect content type
        # 3. Process with appropriate processor
        # 4. Generate embeddings
        # 5. Store in database
        
        return f"Successfully added documentation from {url}"
    except Exception as e:
        error_msg = f"Error adding documentation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

@mcp_server.tool()
async def search_documentation(query: str, limit: int = 5) -> str:
    """Search through stored documentation
    
    Args:
        query: Search query
        limit: Maximum number of results to return (default: 5)
    """
    try:
        logger.info(f"Searching documentation with query: {query}")
        
        # Generate embedding for query
        embedding = await embedding_service.generate_embedding(query)
        
        # Search for similar documents
        results = await storage_service.search(embedding, limit)
        
        if not results or len(results) == 0:
            return "No results found for your query."
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            chunk = result.chunk
            score = result.score
            
            # Get metadata
            source = "Unknown source"
            if hasattr(chunk.metadata, 'url') and chunk.metadata.url:
                source = chunk.metadata.url
            elif hasattr(chunk.metadata, 'source') and chunk.metadata.source:
                source = chunk.metadata.source
            
            title = source
            if hasattr(chunk.metadata, 'title') and chunk.metadata.title:
                title = chunk.metadata.title
            
            formatted = f"[{i+1}] {title} (Score: {score:.2f})\n"
            formatted += f"Source: {source}\n\n"
            formatted += chunk.text
            
            formatted_results.append(formatted)
        
        formatted_text = "\n\n---\n\n".join(formatted_results)
        return formatted_text
            
    except Exception as e:
        error_msg = f"Error searching documentation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

@mcp_server.tool()
async def list_sources() -> str:
    """List all documentation sources currently stored"""
    try:
        logger.info("Listing documentation sources")
        
        sources = await storage_service.list_sources()
        
        if not sources or len(sources) == 0:
            return "No documentation sources found."
        
        formatted = "Documentation sources:\n\n"
        for i, source in enumerate(sources, 1):
            formatted += f"{i}. {source}\n"
        
        return formatted
    except Exception as e:
        error_msg = f"Error listing sources: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

@mcp_server.tool()
async def add_directory(path: str) -> str:
    """Add all supported files from a directory to the RAG database
    
    Args:
        path: Path to the directory containing documents
    """
    try:
        logger.info(f"Adding documentation from directory: {path}")
        
        # Check if directory exists
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory or doesn't exist"
        
        # Create processors
        pdf_processor = PDFProcessor(logger=logger)
        text_processor = TextProcessor(logger=logger)
        
        # Statistics
        stats = {
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "total_chunks": 0
        }
        
        # Track processed files
        processed_files = []
        failed_files = []
        
        # Process files
        for root, _, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                try:
                    # Check supported file types
                    chunks = None
                    if pdf_processor.can_process(file_path):
                        logger.info(f"Processing PDF file: {file_path}")
                        chunks = await pdf_processor.process_content(file_path)
                    elif text_processor.can_process(file_path):
                        logger.info(f"Processing text file: {file_path}")
                        chunks = await text_processor.process_content(file_path)
                    else:
                        logger.info(f"Skipping unsupported file: {file_path}")
                        stats["skipped"] += 1
                        continue
                    
                    if not chunks:
                        logger.info(f"No content extracted from: {file_path}")
                        stats["skipped"] += 1
                        continue
                    
                    # Generate embeddings and store
                    embeddings = []
                    for chunk in chunks:
                        embedding = await embedding_service.generate_embedding(chunk.text)
                        embeddings.append(embedding)
                    
                    # Store documents
                    await storage_service.add_documents(embeddings, chunks)
                    
                    processed_files.append(file_path)
                    stats["processed"] += 1
                    stats["total_chunks"] += len(chunks)
                    logger.info(f"Successfully processed {file_path}: {len(chunks)} chunks")
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    failed_files.append(file_path)
                    stats["failed"] += 1
        
        # Create summary
        summary = f"Directory Processing Results:\n\n"
        summary += f"Processed {stats['processed']} files successfully\n"
        summary += f"Failed to process {stats['failed']} files\n"
        summary += f"Skipped {stats['skipped']} unsupported files\n"
        summary += f"Added {stats['total_chunks']} total chunks to the database\n\n"
        
        if processed_files:
            summary += "Successfully processed files:\n"
            for i, file_path in enumerate(processed_files[:10], 1):
                summary += f"{i}. {file_path}\n"
            
            if len(processed_files) > 10:
                summary += f"...and {len(processed_files) - 10} more files\n"
        
        if failed_files:
            summary += "\nFailed files:\n"
            for i, file_path in enumerate(failed_files[:5], 1):
                summary += f"{i}. {file_path}\n"
            
            if len(failed_files) > 5:
                summary += f"...and {len(failed_files) - 5} more files\n"
        
        return summary
    except Exception as e:
        error_msg = f"Error adding directory: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

# MCP Prompts
@mcp_server.prompt()
async def search_template(topic: str) -> Dict:
    """Generate a search template for a specific topic
    
    Args:
        topic: Topic to search for
    """
    search_prompt = f"""
I need to search for information about: {topic}

Please help me find relevant documentation and information about this topic.
Here are some specific aspects I'm interested in:
1. Overview and basic concepts
2. Best practices and recommendations
3. Common issues and solutions
4. Examples and use cases
5. Related topics and resources

Search query: {topic}
"""
    
    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": search_prompt
                }
            }
        ]
    }

@mcp_server.prompt()
async def analyze_documentation() -> Dict:
    """Generate a prompt for analyzing stored documentation"""
    
    analysis_prompt = """
Please analyze the documentation currently stored in the RAG database.

I'd like to understand:
1. What topics are covered in the documentation
2. The main themes and concepts
3. Any gaps or areas that need more documentation
4. Suggestions for organizing the information better

Start by listing the sources and then provide your analysis.
"""
    
    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": analysis_prompt
                }
            }
        ]
    }
