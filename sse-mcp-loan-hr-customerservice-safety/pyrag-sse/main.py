#!/usr/bin/env python3
"""
PyRAGDoc MCP Server with SSE Transport
Main application entry point
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import asyncio
import json
import uuid

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyragdoc.config import load_config
from pyragdoc.core.embedding import create_embedding_service
from pyragdoc.core.storage import create_storage_service
from app.rag_services import initialize_services

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SSE connections storage
sse_connections = {}

# Global service instances
embedding_service = None
storage_service = None

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting PyRAGDoc SSE Server...")
    # Initialize services
    await initialize_rag_services()
    yield
    # Cleanup resources here
    logger.info("Shutting down PyRAGDoc SSE Server...")

# Create FastAPI application
app = FastAPI(
    title="PyRAGDoc MCP Server",
    description="Model Context Protocol server for RAG Documentation with SSE transport",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_rag_services():
    """Initialize RAG services"""
    try:
        global embedding_service, storage_service
        
        config = load_config()
        logger.info("Initializing RAG services...")
        
        # Create services
        embedding_service = create_embedding_service(config["embedding"])
        storage_service = create_storage_service(config["database"])
        
        # Set vector size in storage service
        vector_size = embedding_service.get_vector_size()
        storage_service.vector_size = vector_size
        
        # Initialize storage
        await storage_service.initialize()
        
        # Initialize services in app modules
        initialize_services(embedding_service, storage_service)
        
        logger.info("RAG services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "pyragdoc-sse-server",
        "transport": "sse"
    }

# Root endpoint
@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "service": "PyRAGDoc MCP Server",
        "version": "1.0.0",
        "transport": "SSE",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health"
        }
    }

# SSE endpoint - Support both GET and HEAD
@app.api_route("/sse", methods=["GET", "HEAD"])
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication."""
    
    # Handle HEAD request for connection testing
    if request.method == "HEAD":
        return Response(
            status_code=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    
    # Handle GET request - original SSE logic
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sse_connections[session_id] = queue
    
    logger.info(f"New SSE connection: {session_id}")
    
    async def event_stream():
        try:
            # Send endpoint event as per MCP SSE specification
            endpoint_url = f"/messages?session_id={session_id}"
            yield f"event: endpoint\ndata: {endpoint_url}\n\n"
            
            # Keep connection alive and wait for messages
            while True:
                try:
                    # Wait for message from queue with timeout
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    # Send MCP message as SSE message event
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send keep-alive comment
                    yield f": keep-alive\n\n"
                    continue
                
        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled: {session_id}")
        except Exception as e:
            logger.error(f"SSE error: {e}")
        finally:
            # Clean up connection
            if session_id in sse_connections:
                del sse_connections[session_id]
                logger.info(f"Cleaned up SSE connection: {session_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# Message endpoint
@app.post("/messages")
async def message_endpoint(request: Request):
    """HTTP endpoint for receiving messages from MCP clients."""
    try:
        # Get session ID from query parameters
        session_id = request.query_params.get("session_id")
        if not session_id or session_id not in sse_connections:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        # Parse JSON-RPC message
        message = await request.json()
        
        # Process MCP message and get response
        response = await process_mcp_message(message)
        
        # Send response through SSE if it exists
        if response and session_id in sse_connections:
            await sse_connections[session_id].put(response)
        
        return JSONResponse({"status": "received"})
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def process_mcp_message(message: dict) -> Optional[dict]:
    """Process an MCP message and return response."""
    try:
        method = message.get("method")
        params = message.get("params", {})
        message_id = message.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "pyragdoc-sse-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            # Get tools from MCP server
            tools = [
                {
                    "name": "add_documentation",
                    "description": "Add documentation from a URL to the RAG database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL of the documentation to fetch"}
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "search_documentation",
                    "description": "Search through stored documentation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {"type": "number", "description": "Maximum number of results to return", "default": 5}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "list_sources",
                    "description": "List all documentation sources currently stored",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "add_directory",
                    "description": "Add all supported files from a directory to the RAG database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the directory containing documents"}
                        },
                        "required": ["path"]
                    }
                }
            ]
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "tools": tools
                }
            }
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Import tool functions
            from app.mcp_server import (
                add_documentation, 
                search_documentation, 
                list_sources, 
                add_directory
            )
            
            # Call the appropriate tool
            if name == "add_documentation":
                result = await add_documentation(**arguments)
            elif name == "search_documentation":
                result = await search_documentation(**arguments)
            elif name == "list_sources":
                result = await list_sources()
            elif name == "add_directory":
                result = await add_directory(**arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": f"Unknown tool: {name}"
                    }
                }
            
            # Format response
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            }
        elif method == "resources/list":
            resources = [
                {
                    "uri": "rag://sources",
                    "name": "Documentation Sources",
                    "description": "List all documentation sources in the database"
                },
                {
                    "uri": "rag://stats",
                    "name": "Database Statistics",
                    "description": "Get statistics about the RAG database"
                }
            ]
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "resources": resources
                }
            }
        elif method == "resources/read":
            uri = params.get("uri")
            
            # Import resource functions
            from app.mcp_server import get_sources_resource, get_stats_resource
            
            if uri == "rag://sources":
                result = await get_sources_resource()
            elif uri == "rag://stats":
                result = await get_stats_resource()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": f"Unknown resource URI: {uri}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": result
                        }
                    ]
                }
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error processing MCP message: {e}", exc_info=True)
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENVIRONMENT", "development") == "development" else False,
        log_level="info"
    )
