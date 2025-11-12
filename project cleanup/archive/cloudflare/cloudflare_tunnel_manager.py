#!/usr/bin/env python3
"""
Cloudflare Tunnel Manager - Create and Manage Persistent Tunnels
Part of Conductor SMS System

Usage:
    python cloudflare_tunnel_manager.py create --name "n8n-tunnel" --subdomain "n8n" --zone-id ZONE_ID
    python cloudflare_tunnel_manager.py list
    python cloudflare_tunnel_manager.py delete --tunnel-id TUNNEL_ID
    
Architecture:
    API-based tunnel creation and management for n8n integration
"""

import requests
import json
import sys
import logging
import argparse
import time
from typing import Optional, Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cloudflare_tunnels.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
DEFAULT_ACCOUNT_ID = "ed835396a75f0a35ea698cc764615662"  # From your curl command
DEFAULT_TOKEN = "4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf"  # From your curl command

class CloudflareTunnelManager:
    """Cloudflare Tunnel management client"""
    
    def __init__(self, account_id: str, token: str):
        """
        Initialize Cloudflare Tunnel Manager
        
        Args:
            account_id: Cloudflare account ID
            token: API token with Tunnel:Edit and DNS:Edit permissions
        """
        self.account_id = account_id
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def create_tunnel(self, name: str, config_src: str = "cloudflare") -> Dict[str, Any]:
        """
        Create a new Cloudflare tunnel
        
        Args:
            name: Tunnel name (e.g., "n8n-tunnel")
            config_src: Configuration source (default: "cloudflare")
            
        Returns:
            Dict containing tunnel creation response or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/cfd_tunnel"
        
        payload = {
            "name": name,
            "config_src": config_src
        }
        
        try:
            logger.info(f"Creating tunnel: {name}")
            logger.debug(f"API URL: {url}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Tunnel created successfully")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Tunnel creation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": error_data
                    }
                except:
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "error": response.text
                    }
                    
        except requests.exceptions.Timeout:
            logger.error("[ERROR] Request timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except requests.exceptions.ConnectionError:
            logger.error("[ERROR] Connection error")
            return {
                "success": False,
                "error": "Connection error"
            }
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_tunnels(self) -> Dict[str, Any]:
        """
        List all tunnels in the account
        
        Returns:
            Dict containing tunnels list or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/cfd_tunnel"
        
        try:
            logger.info("Fetching tunnel list...")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Tunnels retrieved successfully")
                return {
                    "success": True,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Failed to get tunnels: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Error getting tunnels: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_tunnel(self, tunnel_id: str) -> Dict[str, Any]:
        """
        Delete a tunnel
        
        Args:
            tunnel_id: ID of tunnel to delete
            
        Returns:
            Dict containing deletion response or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/cfd_tunnel/{tunnel_id}"
        
        try:
            logger.info(f"Deleting tunnel: {tunnel_id}")
            response = requests.delete(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Tunnel deleted successfully")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Failed to delete tunnel: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Error deleting tunnel: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_dns_record(self, zone_id: str, subdomain: str, tunnel_id: str, domain: str) -> Dict[str, Any]:
        """
        Create DNS CNAME record for tunnel
        
        Args:
            zone_id: Cloudflare zone ID
            subdomain: Subdomain (e.g., "n8n")
            tunnel_id: Tunnel ID
            domain: Base domain (e.g., "marketsuite.co")
            
        Returns:
            Dict containing DNS creation response or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records"
        
        payload = {
            "type": "CNAME",
            "name": f"{subdomain}.{domain}",
            "content": f"{tunnel_id}.cfargotunnel.com",
            "ttl": 1,
            "proxied": True
        }
        
        try:
            logger.info(f"Creating DNS record: {subdomain}.{domain} -> {tunnel_id}.cfargotunnel.com")
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] DNS record created successfully")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Failed to create DNS record: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Error creating DNS record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_tunnel_token(self, tunnel_id: str) -> Dict[str, Any]:
        """
        Get tunnel token for cloudflared authentication
        
        Args:
            tunnel_id: Tunnel ID
            
        Returns:
            Dict containing tunnel token or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/cfd_tunnel/{tunnel_id}/token"
        
        try:
            logger.info(f"Getting token for tunnel: {tunnel_id}")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Tunnel token retrieved successfully")
                return {
                    "success": True,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Failed to get tunnel token: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Error getting tunnel token: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def print_tunnel_info(tunnel_data: Dict[str, Any]):
    """Print formatted tunnel information"""
    if tunnel_data.get("success"):
        result = tunnel_data["data"].get("result", {})
        print(f"Tunnel ID: {result.get('id', 'N/A')}")
        print(f"Name: {result.get('name', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Created: {result.get('created_at', 'N/A')}")
        if 'token' in result:
            print(f"Token: {result['token']}")
    else:
        print("[FAILED]")
        if "error" in tunnel_data:
            print(f"Error: {tunnel_data['error']}")

def print_tunnels_list(tunnels_data: Dict[str, Any]):
    """Print formatted tunnels list"""
    if tunnels_data.get("success"):
        results = tunnels_data["data"].get("result", [])
        if not results:
            print("No tunnels found")
            return
            
        print(f"Found {len(results)} tunnel(s):")
        print("-" * 60)
        for tunnel in results:
            print(f"ID: {tunnel.get('id', 'N/A')}")
            print(f"Name: {tunnel.get('name', 'N/A')}")
            print(f"Status: {tunnel.get('status', 'N/A')}")
            print(f"Created: {tunnel.get('created_at', 'N/A')}")
            print("-" * 60)
    else:
        print("[FAILED]")
        if "error" in tunnels_data:
            print(f"Error: {tunnels_data['error']}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Cloudflare Tunnel Manager")
    parser.add_argument("command", choices=["create", "list", "delete", "get-token"], help="Command to execute")
    parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID, help="Cloudflare account ID")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="API token")
    parser.add_argument("--name", help="Tunnel name (for create)")
    parser.add_argument("--tunnel-id", help="Tunnel ID (for delete)")
    parser.add_argument("--subdomain", help="Subdomain for DNS record (for create)")
    parser.add_argument("--zone-id", help="Zone ID for DNS record (for create)")
    parser.add_argument("--domain", default="marketsuite.co", help="Base domain (for create)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Mask token in logs for security
    masked_token = f"{args.token[:8]}...{args.token[-4:]}" if len(args.token) > 12 else "***"
    logger.info(f"Starting Cloudflare Tunnel Manager")
    logger.info(f"Account ID: {args.account_id[:8]}...")
    logger.info(f"Token: {masked_token}")
    
    # Initialize tunnel manager
    tunnel_manager = CloudflareTunnelManager(args.account_id, args.token)
    
    if args.command == "create":
        if not args.name:
            print("ERROR: --name is required for create command")
            sys.exit(1)
            
        # Create tunnel
        result = tunnel_manager.create_tunnel(args.name)
        print_result(result, args.verbose)
        
        if result["success"] and args.subdomain and args.zone_id:
            tunnel_id = result["data"]["result"]["id"]
            print("\n" + "="*50)
            print("CREATING DNS RECORD")
            print("="*50)
            dns_result = tunnel_manager.create_dns_record(args.zone_id, args.subdomain, tunnel_id, args.domain)
            print_result(dns_result, args.verbose)
            
            if dns_result["success"]:
                print("\n" + "="*50)
                print("TUNNEL SETUP COMPLETE")
                print("="*50)
                print(f"Tunnel URL: https://{args.subdomain}.{args.domain}")
                print(f"Tunnel ID: {tunnel_id}")
                print("\nTo run the tunnel:")
                print(f"cloudflared tunnel --no-autoupdate run --token <TUNNEL_TOKEN>")
                print("\nTo get the tunnel token:")
                print(f"python cloudflare_tunnel_manager.py get-token --tunnel-id {tunnel_id}")
        
    elif args.command == "list":
        result = tunnel_manager.list_tunnels()
        print_tunnels_list(result)
        
    elif args.command == "delete":
        if not args.tunnel_id:
            print("ERROR: --tunnel-id is required for delete command")
            sys.exit(1)
            
        result = tunnel_manager.delete_tunnel(args.tunnel_id)
        print_result(result, args.verbose)
        
    elif args.command == "get-token":
        if not args.tunnel_id:
            print("ERROR: --tunnel-id is required for get-token command")
            sys.exit(1)
            
        result = tunnel_manager.get_tunnel_token(args.tunnel_id)
        if result["success"]:
            token = result["data"]["result"]["token"]
            print(f"Tunnel Token: {token}")
            print("\nTo run the tunnel:")
            print(f"cloudflared tunnel --no-autoupdate run --token {token}")
        else:
            print_result(result, args.verbose)

if __name__ == "__main__":
    main()
