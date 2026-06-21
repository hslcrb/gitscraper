#!/usr/bin/env python3
"""
GitHub Profile Analyzer - RICH TUI Main
RICH 라이브러리 기반 터미널 UI 메인 프로그램
보안: Token을 메모리에만 유지하고 파일에 저장하지 않음
"""

import sys
import os
from pathlib import Path
from getpass import getpass

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.tree import Tree
import time

from github_scraper import GitHubProfileAnalyzer

console = Console()

# 전역 토큰 변수 (세션 동안만 메모리에 유지)
_github_token = None


def show_banner():
    """배너 표시"""
    banner = Text()
    banner.append("╔═══════════════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║                                                               ║\n", style="bold cyan")
    banner.append("║           ", style="bold cyan")
    banner.append("GitHub Profile Analyzer", style="bold white on blue")
    banner.append("                      ║\n", style="bold cyan")
    banner.append("║                                                               ║\n", style="bold cyan")
    banner.append("║          ", style="bold cyan")
    banner.append("RICH TUI 기반 프로필 분석 도구", style="bold yellow")
    banner.append("                 ║\n", style="bold cyan")
    banner.append("║                                                               ║\n", style="bold cyan")
    banner.append("╚═══════════════════════════════════════════════════════════════╝", style="bold cyan")
    
    console.print(banner)
    console.print()


def show_main_menu():
    """메인 메뉴 표시"""
    menu_panel = Panel(
        "[bold cyan]1[/] [*] 프로필 기본 분석\n"
        "[bold cyan]2[/] [+] 프로필 고급 분석\n"
        "[bold cyan]3[/] [~] 시각화 생성\n"
        "[bold cyan]4[/] [=] 프로필 비교\n"
        "[bold cyan]5[/] [@] 리포트 내보내기\n"
        "[bold cyan]6[/] [#] 설정\n"
        "[bold cyan]0[/] [X] 종료",
        title="[bold white on blue] 메인 메뉴 ",
        border_style="cyan",
        box=box.DOUBLE
    )
    console.print(menu_panel)


def create_stats_table(stats: dict) -> Table:
    """통계 테이블 생성"""
    table = Table(
        title="[*] 종합 통계",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        border_style="cyan"
    )
    
    table.add_column("항목", style="cyan", justify="left")
    table.add_column("값", style="green", justify="right")
    
    table.add_row("총 리포지토리", f"{stats.get('total_repositories', 0):,}")
    table.add_row("총 커밋 수", f"{stats.get('total_commits', 0):,}")
    table.add_row("총 스타 수", f"{stats.get('total_stars', 0):,}")
    table.add_row("총 포크 수", f"{stats.get('total_forks', 0):,}")
    table.add_row("총 코드량", f"{stats.get('total_size_mb', 0):.2f} MB")
    table.add_row("평균 커밋/리포", f"{stats.get('avg_commits_per_repo', 0):.2f}")
    table.add_row("평균 스타/리포", f"{stats.get('avg_stars_per_repo', 0):.2f}")
    
    return table


def create_language_table(lang_dist: dict) -> Table:
    """언어 분포 테이블 생성"""
    table = Table(
        title="[</>] 언어별 코드 분포",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold yellow",
        border_style="yellow"
    )
    
    table.add_column("순위", style="cyan", justify="center", width=6)
    table.add_column("언어", style="magenta", justify="left")
    table.add_column("비율", style="green", justify="right")
    table.add_column("크기", style="blue", justify="right")
    table.add_column("바", style="white", justify="left", width=30)
    
    total_bytes = sum(lang_dist.values())
    sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (lang, bytes_count) in enumerate(sorted_langs, 1):
        percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
        mb_size = bytes_count / (1024 * 1024)
        
        # 프로그레스 바
        bar_length = int(percentage / 100 * 25)
        bar = "█" * bar_length + "░" * (25 - bar_length)
        
        table.add_row(
            f"{i}",
            lang,
            f"{percentage:.2f}%",
            f"{mb_size:.2f} MB",
            bar
        )
    
    return table


def create_repo_tree(repos: list) -> Tree:
    """리포지토리 트리 생성"""
    tree = Tree("[#] [bold cyan]리포지토리 목록")
    
    sorted_repos = sorted(repos, key=lambda x: x.get('commit_count', 0), reverse=True)[:15]
    
    for repo in sorted_repos:
        repo_branch = tree.add(f"[bold yellow]{repo['name']}")
        repo_branch.add(f"[>] {repo['url']}")
        repo_branch.add(f"[-] {repo.get('description', 'No description')[:60]}...")
        
        stats_text = (f"[*] {repo.get('stars', 0):,} | "
                     f"[+] {repo.get('forks', 0):,} | "
                     f"[~] {repo.get('commit_count', 0):,} commits")
        repo_branch.add(stats_text)
        
        if repo.get('languages'):
            langs = ', '.join(list(repo['languages'].keys())[:3])
            repo_branch.add(f"[</>] {langs}")
    
    return tree


def get_github_token():
    """GitHub Token 가져오기 (보안: 화면에 표시 안 됨)"""
    global _github_token
    
    if _github_token:
        return _github_token
    
    console.print("\n[yellow][!] GitHub Personal Access Token이 필요합니다.")
    console.print("[dim]Token은 메모리에만 저장되며 파일로 저장되지 않습니다.\n")
    
    token = getpass("Token을 입력하세요 (입력 내용은 화면에 표시되지 않습니다): ")
    
    if not token:
        console.print("[red][X] Token이 필요합니다.")
        return None
    
    _github_token = token
    console.print("[green][+] Token이 설정되었습니다.\n")
    return token


def clear_token():
    """Token 메모리에서 제거"""
    global _github_token
    if _github_token:
        _github_token = None
        console.print("[yellow][#] Token이 메모리에서 제거되었습니다.")


def analyze_profile_with_progress(username: str):
    """프로그레스바와 함께 프로필 분석"""
    console.print()
    
    token = get_github_token()
    if not token:
        return None
    
    try:
        analyzer = GitHubProfileAnalyzer(token=token)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            # 리포지토리 가져오기
            task1 = progress.add_task(
                f"[cyan][?] {username}의 리포지토리 검색 중...",
                total=100
            )
            repos = analyzer.get_user_repos(username)
            progress.update(task1, completed=100)
            
            if not repos:
                console.print("[red][X] 리포지토리를 찾을 수 없습니다.")
                return None
            
            console.print(f"\n[green][+] {len(repos)}개의 공개 리포지토리 발견!\n")
            
            # 각 리포지토리 분석
            task2 = progress.add_task(
                "[cyan][*] 리포지토리 분석 중...",
                total=len(repos)
            )
            
            repos_data = []
            for repo in repos:
                repo_info = analyzer.analyze_repository(repo)
                if repo_info:
                    repos_data.append(repo_info)
                progress.update(task2, advance=1)
            
            # 통계 생성
            task3 = progress.add_task(
                "[cyan][~] 통계 생성 중...",
                total=100
            )
            stats = analyzer.generate_statistics(repos_data)
            progress.update(task3, completed=100)
        
        result = {
            'username': username,
            'repositories': repos_data,
            'statistics': stats
        }
        
        return result
        
    except Exception as e:
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
        console.print(f"[red][X] 오류 발생: {error_msg}")
        return None


def show_analysis_results(result: dict):
    """분석 결과 표시"""
    console.clear()
    show_banner()
    
    username = result.get('username', 'Unknown')
    repos = result.get('repositories', [])
    stats = result.get('statistics', {})
    
    # 헤더
    header = Panel(
        f"[bold white on blue] 분석 완료: {username} ",
        border_style="cyan"
    )
    console.print(header)
    console.print()
    
    # 통계 테이블
    stats_table = create_stats_table(stats)
    console.print(stats_table)
    console.print()
    
    # 언어 분포
    lang_dist = stats.get('language_distribution', {})
    if lang_dist:
        lang_table = create_language_table(lang_dist)
        console.print(lang_table)
        console.print()
    
    # 리포지토리 트리
    repo_tree = create_repo_tree(repos)
    console.print(repo_tree)
    console.print()
    
    # JSON 저장 옵션
    if Confirm.ask("[?] 결과를 JSON 파일로 저장하시겠습니까?", default=False):
        import json
        filename = f"{username}_analysis.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            console.print(f"[green][+] 저장 완료: {filename}")
        except Exception as e:
            error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
            console.print(f"[red][X] 저장 실패: {error_msg}")
    
    console.print()
    Prompt.ask("계속하려면 Enter를 누르세요")


def basic_analysis():
    """기본 분석 실행"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold cyan]GitHub 프로필 기본 분석\n\n"
        "사용자명 또는 프로필 URL을 입력하세요.",
        title="[bold white on blue] 기본 분석 ",
        border_style="cyan"
    )
    console.print(panel)
    console.print()
    
    username = Prompt.ask("[>] [cyan]GitHub 사용자명")
    
    # URL에서 사용자명 추출
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    if not username:
        console.print("[red][X] 사용자명을 입력해주세요.")
        time.sleep(2)
        return
    
    # 분석 실행
    result = analyze_profile_with_progress(username)
    
    if result:
        show_analysis_results(result)


def advanced_analysis():
    """고급 분석 실행"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold yellow][+] 고급 분석 기능\n\n"
        "코드 변경량, 활동 패턴, 기여도 등을 상세 분석합니다.\n"
        "[dim]구현 예정...",
        title="[bold white on blue] 고급 분석 ",
        border_style="yellow"
    )
    console.print(panel)
    console.print()
    Prompt.ask("계속하려면 Enter를 누르세요")


def visualize_data():
    """시각화 생성"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold green][~] 데이터 시각화\n\n"
        "차트와 그래프를 생성합니다.\n"
        "[dim]구현 예정...",
        title="[bold white on blue] 시각화 ",
        border_style="green"
    )
    console.print(panel)
    console.print()
    Prompt.ask("계속하려면 Enter를 누르세요")


def compare_profiles():
    """프로필 비교"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold magenta][=] 프로필 비교\n\n"
        "여러 GitHub 프로필을 비교 분석합니다.\n"
        "[dim]구현 예정...",
        title="[bold white on blue] 프로필 비교 ",
        border_style="magenta"
    )
    console.print(panel)
    console.print()
    Prompt.ask("계속하려면 Enter를 누르세요")


def export_report():
    """리포트 내보내기"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold blue][@] 리포트 내보내기\n\n"
        "Markdown, HTML, CSV 등 다양한 형식으로 내보냅니다.\n"
        "[dim]구현 예정...",
        title="[bold white on blue] 리포트 내보내기 ",
        border_style="blue"
    )
    console.print(panel)
    console.print()
    Prompt.ask("계속하려면 Enter를 누르세요")


def show_settings():
    """설정 화면"""
    console.clear()
    show_banner()
    
    panel = Panel(
        "[bold cyan][#] 설정\n\n"
        "[yellow]1[/] [+] Token 재설정\n"
        "[yellow]2[/] [#] Token 제거 (메모리)\n"
        "[yellow]3[/] [?] Token 상태 확인\n"
        "[yellow]0[/] [<] 뒤로 가기",
        title="[bold white on blue] 설정 ",
        border_style="cyan"
    )
    console.print(panel)
    console.print()
    
    choice = Prompt.ask(
        "[>] [bold cyan]선택",
        choices=["0", "1", "2", "3"],
        default="0"
    )
    
    if choice == "1":
        clear_token()
        console.print("[green]Token을 재설정하려면 다시 분석을 실행하세요.")
        time.sleep(2)
    elif choice == "2":
        clear_token()
        time.sleep(2)
    elif choice == "3":
        global _github_token
        if _github_token:
            console.print(f"[green][+] Token 설정됨 (길이: {len(_github_token)} 문자)")
        else:
            console.print("[yellow][!] Token이 설정되지 않았습니다.")
        time.sleep(2)


def main():
    """메인 함수"""
    try:
        # 시작 시 보안 안내
        console.print("\n[bold cyan][!] 보안 알림:")
        console.print("[dim]이 프로그램은 GitHub Token을 메모리에만 저장하며,")
        console.print("파일로 저장하지 않습니다. 프로그램 종료 시 자동으로 제거됩니다.\n")
        time.sleep(1)
        
        while True:
            console.clear()
            show_banner()
            show_main_menu()
            console.print()
            
            choice = Prompt.ask(
                "[>] [bold cyan]선택",
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="1"
            )
            
            if choice == "0":
                # 종료 시 Token 제거
                clear_token()
                console.print("\n[bold green][!] 프로그램을 종료합니다. 감사합니다!\n")
                break
            elif choice == "1":
                basic_analysis()
            elif choice == "2":
                advanced_analysis()
            elif choice == "3":
                visualize_data()
            elif choice == "4":
                compare_profiles()
            elif choice == "5":
                export_report()
            elif choice == "6":
                show_settings()
    
    except KeyboardInterrupt:
        # Ctrl+C 시에도 Token 제거
        clear_token()
        console.print("\n\n[yellow][!] 사용자에 의해 중단되었습니다.\n")
    except Exception as e:
        clear_token()
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]')
        console.print(f"\n[red][X] 오류 발생: {error_msg}\n")
        return 1
    finally:
        # 최종 정리: Token 확실히 제거
        clear_token()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
