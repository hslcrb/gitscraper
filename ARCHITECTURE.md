# GitHub Profile Analyzer - 아키텍처 문서

## 시스템 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Profile Analyzer                      │
│                   통합 분석 시스템 v2.0                          │
└─────────────────────────────────────────────────────────────────┘
```

## 실행 흐름

```
./run.sh
   │
   ├─→ 가상환경 확인/생성
   │   └─→ venv/ 디렉토리
   │
   ├─→ 의존성 설치 (첫 실행시)
   │   └─→ requirements.txt
   │
   └─→ python main.py
       │
       └─→ Main Menu
           ├─→ [1] Start Analysis
           │   │
           │   ├─→ 사용자명 입력
           │   ├─→ 리포 타입 선택 (Public/Private/Both)
           │   ├─→ Token 입력 (getpass)
           │   │
           │   └─→ UnifiedGitHubAnalyzer
           │       │
           │       ├─→ GitHub API 호출
           │       ├─→ 리포지토리 수집
           │       ├─→ 메타데이터 수집
           │       ├─→ 통계 생성
           │       │
           │       └─→ 결과 반환
           │           │
           │           ├─→ JSON 저장 (file_utils)
           │           │   └─→ {username}_analysis.json
           │           │
           │           └─→ HTML 생성 (html_visualizer)
           │               └─→ {username}_visualization.html
           │
           └─→ [0] Exit
```

## 모듈 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                           main.py                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ - 심플한 RICH TUI                                        │   │
│  │ - 2가지 메뉴 (Start/Exit)                                │   │
│  │ - Token 보안 처리                                        │   │
│  │ - 진행률 표시                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  src/unified_analyzer.py                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ UnifiedGitHubAnalyzer                                    │   │
│  │ ├─ __init__(token)          # Token 즉시 사용           │   │
│  │ ├─ get_user_repos()         # 리포 목록 가져오기        │   │
│  │ ├─ analyze_repository()     # 리포 상세 분석            │   │
│  │ ├─ generate_statistics()    # 통계 생성                 │   │
│  │ ├─ analyze_profile()        # 전체 분석 실행            │   │
│  │ └─ cleanup()                # 리소스 정리               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   src/file_utils.py      │  │  src/html_visualizer.py  │
│  ┌───────────────────┐   │  │  ┌───────────────────┐   │
│  │ File Management   │   │  │  │ HTML Generation   │   │
│  ├───────────────────┤   │  │  ├───────────────────┤   │
│  │ - Unique filename │   │  │  │ - Chart.js charts │   │
│  │ - _1, _2 suffixes │   │  │  │ - Export to image │   │
│  │ - Directory mgmt  │   │  │  │ - Print/PDF       │   │
│  └───────────────────┘   │  │  │ - Light theme     │   │
└──────────────────────────┘  │  └───────────────────┘   │
                              └──────────────────────────┘
```

## 데이터 흐름

```
GitHub API
    │
    │ (PyGithub)
    ▼
UnifiedGitHubAnalyzer
    │
    ├─→ Repository Data
    │   ├─ Basic info (name, url, description)
    │   ├─ Statistics (commits, stars, forks)
    │   ├─ Timestamps (created, updated, pushed)
    │   ├─ Languages (bytes per language)
    │   ├─ Contributors count
    │   ├─ Branches count
    │   ├─ Tags count
    │   └─ License info
    │
    └─→ Comprehensive Statistics
        ├─ Total counts
        ├─ Language distribution
        ├─ Time analysis
        ├─ Activity status
        └─ Averages
            │
            ├─→ JSON File (file_utils)
            │   └─ {username}_analysis.json
            │
            └─→ HTML Report (html_visualizer)
                └─ {username}_visualization.html
                    ├─ 5 Chart.js charts
                    ├─ Statistics cards
                    ├─ Repository table
                    └─ Export buttons
```

## 보안 계층

```
┌─────────────────────────────────────────────────────────────────┐
│                        Security Layer                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Token Input (getpass)                                          │
│       │                                                         │
│       ├─→ 화면에 표시 안 됨                                     │
│       └─→ 메모리에만 저장                                       │
│           │                                                     │
│           ▼                                                     │
│  UnifiedGitHubAnalyzer(token)                                   │
│       │                                                         │
│       ├─→ Github 객체 생성                                      │
│       └─→ del token (즉시 삭제)                                 │
│           │                                                     │
│           ▼                                                     │
│  gc.collect()                                                   │
│       └─→ 강제 가비지 컬렉션                                    │
│           │                                                     │
│           ▼                                                     │
│  분석 실행                                                      │
│       │                                                         │
│       ▼                                                         │
│  analyzer.cleanup()                                             │
│       ├─→ del self.github                                       │
│       └─→ gc.collect()                                          │
│           │                                                     │
│           ▼                                                     │
│  Token 완전 제거 확인 ✓                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 파일 시스템 구조

```
gitscraper/
│
├── main.py                     # 메인 프로그램
├── run.sh                      # 실행 스크립트
├── requirements.txt            # 의존성
├── .gitignore                  # Git 제외 파일
│
├── src/                        # 소스 코드
│   ├── __init__.py
│   ├── unified_analyzer.py     # [핵심] 통합 분석기
│   ├── file_utils.py           # [핵심] 파일 유틸리티
│   ├── html_visualizer.py      # [핵심] HTML 시각화
│   │
│   └── (레거시 모듈들)
│       ├── github_scraper.py
│       ├── advanced_analyzer.py
│       ├── visualizer.py
│       └── ...
│
├── docs/                       # 문서
│   ├── README.md               # 프로젝트 소개
│   ├── 사용법.md               # 한국어 가이드
│   ├── COMPLETED_REDESIGN.md   # 재설계 문서
│   ├── COMPLETION_SUMMARY.md   # 완료 요약
│   └── ARCHITECTURE.md         # 이 파일
│
└── output/                     # 생성 파일 (gitignore)
    ├── {username}_analysis.json
    └── {username}_visualization.html
```

## 의존성 그래프

```
main.py
  ├─→ rich                      (TUI)
  ├─→ getpass                   (Token 입력)
  └─→ src/
      ├─→ unified_analyzer
      │   ├─→ github (PyGithub)
      │   ├─→ datetime
      │   └─→ gc
      │
      ├─→ file_utils
      │   ├─→ os
      │   └─→ pathlib
      │
      └─→ html_visualizer
          ├─→ json
          └─→ datetime
```

## API 호출 흐름

```
User Input
    │
    ├─ Username: "octocat"
    ├─ Type: "all"
    └─ Token: "ghp_xxxxx"
        │
        ▼
GitHub API (PyGithub)
    │
    ├─→ get_user("octocat")
    │   └─→ User 객체
    │
    ├─→ user.get_repos()
    │   └─→ Repository 리스트
    │
    └─→ For each repository:
        │
        ├─→ repo.get_commits()      # 커밋 수
        ├─→ repo.get_contributors() # 기여자
        ├─→ repo.get_branches()     # 브랜치
        ├─→ repo.get_tags()         # 태그
        ├─→ repo.get_languages()    # 언어 분포
        │
        └─→ Repository 상세 정보
            │
            ├─ name, url, description
            ├─ stars, forks, watchers
            ├─ created_at, updated_at, pushed_at
            ├─ language, languages{}
            ├─ contributors_count
            ├─ branches_count
            ├─ tags_count
            └─ license
```

## HTML 시각화 구조

```
{username}_visualization.html
│
├── <head>
│   ├─ Chart.js 4.4.0 CDN
│   ├─ html2canvas 1.4.1 CDN
│   └─ CSS (Light Theme)
│
└── <body>
    ├── Header
    │   ├─ Title
    │   └─ Analysis Info
    │
    ├── Statistics Cards (6개)
    │   ├─ Total Repositories
    │   ├─ Total Commits
    │   ├─ Total Stars
    │   ├─ Total Forks
    │   ├─ Code Size
    │   └─ Languages Used
    │
    ├── Export Buttons
    │   ├─ Export as Image
    │   ├─ Export Table as Image
    │   └─ Print/PDF
    │
    ├── Charts (5개)
    │   ├─ Language Distribution (Pie)
    │   ├─ Repository Activity (Bar)
    │   ├─ Repository Popularity (Bar)
    │   ├─ Repo Type Distribution (Doughnut)
    │   └─ Activity Status (Bar)
    │
    ├── Repository Table
    │   └─ Top 30 repositories
    │
    └── Footer
        └─ Generated timestamp
```

## 상태 관리

```
Program State
│
├─ NOT_STARTED
│   └─ 프로그램 시작
│       │
│       ▼
├─ MENU_DISPLAY
│   └─ 메뉴 표시
│       │
│       ├─[1]─→ INPUT_USERNAME
│       │       │
│       │       ▼
│       │   INPUT_REPO_TYPE
│       │       │
│       │       ▼
│       │   INPUT_TOKEN
│       │       │
│       │       ▼
│       │   ANALYZING
│       │       ├─→ Token 즉시 폐기 ✓
│       │       ├─→ API 호출
│       │       ├─→ 데이터 수집
│       │       └─→ 통계 생성
│       │           │
│       │           ▼
│       │       DISPLAY_RESULTS
│       │           │
│       │           ▼
│       │       SAVE_FILES
│       │           ├─→ JSON
│       │           └─→ HTML
│       │               │
│       │               ▼
│       │           COMPLETED
│       │               └─→ MENU_DISPLAY
│       │
│       └─[0]─→ EXIT
│
└─ EXIT
    └─ 프로그램 종료
```

## 에러 처리

```
Try-Catch Hierarchy
│
├─ main()
│   ├─→ KeyboardInterrupt
│   │   └─ 사용자 중단 처리
│   │
│   └─→ Exception
│       └─ 치명적 오류 처리
│
├─ run_unified_analysis()
│   └─→ Exception
│       ├─ Token 정리
│       ├─ Analyzer 정리
│       └─ 에러 메시지 표시
│
└─ UnifiedGitHubAnalyzer
    ├─ get_user_repos()
    │   └─→ Exception (사용자 없음)
    │
    └─ analyze_repository()
        └─→ Exception (리포 접근 실패)
```

## 성능 고려사항

### API Rate Limit
```
Without Token: 60 requests/hour
With Token:    5,000 requests/hour

권장: Personal Access Token 사용
```

### 메모리 사용
```
Token:      즉시 폐기
Analyzer:   분석 후 정리
Data:       JSON 저장 후 해제
```

### 파일 I/O
```
Read:   최소화 (설정 파일만)
Write:  필요시에만 (JSON, HTML)
```

## 확장성

### 새 분석 기능 추가
```python
# src/unified_analyzer.py

def analyze_repository_detailed(self, repo):
    # 기존 분석 코드
    ...
    
    # 새 기능 추가
    repo_info['new_feature'] = self.get_new_feature(repo)
    
    return repo_info
```

### 새 시각화 추가
```javascript
// src/html_visualizer.py

// HTML 템플릿에 새 차트 추가
<canvas id="newChart"></canvas>

// JavaScript에 차트 생성 코드 추가
new Chart(ctx, {
    type: 'line',
    data: {...},
    options: {...}
});
```

### 새 Export 형식
```python
# src/export_utils.py (새 파일)

def export_to_pdf(data, filename):
    # PDF export 구현
    pass

def export_to_csv(data, filename):
    # CSV export 구현
    pass
```

## 테스트 전략

### Unit Tests
```python
# tests/test_file_utils.py
def test_get_unique_filename():
    assert get_unique_filename('test', '.txt') == './test.txt'
    
# tests/test_unified_analyzer.py
def test_token_cleanup():
    # Token이 제대로 제거되는지 확인
    pass
```

### Integration Tests
```python
# tests/test_integration.py
def test_full_analysis_flow():
    # 전체 분석 흐름 테스트
    pass
```

### Security Tests
```python
# tests/test_security.py
def test_token_not_in_memory():
    # Token이 메모리에 남지 않는지 확인
    pass
```

## 배포 체크리스트

- [x] 코드 구현
- [x] 테스트 통과
- [x] 문서 작성
- [x] Git 커밋
- [x] Git 푸시
- [ ] 릴리스 노트
- [ ] 버전 태그

## 버전 히스토리

```
v2.0 - 2024 (현재)
  - 통합 분석 시스템
  - Token 즉시 폐기
  - HTML 시각화
  - 라이트 테마

v1.0 - 이전
  - 기본 분석 기능
  - 다중 메뉴 시스템
  - matplotlib 시각화
```

---

**작성일**: 2024  
**버전**: 2.0  
**상태**: 완료  
