#!/usr/bin/env -S uvx --with fastmcp --with python-dateutil
from fastmcp import FastMCP
import json
import os
from datetime import datetime, date
from dateutil import parser
from typing import List, Dict, Optional, Union
import re

# Initialize the MCP server
mcp = FastMCP("Case Chronology Builder")

# Helper functions for data persistence
def load_chronology():
    if os.path.exists('case_chronology.json'):
        with open('case_chronology.json', 'r') as f:
            return json.load(f)
    return {"events": [], "next_id": 1, "parties": {}, "documents": {}}

def save_chronology(data):
    with open('case_chronology.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)

# Date parsing helper
def parse_date_with_precision(date_string: str) -> tuple:
    """Parse various date formats and return (date, precision)"""
    date_string = date_string.strip()
    
    # Exact date patterns
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_string):
        return parser.parse(date_string).date(), "exact"
    
    # Year-month patterns
    if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}$', date_string, re.I):
        parsed = parser.parse(date_string)
        return parsed.date().replace(day=1), "month"
    
    # Approximate patterns
    if re.match(r'^(early|mid|late|around|approximately)', date_string, re.I):
        # Extract the actual date part
        date_part = re.sub(r'^(early|mid|late|around|approximately)\s*', '', date_string, flags=re.I)
        parsed = parser.parse(date_part)
        
        if 'early' in date_string.lower():
            return parsed.date().replace(day=1), "approximate"
        elif 'mid' in date_string.lower():
            return parsed.date().replace(day=15), "approximate"
        elif 'late' in date_string.lower():
            return parsed.date().replace(day=28), "approximate"
        else:
            return parsed.date(), "approximate"
    
    # Quarter patterns (Q1 2023, etc.)
    quarter_match = re.match(r'^Q(\d)\s+(\d{4})$', date_string)
    if quarter_match:
        quarter, year = int(quarter_match.group(1)), int(quarter_match.group(2))
        month = (quarter - 1) * 3 + 1
        return date(year, month, 1), "quarter"
    
    # Default parsing
    try:
        parsed = parser.parse(date_string)
        return parsed.date(), "exact"
    except:
        raise ValueError(f"Could not parse date: {date_string}")

@mcp.tool()
def add_event(
    date_string: str,
    description: str,
    parties: List[str],
    document_source: str = "",
    document_excerpt: str = "",
    tags: List[str] = [],
    significance: str = ""
) -> Dict:
    """Add a chronology event with automatic date parsing"""
    data = load_chronology()
    
    # Parse date
    try:
        event_date, precision = parse_date_with_precision(date_string)
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    
    # Create event
    event = {
        "id": data["next_id"],
        "date": str(event_date),
        "date_precision": precision,
        "description": description,
        "parties": parties,
        "document_source": document_source,
        "document_excerpt": document_excerpt,
        "tags": tags,
        "significance": significance,
        "created_at": datetime.now().isoformat()
    }
    
    # Update party index
    for party in parties:
        if party not in data["parties"]:
            data["parties"][party] = []
        data["parties"][party].append(event["id"])
    
    # Update document index
    if document_source:
        if document_source not in data["documents"]:
            data["documents"][document_source] = []
        data["documents"][document_source].append(event["id"])
    
    data["events"].append(event)
    data["next_id"] += 1
    save_chronology(data)
    
    return {
        "status": "success", 
        "event_id": event["id"],
        "message": f"Added event on {event_date} ({precision}): {description[:50]}..."
    }

@mcp.tool()
def parse_document(
    content: str,
    document_name: str,
    default_parties: List[str] = []
) -> Dict:
    """Parse a document and extract potential chronology events"""
    # Common date patterns in legal documents
    date_patterns = [
        r'(?:on|dated|as of)\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'(?:on|dated|as of)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
    ]
    
    events_found = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for dates
        for pattern in date_patterns:
            matches = re.finditer(pattern, line, re.I)
            for match in matches:
                date_str = match.group(1)
                
                # Get context (surrounding text)
                start = max(0, match.start() - 50)
                end = min(len(line), match.end() + 100)
                context = line[start:end].strip()
                
                # Clean up context
                if start > 0:
                    context = "..." + context
                if end < len(line):
                    context = context + "..."
                
                events_found.append({
                    "date_string": date_str,
                    "context": context,
                    "line_number": i + 1,
                    "suggested_description": context[:100]
                })
    
    # Add the events
    added_events = []
    for event_data in events_found:
        result = add_event(
            date_string=event_data["date_string"],
            description=event_data["suggested_description"],
            parties=default_parties,
            document_source=document_name,
            document_excerpt=event_data["context"],
            tags=["auto-extracted"]
        )
        if result["status"] == "success":
            added_events.append(result["event_id"])
    
    return {
        "status": "success",
        "events_found": len(events_found),
        "events_added": len(added_events),
        "event_ids": added_events,
        "message": f"Extracted {len(added_events)} events from {document_name}"
    }

@mcp.tool()
def search_timeline(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    parties: Optional[List[str]] = None,
    keywords: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> List[Dict]:
    """Search chronology by date range, parties, keywords, or tags"""
    data = load_chronology()
    results = []
    
    # Parse date range if provided
    start = parser.parse(start_date).date() if start_date else None
    end = parser.parse(end_date).date() if end_date else None
    
    for event in data["events"]:
        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
        
        # Date range filter
        if start and event_date < start:
            continue
        if end and event_date > end:
            continue
        
        # Party filter
        if parties and not any(p in event["parties"] for p in parties):
            continue
        
        # Keyword filter
        if keywords:
            searchable = f"{event['description']} {event['document_excerpt']} {event['significance']}"
            if keywords.lower() not in searchable.lower():
                continue
        
        # Tag filter
        if tags and not any(t in event["tags"] for t in tags):
            continue
        
        results.append(event)
    
    # Sort by date
    results.sort(key=lambda x: x["date"])
    return results

@mcp.tool()
def get_timeline_summary() -> Dict:
    """Get summary statistics about the chronology"""
    data = load_chronology()
    
    if not data["events"]:
        return {
            "total_events": 0,
            "date_range": "No events",
            "parties": [],
            "documents": []
        }
    
    # Sort events by date
    sorted_events = sorted(data["events"], key=lambda x: x["date"])
    
    return {
        "total_events": len(data["events"]),
        "date_range": f"{sorted_events[0]['date']} to {sorted_events[-1]['date']}",
        "parties": list(data["parties"].keys()),
        "documents": list(data["documents"].keys()),
        "tags": list(set(tag for event in data["events"] for tag in event["tags"]))
    }

@mcp.tool()
def export_chronology(
    format: str = "markdown",
    include_documents: bool = True,
    include_significance: bool = True
) -> str:
    """Export chronology in various formats"""
    data = load_chronology()
    
    if not data["events"]:
        return "No events in chronology"
    
    # Sort events by date
    sorted_events = sorted(data["events"], key=lambda x: x["date"])
    
    if format == "markdown":
        result = ["# Case Chronology\n"]
        result.append(f"*Generated on {datetime.now().strftime('%B %d, %Y')}*\n")
        
        for event in sorted_events:
            date_str = event["date"]
            if event["date_precision"] != "exact":
                date_str += f" ({event['date_precision']})"
            
            result.append(f"\n## {date_str}")
            result.append(f"\n{event['description']}\n")
            
            if event["parties"]:
                result.append(f"**Parties:** {', '.join(event['parties'])}\n")
            
            if include_documents and event["document_source"]:
                result.append(f"**Source:** {event['document_source']}\n")
                if event["document_excerpt"]:
                    result.append(f"> {event['document_excerpt']}\n")
            
            if include_significance and event["significance"]:
                result.append(f"**Significance:** {event['significance']}\n")
            
            if event["tags"]:
                result.append(f"**Tags:** {', '.join(event['tags'])}\n")
        
        return "\n".join(result)
    
    elif format == "csv":
        lines = ["Date,Precision,Description,Parties,Document,Tags"]
        for event in sorted_events:
            lines.append(
                f'"{event["date"]}","{event["date_precision"]}",'
                f'"{event["description"]}","{"|".join(event["parties"])}",'
                f'"{event["document_source"]}","{"|".join(event["tags"])}"'
            )
        return "\n".join(lines)
    
    elif format == "brief":
        lines = []
        for event in sorted_events:
            date_str = event["date"]
            if event["date_precision"] != "exact":
                date_str += f" ({event['date_precision']})"
            lines.append(f"{date_str}: {event['description']}")
        return "\n".join(lines)
    
    else:
        return json.dumps(sorted_events, indent=2, default=str)

@mcp.tool()
def update_event(
    event_id: int,
    date_string: Optional[str] = None,
    description: Optional[str] = None,
    parties: Optional[List[str]] = None,
    significance: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict:
    """Update an existing chronology event"""
    data = load_chronology()
    
    for event in data["events"]:
        if event["id"] == event_id:
            if date_string:
                event_date, precision = parse_date_with_precision(date_string)
                event["date"] = str(event_date)
                event["date_precision"] = precision
            
            if description:
                event["description"] = description
            
            if parties is not None:
                # Update party index
                for old_party in event["parties"]:
                    if old_party in data["parties"]:
                        data["parties"][old_party].remove(event_id)
                
                event["parties"] = parties
                for party in parties:
                    if party not in data["parties"]:
                        data["parties"][party] = []
                    data["parties"][party].append(event_id)
            
            if significance is not None:
                event["significance"] = significance
            
            if tags is not None:
                event["tags"] = tags
            
            event["updated_at"] = datetime.now().isoformat()
            save_chronology(data)
            
            return {"status": "success", "message": f"Updated event {event_id}"}
    
    return {"status": "error", "message": f"Event {event_id} not found"}

@mcp.tool()
def delete_event(event_id: int) -> Dict:
    """Delete a chronology event"""
    data = load_chronology()
    
    # Find and remove event
    event_to_delete = None
    for i, event in enumerate(data["events"]):
        if event["id"] == event_id:
            event_to_delete = data["events"].pop(i)
            break
    
    if event_to_delete:
        # Update party index
        for party in event_to_delete["parties"]:
            if party in data["parties"]:
                data["parties"][party].remove(event_id)
                if not data["parties"][party]:
                    del data["parties"][party]
        
        # Update document index
        doc_source = event_to_delete["document_source"]
        if doc_source and doc_source in data["documents"]:
            data["documents"][doc_source].remove(event_id)
            if not data["documents"][doc_source]:
                del data["documents"][doc_source]
        
        save_chronology(data)
        return {"status": "success", "message": f"Deleted event {event_id}"}
    
    return {"status": "error", "message": f"Event {event_id} not found"}

@mcp.resource("schema://chronology")
def get_schema() -> str:
    """Provide information about the chronology data structure"""
    return """Case Chronology Schema:
    
    Event Structure:
    - id: Unique identifier
    - date: ISO date string (YYYY-MM-DD)
    - date_precision: "exact", "approximate", "month", "quarter"
    - description: Brief description of the event
    - parties: List of parties involved
    - document_source: Source document name/identifier
    - document_excerpt: Relevant excerpt from source
    - tags: Categorization tags
    - significance: Why this event matters to the case
    - created_at: Timestamp of creation
    - updated_at: Timestamp of last update
    
    Date Parsing Examples:
    - "3/15/2023" → exact date
    - "March 2023" → month precision
    - "early March 2023" → approximate (uses March 1)
    - "mid March 2023" → approximate (uses March 15)
    - "late March 2023" → approximate (uses March 28)
    - "Q1 2023" → quarter precision
    - "around 3/15/2023" → approximate
    """

def main():
    """Entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()