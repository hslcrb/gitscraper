#!/usr/bin/env python3
"""
GitHub Profile Analyzer - Simplified Unified Version
통합 분석 전용, 라이트 테마, Token 즉시 폐기
"""

import sys
import os
from pathlib import Path
from getpass import getpass
import json
import gc

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich import box
import time

from unified_analyzer import UnifiedGitHubAnalyzer
from file_utils import get_analysis_filename, get_visualization_filename
from html_visualizer import generate_html_visualization

# 라이트 테마 설정
custom_theme = Theme({
    "info": "blue",
    "warning": "yellow",
    "error": "red",
    "success": "green",
})

console = Console(theme=custom_theme)


def show_banner():
    """간단한 배너 표시 (도형문자 제거)"""
    console.print("\n[bold blue]GitHub Profile Analyzer[/bold blue]")
    console.print("[dim]Unified Analysis Tool[/dim]\n")


def show_main_menu():
    """메인 메뉴 표시"""
    menu = Panel(
        "[bold]1[/bold] Start Analysis\n"
        "[bold]0[/bold] Exit",
        title="Main Menu",
        border_style="blue",
        box=box.ROUNDED
    )
    console.print(menu)


def secure_token_input():
    """Token 입력 및 즉시 사용"""
    console.print("\n[yellow]GitHub Personal Access Token Required")
    console.print("[dim]Token will be used immediately and discarded[/dim]\n")
    
    token = getpass("Enter Token (hidden): ")
    
    if not token:
        console.print("[red]Token is required")
        return None
    
    console.print("[green]Token received\n")
    return token


def get_repo_type_choice():
    """리포지토리 타입 선택"""
    console.print("\n[bold]Repository Type Selection:[/bold]")
    console.print("1. Public only")
    console.print("2. Private only")
    console.print("3. Both (default)\n")
    
    choice = Prompt.ask(
        "Select type",
        choices=["1", "2", "3"],
        default="3"
    )
    
    type_map = {
        "1": "public",
        "2": "private",
        "3": "all"
    }
    
    return type_map[choice]


def display_results_table(stats: dict):
    """결과를 테이블로 표시"""
    table = Table(
        title="Analysis Results",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold blue"
    )
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    
    # 주요 통계
    table.add_row("Total Repositories", f"{stats.get('total_repositories', 0):,}")
    table.add_row("Public Repositories", f"{stats.get('public_repositories', 0):,}")
    table.add_row("Private Repositories", f"{stats.get('private_repositories', 0):,}")
    table.add_row("", "")  # 구분선
    table.add_row("Total Commits", f"{stats.get('total_commits', 0):,}")
    table.add_row("Total Stars", f"{stats.get('total_stars', 0):,}")
    table.add_row("Total Forks", f"{stats.get('total_forks', 0):,}")
    table.add_row("", "")
    table.add_row("Code Size (MB)", f"{stats.get('total_size_mb', 0):.2f}")
    table.add_row("Total Languages", f"{stats.get('total_languages', 0)}")
    table.add_row("Primary Language", stats.get('primary_language', 'N/A'))
    table.add_row("", "")
    table.add_row("Recently Active", f"{stats.get('recently_updated_count', 0)}")
    table.add_row("Inactive Repos", f"{stats.get('inactive_repos_count', 0)}")
    
    console.print("\n")
    console.print(table)
    console.print("\n")


def display_language_distribution(stats: dict):
    """언어 분포 표시"""
    lang_dist = stats.get('language_distribution', {})
    if not lang_dist:
        return
    
    console.print("[bold]Top 10 Languages:[/bold]\n")
    
    table = Table(box=box.SIMPLE)
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Language", style="yellow")
    table.add_column("Size (MB)", style="green", justify="right")
    table.add_column("Bar", style="blue")
    
    total_bytes = sum(lang_dist.values())
    sorted_langs = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (lang, bytes_count) in enumerate(sorted_langs, 1):
        mb_size = bytes_count / (1024 * 1024)
        percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
        
        # 간단한 바 (최대 20칸)
        bar_length = int(percentage / 100 * 20)
        bar = "=" * bar_length
        
        table.add_row(f"#{i}", lang, f"{mb_size:.2f}", bar)
    
    console.print(table)
    console.print("\n")


def run_unified_analysis():
    """통합 분석 실행"""
    console.clear()
    show_banner()
    
    console.print("[bold blue]Unified GitHub Profile Analysis[/bold blue]\n")
    
    # 1. 사용자명 입력
    username = Prompt.ask("[cyan]GitHub Username")
    
    # URL에서 사용자명 추출
    if 'github.com' in username:
        username = username.rstrip('/').split('/')[-1]
    
    if not username:
        console.print("[red]Username is required")
        time.sleep(2)
        return
    
    # 2. 리포지토리 타입 선택
    repo_type = get_repo_type_choice()
    
    # 3. Token 입력
    token = secure_token_input()
    if not token:
        return
    
    # 4. 분석 시작
    console.print(f"\n[blue]Starting analysis for: {username}")
    console.print(f"[dim]Type: {repo_type.upper()}[/dim]\n")
    
    try:
        # Analyzer 생성 (Token 즉시 사용)
        analyzer = UnifiedGitHubAnalyzer(token)
        
        # Token 즉시 제거 (메모리에서)
        del token
        gc.collect()
        console.print("[green]Token discarded from memory\n")
        
        # 진행률 표시와 함께 분석
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("[cyan]Analyzing repositories...", total=100)
            
            def progress_callback(current, total, repo_name):
                progress.update(task, completed=(current / total * 100))
            
            result = analyzer.analyze_profile(username, repo_type, progress_callback)
        
        # Analyzer 정리
        analyzer.cleanup()
        del analyzer
        gc.collect()
        
        # 5. 결과 확인
        if 'error' in result:
            console.print(f"[red]Error: {result['error']}")
            return
        
        stats = result.get('statistics', {})
        
        # 6. 결과 표시
        console.clear()
        show_banner()
        
        console.print(f"[bold green]Analysis Complete: {username}[/bold green]\n")
        
        display_results_table(stats)
        display_language_distribution(stats)
        
        # 7. 저장 옵션
        console.print("[bold]Save Options:[/bold]\n")
        
        # JSON 저장
        if Confirm.ask("Save as JSON?", default=True):
            json_file = get_analysis_filename(username, "json", ".")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            console.print(f"[green]Saved: {json_file}")
        
        # HTML 시각화 생성
        if Confirm.ask("Generate HTML Visualization?", default=True):
            html_file = get_visualization_filename(username, ".")
            generate_html_visualization(result, html_file)
            console.print(f"[green]Generated: {html_file}")
            console.print("[dim]Open in browser to view charts and export options[/dim]")
        
        console.print("\n[green]All data saved successfully!")
        console.print("\n")
        Prompt.ask("Press Enter to continue")
        
    except Exception as e:
        # 오류 시에도 Token 제거
        if 'token' in locals():
            del token
        if 'analyzer' in locals():
            analyzer.cleanup()
            del analyzer
        gc.collect()
        
        error_msg = str(e).replace('[', '(').replace(']', ')')
        console.print(f"\n[red]Error: {error_msg}")
        console.print("\n")
        Prompt.ask("Press Enter to continue")


def main():
    """메인 함수"""
    try:
        console.print("\n[blue]Security Notice:")
        console.print("[dim]Tokens are used immediately and never stored on disk")
        console.print("All tokens are removed from memory after use[/dim]\n")
        time.sleep(1)
        
        while True:
            console.clear()
            show_banner()
            show_main_menu()
            console.print()
            
            choice = Prompt.ask(
                "Select option",
                choices=["0", "1"],
                default="1"
            )
            
            if choice == "0":
                console.print("\n[green]Thank you for using GitHub Profile Analyzer!")
                console.print("[dim]All tokens have been removed from memory[/dim]\n")
                break
            elif choice == "1":
                run_unified_analysis()
        
        return 0
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user")
        console.print("[dim]All tokens removed from memory[/dim]\n")
        return 0
    except Exception as e:
        error_msg = str(e).replace('[', '(').replace(']', ')')
        console.print(f"\n[red]Fatal error: {error_msg}\n")
        return 1
    finally:
        # 최종 정리
        gc.collect()


if __name__ == "__main__":
    sys.exit(main())
