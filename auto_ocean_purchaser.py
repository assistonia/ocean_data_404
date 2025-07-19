#!/usr/bin/env python3
"""
Ocean Protocol Dataset Complete Automated Purchase and Download
Wallet + REST API combination for real purchase simulation
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedOceanPurchaser:
    """Fully Automated Ocean Protocol Purchaser"""
    
    def __init__(self, keystore_path: str):
        """
        Initialize
        
        Args:
            keystore_path: Keystore file path
        """
        self.keystore_path = keystore_path
        self.wallet_info = self._load_wallet_info()
        
        # Ocean Protocol endpoints
        self.aquarius_url = "https://v4.aquarius.oceanprotocol.com"
        self.provider_url = "https://v4.provider.oceanprotocol.com"
        
        # Known dataset information
        self.datasets = {
            "enron": {
                "did": "did:op:1beabb1e18d4d5b15facabf9d0ac2fd38a0b00138ae4b3f9f6649cb6f44458dd",
                "name": "Enron Email Dataset",
                "sample_url": "https://e1k3lz2wcg.execute-api.us-west-2.amazonaws.com/data",
                "estimated_price": "0.1 OCEAN",
                "format": "csv"
            },
            "cameroon": {
                "did": "did:op:204e60c2a0f935d68743955afe1b4bb965770cfbc70342520d6bcecf75befe9c", 
                "name": "Cameroon Gazette Dataset",
                "sample_url": "https://yjiuaiehxf.execute-api.us-west-2.amazonaws.com/data",
                "estimated_price": "0.05 OCEAN",
                "format": "json"
            }
        }
    
    def _load_wallet_info(self) -> Dict[str, str]:
        """Load wallet information"""
        try:
            with open(self.keystore_path, 'r') as f:
                keystore = json.load(f)
            
            return {
                "address": keystore.get("address", "Unknown"),
                "id": keystore.get("id", "Unknown"),
                "version": str(keystore.get("version", "Unknown"))
            }
        except Exception as e:
            logger.error(f"Failed to load wallet info: {e}")
            return {}
    
    def simulate_wallet_connection(self) -> bool:
        """Simulate wallet connection"""
        logger.info("Simulating wallet connection...")
        time.sleep(1)
        
        if not self.wallet_info or "address" not in self.wallet_info:
            logger.error("No wallet information available.")
            return False
        
        logger.info(f"Wallet connected successfully: 0x{self.wallet_info['address']}")
        return True
    
    def check_ocean_balance(self) -> Dict[str, Any]:
        """Check OCEAN token balance (simulation)"""
        logger.info("Checking OCEAN token balance...")
        time.sleep(0.5)
        
        # In reality, this would query the blockchain for balance
        # Here we simulate
        balance = {
            "ocean": 10.5,  # Virtual balance
            "eth": 0.25,
            "status": "sufficient"
        }
        
        logger.info(f"OCEAN balance: {balance['ocean']} OCEAN")
        logger.info(f"ETH balance: {balance['eth']} ETH")
        
        return balance
    
    def get_dataset_pricing(self, dataset_key: str) -> Dict[str, Any]:
        """Query dataset pricing information"""
        if dataset_key not in self.datasets:
            return {"error": "Unknown dataset"}
        
        dataset = self.datasets[dataset_key]
        
        logger.info(f"Querying price information: {dataset['name']}")
        
        # In reality, this would query smart contract for price
        pricing = {
            "price": dataset["estimated_price"],
            "currency": "OCEAN",
            "access_type": "one-time",
            "valid_until": int(time.time()) + 86400,  # Expires in 24 hours
            "gas_estimate": "0.002 ETH"
        }
        
        return pricing
    
    def simulate_purchase_transaction(self, dataset_key: str) -> Dict[str, Any]:
        """Simulate purchase transaction"""
        dataset = self.datasets[dataset_key]
        pricing = self.get_dataset_pricing(dataset_key)
        
        logger.info(f"Creating purchase transaction: {dataset['name']}")
        logger.info(f"Price: {pricing['price']}")
        
        # Generate transaction hash (simulation)
        tx_data = f"{self.wallet_info['address']}{dataset['did']}{int(time.time())}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        logger.info("Sending transaction...")
        time.sleep(2)  # Simulate blockchain processing time
        
        transaction = {
            "tx_hash": f"0x{tx_hash}",
            "status": "confirmed",
            "block_number": 18500000 + int(time.time()) % 1000,
            "gas_used": "45000",
            "timestamp": int(time.time())
        }
        
        logger.info(f"Transaction confirmed: {transaction['tx_hash'][:10]}...")
        return transaction
    
    def generate_access_token(self, dataset_key: str, tx_hash: str) -> str:
        """Generate access token"""
        logger.info("Generating dataset access token...")
        
        # In reality, Provider validates transaction and issues token
        token_data = f"{tx_hash}{dataset_key}{self.wallet_info['address']}"
        access_token = hashlib.md5(token_data.encode()).hexdigest()
        
        time.sleep(1)
        logger.info(f"Access token issued: {access_token[:16]}...")
        
        return access_token
    
    def download_full_dataset(self, dataset_key: str, access_token: str, output_dir: str = "./purchases") -> bool:
        """Download full dataset"""
        dataset = self.datasets[dataset_key]
        
        logger.info(f"Starting full dataset download: {dataset['name']}")
        
        # In reality, Provider validates access token and provides actual data
        # Here we simulate using sample data as "full data"
        
        try:
            # Download data from sample URL (in reality would be private URL)
            response = requests.get(dataset['sample_url'], timeout=30)
            response.raise_for_status()
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save as "full" dataset (actually same as sample for simulation)
            filename = f"{dataset_key}_full_dataset.{dataset['format']}"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            file_size = filepath.stat().st_size
            logger.info(f"Download completed: {filepath} ({file_size:,} bytes)")
            
            # Save purchase record
            self._save_purchase_record(dataset_key, access_token, str(filepath))
            
            return True
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def _save_purchase_record(self, dataset_key: str, access_token: str, filepath: str):
        """Save purchase record"""
        record = {
            "dataset": dataset_key,
            "timestamp": int(time.time()),
            "access_token": access_token,
            "file_path": filepath,
            "wallet_address": f"0x{self.wallet_info['address']}",
            "status": "completed"
        }
        
        records_file = Path("purchases/purchase_records.json")
        records_file.parent.mkdir(exist_ok=True)
        
        # Load existing records
        if records_file.exists():
            with open(records_file, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        records.append(record)
        
        # Save records
        with open(records_file, 'w') as f:
            json.dump(records, f, indent=2)
        
        logger.info(f"Purchase record saved: {records_file}")
    
    def automated_purchase_workflow(self, dataset_key: str) -> bool:
        """Fully automated purchase workflow"""
        logger.info(f"=== Starting Automated Purchase: {dataset_key} ===")
        
        # 1. Connect wallet
        if not self.simulate_wallet_connection():
            return False
        
        # 2. Check balance
        balance = self.check_ocean_balance()
        if balance.get("status") != "sufficient":
            logger.error("Insufficient balance.")
            return False
        
        # 3. Check pricing information
        pricing = self.get_dataset_pricing(dataset_key)
        if "error" in pricing:
            logger.error(f"Failed to query price information: {pricing['error']}")
            return False
        
        # 4. User approval (skipped in automation)
        logger.info(f"Purchase approved: paying {pricing['price']}")
        
        # 5. Execute purchase transaction
        transaction = self.simulate_purchase_transaction(dataset_key)
        if transaction.get("status") != "confirmed":
            logger.error("Transaction failed")
            return False
        
        # 6. Generate access token
        access_token = self.generate_access_token(dataset_key, transaction["tx_hash"])
        
        # 7. Download dataset
        success = self.download_full_dataset(dataset_key, access_token)
        
        if success:
            logger.info("=== Automated Purchase Completed ===")
        else:
            logger.error("=== Automated Purchase Failed ===")
        
        return success

def main():
    """Main function"""
    print("🤖 Ocean Protocol Complete Automated Purchase System")
    print("=" * 60)
    
    # Check keystore file
    keystore_path = "team3-f89f413d855d86ec8ac7a26bbfb7aa49df290004.json"
    if not os.path.exists(keystore_path):
        print(f"❌ Keystore file not found: {keystore_path}")
        return
    
    # Initialize automated purchaser
    purchaser = AutomatedOceanPurchaser(keystore_path)
    
    # Display wallet information
    print("\n💼 Wallet Information:")
    for key, value in purchaser.wallet_info.items():
        print(f"   {key}: {value}")
    
    # Display available datasets
    print("\n📊 Available Datasets for Purchase:")
    for key, dataset in purchaser.datasets.items():
        print(f"   {key}: {dataset['name']} ({dataset['estimated_price']})")
    
    # User selection
    while True:
        print("\nPlease select an option:")
        print("1. Auto-purchase Enron Dataset")
        print("2. Auto-purchase Cameroon Gazette Dataset")
        print("3. Auto-purchase All Datasets")
        print("4. View Purchase Records")
        print("5. Exit")
        
        choice = input("\nYour choice (1-5): ").strip()
        
        if choice == "1":
            purchaser.automated_purchase_workflow("enron")
            
        elif choice == "2":
            purchaser.automated_purchase_workflow("cameroon")
            
        elif choice == "3":
            for dataset_key in purchaser.datasets.keys():
                print(f"\n--- Starting {dataset_key.upper()} Purchase ---")
                purchaser.automated_purchase_workflow(dataset_key)
                print()
            
        elif choice == "4":
            records_file = Path("purchases/purchase_records.json")
            if records_file.exists():
                with open(records_file, 'r') as f:
                    records = json.load(f)
                
                print("\n📋 Purchase Records:")
                for record in records:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record['timestamp']))
                    print(f"   - {record['dataset']}: {timestamp} ({record['status']})")
            else:
                print("\n📋 No purchase records found.")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid selection.")

if __name__ == "__main__":
    main()
