#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Unified Analyzer
통합 분석기: Private/Public 선택 가능, 즉시 Token 폐기
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, Repository
from collections import defaultdict
import gc


class UnifiedGitHubAnalyzer:
    """통합 GitHub 분석기"""
    
    def __init__(self, token: str):
        """초기화 - Token은 즉시 사용 후 폐기"""
        if not token:
            raise ValueError("GitHub token이 필요합니다.")
        
        self.github = Github(token)
        # Token은 Github 객체에 저장되므로 로컬 변수에서 즉시 제거
        del token
        gc.collect()  # 강제 가비지 컬렉션
    
    def get_user_repos(self, username: str, repo_type: str = "all") -> List[Repository.Repository]:
        """
        사용자의 리포지토리 목록 가져오기
        
        Args:
            username: GitHub 사용자명
            repo_type: "public", "private", "all" (기본값: "all")
            
        Returns:
            리포지토리 목록
        """
        try:
            user = self.github.get_user(username)
            repos = list(user.get_repos())
            
            # Fork 제외
            repos = [repo for repo in repos if not repo.fork]
            
            # 타입별 필터링
            if repo_type == "public":
                repos = [repo for repo in repos if not repo.private]
            elif repo_type == "private":
                repos = [repo for repo in repos if repo.private]
            # "all"이면 필터링 없음
            
            return repos
        except Exception as e:
            print(f"사용자 정보를 가져오는 중 오류 발생: {e}")
            return []
    
    def analyze_repository_detailed(self, repo: Repository.Repository) -> Optional[Dict[str, Any]]:
        """
        리포지토리 상세 분석 (모든 가능한 정보 수집)
        
        Args:
            repo: GitHub 리포지토리 객체
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 기본 정보
            repo_info = {
                'name': repo.name,
                'full_name': repo.full_name,
                'url': repo.html_url,
                'description': repo.description or 'No description',
                'private': repo.private,
                'fork': repo.fork,
                'archived': repo.archived,
                'disabled': repo.disabled,
                
                # 통계
                'stars': repo.stargazers_count,
                'watchers': repo.watchers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'size': repo.size,  # KB
                
                # 언어
                'language': repo.language,
                'languages': repo.get_languages(),
                
                # 시간 정보
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                
                # 날짜만 (추가 편의성)
                'created_date': repo.created_at.strftime('%Y-%m-%d'),
                'updated_date': repo.updated_at.strftime('%Y-%m-%d'),
                'pushed_date': repo.pushed_at.strftime('%Y-%m-%d') if repo.pushed_at else None,
                
                # 기간 계산
                'age_days': (datetime.now(repo.created_at.tzinfo) - repo.created_at).days,
                'last_update_days_ago': (datetime.now(repo.updated_at.tzinfo) - repo.updated_at).days,
                
                # 라이선스
                'license': repo.license.name if repo.license else None,
                
                # 브랜치
                'default_branch': repo.default_branch,
                
                # URL들
                'clone_url': repo.clone_url,
                'git_url': repo.git_url,
                'ssh_url': repo.ssh_url,
                
                # 기타
                'has_issues': repo.has_issues,
                'has_projects': repo.has_projects,
                'has_wiki': repo.has_wiki,
                'has_pages': repo.has_pages,
                'has_downloads': repo.has_downloads,
            }
            
            # 커밋 수 가져오기
            try:
                commits = repo.get_commits()
                repo_info['commit_count'] = commits.totalCount
            except:
                repo_info['commit_count'] = 0
            
            # 기여자 수
            try:
                contributors = list(repo.get_contributors())
                repo_info['contributors_count'] = len(contributors)
            except:
                repo_info['contributors_count'] = 0
            
            # 브랜치 수
            try:
                branches = list(repo.get_branches())
                repo_info['branches_count'] = len(branches)
            except:
                repo_info['branches_count'] = 0
            
            # 태그/릴리스 수
            try:
                tags = list(repo.get_tags())
                repo_info['tags_count'] = len(tags)
            except:
                repo_info['tags_count'] = 0
            
            return repo_info
            
        except Exception as e:
            print(f"리포지토리 {repo.name} 분석 중 오류: {e}")
            return None
    
    def generate_comprehensive_statistics(self, repos_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        종합 통계 생성
        
        Args:
            repos_data: 리포지토리 분석 데이터 목록
            
        Returns:
            통계 딕셔너리
        """
        if not repos_data:
            return {}
        
        # 기본 집계
        total_commits = sum(repo['commit_count'] for repo in repos_data)
        total_stars = sum(repo['stars'] for repo in repos_data)
        total_watchers = sum(repo['watchers'] for repo in repos_data)
        total_forks = sum(repo['forks'] for repo in repos_data)
        total_issues = sum(repo['open_issues'] for repo in repos_data)
        total_size = sum(repo['size'] for repo in repos_data)
        total_contributors = sum(repo.get('contributors_count', 0) for repo in repos_data)
        
        # Private vs Public
        public_repos = [r for r in repos_data if not r['private']]
        private_repos = [r for r in repos_data if r['private']]
        
        # 언어별 코드량 집계
        language_stats = defaultdict(int)
        language_repo_count = defaultdict(int)
        for repo in repos_data:
            for lang, bytes_count in repo['languages'].items():
                language_stats[lang] += bytes_count
                language_repo_count[lang] += 1
        
        sorted_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
        
        # 시간 분석
        dates = [datetime.fromisoformat(repo['created_at']) for repo in repos_data]
        if dates:
            oldest_repo_date = min(dates).strftime('%Y-%m-%d')
            newest_repo_date = max(dates).strftime('%Y-%m-%d')
        else:
            oldest_repo_date = newest_repo_date = None
        
        # 활동성 분석
        recently_updated = [r for r in repos_data if r['last_update_days_ago'] <= 30]
        active_repos = [r for r in repos_data if r['last_update_days_ago'] <= 90]
        
        # 라이선스 통계
        licenses = defaultdict(int)
        for repo in repos_data:
            lic = repo.get('license', 'No License')
            licenses[lic] += 1
        
        stats = {
            # 기본 통계
            'total_repositories': len(repos_data),
            'public_repositories': len(public_repos),
            'private_repositories': len(private_repos),
            'archived_repositories': sum(1 for r in repos_data if r.get('archived', False)),
            
            # 참여 통계
            'total_commits': total_commits,
            'total_stars': total_stars,
            'total_watchers': total_watchers,
            'total_forks': total_forks,
            'total_open_issues': total_issues,
            'total_contributors': total_contributors,
            
            # 코드량
            'total_size_kb': total_size,
            'total_size_mb': round(total_size / 1024, 2),
            'total_size_gb': round(total_size / (1024 * 1024), 2),
            
            # 평균
            'avg_commits_per_repo': round(total_commits / len(repos_data), 2) if repos_data else 0,
            'avg_stars_per_repo': round(total_stars / len(repos_data), 2) if repos_data else 0,
            'avg_forks_per_repo': round(total_forks / len(repos_data), 2) if repos_data else 0,
            'avg_size_mb_per_repo': round(total_size / 1024 / len(repos_data), 2) if repos_data else 0,
            
            # 언어 통계
            'language_distribution': dict(sorted_languages),
            'language_repo_count': dict(sorted(language_repo_count.items(), key=lambda x: x[1], reverse=True)),
            'total_languages': len(language_stats),
            'primary_language': sorted_languages[0][0] if sorted_languages else None,
            
            # 시간 통계
            'oldest_repo_date': oldest_repo_date,
            'newest_repo_date': newest_repo_date,
            'account_age_days': (datetime.now() - min(dates)).days if dates else 0,
            
            # 활동성
            'recently_updated_count': len(recently_updated),
            'active_repos_count': len(active_repos),
            'inactive_repos_count': len(repos_data) - len(active_repos),
            
            # 라이선스
            'license_distribution': dict(licenses),
            
            # 기타
            'total_branches': sum(repo.get('branches_count', 0) for repo in repos_data),
            'total_tags': sum(repo.get('tags_count', 0) for repo in repos_data),
            
            # 분석 시간
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return stats
    
    def analyze_profile(self, username: str, repo_type: str = "all", progress_callback=None) -> Dict[str, Any]:
        """
        프로필 전체 분석 실행
        
        Args:
            username: GitHub 사용자명
            repo_type: "public", "private", "all"
            progress_callback: 진행상황 콜백 함수
            
        Returns:
            분석 결과
        """
        # 리포지토리 목록 가져오기
        repos = self.get_user_repos(username, repo_type)
        
        if not repos:
            return {
                'username': username,
                'repo_type': repo_type,
                'error': 'No repositories found',
                'repositories': [],
                'statistics': {}
            }
        
        # 각 리포지토리 분석
        repos_data = []
        total = len(repos)
        
        for i, repo in enumerate(repos, 1):
            if progress_callback:
                progress_callback(i, total, repo.name)
            
            repo_info = self.analyze_repository_detailed(repo)
            if repo_info:
                repos_data.append(repo_info)
        
        # 통계 생성
        stats = self.generate_comprehensive_statistics(repos_data)
        
        result = {
            'username': username,
            'repo_type': repo_type,
            'repositories': repos_data,
            'statistics': stats,
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'total_analyzed': len(repos_data),
                'analysis_type': repo_type,
            }
        }
        
        return result
    
    def cleanup(self):
        """리소스 정리 및 Token 제거"""
        if hasattr(self, 'github'):
            del self.github
        gc.collect()
