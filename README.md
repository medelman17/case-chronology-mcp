# Case Chronology MCP Server

A Model Context Protocol (MCP) server for building and managing chronological timelines of case events. Perfect for legal professionals who need to organize complex case histories.

## Features

- **Smart Date Parsing**: Handles various date formats including exact dates, approximate dates, months, and quarters
- **Document Parsing**: Automatically extract dates and events from pasted documents
- **Multi-format Export**: Generate timelines in Markdown, CSV, brief text, or JSON
- **Advanced Search**: Query by date range, parties, keywords, or tags
- **Party & Document Indexing**: Quick lookups by involved parties or source documents

## Installation

### Option 1: Using uvx (Recommended)

No installation needed! The server can be run directly with `uvx`.

### Option 2: Traditional Installation

1. Clone this repository:
```bash
git clone https://github.com/medelman17/case-chronology-mcp.git
cd case-chronology-mcp
```

2. Install with uv:
```bash
uv pip install -e .
```

Or with pip:
```bash
pip install -r requirements.txt
```

## Configuration

Add the server to your Claude Desktop configuration:

### Windows Users - Step by Step

#### Step 1: Download and Setup
1. Open **PowerShell** or **Command Prompt**
2. Navigate to where you want to install (e.g., your GitHub folder):
   ```powershell
   cd C:\Users\%USERNAME%\GitHub
   ```
3. Clone the repository:
   ```powershell
   git clone https://github.com/medelman17/case-chronology-mcp.git
   cd case-chronology-mcp
   ```
4. **IMPORTANT:** Run the setup script (this creates a virtual environment and installs dependencies):
   ```powershell
   .\setup.bat
   ```
   Wait for it to complete. You should see "Setup complete!" at the end.

#### Step 2: Configure Claude Desktop
1. Open **Claude Desktop**
2. Go to **Settings** (gear icon in bottom left)
3. Click **Developer** tab
4. Find the **MCP Servers Configuration** section
5. Add this configuration (**replace `%USERNAME%` with your actual username**):

```json
{
  "mcpServers": {
    "case-chronology": {
      "command": "C:\\Users\\%USERNAME%\\GitHub\\case-chronology-mcp\\run_server.bat"
    }
  }
}
```

**For example, if your username is `mikee`, use:**
```json
{
  "mcpServers": {
    "case-chronology": {
      "command": "C:\\Users\\mikee\\GitHub\\case-chronology-mcp\\run_server.bat"
    }
  }
}
```

6. **Save** the configuration
7. **Restart Claude Desktop**

#### Step 3: Test It Works
After restarting Claude Desktop, you should see the Case Chronology server connected. Try asking:
> "Add an event: January 15, 2024 - Contract signed between ABC Corp and XYZ LLC"

### Mac/Linux Users

#### Option 1: Using uvx (Recommended)

```json
{
  "mcpServers": {
    "case-chronology": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/medelman17/case-chronology-mcp.git",
        "case-chronology-mcp"
      ]
    }
  }
}
```

#### Option 2: Local Installation

```json
{
  "mcpServers": {
    "case-chronology": {
      "command": "python",
      "args": ["/full/path/to/case-chronology-mcp/chronology_server.py"]
    }
  }
}
```

## Usage Examples

### Adding Events

**Simple event:**
```
"Add event: March 15, 2023 - Smith emails Jones about breach of contract. Parties: Smith, Jones"
```

**Event with details:**
```
"Add event: 3/15/2023 - Contract breach notification sent. Parties: Smith, Jones. Tag: breach, notice. Significance: First formal notice of breach"
```

### Document Parsing

```
"Parse this email and add events to the chronology:

From: Bob Smith
To: Alice Jones
Date: March 15, 2023

I am writing to inform you that your failure to deliver by March 1, 2023 constitutes a breach..."
```

### Searching the Timeline

- "Show all events in March 2023"
- "Find events involving Smith"
- "Search for events tagged 'breach'"
- "Show events between 1/1/2023 and 6/30/2023"

### Exporting

- "Export the chronology as markdown"
- "Give me a brief timeline"
- "Export as CSV for Excel"
- "Export full JSON data"

## Date Format Support

The server intelligently parses various date formats:

- **Exact dates**: `3/15/2023`, `March 15, 2023`
- **Approximate dates**: `early March 2023`, `mid March 2023`, `late March 2023`
- **Month precision**: `March 2023`
- **Quarter precision**: `Q1 2023`
- **Approximate markers**: `around 3/15/2023`, `approximately March 2023`

## Data Storage

Events are stored in `case_chronology.json` in the same directory as the server. The file is created automatically on first use.

## Troubleshooting (Windows)

### ❌ "Virtual environment not found" error
- Make sure you ran `.\setup.bat` first
- Check that the `venv` folder exists in your project directory

### ❌ "Python not found" error  
- Install Python 3.10 or later from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### ❌ "Setup failed" error
- Try running PowerShell as Administrator
- Or manually create the environment:
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

### ❌ Server disconnects immediately
- Check that your path in Claude Desktop config is correct
- Make sure to use **double backslashes** (`\\`) in the JSON path
- Verify your username is correct in the path

### ❌ "Permission denied" errors
- Run PowerShell as Administrator
- Or try installing in a different location (like your Documents folder)

## Testing

Test the server with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python chronology_server.py
```

## Tools Available

- `add_event` - Add a single event to the chronology
- `parse_document` - Extract events from document text
- `search_timeline` - Search events by various criteria
- `get_timeline_summary` - Get overview statistics
- `export_chronology` - Export in different formats
- `update_event` - Modify existing events
- `delete_event` - Remove events from timeline

## License

MIT