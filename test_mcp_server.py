#!/usr/bin/env python3
"""
Test script for Mistral PDF OCR MCP server

Tests the main functionalities of the server.
"""

import asyncio
import json
from pathlib import Path

# Simulate MCP tool calls


async def test_mcp_tools():
    """Tests MCP tools."""

    print("🧪 Testing Mistral PDF OCR MCP Server\n")
    print("=" * 60)

    # Import server
    try:
        from mistral_mcp_server import mcp
        list_tools = mcp.list_tools
        call_tool = mcp.call_tool
        print("✅ MCP server imported successfully\n")
    except Exception as e:
        print(f"❌ Error importing server: {e}")
        return

    # Test 1: List tools
    print("📋 Test 1: List available tools")
    print("-" * 60)
    try:
        tools = await list_tools()
        print(f"✅ Found {len(tools)} tools:\n")
        for tool in tools:
            print(f"  🔧 {tool.name}")
            print(f"     {tool.description[:80]}...")
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Test 2: Get PDF info (if sample exists)
    print("📊 Test 2: Get PDF information")
    print("-" * 60)

    sample_pdf = Path("sample/sample.pdf")
    if sample_pdf.exists():
        try:
            result = await call_tool(
                name="get_pdf_info",
                arguments={"pdf_paths": [str(sample_pdf.absolute())]}
            )
            if isinstance(result, tuple):
                result = result[0]
            print(f"✅ Result:")
            for content in result:
                print(content.text)
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    else:
        print(f"⚠️ sample.pdf not found, skipping test\n")

    # Test 3: List Mistral files
    print("📂 Test 3: List files in Mistral service")
    print("-" * 60)
    try:
        result = await call_tool(
            name="list_mistral_files",
            arguments={}
        )
        if isinstance(result, tuple):
            result = result[0]
        print(f"✅ Result:")
        for content in result:
            print(content.text)
        print()
    except Exception as e:
        print(f"⚠️ Note: {e}")
        print("   (This may be expected if API key is not configured)\n")

    # Test 4: Process sample PDF (COMMENTED - uncomment to test)
    # print("🔄 Test 4: Process sample PDF")
    # print("-" * 60)
    # if sample_pdf.exists():
    #     try:
    #         result = await call_tool(
    #             name="process_pdf",
    #             arguments={
    #                 "pdf_path": str(sample_pdf.absolute()),
    #                 "save_images": False  # Text only for quick test
    #             }
    #         )
    #         if isinstance(result, tuple):
    #             result = result[0]
    #         print(f"✅ Result:")
    #         for content in result:
    #             print(content.text)
    #         print()
    #     except Exception as e:
    #         print(f"❌ Error: {e}\n")
    # else:
    #     print(f"⚠️ sample.pdf not found, skipping test\n")

    print("=" * 60)
    print("✅ Tests completed!")
    print("\n💡 Tip: To test actual processing, uncomment Test 4")
    print("   and make sure you have the Mistral API key configured.\n")


async def test_tool_schemas():
    """Validates tool schemas."""
    print("\n🔍 Validating tool schemas...")
    print("-" * 60)

    from mistral_mcp_server import mcp

    tools = await mcp.list_tools()

    for tool in tools:
        print(f"\n📝 {tool.name}")
        print(f"   Schema valid: ", end="")

        # Validate inputSchema exists
        if hasattr(tool, 'inputSchema'):
            schema = tool.inputSchema

            # Validate basic structure
            if 'type' in schema and 'properties' in schema:
                # Validate required fields
                required = schema.get('required', [])
                props = schema['properties']

                missing_required = [r for r in required if r not in props]
                if missing_required:
                    print(f"❌ Missing required fields: {missing_required}")
                else:
                    print("✅")

                    # Show parameters
                    if props:
                        print("   Parameters:")
                        for param, details in props.items():
                            req = " (required)" if param in required else " (optional)"
                            ptype = details.get('type', 'any')
                            print(f"     • {param}: {ptype}{req}")
            else:
                print("❌ Invalid schema")
        else:
            print("❌ inputSchema not defined")

    print("\n" + "=" * 60)


def test_pdf_page_extraction():
    """Unit test for PDF page range validation and extraction error handling."""
    print("🧪 Test 5: PDF page range validation")
    print("-" * 60)

    from mistral_core import process_pdf_pages
    sample_pdf = Path("sample/sample.pdf")

    if sample_pdf.exists():
        # Test 1: Invalid page range (start > total)
        success, message, count = process_pdf_pages(
            pdf_path=str(sample_pdf.absolute()),
            md_path="dummy.md",
            start_page=5,
            end_page=10,
            save_images=False
        )
        if not success and "exceeds total pages" in message:
            print("✅ Successfully caught out of bounds page range")
        else:
            print(f"❌ Failed out of bounds test: {message}")

        # Test 2: Invalid page range (end < start)
        success, message, count = process_pdf_pages(
            pdf_path=str(sample_pdf.absolute()),
            md_path="dummy.md",
            start_page=3,
            end_page=2,
            save_images=False
        )
        if not success and "less than start page" in message:
            print("✅ Successfully caught invalid interval (end < start)")
        else:
            print(f"❌ Failed invalid interval test: {message}")
    else:
        print("⚠️ sample.pdf not found, skipping unit test")


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print(" Mistral PDF OCR - MCP Server Test Suite")
    print("=" * 60 + "\n")

    # Run tests
    asyncio.run(test_mcp_tools())
    asyncio.run(test_tool_schemas())
    test_pdf_page_extraction()

    print("\n🎉 All validation tests completed!\n")


if __name__ == "__main__":
    main()
