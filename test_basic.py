#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Basic Tests
기본 기능 테스트
"""

import os
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from github_scraper import GitHubProfileAnalyzer
from dotenv import load_dotenv

load_dotenv()


def test_token_loading():
    """토큰 로딩 테스트"""
    print("테스트 1: 토큰 로딩...")
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️  GITHUB_TOKEN이 설정되지 않았습니다 (일부 API 테스트는 스킵됩니다).")
            return True
        print(f"✅ 토큰 로딩 성공 (길이: {len(token)})")
        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_analyzer_init():
    """분석기 초기화 테스트"""
    print("\n테스트 2: 분석기 초기화...")
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️  GITHUB_TOKEN이 없으므로 더미 토큰으로 초기화를 시도합니다.")
            token = "dummy_token"
        analyzer = GitHubProfileAnalyzer(token)
        print("✅ 분석기 초기화 성공")
        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_get_repos():
    """리포지토리 가져오기 테스트 (공개 유명 계정)"""
    print("\n테스트 3: 리포지토리 가져오기...")
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️  GITHUB_TOKEN이 없어 API 테스트를 건너뜁니다.")
            return True
        analyzer = GitHubProfileAnalyzer(token)
        # 테스트용으로 유명한 계정 사용
        repos = analyzer.get_user_repos('octocat')
        
        if repos:
            print(f"✅ 리포지토리 {len(repos)}개 가져오기 성공")
            print(f"   예시: {repos[0].name if repos else 'None'}")
            return True
        else:
            print("⚠️  리포지토리를 찾을 수 없습니다 (정상일 수 있음)")
            return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_analyze_single_repo():
    """단일 리포지토리 분석 테스트"""
    print("\n테스트 4: 리포지토리 분석...")
    try:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️  GITHUB_TOKEN이 없어 API 테스트를 건너뜁니다.")
            return True
        analyzer = GitHubProfileAnalyzer(token)
        repos = analyzer.get_user_repos('octocat')
        
        if not repos:
            print("⚠️  테스트할 리포지토리 없음 (스킵)")
            return True
        
        repo_info = analyzer.analyze_repository(repos[0])
        
        if repo_info:
            print("✅ 리포지토리 분석 성공")
            print(f"   이름: {repo_info.get('name')}")
            print(f"   커밋: {repo_info.get('commit_count')}")
            return True
        else:
            print("❌ 분석 실패")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_statistics_generation():
    """통계 생성 테스트"""
    print("\n테스트 5: 통계 생성...")
    try:
        token = os.getenv('GITHUB_TOKEN') or "dummy_token"
        analyzer = GitHubProfileAnalyzer(token)
        
        # 샘플 데이터
        sample_data = [
            {
                'name': 'test-repo',
                'commit_count': 100,
                'stars': 10,
                'forks': 5,
                'size': 1000,
                'languages': {'Python': 5000, 'JavaScript': 3000}
            }
        ]
        
        stats = analyzer.generate_statistics(sample_data)
        
        if stats:
            print("✅ 통계 생성 성공")
            print(f"   총 커밋: {stats.get('total_commits')}")
            print(f"   언어 수: {len(stats.get('language_distribution', {}))}")
            return True
        else:
            print("❌ 통계 생성 실패")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("="*80)
    print("GitHub Profile Analyzer - 기본 테스트 실행")
    print("="*80 + "\n")
    
    tests = [
        test_token_loading,
        test_analyzer_init,
        test_get_repos,
        test_analyze_single_repo,
        test_statistics_generation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*80)
    print("테스트 결과")
    print("="*80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"통과: {passed}/{total}")
    
    if passed == total:
        print("✅ 모든 테스트 통과!")
        return 0
    else:
        print(f"❌ {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
