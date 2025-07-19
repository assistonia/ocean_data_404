#!/usr/bin/env python3
"""
Ocean Protocol 데이터셋 간단 다운로드 도구
복잡한 의존성 없이 REST API를 직접 사용
"""

import json
import os
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleOceanDownloader:
    """간단한 Ocean Protocol 데이터 다운로더"""
    
    def __init__(self):
        self.aquarius_url = "https://v4.aquarius.oceanprotocol.com"
        self.provider_url = "https://v4.provider.oceanprotocol.com"
        
        # 알려진 샘플 데이터 URL들
        self.sample_data = {
            "enron": {
                "name": "Enron Email Dataset (Sample)",
                "url": "https://e1k3lz2wcg.execute-api.us-west-2.amazonaws.com/data",
                "format": "csv",
                "did": "did:op:1beabb1e18d4d5b15facabf9d0ac2fd38a0b00138ae4b3f9f6649cb6f44458dd"
            },
            "cameroon": {
                "name": "Cameroon Gazette Dataset (Sample)",
                "url": "https://yjiuaiehxf.execute-api.us-west-2.amazonaws.com/data", 
                "format": "json",
                "did": "did:op:204e60c2a0f935d68743955afe1b4bb965770cfbc70342520d6bcecf75befe9c"
            }
        }
    
    def get_dataset_metadata(self, did: str) -> Optional[Dict[str, Any]]:
        """
        Aquarius에서 데이터셋 메타데이터 조회
        
        Args:
            did: 데이터셋 DID
            
        Returns:
            메타데이터 정보
        """
        try:
            url = f"{self.aquarius_url}/api/aquarius/assets/ddo/{did}"
            logger.info(f"메타데이터 조회: {url}")
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                ddo = response.json()
                
                metadata = {
                    'did': did,
                    'name': ddo.get('metadata', {}).get('name', 'Unknown'),
                    'description': ddo.get('metadata', {}).get('description', ''),
                    'author': ddo.get('metadata', {}).get('author', 'Unknown'),
                    'created': ddo.get('metadata', {}).get('created', ''),
                    'type': ddo.get('metadata', {}).get('type', 'dataset'),
                    'services': len(ddo.get('services', [])),
                    'files': len(ddo.get('metadata', {}).get('files', []))
                }
                
                logger.info(f"메타데이터 조회 성공: {metadata['name']}")
                return metadata
            else:
                logger.warning(f"메타데이터 조회 실패: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"메타데이터 조회 중 오류: {e}")
            return None
    
    def download_sample_data(self, dataset_key: str, output_dir: str = "./downloads") -> bool:
        """
        샘플 데이터 다운로드
        
        Args:
            dataset_key: 데이터셋 키 (enron, cameroon)
            output_dir: 출력 디렉토리
            
        Returns:
            성공 여부
        """
        if dataset_key not in self.sample_data:
            logger.error(f"알 수 없는 데이터셋: {dataset_key}")
            return False
        
        dataset = self.sample_data[dataset_key]
        
        try:
            logger.info(f"다운로드 시작: {dataset['name']}")
            
            # HTTP 요청
            response = requests.get(dataset['url'], timeout=60)
            response.raise_for_status()
            
            # 출력 디렉토리 생성
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 파일명 생성
            filename = f"{dataset_key}_sample.{dataset['format']}"
            filepath = output_path / filename
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            file_size = filepath.stat().st_size
            logger.info(f"다운로드 완료: {filepath} ({file_size:,} bytes)")
            
            return True
            
        except Exception as e:
            logger.error(f"다운로드 실패: {e}")
            return False
    
    def analyze_downloaded_data(self, filepath: str) -> Dict[str, Any]:
        """
        다운로드된 데이터 분석
        
        Args:
            filepath: 파일 경로
            
        Returns:
            분석 결과
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return {"error": "파일이 존재하지 않음"}
            
            file_size = path.stat().st_size
            
            if filepath.endswith('.csv'):
                # CSV 파일 분석
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                return {
                    "format": "CSV",
                    "file_size": file_size,
                    "total_lines": len(lines),
                    "header": lines[0].strip() if lines else "",
                    "sample_lines": lines[1:6] if len(lines) > 1 else []
                }
                
            elif filepath.endswith('.json'):
                # JSON 파일 분석
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    "format": "JSON",
                    "file_size": file_size,
                    "structure": type(data).__name__,
                    "keys": list(data.keys()) if isinstance(data, dict) else None,
                    "preview": str(data)[:500]
                }
            
            else:
                return {
                    "format": "Unknown",
                    "file_size": file_size
                }
                
        except Exception as e:
            return {"error": str(e)}

def load_wallet_info(keystore_path: str) -> Dict[str, str]:
    """
    키스토어 파일에서 기본 정보 읽기 (비밀번호 없이)
    
    Args:
        keystore_path: 키스토어 파일 경로
        
    Returns:
        지갑 정보
    """
    try:
        with open(keystore_path, 'r') as f:
            keystore = json.load(f)
        
        return {
            "address": keystore.get("address", "Unknown"),
            "id": keystore.get("id", "Unknown"),
            "version": str(keystore.get("version", "Unknown"))
        }
    except Exception as e:
        return {"error": str(e)}

def interactive_demo():
    """대화형 데모"""
    downloader = SimpleOceanDownloader()
    
    print("🌊 Ocean Protocol 데이터셋 다운로드 도구")
    print("=" * 60)
    
    # 지갑 정보 표시
    keystore_path = "team3-f89f413d855d86ec8ac7a26bbfb7aa49df290004.json"
    if os.path.exists(keystore_path):
        wallet_info = load_wallet_info(keystore_path)
        print(f"\n💼 지갑 정보:")
        for key, value in wallet_info.items():
            print(f"   {key}: {value}")
    
    while True:
        print("\n📋 사용 가능한 옵션:")
        print("1. 샘플 데이터 다운로드")
        print("2. 데이터셋 메타데이터 조회")
        print("3. 다운로드된 파일 분석")
        print("4. 종료")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == "1":
            print("\n📊 사용 가능한 데이터셋:")
            for key, dataset in downloader.sample_data.items():
                print(f"   {key}: {dataset['name']}")
            
            dataset_choice = input("\n다운로드할 데이터셋 (enron/cameroon): ").strip().lower()
            
            if dataset_choice in downloader.sample_data:
                success = downloader.download_sample_data(dataset_choice)
                if success:
                    print("✅ 다운로드 완료!")
                else:
                    print("❌ 다운로드 실패!")
            else:
                print("❌ 잘못된 선택입니다.")
        
        elif choice == "2":
            print("\n🔍 메타데이터 조회")
            for key, dataset in downloader.sample_data.items():
                print(f"\n--- {dataset['name']} ---")
                metadata = downloader.get_dataset_metadata(dataset['did'])
                
                if metadata:
                    for field, value in metadata.items():
                        if field == 'description' and len(str(value)) > 100:
                            print(f"   {field}: {str(value)[:100]}...")
                        else:
                            print(f"   {field}: {value}")
                else:
                    print("   메타데이터 조회 실패")
        
        elif choice == "3":
            downloads_dir = Path("./downloads")
            if not downloads_dir.exists():
                print("❌ downloads 폴더가 없습니다. 먼저 데이터를 다운로드하세요.")
                continue
            
            files = list(downloads_dir.glob("*"))
            if not files:
                print("❌ 다운로드된 파일이 없습니다.")
                continue
            
            print("\n📁 다운로드된 파일들:")
            for i, file in enumerate(files, 1):
                print(f"   {i}. {file.name}")
            
            try:
                file_choice = int(input("\n분석할 파일 번호: ")) - 1
                if 0 <= file_choice < len(files):
                    analysis = downloader.analyze_downloaded_data(str(files[file_choice]))
                    
                    print(f"\n📊 {files[file_choice].name} 분석 결과:")
                    for key, value in analysis.items():
                        if key == 'sample_lines':
                            print(f"   {key}: {len(value)} 샘플 라인")
                            for line in value[:3]:
                                print(f"      {line.strip()[:100]}...")
                        elif key == 'preview' and len(str(value)) > 200:
                            print(f"   {key}: {str(value)[:200]}...")
                        else:
                            print(f"   {key}: {value}")
                else:
                    print("❌ 잘못된 파일 번호입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        
        elif choice == "4":
            print("👋 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다.")

def quick_download_all():
    """모든 샘플 데이터 빠른 다운로드"""
    downloader = SimpleOceanDownloader()
    
    print("🚀 모든 샘플 데이터 다운로드 시작...")
    
    for key in downloader.sample_data.keys():
        success = downloader.download_sample_data(key)
        if success:
            print(f"✅ {key} 완료")
        else:
            print(f"❌ {key} 실패")
    
    print("\n📁 downloads 폴더를 확인하세요.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_download_all()
    else:
        interactive_demo()
