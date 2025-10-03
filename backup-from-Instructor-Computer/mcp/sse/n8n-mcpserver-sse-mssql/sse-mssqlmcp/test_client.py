#!/usr/bin/env python3
"""
Test script for SSE MCP Server
"""
import asyncio
import json
import logging
from typing import Optional

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server URL
SERVER_URL = "http://localhost:9000/sse"

class TestMCPClient:
    """Test client for MCP SSE server"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
    
    async def connect(self, url: str):
        """Connect to MCP server"""
        logger.info(f"Connecting to {url}")
        
        # Create SSE client
        async with sse_client(url) as streams:
            self.session = ClientSession(*streams)
            await self.session.initialize()
            
            logger.info("Connected successfully!")
            
            # List available tools
            tools_response = await self.session.list_tools()
            logger.info(f"Available tools: {[tool.name for tool in tools_response.tools]}")
            
            # List available resources
            resources_response = await self.session.list_resources()
            logger.info(f"Available resources: {[res.uri for res in resources_response.resources]}")
            
            # Test execute_query tool
            await self.test_execute_query()
            
            # Test preview_table tool
            await self.test_preview_table()
            
            # Test database info
            await self.test_database_info()
    
    async def test_execute_query(self):
        """Test execute_query tool"""
        logger.info("\nTesting execute_query tool...")
        
        result = await self.session.call_tool(
            "execute_query_tool",
            {"query": "SELECT TOP 5 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"}
        )
        
        logger.info(f"Query result: {json.dumps(result.content, indent=2)}")
    
    async def test_preview_table(self):
        """Test preview_table tool"""
        logger.info("\nTesting preview_table tool...")
        
        # First get list of tables
        resources = await self.session.read_resource("mssql://tables")
        tables = json.loads(resources.contents[0].text)
        
        if tables:
            # Preview first table
            table_name = tables[0]
            logger.info(f"Previewing table: {table_name}")
            
            result = await self.session.call_tool(
                "preview_table",
                {"table_name": table_name, "limit": 5}
            )
            
            logger.info(f"Preview result: {json.dumps(result.content, indent=2)}")
    
    async def test_database_info(self):
        """Test database info tool"""
        logger.info("\nTesting get_database_info tool...")
        
        result = await self.session.call_tool("get_database_info_tool", {})
        logger.info(f"Database info: {json.dumps(result.content, indent=2)}")

async def main():
    """Main test function"""
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/health")
            response.raise_for_status()
            logger.info("Server is healthy!")
    except Exception as e:
        logger.error(f"Server health check failed: {e}")
        logger.error("Make sure the server is running on http://localhost:9000")
        return
    
    # Test MCP connection
    client = TestMCPClient()
    try:
        await client.connect(SERVER_URL)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
