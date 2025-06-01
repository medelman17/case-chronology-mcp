# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Case Chronology MCP (Model Context Protocol) Server that helps legal professionals build and manage chronological timelines of case events. It integrates with Claude Desktop and provides tools for parsing documents, extracting dates, and building comprehensive case timelines.

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastmcp python-dateutil
```

### Running the Server
```bash
# Run the MCP server
python chronology_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python chronology_server.py
```

## Architecture

### Core Components

1. **chronology_server.py** - Main server implementation using FastMCP
   - Implements MCP tools for chronology management
   - Handles date parsing with multiple precision levels
   - Manages persistent storage in `case_chronology.json`

2. **Data Structure** - JSON-based storage with:
   - Events array with full event details
   - Party index for quick party-based searches
   - Document index for document-based lookups
   - Auto-incrementing event IDs

### Key Features

- **Smart Date Parsing**: Handles exact dates, approximate dates (early/mid/late), month precision, and quarters
- **Document Parsing**: Automatically extracts dates and events from pasted documents
- **Multi-format Export**: Markdown, CSV, brief timeline, or JSON
- **Search Capabilities**: By date range, parties, keywords, or tags

### MCP Tools

- `add_event`: Add single events with date parsing
- `parse_document`: Extract events from document text
- `search_timeline`: Query events by various criteria
- `get_timeline_summary`: Overview statistics
- `export_chronology`: Generate outputs in different formats
- `update_event`: Modify existing events
- `delete_event`: Remove events from timeline

## Configuration

Add to Claude Desktop's `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "case-chronology": {
      "command": "python",
      "args": ["/full/path/to/chronology_server.py"]
    }
  }
}
```

## Data Persistence

Events are stored in `case_chronology.json` with automatic indexing for:
- Parties involved in each event
- Source documents
- Chronological ordering

The file is created automatically on first use and updated with each operation.