# PyRAGDoc MCP Server with SSE Transport

A Model Context Protocol (MCP) server for RAG (Retrieval-Augmented Generation) documentation system with SSE (Server-Sent Events) transport, containerized with Docker.

## Features

- **SSE Transport**: Real-time communication using Server-Sent Events
- **Vector Database Integration**: Uses Qdrant for semantic search
- **Document Processing**: Support for PDF and text files
- **Embedding Support**: Ollama and OpenAI embeddings
- **FastAPI Backend**: Modern, fast web framework
- **Docker Support**: Fully containerized application with docker-compose
- **MCP Tools**: 
  - Add documentation from URLs
  - Search stored documentation
  - List documentation sources
  - Add entire directories
- **MCP Resources**:
  - List all documentation sources
  - Get database statistics
- **MCP Prompts**:
  - Search templates
  - Documentation analysis

## Architecture

Based on the successful SSE-MSSQLMCP pattern, this project provides:
- SSE endpoint for real-time MCP communication
- Message endpoint for handling MCP requests
- Integration with Qdrant vector database
- Support for multiple embedding providers

## Quick Start

### Using Docker Compose

1. Clone the repository and navigate to the project directory

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up
```

This will start:
- Qdrant vector database on port 6333
- PyRAGDoc SSE server on port 9000

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Qdrant (using Docker)
docker run -p 6333:6333 qdrant/qdrant

# Run the server
python main.py
```

## Configuration

Create a `.env` file with your configuration:

```env
# Qdrant Vector Database URL
QDRANT_URL=http://localhost:6333

# Embedding Provider (ollama or openai)
EMBEDDING_PROVIDER=ollama

# Embedding Model
EMBEDDING_MODEL=nomic-embed-text

# Ollama URL (if using Ollama)
OLLAMA_URL=http://localhost:11434

# OpenAI API Key (if using OpenAI)
# OPENAI_API_KEY=your-api-key-here
```

## API Endpoints

- `GET /sse` - SSE connection endpoint for MCP
- `POST /messages` - Message handling endpoint
- `GET /health` - Health check endpoint
- `GET /` - API documentation

**Note:** When using Docker, the server runs internally on port 8000 but is exposed externally on port 9000.

## MCP Client Configuration

For Claude Desktop or other MCP clients, add to your configuration:

```json
{
  "mcpServers": {
    "pyragdoc-sse": {
      "url": "http://localhost:9000/sse",
      "transport": "sse"
    }
  }
}
```

## Usage Examples

### Add Documentation from Directory
```
Use the add_directory tool to add all PDF and text files from a directory:
- Path: /path/to/your/documents
```

### Search Documentation
```
Use the search_documentation tool to find relevant information:
- Query: "your search terms"
- Limit: 5 (optional)
```

### List Sources
```
Use the list_sources tool to see all indexed documentation sources
```

## Supported File Types

- **PDF files**: `.pdf`
- **Text files**: `.txt`, `.md`, `.markdown`
- **Source code**: `.py`, `.js`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`
- **Web files**: `.html`, `.css`, `.json`, `.yaml`, `.yml`, `.xml`

## Development

### Project Structure
```
pyrag-sse/
├── app/
│   ├── mcp_server.py     # MCP server implementation
│   └── rag_services.py    # Service management
├── pyragdoc/
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   └── utils/             # Utilities
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose setup
```

### Building Docker Image

```bash
docker build -t pyragdoc-sse .
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Embedding Providers

### Ollama (Default)
- Free and runs locally
- Models: nomic-embed-text, all-minilm, e5-small, e5-large
- Requires Ollama to be running locally

### OpenAI
- Requires API key
- Models: text-embedding-3-small, text-embedding-3-large
- Better quality but has costs

## Troubleshooting

### Qdrant Connection Issues
- Ensure Qdrant is running on the correct port
- Check firewall settings
- Verify QDRANT_URL in .env

### Ollama Connection Issues
- Ensure Ollama is installed and running
- Check OLLAMA_URL in .env
- Verify the model is pulled: `ollama pull nomic-embed-text`

### SSE Connection Issues
- Check that port 9000 is not in use
- Verify no firewall blocking
- Check logs for detailed error messages

## License

MIT

## Credits

Based on the SSE-MSSQLMCP pattern for MCP server implementation with SSE transport.
