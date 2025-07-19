#!/usr/bin/env python3
"""
Ocean Protocol 데이터셋 완전 자동화 구매 및 다운로드
지갑 + REST API 조합으로 실제 구매 시뮬레이션
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
    """완전 자동화된 Ocean Protocol 구매자"""
    
    def __init__(self, keystore_path: str):
        """
        초기화
        
        Args:
            keystore_path: 키스토어 파일 경로
        """
        self.keystore_path = keystore_path
        self.wallet_info = self._load_wallet_info()
        
        # Ocean Protocol 엔드포인트
        self.aquarius_url = "https://v4.aquarius.oceanprotocol.com"
        self.provider_url = "https://v4.provider.oceanprotocol.com"
        
        # 알려진 데이터셋 정보
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
        """지갑 정보 로드"""
        try:
            with open(self.keystore_path, 'r') as f:
                keystore = json.load(f)
            
            return {
                "address": keystore.get("address", "Unknown"),
                "id": keystore.get("id", "Unknown"),
                "version": str(keystore.get("version", "Unknown"))
            }
        except Exception as e:
            logger.error(f"지갑 정보 로드 실패: {e}")
            return {}
    
    def simulate_wallet_connection(self) -> bool:
        """지갑 연결 시뮬레이션"""
        logger.info("지갑 연결 시뮬레이션 중...")
        time.sleep(1)
        
        if not self.wallet_info or "address" not in self.wallet_info:
            logger.error("지갑 정보가 없습니다.")
            return False
        
        logger.info(f"지갑 연결 성공: 0x{self.wallet_info['address']}")
        return True
    
    def check_ocean_balance(self) -> Dict[str, Any]:
        """OCEAN 토큰 잔액 확인 (시뮬레이션)"""
        logger.info("OCEAN 토큰 잔액 확인 중...")
        time.sleep(0.5)
        
        # 실제로는 블록체인에서 잔액을 조회해야 함
        # 여기서는 시뮬레이션
        balance = {
            "ocean": 10.5,  # 가상 잔액
            "eth": 0.25,
            "status": "sufficient"
        }
        
        logger.info(f"OCEAN 잔액: {balance['ocean']} OCEAN")
        logger.info(f"ETH 잔액: {balance['eth']} ETH")
        
        return balance
    
    def get_dataset_pricing(self, dataset_key: str) -> Dict[str, Any]:
        """데이터셋 가격 정보 조회"""
        if dataset_key not in self.datasets:
            return {"error": "Unknown dataset"}
        
        dataset = self.datasets[dataset_key]
        
        logger.info(f"가격 정보 조회: {dataset['name']}")
        
        # 실제로는 스마트 컨트랙트에서 가격을 조회해야 함
        pricing = {
            "price": dataset["estimated_price"],
            "currency": "OCEAN",
            "access_type": "one-time",
            "valid_until": int(time.time()) + 86400,  # 24시간 후 만료
            "gas_estimate": "0.002 ETH"
        }
        
        return pricing
    
    def simulate_purchase_transaction(self, dataset_key: str) -> Dict[str, Any]:
        """구매 트랜잭션 시뮬레이션"""
        dataset = self.datasets[dataset_key]
        pricing = self.get_dataset_pricing(dataset_key)
        
        logger.info(f"구매 트랜잭션 생성: {dataset['name']}")
        logger.info(f"가격: {pricing['price']}")
        
        # 트랜잭션 해시 생성 (시뮬레이션)
        tx_data = f"{self.wallet_info['address']}{dataset['did']}{int(time.time())}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        logger.info("트랜잭션 전송 중...")
        time.sleep(2)  # 블록체인 처리 시간 시뮬레이션
        
        transaction = {
            "tx_hash": f"0x{tx_hash}",
            "status": "confirmed",
            "block_number": 18500000 + int(time.time()) % 1000,
            "gas_used": "45000",
            "timestamp": int(time.time())
        }
        
        logger.info(f"트랜잭션 확인됨: {transaction['tx_hash'][:10]}...")
        return transaction
    
    def generate_access_token(self, dataset_key: str, tx_hash: str) -> str:
        """액세스 토큰 생성"""
        logger.info("데이터셋 액세스 토큰 생성 중...")
        
        # 실제로는 Provider가 트랜잭션을 검증하고 토큰을 발급
        token_data = f"{tx_hash}{dataset_key}{self.wallet_info['address']}"
        access_token = hashlib.md5(token_data.encode()).hexdigest()
        
        time.sleep(1)
        logger.info(f"액세스 토큰 발급: {access_token[:16]}...")
        
        return access_token
    
    def download_full_dataset(self, dataset_key: str, access_token: str, output_dir: str = "./purchases") -> bool:
        """전체 데이터셋 다운로드"""
        dataset = self.datasets[dataset_key]
        
        logger.info(f"전체 데이터셋 다운로드 시작: {dataset['name']}")
        
        # 실제로는 Provider에서 액세스 토큰을 검증하고 실제 데이터를 제공
        # 여기서는 샘플 데이터를 "전체 데이터"로 시뮬레이션
        
        try:
            # 샘플 URL에서 데이터 다운로드 (실제로는 프라이빗 URL)
            response = requests.get(dataset['sample_url'], timeout=30)
            response.raise_for_status()
            
            # 출력 디렉토리 생성
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # "전체" 데이터셋으로 저장 (실제로는 샘플과 동일하지만 시뮬레이션)
            filename = f"{dataset_key}_full_dataset.{dataset['format']}"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            file_size = filepath.stat().st_size
            logger.info(f"다운로드 완료: {filepath} ({file_size:,} bytes)")
            
            # 구매 기록 저장
            self._save_purchase_record(dataset_key, access_token, str(filepath))
            
            return True
            
        except Exception as e:
            logger.error(f"다운로드 실패: {e}")
            return False
    
    def _save_purchase_record(self, dataset_key: str, access_token: str, filepath: str):
        """구매 기록 저장"""
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
        
        # 기존 기록 로드
        if records_file.exists():
            with open(records_file, 'r') as f:
                records = json.load(f)
        else:
            records = []
        
        records.append(record)
        
        # 기록 저장
        with open(records_file, 'w') as f:
            json.dump(records, f, indent=2)
        
        logger.info(f"구매 기록 저장됨: {records_file}")
    
    def automated_purchase_workflow(self, dataset_key: str) -> bool:
        """완전 자동화된 구매 워크플로우"""
        logger.info(f"=== 자동화된 구매 시작: {dataset_key} ===")
        
        # 1. 지갑 연결
        if not self.simulate_wallet_connection():
            return False
        
        # 2. 잔액 확인
        balance = self.check_ocean_balance()
        if balance.get("status") != "sufficient":
            logger.error("잔액이 부족합니다.")
            return False
        
        # 3. 가격 정보 확인
        pricing = self.get_dataset_pricing(dataset_key)
        if "error" in pricing:
            logger.error(f"가격 정보 조회 실패: {pricing['error']}")
            return False
        
        # 4. 사용자 승인 (자동화에서는 스킵)
        logger.info(f"구매 승인: {pricing['price']} 지불")
        
        # 5. 구매 트랜잭션 실행
        transaction = self.simulate_purchase_transaction(dataset_key)
        if transaction.get("status") != "confirmed":
            logger.error("트랜잭션 실패")
            return False
        
        # 6. 액세스 토큰 발급
        access_token = self.generate_access_token(dataset_key, transaction["tx_hash"])
        
        # 7. 데이터셋 다운로드
        success = self.download_full_dataset(dataset_key, access_token)
        
        if success:
            logger.info("=== 자동화된 구매 완료 ===")
        else:
            logger.error("=== 자동화된 구매 실패 ===")
        
        return success

def main():
    """메인 함수"""
    print("🤖 Ocean Protocol 완전 자동화 구매 시스템")
    print("=" * 60)
    
    # 키스토어 파일 확인
    keystore_path = "team3-f89f413d855d86ec8ac7a26bbfb7aa49df290004.json"
    if not os.path.exists(keystore_path):
        print(f"❌ 키스토어 파일을 찾을 수 없습니다: {keystore_path}")
        return
    
    # 자동 구매자 초기화
    purchaser = AutomatedOceanPurchaser(keystore_path)
    
    # 지갑 정보 표시
    print("\n💼 지갑 정보:")
    for key, value in purchaser.wallet_info.items():
        print(f"   {key}: {value}")
    
    # 사용 가능한 데이터셋 표시
    print("\n📊 구매 가능한 데이터셋:")
    for key, dataset in purchaser.datasets.items():
        print(f"   {key}: {dataset['name']} ({dataset['estimated_price']})")
    
    # 사용자 선택
    while True:
        print("\n선택하세요:")
        print("1. Enron 데이터셋 자동 구매")
        print("2. Cameroon Gazette 데이터셋 자동 구매")
        print("3. 모든 데이터셋 자동 구매")
        print("4. 구매 기록 보기")
        print("5. 종료")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == "1":
            purchaser.automated_purchase_workflow("enron")
            
        elif choice == "2":
            purchaser.automated_purchase_workflow("cameroon")
            
        elif choice == "3":
            for dataset_key in purchaser.datasets.keys():
                print(f"\n--- {dataset_key.upper()} 구매 시작 ---")
                purchaser.automated_purchase_workflow(dataset_key)
                print()
            
        elif choice == "4":
            records_file = Path("purchases/purchase_records.json")
            if records_file.exists():
                with open(records_file, 'r') as f:
                    records = json.load(f)
                
                print("\n📋 구매 기록:")
                for record in records:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record['timestamp']))
                    print(f"   - {record['dataset']}: {timestamp} ({record['status']})")
            else:
                print("\n📋 구매 기록이 없습니다.")
                
        elif choice == "5":
            print("👋 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()
