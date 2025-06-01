#!/usr/bin/env python3
"""Test script for the Case Chronology MCP Server"""

import json
from chronology_server import (
    add_event, 
    parse_document, 
    search_timeline, 
    get_timeline_summary,
    export_chronology,
    parse_date_with_precision
)

print("Testing Case Chronology MCP Server\n")

# Test 1: Date parsing
print("1. Testing date parsing:")
test_dates = [
    "3/15/2023",
    "March 15, 2023",
    "March 2023",
    "early March 2023",
    "mid March 2023",
    "late March 2023",
    "Q1 2023",
    "around 3/15/2023"
]

for date_str in test_dates:
    try:
        date, precision = parse_date_with_precision(date_str)
        print(f"  '{date_str}' -> {date} ({precision})")
    except Exception as e:
        print(f"  '{date_str}' -> ERROR: {e}")

# Test 2: Adding events
print("\n2. Testing event addition:")
events = [
    {
        "date_string": "January 10, 2023",
        "description": "Contract signed between Smith Corp and Jones LLC",
        "parties": ["Smith Corp", "Jones LLC"],
        "tags": ["contract", "agreement"],
        "significance": "Initial agreement establishing terms"
    },
    {
        "date_string": "March 1, 2023",
        "description": "Delivery deadline missed by Jones LLC",
        "parties": ["Jones LLC"],
        "tags": ["breach", "deadline"],
        "significance": "First instance of non-performance"
    },
    {
        "date_string": "March 15, 2023",
        "description": "Smith Corp sends breach notification email",
        "parties": ["Smith Corp", "Jones LLC"],
        "document_source": "Email_03152023.pdf",
        "tags": ["breach", "notice"],
        "significance": "Formal notice of breach"
    }
]

for event in events:
    result = add_event(**event)
    print(f"  Added: {result['message']}")

# Test 3: Timeline summary
print("\n3. Getting timeline summary:")
summary = get_timeline_summary()
print(f"  Total events: {summary['total_events']}")
print(f"  Date range: {summary['date_range']}")
print(f"  Parties: {', '.join(summary['parties'])}")
print(f"  Tags: {', '.join(summary['tags'])}")

# Test 4: Search functionality
print("\n4. Testing search:")
march_events = search_timeline(start_date="3/1/2023", end_date="3/31/2023")
print(f"  Events in March 2023: {len(march_events)}")

breach_events = search_timeline(tags=["breach"])
print(f"  Events tagged 'breach': {len(breach_events)}")

# Test 5: Document parsing
print("\n5. Testing document parsing:")
test_document = """
From: Bob Smith, CEO Smith Corp
To: Alice Jones, President Jones LLC
Date: March 15, 2023
Subject: Notice of Breach

Dear Ms. Jones,

This letter serves as formal notice that as of March 1, 2023, Jones LLC has failed 
to deliver the goods specified in our agreement dated January 10, 2023. The contract 
clearly states that delivery was due by March 1, 2023.

We first discussed this matter on February 20, 2023 during our conference call.

Please respond by March 20, 2023 with your proposed remedy.

Sincerely,
Bob Smith
"""

parse_result = parse_document(
    content=test_document,
    document_name="Breach_Notice_Email.pdf",
    default_parties=["Smith Corp", "Jones LLC"]
)
print(f"  Found {parse_result['events_found']} dates")
print(f"  Added {parse_result['events_added']} events")

# Test 6: Export formats
print("\n6. Testing export formats:")
print("\n  Brief timeline:")
brief = export_chronology(format="brief")
for line in brief.split('\n')[:3]:
    print(f"    {line}")

print("\n7. Final summary:")
final_summary = get_timeline_summary()
print(f"  Total events in chronology: {final_summary['total_events']}")

# Clean up test data
import os
if os.path.exists('case_chronology.json'):
    os.remove('case_chronology.json')
    print("\n✓ Test data cleaned up")