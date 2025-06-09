# test_document_count.py
"""
Simple test to get total count of all documents using MongoDB Search Tool
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from mcp_server.tools.mongodb_search_tool import MongoDBSearchTool
from database.mongodb_client import mongodb_client

async def test_total_document_count():
    """
    Test function to get total count of all documents
    """
    print("Testing MongoDB Search Tool - Getting total document count...")

    try:
        # Initialize the MongoDB search tool
        search_tool = MongoDBSearchTool()

        # Create input for getting all documents (empty query = match all)
        test_inputs = {
            "query": {},  # Empty query matches all documents
            "limit": 1,   # We only need 1 document since we're interested in total count
            "skip": 0
        }

        # Execute the search
        result = await search_tool.execute(test_inputs)

        if result.success:
            print("✅ Search executed successfully!")
            print(f"📊 Total document count: {result.metadata['total_count']}")
            print(f"📄 Documents returned: {result.metadata['returned_count']}")
            print(f"🔍 Query used: {result.metadata['query']}")

            # If you want to see a sample document structure
            if result.data:
                print("\n📋 Sample document structure:")
                sample_doc = result.data[0]
                for key in sample_doc.keys():
                    print(f"  - {key}: {type(sample_doc[key]).__name__}")
        else:
            print("❌ Search failed!")
            print(f"Error: {result.error}")

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")

async def test_direct_mongodb_count():
    """
    Alternative: Direct test using MongoDB client
    """
    print("\n" + "="*50)
    print("Direct MongoDB Client Test - Getting total count...")

    try:
        # Get total count directly from MongoDB client
        total_count = mongodb_client.count_documents({})  # Empty query = count all
        print(f"📊 Total documents in collection: {total_count}")

        # You can also test with specific queries
        # Example: Count documents with a specific field
        # count_with_name = mongodb_client.count_documents({"name": {"$exists": True}})
        # print(f"📊 Documents with 'name' field: {count_with_name}")

    except Exception as e:
        print(f"❌ Direct count test failed: {str(e)}")

async def main():
    """
    Main test function
    """
    print("🚀 Starting MongoDB Document Count Tests")
    print("="*50)

    # Test 1: Using the MCP MongoDB Search Tool
    await test_total_document_count()

    # Test 2: Direct MongoDB client test
    await test_direct_mongodb_count()

    print("\n✅ All tests completed!")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())