#!/usr/bin/env python3
"""
Cloudflare API Tool - Token Verification
Part of Conductor SMS System

Usage:
    python cloudflare_api_tool.py verify <token>
    python cloudflare_api_tool.py verify --account-id <account_id> --token <token>
    
Architecture:
    Simple HTTP client for Cloudflare API verification
"""

import requests
import json
import sys
import logging
import argparse
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cloudflare_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
DEFAULT_ACCOUNT_ID = "ed835396a75f0a35ea698cc764615662"  # From your curl command
DEFAULT_TOKEN = "4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf"  # From your curl command

class CloudflareAPITool:
    """Simple Cloudflare API client for token verification"""
    
    def __init__(self, account_id: str, token: str):
        """
        Initialize Cloudflare API client
        
        Args:
            account_id: Cloudflare account ID
            token: API token
        """
        self.account_id = account_id
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def verify_token(self) -> Dict[str, Any]:
        """
        Verify API token by calling Cloudflare's verify endpoint
        
        Returns:
            Dict containing verification response or error info
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}/tokens/verify"
        
        try:
            logger.info(f"Verifying token for account: {self.account_id[:8]}...")
            logger.debug(f"API URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Token verification successful")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Token verification failed: {response.status_code}")
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
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information using the verified token
        
        Returns:
            Dict containing account info or error
        """
        url = f"{CLOUDFLARE_API_BASE}/accounts/{self.account_id}"
        
        try:
            logger.info("Fetching account information...")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("[SUCCESS] Account info retrieved successfully")
                return {
                    "success": True,
                    "data": data
                }
            else:
                logger.error(f"[ERROR] Failed to get account info: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Error getting account info: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def print_result(result: Dict[str, Any], verbose: bool = False):
    """Print formatted result"""
    if result["success"]:
        print("[SUCCESS]")
        if verbose and "data" in result:
            print(json.dumps(result["data"], indent=2))
    else:
        print("[FAILED]")
        if "status_code" in result:
            print(f"Status Code: {result['status_code']}")
        if "error" in result:
            print(f"Error: {result['error']}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Cloudflare API Tool")
    parser.add_argument("command", choices=["verify"], help="Command to execute")
    parser.add_argument("--account-id", default=DEFAULT_ACCOUNT_ID, help="Cloudflare account ID")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="API token")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--account-info", action="store_true", help="Also fetch account info")
    
    args = parser.parse_args()
    
    # Mask token in logs for security
    masked_token = f"{args.token[:8]}...{args.token[-4:]}" if len(args.token) > 12 else "***"
    logger.info(f"Starting Cloudflare API Tool")
    logger.info(f"Account ID: {args.account_id[:8]}...")
    logger.info(f"Token: {masked_token}")
    
    # Initialize API client
    api_client = CloudflareAPITool(args.account_id, args.token)
    
    if args.command == "verify":
        # Verify token
        result = api_client.verify_token()
        print_result(result, args.verbose)
        
        # If verification successful and account-info requested, get account info
        if result["success"] and args.account_info:
            print("\n" + "="*50)
            print("ACCOUNT INFORMATION")
            print("="*50)
            account_result = api_client.get_account_info()
            print_result(account_result, args.verbose)

if __name__ == "__main__":
    main()
