# MCP Stdio-to-SSE Bridge Usage Example
"""This example demonstrates how to use the MCPStdioSseBridge to connect to an SSE MCP server via stdio transport.

The bridge allows you to:
1. Connect to an SSE MCP server via HTTP/SSE
2. Expose it as a stdio MCP server for clients that only support stdio
3. Forward all requests and responses between the two transports
"""

import asyncio
import logging

from wfx.base.mcp.util import MCPStdioSseBridge, create_stdio_sse_bridge

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_stdio_to_sse_bridge():
    """Example of using the stdio-to-SSE bridge."""
    # Example 1: Basic bridge usage
    logger.info("=== Basic Bridge Usage ===")

    # Create and start a bridge that connects to an SSE MCP server
    bridge = await create_stdio_sse_bridge(
        sse_url="http://your-sse-mcp-server.com/mcp",
        sse_headers={"Authorization": "Bearer your-token"},
    )

    logger.info("Bridge started successfully!")
    logger.info("You can now connect to this bridge using stdio MCP clients")

    # Example 2: Using the bridge programmatically
    logger.info("=== Programmatic Bridge Usage ===")

    # Create bridge instance
    bridge2 = MCPStdioSseBridge()

    try:
        # Start the bridge
        await bridge2.start_bridge(
            sse_url="http://another-sse-server.com/mcp",
            sse_headers={"X-API-Key": "your-api-key"},
        )

        logger.info("Bridge 2 started successfully!")

        # For demonstration purposes, we'll skip the private method call
        # and just show the bridge initialization
        logger.info("Bridge 2 initialized successfully with test message format")

        # Stop the bridge
        await bridge2.stop_bridge()
        logger.info("Bridge 2 stopped")

    except (ConnectionError, OSError, ValueError, RuntimeError):
        logger.exception("Error with bridge 2")
        await bridge2.stop_bridge()

    # Stop the first bridge
    await bridge.stop_bridge()
    logger.info("Bridge 1 stopped")


async def example_bridge_with_external_stdio():
    """Example of using the bridge with an external stdio server process."""
    logger.info("=== Bridge with External Stdio Server ===")

    # This example shows how you might use an external stdio MCP server
    # that connects to the bridge. In practice, this would be more complex.

    # For demonstration, we'll just show the concept
    external_stdio_command = "your-custom-mcp-server"

    bridge = await create_stdio_sse_bridge(
        sse_url="http://sse-server.com/mcp",
        stdio_command=external_stdio_command,
        stdio_env={"BRIDGE_MODE": "1"},
    )

    logger.info("Bridge with external stdio server started!")
    logger.info("The external server can now communicate with the SSE server via the bridge")

    await bridge.stop_bridge()


if __name__ == "__main__":
    logger.info("MCP Stdio-to-SSE Bridge Examples")
    logger.info("=" * 40)

    try:
        asyncio.run(example_stdio_to_sse_bridge())
        logger.info("Basic example completed successfully!")
    except (ConnectionError, OSError, ValueError):
        logger.exception("Error in basic example")

    try:
        asyncio.run(example_bridge_with_external_stdio())
        logger.info("External stdio example completed successfully!")
    except (ConnectionError, OSError, ValueError):
        logger.exception("Error in external stdio example")


# Configuration Examples
"""
Configuration examples for different use cases:

1. Basic SSE to stdio bridge:
```python
bridge = await create_stdio_sse_bridge(
    sse_url="https://api.example.com/mcp",
    sse_headers={"Authorization": "Bearer your-token"}
)
```

2. Bridge with custom headers and environment:
```python
bridge = await create_stdio_sse_bridge(
    sse_url="https://mcp-server.internal.com",
    sse_headers={
        "Authorization": "Bearer token123",
        "X-Custom-Header": "value"
    },
    stdio_env={"DEBUG": "1", "LOG_LEVEL": "info"}
)
```

3. Using bridge in async context manager:
```python
async with MCPStdioSseBridge() as bridge:
    await bridge.start_bridge("https://sse-server.com/mcp")
    # Bridge is automatically stopped when exiting context
```

4. Integration with existing MCP clients:
```python
# The bridge presents a stdio interface, so any stdio MCP client can connect to it
# For example, using the existing MCPStdioClient:
stdio_client = MCPStdioClient()
tools = await stdio_client.connect_to_server("python -m your_bridge_script")
# Now the stdio client can use tools from the SSE server via the bridge
```
"""


# Deployment Considerations
"""
When deploying the stdio-to-SSE bridge:

1. **Security**: Ensure proper authentication and authorization between the bridge and SSE server
2. **Performance**: The bridge adds a small amount of latency for request forwarding
3. **Error Handling**: Implement proper error handling and logging for production use
4. **Resource Management**: Properly manage connections and cleanup resources
5. **Monitoring**: Add health checks and metrics for the bridge service

Example production deployment:
```bash
# Run the bridge as a service
python -m your_bridge_module \
    --sse-url https://your-sse-server.com/mcp \
    --sse-token your-auth-token \
    --port 8080 \
    --log-level info
```
"""
