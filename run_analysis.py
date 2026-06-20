#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Complete Analysis Runner
전체 분석 실행 (기본 + 고급 + 시각화)
"""

import argparse
import sys
import json
from github_scraper import GitHubProfileAnalyzer
from advanced_analyzer import AdvancedGitHubAnalyzer
from visualizer import generate_all_visualizations


def run_complete_analysis(username: str, token: str = None, output_dir: str = '.'):
    """
    완전한 분석 실행
    
    Args:
        username: GitHub 사용자명
        token: GitHub Token
        output_dir: 출력 디렉토리
    """
    print("="*80)
    print("GitHub Profile Complete Analysis")
    print("="*80)
    
    # 1. 기본 분석
    print("\n[1/3] 기본 분석 실행 중...")
    try:
        basic_analyzer = GitHubProfileAnalyzer(token=token)
        basic_result = basic_analyzer.analyze_profile(username)
        
        if not basic_result:
            print("❌ 기본 분석 실패")
            return False
        
        # 기본 분석 저장
        basic_file = f"{output_dir}/{username}_basic_analysis.json"
        with open(basic_file, 'w', encoding='utf-8') as f:
            json.dump(basic_result, f, ensure_ascii=False, indent=2)
        print(f"✅ 기본 분석 완료: {basic_file}")
        
    except Exception as e:
        print(f"❌ 기본 분석 오류: {e}")
        return False
    
    # 2. 고급 분석
    print("\n[2/3] 고급 분석 실행 중...")
    try:
        advanced_analyzer = AdvancedGitHubAnalyzer(token=token)
        advanced_result = advanced_analyzer.analyze_profile_advanced(username)
        
        if not advanced_result:
            print("❌ 고급 분석 실패")
            return False
        
        advanced_analyzer.print_advanced_report(advanced_result)
        
        # 고급 분석 저장
        advanced_file = f"{output_dir}/{username}_advanced_analysis.json"
        with open(advanced_file, 'w', encoding='utf-8') as f:
            json.dump(advanced_result, f, ensure_ascii=False, indent=2)
        print(f"✅ 고급 분석 완료: {advanced_file}")
        
    except Exception as e:
        print(f"❌ 고급 분석 오류: {e}")
        return False
    
    # 3. 시각화
    print("\n[3/3] 시각화 생성 중...")
    try:
        generate_all_visualizations(basic_file, output_prefix=output_dir)
        print("✅ 시각화 완료")
        
    except Exception as e:
        print(f"❌ 시각화 오류: {e}")
        print("  (matplotlib 설치 필요: pip install matplotlib)")
        # 시각화 실패는 치명적이지 않음
    
    print("\n" + "="*80)
    print("🎉 전체 분석 완료!")
    print("="*80)
    print(f"\n생성된 파일:")
    print(f"  - {basic_file}")
    print(f"  - {advanced_file}")
    print(f"  - {output_dir}/{username}_*.png (차트 이미지)")
    print()
    
    return True


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='GitHub Profile Complete Analysis - 전체 분석 실행',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s torvalds                    # 기본 분석
  %(prog)s torvalds -o results         # results 폴더에 저장
  %(prog)s torvalds -t YOUR_TOKEN      # 토큰 지정
        """
    )
    
    parser.add_argument(
        'username',
        type=str,
        help='GitHub 사용자명 또는 프로필 URL'
    )
    
    parser.add_argument(
        '-t', '--token',
        type=str,
        help='GitHub Personal Access Token'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='.',
        help='출력 디렉토리 (기본값: 현재 디렉토리)'
    )
    
    args = parser.parse_args()
    
    # URL에서 사용자명 추출
    username = args.username.strip()
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    # 분석 실행
    success = run_complete_analysis(username, args.token, args.output_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
