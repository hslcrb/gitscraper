#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Advanced Analysis
고급 분석 기능: 코드 변경량, 시간대별 활동, 기여도 분석
"""

import os
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from github import Github, Repository, GithubException
from dotenv import load_dotenv

load_dotenv()


class AdvancedGitHubAnalyzer:
    """고급 GitHub 분석기"""
    
    def __init__(self, token: str = None):
        """초기화"""
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token이 필요합니다.")
        self.github = Github(self.token)
    
    def analyze_commit_activity(self, repo: Repository.Repository, username: str) -> Dict[str, Any]:
        """
        커밋 활동 상세 분석
        
        Args:
            repo: GitHub 리포지토리 객체
            username: 분석할 사용자명
            
        Returns:
            커밋 활동 분석 결과
        """
        try:
            commits = list(repo.get_commits(author=username))
            
            if not commits:
                return {
                    'total_commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'net_changes': 0
                }
            
            total_additions = 0
            total_deletions = 0
            commit_dates = []
            hourly_distribution = defaultdict(int)
            daily_distribution = defaultdict(int)
            
            for commit in commits:
                try:
                    # 커밋 상세 정보
                    stats = commit.stats
                    total_additions += stats.additions
                    total_deletions += stats.deletions
                    
                    # 시간 정보
                    commit_date = commit.commit.author.date
                    commit_dates.append(commit_date)
                    hourly_distribution[commit_date.hour] += 1
                    daily_distribution[commit_date.strftime('%A')] += 1
                    
                except Exception as e:
                    # 개별 커밋 처리 오류는 건너뜀
                    continue
            
            # 활동 기간 계산
            if commit_dates:
                first_commit = min(commit_dates)
                last_commit = max(commit_dates)
                active_days = (last_commit - first_commit).days + 1
            else:
                first_commit = last_commit = None
                active_days = 0
            
            return {
                'total_commits': len(commits),
                'additions': total_additions,
                'deletions': total_deletions,
                'net_changes': total_additions - total_deletions,
                'first_commit': first_commit.strftime('%Y-%m-%d') if first_commit else None,
                'last_commit': last_commit.strftime('%Y-%m-%d') if last_commit else None,
                'active_days': active_days,
                'avg_commits_per_day': round(len(commits) / active_days, 2) if active_days > 0 else 0,
                'hourly_distribution': dict(hourly_distribution),
                'daily_distribution': dict(daily_distribution)
            }
            
        except GithubException as e:
            print(f"커밋 분석 중 GitHub API 오류: {e}")
            return {'total_commits': 0, 'additions': 0, 'deletions': 0, 'net_changes': 0}
        except Exception as e:
            print(f"커밋 분석 중 오류: {e}")
            return {'total_commits': 0, 'additions': 0, 'deletions': 0, 'net_changes': 0}
    
    def analyze_contribution_patterns(self, repos_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        기여 패턴 종합 분석
        
        Args:
            repos_data: 리포지토리 분석 데이터 (고급 정보 포함)
            
        Returns:
            기여 패턴 분석 결과
        """
        total_additions = 0
        total_deletions = 0
        total_net_changes = 0
        
        hourly_combined = defaultdict(int)
        daily_combined = defaultdict(int)
        
        active_repo_count = 0
        
        for repo in repos_data:
            activity = repo.get('commit_activity', {})
            
            if activity.get('total_commits', 0) > 0:
                active_repo_count += 1
                total_additions += activity.get('additions', 0)
                total_deletions += activity.get('deletions', 0)
                total_net_changes += activity.get('net_changes', 0)
                
                # 시간대별 분포 합산
                for hour, count in activity.get('hourly_distribution', {}).items():
                    hourly_combined[hour] += count
                
                # 요일별 분포 합산
                for day, count in activity.get('daily_distribution', {}).items():
                    daily_combined[day] += count
        
        # 가장 활동적인 시간대
        most_active_hour = max(hourly_combined.items(), key=lambda x: x[1])[0] if hourly_combined else None
        
        # 가장 활동적인 요일
        most_active_day = max(daily_combined.items(), key=lambda x: x[1])[0] if daily_combined else None
        
        # 요일 순서 정렬
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sorted_daily = {day: daily_combined.get(day, 0) for day in day_order}
        
        return {
            'active_repositories': active_repo_count,
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'total_net_changes': total_net_changes,
            'total_lines_changed': total_additions + total_deletions,
            'most_active_hour': most_active_hour,
            'most_active_day': most_active_day,
            'hourly_distribution': dict(sorted(hourly_combined.items())),
            'daily_distribution': sorted_daily
        }
    
    def get_repository_contributors(self, repo: Repository.Repository) -> List[Dict[str, Any]]:
        """
        리포지토리 기여자 정보 가져오기
        
        Args:
            repo: GitHub 리포지토리 객체
            
        Returns:
            기여자 목록
        """
        try:
            contributors = []
            for contributor in repo.get_contributors():
                contributors.append({
                    'login': contributor.login,
                    'contributions': contributor.contributions,
                    'type': contributor.type
                })
            return contributors
        except Exception as e:
            print(f"기여자 정보 가져오기 오류: {e}")
            return []
    
    def analyze_user_contribution_role(self, repo: Repository.Repository, username: str) -> Dict[str, Any]:
        """
        사용자의 리포지토리 내 기여 역할 분석
        
        Args:
            repo: GitHub 리포지토리 객체
            username: 분석할 사용자명
            
        Returns:
            기여 역할 분석 결과
        """
        contributors = self.get_repository_contributors(repo)
        
        if not contributors:
            return {'is_owner': repo.owner.login == username, 'role': 'unknown'}
        
        # 전체 기여도
        total_contributions = sum(c['contributions'] for c in contributors)
        
        # 사용자 기여도
        user_contribution = next((c for c in contributors if c['login'] == username), None)
        
        if not user_contribution:
            return {
                'is_owner': repo.owner.login == username,
                'role': 'none',
                'contribution_percentage': 0
            }
        
        user_commits = user_contribution['contributions']
        contribution_percentage = (user_commits / total_contributions * 100) if total_contributions > 0 else 0
        
        # 역할 판단
        if repo.owner.login == username:
            role = 'owner'
        elif contribution_percentage >= 50:
            role = 'main_contributor'
        elif contribution_percentage >= 20:
            role = 'major_contributor'
        elif contribution_percentage >= 5:
            role = 'contributor'
        else:
            role = 'minor_contributor'
        
        return {
            'is_owner': repo.owner.login == username,
            'role': role,
            'user_commits': user_commits,
            'total_commits': total_contributions,
            'contribution_percentage': round(contribution_percentage, 2),
            'total_contributors': len(contributors)
        }
    
    def analyze_profile_advanced(self, username: str) -> Dict[str, Any]:
        """
        프로필 고급 분석 실행
        
        Args:
            username: GitHub 사용자명
            
        Returns:
            고급 분석 결과
        """
        print(f"\n🔬 {username}의 고급 분석 수행 중...\n")
        
        try:
            user = self.github.get_user(username)
            repos = [repo for repo in user.get_repos() if not repo.fork and not repo.private]
            
            print(f"총 {len(repos)}개의 리포지토리를 분석합니다.\n")
            
            repos_data = []
            
            for i, repo in enumerate(repos, 1):
                print(f"고급 분석 중: [{i}/{len(repos)}] {repo.name}")
                
                # 기본 정보
                repo_info = {
                    'name': repo.name,
                    'url': repo.html_url,
                    'description': repo.description or 'No description',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'size': repo.size,
                    'languages': repo.get_languages(),
                    'created_at': repo.created_at.strftime('%Y-%m-%d'),
                    'updated_at': repo.updated_at.strftime('%Y-%m-%d')
                }
                
                # 커밋 활동 분석
                commit_activity = self.analyze_commit_activity(repo, username)
                repo_info['commit_activity'] = commit_activity
                
                # 기여 역할 분석
                contribution_role = self.analyze_user_contribution_role(repo, username)
                repo_info['contribution_role'] = contribution_role
                
                repos_data.append(repo_info)
            
            # 종합 패턴 분석
            patterns = self.analyze_contribution_patterns(repos_data)
            
            result = {
                'username': username,
                'repositories': repos_data,
                'contribution_patterns': patterns
            }
            
            return result
            
        except Exception as e:
            print(f"고급 분석 중 오류: {e}")
            return {}
    
    def print_advanced_report(self, data: Dict[str, Any]):
        """
        고급 분석 리포트 출력
        
        Args:
            data: 고급 분석 결과 데이터
        """
        username = data.get('username', 'Unknown')
        patterns = data.get('contribution_patterns', {})
        repos = data.get('repositories', [])
        
        print("\n" + "="*80)
        print(f"Advanced GitHub Profile Analysis: {username}")
        print("="*80 + "\n")
        
        # 코드 변경량 통계
        print("📝 코드 변경량 통계")
        print("-" * 80)
        print(f"활성 리포지토리 수: {patterns.get('active_repositories', 0)}")
        print(f"총 추가된 줄: {patterns.get('total_additions', 0):,}")
        print(f"총 삭제된 줄: {patterns.get('total_deletions', 0):,}")
        print(f"순 변경량: {patterns.get('total_net_changes', 0):,}")
        print(f"총 변경 줄 수: {patterns.get('total_lines_changed', 0):,}")
        
        # 활동 패턴
        print("\n⏰ 활동 패턴")
        print("-" * 80)
        most_active_hour = patterns.get('most_active_hour')
        most_active_day = patterns.get('most_active_day')
        
        if most_active_hour is not None:
            print(f"가장 활동적인 시간대: {most_active_hour}시")
        if most_active_day:
            print(f"가장 활동적인 요일: {most_active_day}")
        
        # 요일별 분포
        daily_dist = patterns.get('daily_distribution', {})
        if daily_dist:
            print("\n요일별 커밋 분포:")
            for day, count in daily_dist.items():
                bar = '█' * (count // 10 + 1)
                print(f"  {day:12} {bar} ({count})")
        
        # 리포지토리별 상세 기여도
        print("\n🎯 리포지토리별 기여도")
        print("-" * 80)
        
        # 기여도로 정렬
        sorted_repos = sorted(
            repos,
            key=lambda x: x.get('commit_activity', {}).get('additions', 0),
            reverse=True
        )
        
        for i, repo in enumerate(sorted_repos[:15], 1):
            activity = repo.get('commit_activity', {})
            role = repo.get('contribution_role', {})
            
            print(f"\n{i}. {repo['name']}")
            print(f"   역할: {role.get('role', 'unknown')} ({role.get('contribution_percentage', 0)}%)")
            print(f"   추가: +{activity.get('additions', 0):,} | 삭제: -{activity.get('deletions', 0):,} | "
                  f"순변경: {activity.get('net_changes', 0):,}")
            print(f"   커밋: {activity.get('total_commits', 0)} | "
                  f"활동 기간: {activity.get('active_days', 0)}일")
        
        print("\n" + "="*80)


def main():
    """메인 함수"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='GitHub 프로필 고급 분석')
    parser.add_argument('username', type=str, help='GitHub 사용자명')
    parser.add_argument('-o', '--output', type=str, help='JSON 출력 파일')
    parser.add_argument('-t', '--token', type=str, help='GitHub Token')
    
    args = parser.parse_args()
    
    # URL에서 사용자명 추출
    username = args.username.strip()
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    try:
        analyzer = AdvancedGitHubAnalyzer(token=args.token)
        result = analyzer.analyze_profile_advanced(username)
        
        if result:
            analyzer.print_advanced_report(result)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n✅ 결과가 {args.output}에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()
