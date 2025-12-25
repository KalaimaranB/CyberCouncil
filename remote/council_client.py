#!/usr/bin/env python3
"""
CyberCouncil Remote Client

CLI client for interacting with CyberCouncil from Kali VM.

Usage:
    ./council-client.py "Found DC at 10.10.10.5"
    ./council-client.py --file nmap_output.txt
    ./council-client.py --crack "aad3b435..."
    
Setup:
    1. On host machine: python council.py, then /server start
    2. On Kali: ./council-client.py --host HOST_IP "message"
"""

import argparse
import requests
import sys
import os

DEFAULT_HOST = "192.168.1.1"  # Change to your host IP
DEFAULT_PORT = 5051


def send_message(host: str, port: int, message: str):
    """Send a message to Council."""
    url = f"http://{host}:{port}/api/send"
    try:
        response = requests.post(url, json={'message': message}, timeout=120)
        data = response.json()
        
        if data.get('status') == 'processed':
            print(f"\n✅ Response:\n{data.get('response', 'No response')}")
        else:
            print(f"\n⚠️  {data.get('message', 'Unknown status')}")
            
    except requests.ConnectionError:
        print(f"\n❌ Could not connect to {host}:{port}")
        print("   Is the Council server running? Use '/server start' in Council.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def import_file(host: str, port: int, filepath: str):
    """Import tool output from file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        output = f.read()
    
    url = f"http://{host}:{port}/api/import"
    try:
        response = requests.post(url, json={'output': output}, timeout=30)
        data = response.json()
        print(f"✅ {data.get('message', 'Imported')}")
    except Exception as e:
        print(f"❌ Error: {e}")


def crack_hash(host: str, port: int, hash_str: str, wordlist: str = None):
    """Send hash for cracking."""
    url = f"http://{host}:{port}/api/crack"
    payload = {'hash': hash_str}
    if wordlist:
        payload['wordlist'] = wordlist
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        print(f"✅ {data.get('message', 'Queued')}")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_status(host: str, port: int):
    """Check server status."""
    url = f"http://{host}:{port}/api/status"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        print(f"✅ Server: {data.get('status')}")
        print(f"   Project: {data.get('project', 'None')}")
    except requests.ConnectionError:
        print(f"❌ Server not reachable at {host}:{port}")


def main():
    parser = argparse.ArgumentParser(
        description="CyberCouncil Remote Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Found DC at 10.10.10.5"
  %(prog)s --file nmap_output.txt
  %(prog)s --crack "31d6cfe0d16ae931b73c59d7e0c089c0"
  %(prog)s --status
        """
    )
    
    parser.add_argument('message', nargs='?', help='Message to send')
    parser.add_argument('--host', '-H', default=DEFAULT_HOST, 
                       help=f'Host IP (default: {DEFAULT_HOST})')
    parser.add_argument('--port', '-p', type=int, default=DEFAULT_PORT,
                       help=f'Port (default: {DEFAULT_PORT})')
    parser.add_argument('--file', '-f', help='Import tool output from file')
    parser.add_argument('--crack', '-c', help='Hash to crack')
    parser.add_argument('--wordlist', '-w', help='Wordlist for cracking')
    parser.add_argument('--status', '-s', action='store_true', 
                       help='Check server status')
    
    args = parser.parse_args()
    
    if args.status:
        check_status(args.host, args.port)
    elif args.file:
        import_file(args.host, args.port, args.file)
    elif args.crack:
        crack_hash(args.host, args.port, args.crack, args.wordlist)
    elif args.message:
        send_message(args.host, args.port, args.message)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
