#!/usr/bin/env python3
"""
GitHub Profile Analyzer
GitHub 프로필의 오픈소스 리포지토리 분석 도구
"""

import os
from typing import List, Dict, Any
from github import Github, Repository
from dotenv import load_dotenv
from collections import defaultdict

# .env 파일에서 환경 변수 로드
load_dotenv()


class GitHubProfileAnalyzer:
    """GitHub 프로필 분석기"""
    
    def __init__(self, token: str = None):
        """
        초기화
        
        Args:
            token: GitHub Personal Access Token (없으면 환경 변수에서 로드)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token이 필요합니다. .env 파일에 GITHUB_TOKEN을 설정하세요.")
        
        self.github = Github(self.token)
    
    def get_user_repos(self, username: str) -> List[Repository.Repository]:
        """
        사용자의 공개 리포지토리 목록 가져오기
        
        Args:
            username: GitHub 사용자명
            
        Returns:
            리포지토리 목록
        """
        try:
            user = self.github.get_user(username)
            repos = [repo for repo in user.get_repos() if not repo.fork and not repo.private]
            return repos
        except Exception as e:
            print(f"사용자 정보를 가져오는 중 오류 발생: {e}")
            return []
    
    def analyze_repository(self, repo: Repository.Repository) -> Dict[str, Any]:
        """
        개별 리포지토리 분석
        
        Args:
            repo: GitHub 리포지토리 객체
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 커밋 수 가져오기
            commits = repo.get_commits()
            commit_count = commits.totalCount
            
            # 언어 정보
            languages = repo.get_languages()
            
            # 기본 정보
            repo_info = {
                'name': repo.name,
                'url': repo.html_url,
                'description': repo.description or 'No description',
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'commit_count': commit_count,
                'languages': languages,
                'created_at': repo.created_at.strftime('%Y-%m-%d'),
                'updated_at': repo.updated_at.strftime('%Y-%m-%d'),
                'size': repo.size  # KB 단위
            }
            
            return repo_info
        except Exception as e:
            print(f"리포지토리 {repo.name} 분석 중 오류: {e}")
            return None
    
    def generate_statistics(self, repos_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        종합 통계 생성
        
        Args:
            repos_data: 리포지토리 분석 데이터 목록
            
        Returns:
            통계 딕셔너리
        """
        if not repos_data:
            return {}
        
        total_commits = sum(repo['commit_count'] for repo in repos_data)
        total_stars = sum(repo['stars'] for repo in repos_data)
        total_forks = sum(repo['forks'] for repo in repos_data)
        total_size = sum(repo['size'] for repo in repos_data)
        
        # 언어별 코드량 집계
        language_stats = defaultdict(int)
        for repo in repos_data:
            for lang, bytes_count in repo['languages'].items():
                language_stats[lang] += bytes_count
        
        # 언어별 정렬
        sorted_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
        
        stats = {
            'total_repositories': len(repos_data),
            'total_commits': total_commits,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_size_kb': total_size,
            'total_size_mb': round(total_size / 1024, 2),
            'language_distribution': dict(sorted_languages),
            'avg_commits_per_repo': round(total_commits / len(repos_data), 2),
            'avg_stars_per_repo': round(total_stars / len(repos_data), 2),
        }
        
        return stats
    
    def print_report(self, username: str, repos_data: List[Dict[str, Any]], stats: Dict[str, Any]):
        """
        분석 결과 출력
        
        Args:
            username: GitHub 사용자명
            repos_data: 리포지토리 데이터
            stats: 통계 데이터
        """
        print("\n" + "="*80)
        print(f"GitHub Profile Analysis Report: {username}")
        print("="*80 + "\n")
        
        # 종합 통계
        print("📊 종합 통계")
        print("-" * 80)
        print(f"총 리포지토리 수: {stats['total_repositories']}")
        print(f"총 커밋 수: {stats['total_commits']:,}")
        print(f"총 스타 수: {stats['total_stars']:,}")
        print(f"총 포크 수: {stats['total_forks']:,}")
        print(f"총 코드량: {stats['total_size_mb']} MB ({stats['total_size_kb']:,} KB)")
        print(f"리포지토리당 평균 커밋: {stats['avg_commits_per_repo']}")
        print(f"리포지토리당 평균 스타: {stats['avg_stars_per_repo']}")
        
        # 언어 분포
        print("\n💻 언어별 코드 분포")
        print("-" * 80)
        total_bytes = sum(stats['language_distribution'].values())
        for lang, bytes_count in list(stats['language_distribution'].items())[:10]:
            percentage = (bytes_count / total_bytes) * 100
            mb_size = bytes_count / (1024 * 1024)
            print(f"{lang:20} {percentage:6.2f}%  ({mb_size:.2f} MB)")
        
        # 리포지토리 상세 정보
        print("\n📦 리포지토리 상세 정보")
        print("-" * 80)
        
        # 커밋 수로 정렬
        sorted_repos = sorted(repos_data, key=lambda x: x['commit_count'], reverse=True)
        
        for i, repo in enumerate(sorted_repos, 1):
            print(f"\n{i}. {repo['name']}")
            print(f"   URL: {repo['url']}")
            print(f"   설명: {repo['description']}")
            print(f"   커밋: {repo['commit_count']:,} | 스타: {repo['stars']} | 포크: {repo['forks']}")
            print(f"   생성일: {repo['created_at']} | 마지막 업데이트: {repo['updated_at']}")
            if repo['languages']:
                langs = ', '.join([f"{k} ({v:,} bytes)" for k, v in list(repo['languages'].items())[:3]])
                print(f"   주요 언어: {langs}")
        
        print("\n" + "="*80)
    
    def analyze_profile(self, username: str) -> Dict[str, Any]:
        """
        프로필 전체 분석 실행
        
        Args:
            username: GitHub 사용자명
            
        Returns:
            분석 결과
        """
        print(f"\n🔍 {username}의 GitHub 프로필 분석 중...\n")
        
        # 리포지토리 목록 가져오기
        repos = self.get_user_repos(username)
        print(f"총 {len(repos)}개의 공개 리포지토리를 찾았습니다.\n")
        
        if not repos:
            print("분석할 리포지토리가 없습니다.")
            return {}
        
        # 각 리포지토리 분석
        repos_data = []
        for i, repo in enumerate(repos, 1):
            print(f"분석 중: [{i}/{len(repos)}] {repo.name}")
            repo_info = self.analyze_repository(repo)
            if repo_info:
                repos_data.append(repo_info)
        
        # 통계 생성
        stats = self.generate_statistics(repos_data)
        
        # 결과 출력
        self.print_report(username, repos_data, stats)
        
        return {
            'username': username,
            'repositories': repos_data,
            'statistics': stats
        }


def main():
    """메인 함수"""
    print("="*80)
    print("GitHub Profile Analyzer")
    print("="*80)
    
    # 사용자 입력
    username = input("\nGitHub 사용자명 또는 프로필 URL을 입력하세요: ").strip()
    
    # URL에서 사용자명 추출
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    try:
        analyzer = GitHubProfileAnalyzer()
        result = analyzer.analyze_profile(username)
        
        if result:
            print("\n✅ 분석이 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
