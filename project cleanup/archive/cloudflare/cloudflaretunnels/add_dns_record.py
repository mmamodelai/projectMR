#!/usr/bin/env python3
"""
Cloudflare DNS Record Manager
Part of Conductor SMS System

Usage:
    python add_dns_record.py --subdomain smsn8n --tunnel-id 2fbac668-5ee0-4ad7-aee6-208dd57d4d86
    
Architecture:
    API-based DNS record creation for Cloudflare Tunnel subdomains
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
        logging.FileHandler('logs/cloudflare_dns.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
DNS_API_TOKEN = "4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf"  # DNS-enabled token
ZONE_NAME = "marketsuite.co"

class CloudflareDNSManager:
    """Cloudflare DNS record management client"""
    
    def __init__(self, token: str):
        """
        Initialize Cloudflare DNS Manager
        
        Args:
            token: API token with DNS:Edit permissions
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_zone_id(self, zone_name: str) -> Optional[str]:
        """
        Get zone ID for a domain
        
        Args:
            zone_name: Domain name (e.g., "marketsuite.co")
            
        Returns:
            Zone ID or None if not found
        """
        try:
            url = f"{CLOUDFLARE_API_BASE}/zones?name={zone_name}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            if data["success"] and data["result"]:
                zone_id = data["result"][0]["id"]
                logger.info(f"Found zone ID for {zone_name}: {zone_id}")
                return zone_id
            else:
                logger.error(f"Zone {zone_name} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting zone ID: {e}")
            return None
    
    def add_cname_record(self, zone_id: str, subdomain: str, tunnel_id: str) -> bool:
        """
        Add CNAME record for tunnel subdomain
        
        Args:
            zone_id: Cloudflare zone ID
            subdomain: Subdomain name (e.g., "smsn8n")
            tunnel_id: Cloudflare tunnel ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{CLOUDFLARE_API_BASE}/zones/{zone_id}/dns_records"
            
            record_data = {
                "type": "CNAME",
                "name": subdomain,
                "content": f"{tunnel_id}.cfargotunnel.com",
                "proxied": True,
                "ttl": 1
            }
            
            response = requests.post(url, headers=self.headers, json=record_data)
            response.raise_for_status()
            
            data = response.json()
            if data["success"]:
                record_id = data["result"]["id"]
                logger.info(f"✅ DNS record created successfully!")
                logger.info(f"   Subdomain: {subdomain}.{ZONE_NAME}")
                logger.info(f"   Target: {tunnel_id}.cfargotunnel.com")
                logger.info(f"   Record ID: {record_id}")
                logger.info(f"   URL: https://{subdomain}.{ZONE_NAME}")
                return True
            else:
                logger.error(f"Failed to create DNS record: {data.get('errors', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating DNS record: {e}")
            return False
    
    def create_tunnel_subdomain(self, subdomain: str, tunnel_id: str) -> bool:
        """
        Create complete tunnel subdomain setup
        
        Args:
            subdomain: Subdomain name
            tunnel_id: Cloudflare tunnel ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Creating tunnel subdomain: {subdomain}.{ZONE_NAME}")
        
        # Get zone ID
        zone_id = self.get_zone_id(ZONE_NAME)
        if not zone_id:
            return False
        
        # Add CNAME record
        success = self.add_cname_record(zone_id, subdomain, tunnel_id)
        
        if success:
            logger.info(f"🎉 Tunnel subdomain ready!")
            logger.info(f"   URL: https://{subdomain}.{ZONE_NAME}")
            logger.info(f"   Test: curl https://{subdomain}.{ZONE_NAME}/api/health")
        
        return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Add Cloudflare DNS record for tunnel")
    parser.add_argument("--subdomain", required=True, help="Subdomain name (e.g., smsn8n)")
    parser.add_argument("--tunnel-id", required=True, help="Cloudflare tunnel ID")
    parser.add_argument("--zone", default=ZONE_NAME, help=f"Zone name (default: {ZONE_NAME})")
    
    args = parser.parse_args()
    
    logger.info("Starting Cloudflare DNS Manager")
    logger.info(f"Token: {DNS_API_TOKEN[:10]}...")
    
    dns_manager = CloudflareDNSManager(DNS_API_TOKEN)
    success = dns_manager.create_tunnel_subdomain(args.subdomain, args.tunnel_id)
    
    if success:
        logger.info("✅ DNS record creation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ DNS record creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
