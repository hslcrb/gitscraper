#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Visualization
분석 결과 시각화 모듈
"""

import json
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform


def setup_korean_font():
    """한글 폰트 설정"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        plt.rc('font', family='AppleGothic')
    elif system == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    else:  # Linux
        # 시스템에 설치된 한글 폰트 찾기
        fonts = [f.name for f in fm.fontManager.ttflist]
        korean_fonts = ['NanumGothic', 'NanumBarunGothic', 'DejaVu Sans']
        
        for font in korean_fonts:
            if font in fonts:
                plt.rc('font', family=font)
                break
    
    # 마이너스 기호 깨짐 방지
    plt.rc('axes', unicode_minus=False)


def plot_language_distribution(stats: Dict[str, Any], output_file: str = 'language_distribution.png'):
    """
    언어 분포 파이 차트
    
    Args:
        stats: 통계 데이터
        output_file: 출력 파일명
    """
    setup_korean_font()
    
    lang_dist = stats.get('language_distribution', {})
    if not lang_dist:
        print("언어 분포 데이터가 없습니다.")
        return
    
    # 상위 10개 언어만 표시
    sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:10]
    languages = [lang for lang, _ in sorted_langs]
    sizes = [size for _, size in sorted_langs]
    
    # 나머지를 'Others'로 묶기
    if len(lang_dist) > 10:
        others_size = sum(size for _, size in sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[10:])
        languages.append('Others')
        sizes.append(others_size)
    
    # 파이 차트 생성
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.Set3(range(len(languages)))
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=languages,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors
    )
    
    # 텍스트 스타일 설정
    for text in texts:
        text.set_fontsize(11)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    ax.set_title('언어별 코드 분포', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 언어 분포 차트 저장: {output_file}")
    plt.close()


def plot_repo_commits(repos_data: List[Dict[str, Any]], output_file: str = 'repo_commits.png'):
    """
    리포지토리별 커밋 수 바 차트
    
    Args:
        repos_data: 리포지토리 데이터
        output_file: 출력 파일명
    """
    setup_korean_font()
    
    if not repos_data:
        print("리포지토리 데이터가 없습니다.")
        return
    
    # 커밋 수로 정렬 (상위 15개)
    sorted_repos = sorted(repos_data, key=lambda x: x['commit_count'], reverse=True)[:15]
    repo_names = [repo['name'] for repo in sorted_repos]
    commit_counts = [repo['commit_count'] for repo in sorted_repos]
    
    # 바 차트 생성
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(repo_names, commit_counts, color='steelblue')
    
    # 각 바에 값 표시
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{int(width):,}',
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    ax.set_xlabel('커밋 수', fontsize=12, fontweight='bold')
    ax.set_title('리포지토리별 커밋 수 (상위 15개)', fontsize=16, fontweight='bold', pad=20)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 커밋 수 차트 저장: {output_file}")
    plt.close()


def plot_repo_popularity(repos_data: List[Dict[str, Any]], output_file: str = 'repo_popularity.png'):
    """
    리포지토리별 스타/포크 수 산점도
    
    Args:
        repos_data: 리포지토리 데이터
        output_file: 출력 파일명
    """
    setup_korean_font()
    
    if not repos_data:
        print("리포지토리 데이터가 없습니다.")
        return
    
    repo_names = [repo['name'] for repo in repos_data]
    stars = [repo['stars'] for repo in repos_data]
    forks = [repo['forks'] for repo in repos_data]
    
    # 산점도 생성
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(stars, forks, s=100, alpha=0.6, c=range(len(repo_names)), cmap='viridis')
    
    # 주요 리포지토리 레이블 표시 (스타 또는 포크가 많은 상위 10개)
    combined_score = [(i, stars[i] + forks[i]) for i in range(len(repo_names))]
    top_repos = sorted(combined_score, key=lambda x: x[1], reverse=True)[:10]
    
    for idx, _ in top_repos:
        ax.annotate(repo_names[idx], 
                   (stars[idx], forks[idx]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.8)
    
    ax.set_xlabel('스타 수', fontsize=12, fontweight='bold')
    ax.set_ylabel('포크 수', fontsize=12, fontweight='bold')
    ax.set_title('리포지토리 인기도 (스타 vs 포크)', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 인기도 차트 저장: {output_file}")
    plt.close()


def generate_all_visualizations(json_file: str, output_prefix: str = ''):
    """
    모든 시각화 생성
    
    Args:
        json_file: 분석 결과 JSON 파일
        output_prefix: 출력 파일명 접두어
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        repos_data = data.get('repositories', [])
        stats = data.get('statistics', {})
        username = data.get('username', 'unknown')
        
        print(f"\n📊 {username}의 시각화 생성 중...\n")
        
        # 파일명 접두어 설정
        prefix = f"{output_prefix}_{username}_" if output_prefix else f"{username}_"
        
        # 각종 차트 생성
        plot_language_distribution(stats, f'{prefix}language_distribution.png')
        plot_repo_commits(repos_data, f'{prefix}repo_commits.png')
        plot_repo_popularity(repos_data, f'{prefix}repo_popularity.png')
        
        print(f"\n✅ 모든 시각화가 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 시각화 생성 중 오류: {e}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub 프로필 분석 결과 시각화')
    parser.add_argument('json_file', type=str, help='분석 결과 JSON 파일')
    parser.add_argument('-p', '--prefix', type=str, default='', help='출력 파일명 접두어')
    
    args = parser.parse_args()
    
    generate_all_visualizations(args.json_file, args.prefix)


if __name__ == "__main__":
    main()
