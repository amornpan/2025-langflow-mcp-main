#!/usr/bin/env python3
"""
MSSQL MCP Server with SSE Transport
Main application entry point
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import asyncio
import json
import uuid

from app.mcp_server import mcp_server, sse_transport
from app.database import db_cache

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

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting MCP SSE Server...")
    # Initialize database cache
    db_cache.refresh()
    yield
    # Cleanup resources here
    logger.info("Shutting down MCP SSE Server...")

# Create FastAPI application
app = FastAPI(
    title="MSSQL MCP Server",
    description="Model Context Protocol server for MSSQL with SSE transport",
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "mssql-mcp-server",
        "transport": "sse"
    }

# Root endpoint
@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "service": "MSSQL MCP Server",
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

# Remove this function - we don't need it anymore

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
                        "name": "mssql-sse-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            # Get tools from MCP server
            tools = [
                {
                    "name": "execute_query_tool",
                    "description": "Execute a read-only SQL query and return the results",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query to execute"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "preview_table",
                    "description": "Get a preview of the data in a table",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string", "description": "Name of the table to preview"},
                            "limit": {"type": "number", "description": "Maximum number of rows to return", "default": 10}
                        },
                        "required": ["table_name"]
                    }
                },
                {
                    "name": "get_database_info_tool",
                    "description": "Get general information about the database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "refresh_db_cache",
                    "description": "Refresh the database schema cache",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
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
            from app.mcp_server import execute_query_tool, preview_table, get_database_info_tool, refresh_db_cache
            
            # Call the appropriate tool
            if name == "execute_query_tool":
                result = await execute_query_tool(**arguments)
            elif name == "preview_table":
                result = await preview_table(**arguments)
            elif name == "get_database_info_tool":
                result = await get_database_info_tool()
            elif name == "refresh_db_cache":
                result = await refresh_db_cache()
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
            
            # Parse result and format response
            try:
                result_data = json.loads(result)
                content = result_data.get("result", result_data.get("error", result))
            except:
                content = result
            
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(content)
                        }
                    ]
                }
            }
        elif method == "resources/list":
            resources = [
                {
                    "uri": "mssql://tables",
                    "name": "Database Tables",
                    "description": "List all tables in the database"
                },
                {
                    "uri": "mssql://schema/{table_name}",
                    "name": "Table Schema",
                    "description": "Get the schema for a specific table"
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
            from app.mcp_server import list_tables, get_schema
            
            if uri == "mssql://tables":
                result = await list_tables()
            elif uri and uri.startswith("mssql://schema/"):
                table_name = uri.replace("mssql://schema/", "")
                result = await get_schema(table_name)
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
