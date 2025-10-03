#!/usr/bin/env python3
"""
Test script for SSE MCP Server - Simple version
"""
import asyncio
import json
import logging
import httpx
from asyncio import wait_for

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server URL
SERVER_URL = "http://localhost:9000/sse"

async def test_sse_connection():
    """Test basic SSE connection"""
    logger.info(f"Testing SSE connection to {SERVER_URL}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health check first
        logger.info("Testing health check...")
        health_response = await client.get("http://localhost:9000/health")
        logger.info(f"Health check response: {health_response.json()}")
        
        # Connect to SSE endpoint
        logger.info("Connecting to SSE endpoint...")
        
        # We need to maintain the SSE connection while sending messages
        # So we'll use a different approach
        
        # First, get the SSE stream
        response = await client.get(SERVER_URL, headers={"Accept": "text/event-stream"})
        
        # Read the first few lines to get endpoint
        content = response.text
        lines = content.strip().split('\n')
        
        endpoint_url = None
        for line in lines:
            logger.info(f"Line: {line}")
            if line.startswith("data: "):
                endpoint_url = line[6:]
                break
        
        if not endpoint_url:
            logger.error("No endpoint URL found")
            return
            
        logger.info(f"Got endpoint URL: {endpoint_url}")
        
        # Extract session_id from endpoint URL
        session_id = endpoint_url.split("session_id=")[1]
        logger.info(f"Session ID: {session_id}")
        
        # Now connect with streaming to keep connection alive
        async with client.stream("GET", SERVER_URL) as sse_response:
            # Skip the first few lines we already read
            endpoint_found = False
            async for line in sse_response.aiter_lines():
                if not endpoint_found and line.startswith("data: "):
                    endpoint_found = True
                    continue
                if endpoint_found:
                    break
            
            # Send initialize message
            message_url = f"http://localhost:9000{endpoint_url}"
            logger.info(f"Sending initialize to {message_url}")
            
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send in a separate client to avoid connection issues
            async with httpx.AsyncClient() as msg_client:
                init_response = await msg_client.post(message_url, json=init_message)
                logger.info(f"Initialize response status: {init_response.status_code}")
                logger.info(f"Initialize response: {init_response.text}")
            
            # Try to read response from SSE
            logger.info("Waiting for SSE response...")
            
            try:
                # Read with timeout
                async def read_sse_message():
                    async for line in sse_response.aiter_lines():
                        logger.info(f"SSE Line: {line}")
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            return data
                    return None
                
                message = await wait_for(read_sse_message(), timeout=5.0)
                if message:
                    logger.info(f"Got SSE message: {message}")
                else:
                    logger.warning("No message received via SSE")
                    
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for SSE message")
            
            # Test tools/list
            logger.info("Testing tools/list...")
            tools_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            async with httpx.AsyncClient() as msg_client:
                tools_response = await msg_client.post(message_url, json=tools_message)
                logger.info(f"Tools/list response status: {tools_response.status_code}")
            
            # Try to read tools response from SSE
            try:
                tools_data = await wait_for(read_sse_message(), timeout=5.0)
                if tools_data:
                    logger.info(f"Got tools list: {tools_data}")
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for tools list")

async def main():
    """Main test function"""
    try:
        await test_sse_connection()
        logger.info("Test completed!")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
