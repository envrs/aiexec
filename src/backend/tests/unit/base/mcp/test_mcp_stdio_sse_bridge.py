"""Tests for MCP stdio-to-SSE bridge functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from wfx.base.mcp.util import MCPStdioSseBridge, create_stdio_sse_bridge


class TestMCPStdioSseBridge:
    """Test the MCPStdioSseBridge functionality."""

    @pytest.fixture
    def bridge(self):
        """Create a bridge instance for testing."""
        return MCPStdioSseBridge()

    @pytest.mark.asyncio
    async def test_bridge_initialization(self, bridge):
        """Test that the bridge initializes correctly."""
        assert bridge.sse_client is not None
        assert not bridge._running
        assert bridge._stdio_server is None

    @pytest.mark.asyncio
    async def test_bridge_start_stop(self, bridge):
        """Test starting and stopping the bridge."""
        # Mock the SSE client connection
        bridge.sse_client.connect_to_server = AsyncMock()
        bridge.sse_client.disconnect = AsyncMock()

        # Start bridge
        await bridge.start_bridge("http://test-sse-server.com", {"Authorization": "Bearer test"})

        assert bridge._running

        # Stop bridge
        await bridge.stop_bridge()

        assert not bridge._running
        bridge.sse_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_bridge_already_running(self, bridge):
        """Test that starting an already running bridge raises an error."""
        bridge._running = True

        with pytest.raises(ValueError, match="Bridge is already running"):
            await bridge.start_bridge("http://test-sse-server.com")

    @pytest.mark.asyncio
    async def test_bridge_sse_connection_failure(self, bridge):
        """Test bridge behavior when SSE connection fails."""
        bridge.sse_client.connect_to_server = AsyncMock(side_effect=ValueError("Connection failed"))

        with pytest.raises(ValueError, match="Connection failed"):
            await bridge.start_bridge("http://test-sse-server.com")

        assert not bridge._running

    @pytest.mark.asyncio
    async def test_handle_stdio_message_initialize(self, bridge):
        """Test handling of initialize message."""
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        response = await bridge._handle_stdio_message(message)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == "2024-11-05"
        assert response["result"]["serverInfo"]["name"] == "stdio-sse-bridge"

    @pytest.mark.asyncio
    async def test_handle_stdio_message_tools_list(self, bridge):
        """Test handling of tools/list message."""
        # Mock the SSE client session and tools list response
        mock_session = AsyncMock()
        mock_tools_response = AsyncMock()
        mock_tools_response.tools = [
            MagicMock(name="test_tool", description="Test tool", inputSchema={"type": "object", "properties": {}})
        ]
        mock_session.list_tools = AsyncMock(return_value=mock_tools_response)
        bridge.sse_client._get_or_create_session = AsyncMock(return_value=mock_session)

        message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        response = await bridge._handle_stdio_message(message)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) == 1
        assert response["result"]["tools"][0]["name"] == "test_tool"

    @pytest.mark.asyncio
    async def test_handle_stdio_message_tools_call(self, bridge):
        """Test handling of tools/call message."""
        # Mock the SSE client tool execution
        bridge.sse_client.run_tool = AsyncMock(return_value={"result": "success"})

        message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"input": "test"},
            },
        }

        response = await bridge._handle_stdio_message(message)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "result" in response
        assert response["result"] == {"result": "success"}

        # Verify the tool was called correctly
        bridge.sse_client.run_tool.assert_called_once_with("test_tool", {"input": "test"})

    @pytest.mark.asyncio
    async def test_handle_stdio_message_unknown_method(self, bridge):
        """Test handling of unknown method."""
        message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "unknown/method",
            "params": {},
        }

        response = await bridge._handle_stdio_message(message)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "not supported" in response["error"]["message"]

    @pytest.mark.asyncio
    async def test_handle_stdio_message_error_handling(self, bridge):
        """Test error handling in stdio message processing."""
        # Mock SSE client to raise an exception
        bridge.sse_client.run_tool = AsyncMock(side_effect=ValueError("SSE server error"))

        message = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {},
            },
        }

        response = await bridge._handle_stdio_message(message)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Internal error" in response["error"]["message"]

    @pytest.mark.asyncio
    async def test_create_stdio_sse_bridge_factory(self):
        """Test the factory function for creating bridges."""
        with patch("wfx.base.mcp.util.MCPStdioSseBridge") as mock_bridge_class:
            mock_bridge = MagicMock()
            mock_bridge_class.return_value = mock_bridge
            mock_bridge.start_bridge = AsyncMock()

            bridge = await create_stdio_sse_bridge(
                "http://test-sse-server.com",
                {"Authorization": "Bearer test"},
                stdio_command="echo test",
                stdio_env={"TEST": "value"},
            )

            mock_bridge_class.assert_called_once()
            mock_bridge.start_bridge.assert_called_once_with(
                "http://test-sse-server.com",
                {"Authorization": "Bearer test"},
                "echo test",
                {"TEST": "value"},
            )
            assert bridge == mock_bridge


class TestMCPStdioSseBridgeIntegration:
    """Integration tests for the stdio-to-SSE bridge."""

    def test_bridge_with_mock_stdio_server(self):
        """Test the bridge with a mock stdio server."""
        # This would be a more complex integration test
        # that simulates actual stdio communication
