#!/usr/bin/env python3
"""
Debug test for SSE endpoint - Fixed version
"""
import httpx
import asyncio
import json

async def test_sse_proper():
    """Test SSE with proper connection handling"""
    print("Testing SSE MCP Server...")
    
    # Use a single long-lived client for SSE
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        print("\n1. Connecting to SSE endpoint...")
        
        # Start SSE connection
        async with client.stream("GET", "http://localhost:9000/sse") as sse_stream:
            print(f"   Connected! Status: {sse_stream.status_code}")
            
            # Create an async iterator once
            lines = sse_stream.aiter_lines()
            
            # Read endpoint
            endpoint_url = None
            async for line in lines:
                print(f"   SSE: {line}")
                if line.startswith("data: "):
                    endpoint_url = line[6:]
                    print(f"   Got endpoint: {endpoint_url}")
                    break
            
            if not endpoint_url:
                print("   ERROR: No endpoint received!")
                return
            
            # Extract session_id properly
            full_url = f"http://localhost:9000{endpoint_url}"
            print(f"\n2. Sending initialize to: {full_url}")
            
            # Send message using a separate client (important!)
            async with httpx.AsyncClient() as msg_client:
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
                
                resp = await msg_client.post(full_url, json=init_message)
                print(f"   Status: {resp.status_code}")
                if resp.status_code != 200:
                    print(f"   Error: {resp.text}")
                else:
                    print(f"   Success: {resp.text}")
            
            print("\n3. Reading SSE response...")
            # Continue reading from the same iterator
            read_timeout = 5
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < read_timeout:
                try:
                    # Get next line with timeout
                    line = await asyncio.wait_for(lines.__anext__(), timeout=1.0)
                    print(f"   SSE: {line}")
                    
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        print(f"   Initialize response: {json.dumps(data, indent=2)}")
                        break
                except asyncio.TimeoutError:
                    print("   (waiting for data...)")
                except StopAsyncIteration:
                    print("   Stream ended!")
                    break
            
            # Test tools/list
            print("\n4. Testing tools/list...")
            async with httpx.AsyncClient() as msg_client:
                tools_msg = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                resp = await msg_client.post(full_url, json=tools_msg)
                print(f"   Status: {resp.status_code}")
            
            # Read tools response
            print("\n5. Reading tools response...")
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < read_timeout:
                try:
                    line = await asyncio.wait_for(lines.__anext__(), timeout=1.0)
                    print(f"   SSE: {line}")
                    
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        print("\n   Tools available:")
                        for tool in data.get("result", {}).get("tools", []):
                            print(f"   - {tool.get('name')}: {tool.get('description')}")
                        break
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    print("   Stream ended!")
                    break

if __name__ == "__main__":
    asyncio.run(test_sse_proper())
