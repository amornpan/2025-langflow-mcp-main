# MSSQL MCP Server with SSE Transport

A Model Context Protocol (MCP) server that provides SQL Server database access through SSE (Server-Sent Events) transport, containerized with Docker.

## Features

- **SSE Transport**: Real-time communication using Server-Sent Events
- **MSSQL Integration**: Connect to Microsoft SQL Server databases
- **FastAPI Backend**: Modern, fast web framework
- **Docker Support**: Fully containerized application
- **MCP Tools**: 
  - Execute SQL queries
  - Preview tables
  - Get database information
  - Refresh schema cache
- **MCP Resources**:
  - List all tables
  - Get table schemas
- **MCP Prompts**:
  - Data analysis templates
  - SQL query generation

## Quick Start

### Using Docker Compose

```bash
docker-compose up
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

## Configuration

Create a `.env` file with your database configuration:

```env
DB_SERVER=your_server_address
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## API Endpoints

- `GET /sse` - SSE connection endpoint
- `POST /messages` - Message handling endpoint
- `GET /health` - Health check endpoint
- `GET /` - API documentation

**Note:** When using Docker, the server runs internally on port 8000 but is exposed externally on port 9000.

## MCP Client Configuration

For Claude Desktop or other MCP clients, use:

```json
{
  "mcpServers": {
    "mssql-sse": {
      "url": "http://localhost:9000/sse"
    }
  }
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building Docker Image

```bash
docker build -t mssql-mcp-sse .
```

## License

MIT
