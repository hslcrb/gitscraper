#!/usr/bin/env python3
"""
File Utilities
파일 이름 중복 방지 및 관리
"""

import os
from pathlib import Path


def get_unique_filename(base_name: str, extension: str = "", directory: str = ".") -> str:
    """
    중복되지 않는 파일명 생성 (접미사 _1, _2, ... 추가)
    
    Args:
        base_name: 기본 파일명 (확장자 제외)
        extension: 파일 확장자 (.json, .html 등)
        directory: 저장 디렉토리
        
    Returns:
        중복되지 않는 전체 파일 경로
    """
    # 확장자 정리
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    # 기본 파일명
    filename = f"{base_name}{extension}"
    filepath = os.path.join(directory, filename)
    
    # 중복 확인 및 번호 추가
    if not os.path.exists(filepath):
        return filepath
    
    counter = 1
    while True:
        filename = f"{base_name}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return filepath
        
        counter += 1
        
        # 무한 루프 방지 (1000개 이상은 비정상)
        if counter > 1000:
            raise RuntimeError(f"파일 생성 실패: {base_name} (너무 많은 중복)")


def ensure_directory(directory: str) -> str:
    """
    디렉토리가 없으면 생성
    
    Args:
        directory: 디렉토리 경로
        
    Returns:
        디렉토리 경로
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory


def get_analysis_filename(username: str, file_type: str = "json", directory: str = ".") -> str:
    """
    분석 결과 파일명 생성
    
    Args:
        username: GitHub 사용자명
        file_type: 파일 타입 (json, html)
        directory: 저장 디렉토리
        
    Returns:
        파일 경로
    """
    base_name = f"{username}_analysis"
    extension = f".{file_type}"
    
    return get_unique_filename(base_name, extension, directory)


def get_visualization_filename(username: str, directory: str = ".") -> str:
    """
    시각화 HTML 파일명 생성
    
    Args:
        username: GitHub 사용자명
        directory: 저장 디렉토리
        
    Returns:
        파일 경로
    """
    base_name = f"{username}_visualization"
    extension = ".html"
    
    return get_unique_filename(base_name, extension, directory)
