#!/usr/bin/env python3
"""
Ocean Protocol Dataset Auto Purchase and Download Script
"""

import json
import os
import getpass
from pathlib import Path
from typing import Optional, Dict, Any
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ocean Protocol SDK imports (installation required)
try:
    from ocean_lib.ocean.ocean import Ocean
    from ocean_lib.config import Config
    from ocean_lib.web3_internal.wallet import Wallet
    from ocean_lib.models.datatoken import Datatoken
    from ocean_lib.models.dispenser import Dispenser
    from ocean_lib.models.fixed_rate_exchange import FixedRateExchange
    from ocean_lib.agreements.service_types import ServiceTypes
    from ocean_lib.data_provider.data_service_provider import DataServiceProvider
    import eth_account
except ImportError as e:
    print(f"Ocean Protocol SDK not installed: {e}")
    print("Install with: pip install ocean-lib")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OceanDatasetPurchaser:
    """Ocean Protocol Dataset Purchaser"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize
        
        Args:
            config_file: Ocean config file path (uses default if not provided)
        """
        self.ocean = None
        self.wallet = None
        self.config = None
        self._setup_ocean(config_file)
    
    def _setup_ocean(self, config_file: Optional[str] = None):
        """Setup Ocean instance for REAL Ocean Protocol marketplace"""
        try:
            if config_file and os.path.exists(config_file):
                self.config = Config(config_file)
            else:
                # Production Ethereum mainnet configuration for REAL purchases
                network_url = os.getenv('NETWORK_URL')
                if not network_url or 'YOUR_INFURA_KEY' in network_url:
                    logger.warning("⚠️  Please set NETWORK_URL in .env file with your Infura project ID")
                    logger.warning("Example: NETWORK_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID")
                
                self.config = Config({
                    'NETWORK_URL': network_url or 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY',
                    'BLOCK_CONFIRMATIONS': 1,
                    'AQUARIUS_URL': os.getenv('AQUARIUS_URL', 'https://v4.aquarius.oceanprotocol.com'),
                    'PROVIDER_URL': os.getenv('PROVIDER_URL', 'https://v4.provider.oceanprotocol.com')
                })
            
            self.ocean = Ocean(self.config)
            logger.info("🌊 Ocean Protocol instance successfully configured for REAL marketplace")
            logger.info(f"📡 Network: {self.config.network_url}")
            logger.info(f"🔍 Aquarius: {self.config.aquarius_url}")
            logger.info(f"⚡ Provider: {self.config.provider_url}")
            
        except Exception as e:
            logger.error(f"❌ Ocean setup failed: {e}")
            raise
    
    def load_wallet_from_keystore(self, keystore_path: str, password: Optional[str] = None) -> bool:
        """
        Load wallet from keystore file
        
        Args:
            keystore_path: Keystore file path
            password: Keystore password (prompts if not provided)
            
        Returns:
            Success status
        """
        try:
            if not os.path.exists(keystore_path):
                logger.error(f"Keystore file not found: {keystore_path}")
                return False
            
            with open(keystore_path, 'r') as f:
                keystore = json.load(f)
            
            if password is None:
                password = getpass.getpass("Enter keystore password: ")
            
            # Restore private key from keystore
            private_key = eth_account.Account.decrypt(keystore, password)
            
            # Create Ocean wallet
            self.wallet = Wallet(
                self.ocean.web3,
                private_key=private_key.hex(),
                block_confirmations=self.config.block_confirmations,
                transaction_timeout=self.config.transaction_timeout
            )
            
            logger.info(f"Wallet address: {self.wallet.address}")
            logger.info("Wallet loaded successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Wallet loading failed: {e}")
            return False
    
    def get_dataset_info(self, did: str) -> Optional[Dict[str, Any]]:
        """
        Get dataset information
        
        Args:
            did: Dataset DID
            
        Returns:
            Dataset information
        """
        try:
            # Query metadata from Aquarius
            ddo = self.ocean.assets.resolve(did)
            
            if not ddo:
                logger.error(f"Dataset not found: {did}")
                return None
            
            info = {
                'did': did,
                'name': ddo.metadata.get('name', 'Unknown'),
                'description': ddo.metadata.get('description', ''),
                'author': ddo.metadata.get('author', 'Unknown'),
                'created': ddo.metadata.get('created', ''),
                'files': len(ddo.metadata.get('files', [])),
                'services': [service.type for service in ddo.services]
            }
            
            # Query price information
            for service in ddo.services:
                if service.type == ServiceTypes.ASSET_ACCESS:
                    datatoken = Datatoken(self.ocean.web3, service.datatoken)
                    
                    # Check Fixed Rate Exchange
                    fre = FixedRateExchange(self.ocean.web3, self.ocean.config.fixed_rate_exchange_address)
                    exchanges = fre.get_exchanges_by_datatoken(service.datatoken)
                    
                    if exchanges:
                        exchange = exchanges[0]
                        price = fre.get_rate(exchange['exchangeId'])
                        info['price'] = {
                            'amount': price,
                            'token': 'OCEAN'
                        }
                    else:
                        # Check Dispenser
                        dispenser = Dispenser(self.ocean.web3, self.ocean.config.dispenser_address)
                        if dispenser.is_active(service.datatoken):
                            info['price'] = {
                                'amount': 0,
                                'token': 'FREE'
                            }
            
            return info
            
        except Exception as e:
            logger.error(f"Dataset info query failed: {e}")
            return None
    
    def purchase_dataset(self, did: str) -> Optional[str]:
        """
        Purchase dataset from REAL Ocean Protocol marketplace
        
        Args:
            did: Dataset DID
            
        Returns:
            Order ID on success, None on failure
        """
        try:
            if not self.wallet:
                logger.error("❌ Wallet not loaded.")
                return None
            
            logger.info(f"💰 Starting REAL dataset purchase from Ocean Protocol marketplace")
            logger.info(f"🔗 Dataset DID: {did}")
            logger.info(f"👛 Wallet address: {self.wallet.address}")
            
            # Resolve dataset
            ddo = self.ocean.assets.resolve(did)
            if not ddo:
                logger.error(f"❌ Dataset not found: {did}")
                return None
            
            # Find access service
            access_service = None
            for service in ddo.services:
                if service.type == ServiceTypes.ASSET_ACCESS:
                    access_service = service
                    break
            
            if not access_service:
                logger.error("Access service not found.")
                return None
            
            logger.info(f"Starting dataset purchase: {ddo.metadata.get('name', did)}")
            
            # Order datatoken
            order_tx_id = self.ocean.assets.pay_for_access_service(
                ddo,
                access_service,
                consume_market_fees=True,
                wallet=self.wallet
            )
            
            logger.info(f"Purchase completed! Order ID: {order_tx_id}")
            return order_tx_id
            
        except Exception as e:
            logger.error(f"Dataset purchase failed: {e}")
            return None
    
    def download_dataset(self, did: str, order_tx_id: str, download_path: str = "./downloads") -> bool:
        """
        Download purchased dataset
        
        Args:
            did: Dataset DID
            order_tx_id: Order ID
            download_path: Download path
            
        Returns:
            Success status
        """
        try:
            if not self.wallet:
                logger.error("Wallet not loaded.")
                return False
            
            # Create download folder
            Path(download_path).mkdir(parents=True, exist_ok=True)
            
            # Resolve dataset
            ddo = self.ocean.assets.resolve(did)
            if not ddo:
                logger.error(f"Dataset not found: {did}")
                return False
            
            # Find access service
            access_service = None
            for service in ddo.services:
                if service.type == ServiceTypes.ASSET_ACCESS:
                    access_service = service
                    break
            
            if not access_service:
                logger.error("Access service not found.")
                return False
            
            logger.info("Starting dataset download...")
            
            # Download files
            downloaded_files = self.ocean.assets.download(
                ddo,
                access_service,
                order_tx_id,
                wallet=self.wallet,
                destination=download_path
            )
            
            if downloaded_files:
                logger.info(f"Download completed: {downloaded_files}")
                return True
            else:
                logger.error("Download failed")
                return False
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def purchase_and_download(self, did: str, download_path: str = "./downloads") -> bool:
        """
        One-stop dataset purchase and download
        
        Args:
            did: Dataset DID
            download_path: Download path
            
        Returns:
            Success status
        """
        try:
            # 1. Get dataset information
            info = self.get_dataset_info(did)
            if not info:
                return False
            
            logger.info(f"Dataset: {info['name']}")
            logger.info(f"Description: {info['description']}")
            if 'price' in info:
                logger.info(f"Price: {info['price']['amount']} {info['price']['token']}")
            
            # 2. Purchase
            order_tx_id = self.purchase_dataset(did)
            if not order_tx_id:
                return False
            
            # 3. Download
            return self.download_dataset(did, order_tx_id, download_path)
            
        except Exception as e:
            logger.error(f"Purchase and download failed: {e}")
            return False

def main():
    """Main function - REAL Ocean Protocol dataset purchase"""
    print("🌊 === Ocean Protocol REAL Dataset Auto Purchaser ===")
    print("⚠️  This will make REAL purchases using OCEAN tokens from your wallet!")
    print("💰 Make sure you have sufficient OCEAN tokens in your wallet.\n")
    
    # Real Ocean Protocol Dataset DID list
    datasets = {
        "enron": "did:op:1beabb1e18d4d5b15facabf9d0ac2fd38a0b00138ae4b3f9f6649cb6f44458dd",
        "cameroon": "did:op:204e60c2a0f935d68743955afe1b4bb965770cfbc70342520d6bcecf75befe9c"
    }
    
    try:
        # Initialize Ocean purchaser for REAL marketplace
        print("🔧 Initializing Ocean Protocol connection...")
        purchaser = OceanDatasetPurchaser()
        
        # Load wallet from environment
        keystore_path = os.getenv('WALLET_KEYSTORE_PATH', 'team3-f89f413d855d86ec8ac7a26bbfb7aa49df290004.json')
        wallet_password = os.getenv('WALLET_PASSWORD')
        
        print("👛 Loading wallet...")
        if not purchaser.load_wallet_from_keystore(keystore_path, wallet_password):
            print("❌ Failed to load wallet.")
            return
        
        # User selection
        print("\n📊 Please select a REAL dataset to purchase from Ocean Protocol:")
        for key, did in datasets.items():
            print(f"  🔸 {key.upper()}: {did}")
        
        choice = input("\n🎯 Your choice (enron/cameroon): ").strip().lower()
        
        if choice not in datasets:
            print("❌ Invalid selection.")
            return
        
        did = datasets[choice]
        download_path = f"./purchases/{choice}_full_dataset"
        
        print(f"\n🚀 Starting REAL purchase and download for {choice.upper()} dataset...")
        print(f"📁 Download path: {download_path}")
        
        # Purchase and download
        success = purchaser.purchase_and_download(did, download_path)
        
        if success:
            print(f"\n🎉 SUCCESS! Real dataset purchased and downloaded to {download_path}")
            print("💾 This is the FULL dataset from Ocean Protocol marketplace!")
        else:
            print("\n❌ FAILED! Error occurred during purchase or download.")
            print("💡 Check your wallet balance, network connection, and configuration.")
            
    except Exception as e:
        print(f"💥 Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
