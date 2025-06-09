#!/usr/bin/env python3
"""
MCP Architecture Main Script
Run this to test the complete MCP setup locally
"""

import asyncio
import json
import time
from mcp_client.client import mcp_client
from mcp_server.server import run_server
from utils.logger import logger
import threading
import sys

def start_server_in_background():
    """Start MCP server in background thread"""
    try:
        logger.info("Starting MCP server in background...")
        run_server()
    except Exception as e:
        logger.error("Failed to start server", error=str(e))

def wait_for_server():
    """Wait for server to be ready"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            health = mcp_client.health_check()
            if health.get("status") == "healthy":
                logger.info("Server is ready!")
                return True
        except:
            pass

        logger.info(f"Waiting for server... ({attempt + 1}/{max_attempts})")
        time.sleep(1)

    logger.error("Server failed to start within timeout")
    return False

def test_mcp_architecture():
    """Test the complete MCP architecture"""
    print("\n" + "="*60)
    print("🚀 TESTING MCP ARCHITECTURE")
    print("="*60)

    # 1. Test server health
    print("\n1. Testing Server Health...")
    health = mcp_client.health_check()
    print(f"   Status: {health.get('status')}")
    print(f"   Tools Count: {health.get('tools_count', 0)}")

    # 2. List available tools
    print("\n2. Available Tools...")
    tools = mcp_client.list_available_tools()
    for tool in tools:
        print(f"   • {tool['name']}: {tool['description']}")

    # 3. Test MongoDB search tool directly
    print("\n3. Testing MongoDB Search Tool...")
    search_result = mcp_client.search_documents(
        query={},  # Empty query to get all documents
        limit=5
    )

    if search_result.get("success"):
        documents = search_result.get("data", [])
        metadata = search_result.get("metadata", {})

        print(f"   ✅ Search successful!")
        print(f"   📊 Total documents: {metadata.get('total_count', 0)}")
        print(f"   📄 Returned: {len(documents)}")

        if documents:
            print(f"   📋 Sample document fields: {list(documents[0].keys())}")
        else:
            print(f"   ⚠️  No documents found in collection")
    else:
        print(f"   ❌ Search failed: {search_result.get('error')}")

    # 4. Test prompt processing
    print("\n4. Testing Prompt Processing...")
    test_prompts = [
        "find all documents",
        "search for python",
        "show me recent data"
    ]

    for prompt in test_prompts:
        print(f"\n   Prompt: '{prompt}'")
        result = mcp_client.process_prompt(prompt)

        if result.get("success"):
            docs_count = len(result.get("data", []))
            total_count = result.get("metadata", {}).get("total_count", 0)
            print(f"   ✅ Found {docs_count} documents (total: {total_count})")
        else:
            print(f"   ❌ Failed: {result.get('error')}")

    print("\n" + "="*60)
    print("🎉 MCP ARCHITECTURE TEST COMPLETED")
    print("="*60)

def interactive_mode():
    """Interactive mode for testing prompts"""
    print("\n" + "="*60)
    print("🔧 INTERACTIVE MCP CLIENT")
    print("="*60)
    print("Enter prompts to search your MongoDB collection.")
    print("Type 'quit' to exit, 'tools' to list available tools.")
    print("Type 'help' for examples.")

    while True:
        try:
            prompt = input("\n🔍 Enter prompt: ").strip()

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            elif prompt.lower() == 'tools':
                tools = mcp_client.list_available_tools()
                print("\n📋 Available Tools:")
                for tool in tools:
                    print(f"   • {tool['name']}: {tool['description']}")
                continue

            elif prompt.lower() == 'help':
                print("\n📚 Example prompts to try:")
                print("   • 'find all documents'")
                print("   • 'search for python programming'")
                print("   • 'show me user data'")
                print("   • 'get recent entries'")
                continue

            elif not prompt:
                continue

            # Process the prompt
            print(f"\n⏳ Processing: '{prompt}'...")
            result = mcp_client.process_prompt(prompt)

            if result.get("success"):
                documents = result.get("data", [])
                metadata = result.get("metadata", {})

                print(f"\n✅ Results:")
                print(f"   📊 Total matches: {metadata.get('total_count', 0)}")
                print(f"   📄 Showing: {len(documents)}")

                # Display documents
                for i, doc in enumerate(documents[:3], 1):  # Show first 3
                    print(f"\n   📋 Document {i}:")
                    print(f"      ID: {doc.get('_id', 'N/A')}")

                    # Display key fields (customize based on your data structure)
                    for key, value in doc.items():
                        if key != '_id' and len(str(value)) < 100:
                            print(f"      {key}: {value}")

                if len(documents) > 3:
                    print(f"   ... and {len(documents) - 3} more documents")

            else:
                print(f"\n❌ Error: {result.get('error')}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "interactive"

    if command == "server":
        # Run only server
        logger.info("Starting MCP server...")
        run_server()

    elif command == "test":
        # Run server in background and test
        server_thread = threading.Thread(target=start_server_in_background, daemon=True)
        server_thread.start()

        if wait_for_server():
            test_mcp_architecture()
        else:
            print("❌ Server failed to start. Please check your MongoDB connection.")

    elif command == "interactive":
        # Run server in background and start interactive mode
        print("🚀 Starting MCP Architecture...")
        server_thread = threading.Thread(target=start_server_in_background, daemon=True)
        server_thread.start()

        if wait_for_server():
            interactive_mode()
        else:
            print("❌ Server failed to start. Please check your MongoDB connection.")

    else:
        print("Usage:")
        print("  python main.py server      # Run server only")
        print("  python main.py test        # Run tests")
        print("  python main.py interactive # Interactive mode (default)")

if __name__ == "__main__":
    main()