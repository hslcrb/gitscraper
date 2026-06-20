#!/usr/bin/env python3
"""
GitHub Profile Analyzer - CLI Interface
향상된 CLI 인터페이스와 JSON 출력 기능
"""

import argparse
import json
import sys
from github_scraper import GitHubProfileAnalyzer


def save_to_json(data: dict, output_file: str):
    """
    분석 결과를 JSON 파일로 저장
    
    Args:
        data: 분석 결과 데이터
        output_file: 출력 파일 경로
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 결과가 {output_file}에 저장되었습니다.")
    except Exception as e:
        print(f"\n❌ 파일 저장 중 오류: {e}")


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description='GitHub Profile Analyzer - GitHub 프로필 분석 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  %(prog)s torvalds                          # 기본 분석
  %(prog)s torvalds -o result.json           # JSON으로 결과 저장
  %(prog)s https://github.com/torvalds       # URL로 분석
  %(prog)s torvalds --no-output              # 리포트 출력 안 함
        """
    )
    
    parser.add_argument(
        'username',
        type=str,
        help='GitHub 사용자명 또는 프로필 URL'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        metavar='FILE',
        help='결과를 JSON 파일로 저장 (예: result.json)'
    )
    
    parser.add_argument(
        '-t', '--token',
        type=str,
        metavar='TOKEN',
        help='GitHub Personal Access Token (환경 변수 대신 사용)'
    )
    
    parser.add_argument(
        '--no-output',
        action='store_true',
        help='콘솔 출력 억제 (파일 저장만 수행)'
    )
    
    parser.add_argument(
        '--json-only',
        action='store_true',
        help='JSON 형식으로만 출력 (파일명 없으면 stdout)'
    )
    
    args = parser.parse_args()
    
    # URL에서 사용자명 추출
    username = args.username.strip()
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    try:
        # 분석기 초기화
        analyzer = GitHubProfileAnalyzer(token=args.token)
        
        # 분석 실행
        if not args.no_output and not args.json_only:
            print(f"\n🔍 {username}의 GitHub 프로필 분석 중...\n")
        
        repos = analyzer.get_user_repos(username)
        
        if not repos:
            print("분석할 리포지토리가 없습니다.")
            return 1
        
        if not args.no_output and not args.json_only:
            print(f"총 {len(repos)}개의 공개 리포지토리를 찾았습니다.\n")
        
        # 각 리포지토리 분석
        repos_data = []
        for i, repo in enumerate(repos, 1):
            if not args.no_output and not args.json_only:
                print(f"분석 중: [{i}/{len(repos)}] {repo.name}")
            repo_info = analyzer.analyze_repository(repo)
            if repo_info:
                repos_data.append(repo_info)
        
        # 통계 생성
        stats = analyzer.generate_statistics(repos_data)
        
        result = {
            'username': username,
            'repositories': repos_data,
            'statistics': stats
        }
        
        # 출력 처리
        if args.json_only:
            # JSON만 출력
            if args.output:
                save_to_json(result, args.output)
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 일반 리포트 출력
            if not args.no_output:
                analyzer.print_report(username, repos_data, stats)
                print("\n✅ 분석이 완료되었습니다!")
            
            # 파일 저장
            if args.output:
                save_to_json(result, args.output)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
