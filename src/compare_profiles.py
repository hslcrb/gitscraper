#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Profile Comparison
여러 프로필 비교 분석 도구
"""

import json
import sys
from typing import List, Dict, Any
import argparse


def load_analysis_file(filepath: str) -> Dict[str, Any]:
    """JSON 분석 파일 로드"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 파일 로드 오류 ({filepath}): {e}")
        return None


def compare_statistics(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    여러 프로필의 통계 비교
    
    Args:
        profiles: 프로필 데이터 리스트
        
    Returns:
        비교 결과
    """
    comparison = {
        'profiles': [],
        'rankings': {
            'by_commits': [],
            'by_repositories': [],
            'by_stars': [],
            'by_code_size': []
        }
    }
    
    for profile in profiles:
        username = profile.get('username', 'Unknown')
        stats = profile.get('statistics', {})
        
        profile_summary = {
            'username': username,
            'repositories': stats.get('total_repositories', 0),
            'commits': stats.get('total_commits', 0),
            'stars': stats.get('total_stars', 0),
            'forks': stats.get('total_forks', 0),
            'code_size_mb': stats.get('total_size_mb', 0),
            'avg_commits_per_repo': stats.get('avg_commits_per_repo', 0),
            'avg_stars_per_repo': stats.get('avg_stars_per_repo', 0),
            'top_language': None
        }
        
        # 가장 많이 사용한 언어
        lang_dist = stats.get('language_distribution', {})
        if lang_dist:
            top_lang = max(lang_dist.items(), key=lambda x: x[1])
            profile_summary['top_language'] = top_lang[0]
        
        comparison['profiles'].append(profile_summary)
    
    # 랭킹 생성
    comparison['rankings']['by_commits'] = sorted(
        comparison['profiles'],
        key=lambda x: x['commits'],
        reverse=True
    )
    
    comparison['rankings']['by_repositories'] = sorted(
        comparison['profiles'],
        key=lambda x: x['repositories'],
        reverse=True
    )
    
    comparison['rankings']['by_stars'] = sorted(
        comparison['profiles'],
        key=lambda x: x['stars'],
        reverse=True
    )
    
    comparison['rankings']['by_code_size'] = sorted(
        comparison['profiles'],
        key=lambda x: x['code_size_mb'],
        reverse=True
    )
    
    return comparison


def print_comparison_table(comparison: Dict[str, Any]):
    """비교 테이블 출력"""
    print("\n" + "="*100)
    print("GitHub Profile Comparison")
    print("="*100 + "\n")
    
    profiles = comparison['profiles']
    
    # 테이블 헤더
    print(f"{'사용자명':<20} {'리포지토리':<12} {'총 커밋':<12} {'총 스타':<12} "
          f"{'코드량(MB)':<12} {'주요 언어':<15}")
    print("-" * 100)
    
    # 각 프로필 데이터
    for profile in profiles:
        print(f"{profile['username']:<20} "
              f"{profile['repositories']:<12} "
              f"{profile['commits']:<12,} "
              f"{profile['stars']:<12,} "
              f"{profile['code_size_mb']:<12.2f} "
              f"{profile['top_language'] or 'N/A':<15}")
    
    # 랭킹 섹션
    print("\n" + "="*100)
    print("랭킹")
    print("="*100 + "\n")
    
    # 커밋 수 랭킹
    print("📊 커밋 수 랭킹")
    print("-" * 50)
    for i, profile in enumerate(comparison['rankings']['by_commits'][:5], 1):
        print(f"{i}. {profile['username']}: {profile['commits']:,} commits")
    
    # 스타 수 랭킹
    print("\n⭐ 스타 수 랭킹")
    print("-" * 50)
    for i, profile in enumerate(comparison['rankings']['by_stars'][:5], 1):
        print(f"{i}. {profile['username']}: {profile['stars']:,} stars")
    
    # 리포지토리 수 랭킹
    print("\n📦 리포지토리 수 랭킹")
    print("-" * 50)
    for i, profile in enumerate(comparison['rankings']['by_repositories'][:5], 1):
        print(f"{i}. {profile['username']}: {profile['repositories']} repos")
    
    # 코드량 랭킹
    print("\n💾 코드량 랭킹")
    print("-" * 50)
    for i, profile in enumerate(comparison['rankings']['by_code_size'][:5], 1):
        print(f"{i}. {profile['username']}: {profile['code_size_mb']:.2f} MB")
    
    print("\n" + "="*100)


def compare_languages(profiles: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    프로필 간 언어 사용 비교
    
    Args:
        profiles: 프로필 데이터 리스트
        
    Returns:
        사용자별 언어 통계
    """
    language_comparison = {}
    
    for profile in profiles:
        username = profile.get('username', 'Unknown')
        stats = profile.get('statistics', {})
        lang_dist = stats.get('language_distribution', {})
        
        language_comparison[username] = lang_dist
    
    return language_comparison


def print_language_comparison(lang_comparison: Dict[str, Dict[str, int]]):
    """언어 비교 출력"""
    print("\n" + "="*100)
    print("언어 사용 비교")
    print("="*100 + "\n")
    
    # 모든 언어 수집
    all_languages = set()
    for langs in lang_comparison.values():
        all_languages.update(langs.keys())
    
    # 상위 10개 언어만 표시
    top_languages = sorted(
        all_languages,
        key=lambda lang: sum(lang_comparison[user].get(lang, 0) for user in lang_comparison),
        reverse=True
    )[:10]
    
    # 테이블 출력
    print(f"{'언어':<15}", end='')
    for username in lang_comparison.keys():
        print(f"{username:<20}", end='')
    print()
    print("-" * (15 + 20 * len(lang_comparison)))
    
    for lang in top_languages:
        print(f"{lang:<15}", end='')
        for username in lang_comparison.keys():
            bytes_count = lang_comparison[username].get(lang, 0)
            mb_size = bytes_count / (1024 * 1024)
            print(f"{mb_size:<20.2f}", end='')
        print()
    
    print("\n" + "="*100)


def export_comparison_csv(comparison: Dict[str, Any], output_file: str):
    """비교 결과를 CSV로 내보내기"""
    try:
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['username', 'repositories', 'commits', 'stars', 
                         'forks', 'code_size_mb', 'avg_commits_per_repo', 
                         'avg_stars_per_repo', 'top_language']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for profile in comparison['profiles']:
                writer.writerow(profile)
        
        print(f"\n✅ CSV 파일로 저장: {output_file}")
        
    except Exception as e:
        print(f"\n❌ CSV 저장 오류: {e}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='GitHub Profile Comparison - 프로필 비교 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s user1.json user2.json user3.json
  %(prog)s user1.json user2.json -o comparison.json
  %(prog)s user1.json user2.json --csv comparison.csv
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        type=str,
        help='비교할 분석 결과 JSON 파일들'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='비교 결과를 JSON 파일로 저장'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        help='비교 결과를 CSV 파일로 저장'
    )
    
    parser.add_argument(
        '--no-language',
        action='store_true',
        help='언어 비교 출력 생략'
    )
    
    args = parser.parse_args()
    
    # 파일 로드
    print(f"\n📂 {len(args.files)}개의 파일 로드 중...\n")
    
    profiles = []
    for filepath in args.files:
        data = load_analysis_file(filepath)
        if data:
            profiles.append(data)
            print(f"✅ {filepath} 로드 완료")
        else:
            print(f"❌ {filepath} 로드 실패")
    
    if len(profiles) < 2:
        print("\n❌ 비교하려면 최소 2개의 유효한 파일이 필요합니다.")
        return 1
    
    # 비교 수행
    comparison = compare_statistics(profiles)
    
    # 결과 출력
    print_comparison_table(comparison)
    
    # 언어 비교
    if not args.no_language:
        lang_comparison = compare_languages(profiles)
        print_language_comparison(lang_comparison)
    
    # JSON 저장
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 비교 결과 저장: {args.output}")
        except Exception as e:
            print(f"\n❌ JSON 저장 오류: {e}")
    
    # CSV 저장
    if args.csv:
        export_comparison_csv(comparison, args.csv)
    
    print("\n✅ 비교 완료!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
