from typing import List, Dict, Any, Optional, Tuple
from mcp.server.fastmcp import FastMCP
import ngrok
import argparse

from datetime import datetime
from whatsapp import (
    search_contacts as whatsapp_search_contacts,
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message
)

PORT = 8055

# Initialize FastMCP server
mcp = FastMCP("whatsapp", port=PORT)

@mcp.tool()
def search_contacts(query: str) -> List[Dict[str, Any]]:
    """Search WhatsApp contacts by name or phone number.
    
    Args:
        query: Search term to match against contact names or phone numbers
    """
    contacts = whatsapp_search_contacts(query)
    return contacts

@mcp.tool()
def list_messages(
    date_range: Optional[List[datetime]] = None,
    sender_phone_number: Optional[str] = None,
    chat_jid: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_context: bool = True,
    context_before: int = 1,
    context_after: int = 1
) -> List[Dict[str, Any]]:
    """Get WhatsApp messages matching specified criteria with optional context.
    
    Args:
        date_range: Optional tuple of (start_date, end_date) to filter messages by date
        sender_phone_number: Optional phone number to filter messages by sender
        chat_jid: Optional chat JID to filter messages by chat
        query: Optional search term to filter messages by content
        limit: Maximum number of messages to return (default 20)
        page: Page number for pagination (default 0)
        include_context: Whether to include messages before and after matches (default True)
        context_before: Number of messages to include before each match (default 1)
        context_after: Number of messages to include after each match (default 1)
    """
    messages = whatsapp_list_messages(
        date_range=date_range,
        sender_phone_number=sender_phone_number,
        chat_jid=chat_jid,
        query=query,
        limit=limit,
        page=page,
        include_context=include_context,
        context_before=context_before,
        context_after=context_after
    )
    return messages

@mcp.tool()
def list_chats(
    query: Optional[str] = None,
    limit: int = 20,
    page: int = 0,
    include_last_message: bool = True,
    sort_by: str = "last_active"
) -> List[Dict[str, Any]]:
    """Get WhatsApp chats matching specified criteria.
    
    Args:
        query: Optional search term to filter chats by name or JID
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
        include_last_message: Whether to include the last message in each chat (default True)
        sort_by: Field to sort results by, either "last_active" or "name" (default "last_active")
    """
    chats = whatsapp_list_chats(
        query=query,
        limit=limit,
        page=page,
        include_last_message=include_last_message,
        sort_by=sort_by
    )
    return chats

@mcp.tool()
def get_chat(chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by JID.
    
    Args:
        chat_jid: The JID of the chat to retrieve
        include_last_message: Whether to include the last message (default True)
    """
    chat = whatsapp_get_chat(chat_jid, include_last_message)
    return chat

@mcp.tool()
def get_direct_chat_by_contact(sender_phone_number: str) -> Dict[str, Any]:
    """Get WhatsApp chat metadata by sender phone number.
    
    Args:
        sender_phone_number: The phone number to search for
    """
    chat = whatsapp_get_direct_chat_by_contact(sender_phone_number)
    return chat

@mcp.tool()
def get_contact_chats(jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
    """Get all WhatsApp chats involving the contact.
    
    Args:
        jid: The contact's JID to search for
        limit: Maximum number of chats to return (default 20)
        page: Page number for pagination (default 0)
    """
    chats = whatsapp_get_contact_chats(jid, limit, page)
    return chats

@mcp.tool()
def get_last_interaction(jid: str) -> Dict[str, Any]:
    """Get most recent WhatsApp message involving the contact.
    
    Args:
        jid: The JID of the contact to search for
    """
    message = whatsapp_get_last_interaction(jid)
    return message

@mcp.tool()
def get_message_context(
    message_id: str,
    before: int = 5,
    after: int = 5
) -> Dict[str, Any]:
    """Get context around a specific WhatsApp message.
    
    Args:
        message_id: The ID of the message to get context for
        before: Number of messages to include before the target message (default 5)
        after: Number of messages to include after the target message (default 5)
    """
    context = whatsapp_get_message_context(message_id, before, after)
    return context

@mcp.tool()
def send_message(
    recipient: str,
    message: str
) -> Dict[str, Any]:
    """Send a WhatsApp message to a person or group. For group chats use the JID.

    Args:
        recipient: The recipient - either a phone number with country code but no + or other symbols,
                 or a JID (e.g., "123456789@s.whatsapp.net" or a group JID like "123456789@g.us")
        message: The message text to send
    
    Returns:
        A dictionary containing success status and a status message
    """
    # Validate input
    if not recipient:
        return {
            "success": False,
            "message": "Recipient must be provided"
        }
    
    # Call the whatsapp_send_message function with the unified recipient parameter
    success, status_message = whatsapp_send_message(recipient, message)
    return {
        "success": success,
        "message": status_message
    }

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='WhatsApp MCP Server')
    parser.add_argument('--ngrok-token', type=str, help='Ngrok authentication token')
    args = parser.parse_args()

    # Initialize and run the server
    ngrok_token = args.ngrok_token
    
    # Try to get token from environment if not provided as argument
    if not ngrok_token:
        try:
            # Test if we can connect using environment variable
            test_listener = ngrok.forward(PORT, authtoken_from_env=True)
            test_listener.close()
            print("✅ Using ngrok token from environment")
        except Exception:
            # Prompt for token if not in environment
            print("\n⚠️  No ngrok authentication token found in environment variables.")
            import getpass
            ngrok_token = getpass.getpass("Please enter your ngrok authentication token: ").strip()
            if not ngrok_token:
                print("❌ Error: Ngrok authentication token is required")
                exit(1)

    # Connect using the token (either from args, env, or user input)
    try:
        listener = ngrok.forward(
            PORT,
            authtoken=ngrok_token if ngrok_token else None,
            authtoken_from_env=True if not ngrok_token else False
        )
        print("\n" + "="*50)
        print("\n🌍 MCP Server is running!")
        print("\n📋 Copy this URL to connect:")
        print(f"\n    \033[1m{listener.url()}/sse\033[0m")
        print("\n⚠️  Warning: Be careful sharing this URL publicly!")
        print("\n❌ Press Ctrl+C to stop the server")
        print("\n" + "="*50 + "\n")
        mcp.run(transport='sse')
    except Exception as e:
        print(f"\n❌ Error connecting to ngrok: {str(e)}")
        exit(1)