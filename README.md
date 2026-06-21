# GitHub Profile Analyzer

**RICH TUI 기반** GitHub 프로필 통합 분석 도구

간단한 터미널 UI로 GitHub 프로필의 커밋 수, 코드량, 언어 분포 등의 종합 통계를 제공합니다.

## ✨ 주요 특징

### 🎯 **통합 분석**
- Public/Private/All 리포지토리 선택 가능 (기본값: All)
- GitHub 프로필의 모든 정보를 한 번에 분석
- 총 커밋 수, 스타 수, 포크 수 집계
- 💻 언어별 코드 분포 분석
- 📦 리포지토리별 상세 정보 제공
- 📋 종합 통계 리포트 생성

### 🕒 **시간 정보 수집**
- 생성일, 업데이트일, 푸시일
- 리포지토리 나이 계산
- 마지막 업데이트 경과 시간
- 활동성 분석 (최근 30일/90일)

### 📈 **HTML 시각화**
- Chart.js 기반 인터랙티브 차트
- 언어별 코드 분포 파이 차트
- 리포지토리별 커밋 수 바 차트
- 스타/포크 인기도 차트
- Public vs Private 도넛 차트
- 활동성 상태 차트
- 이미지로 Export 가능
- Print/PDF 저장 지원

### 🎨 **심플한 라이트 테마**
- 깔끔한 라이트 테마 UI
- 실시간 프로그레스 바
- 컬러풀한 통계 테이블
- 간단한 2가지 메뉴 (분석 시작 / 종료)

## 🚀 빠른 시작

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/hslcrb/gitscraper.git
cd gitscraper
```

2. **가상환경 생성 및 활성화** (리눅스 필수)
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **GitHub Token 준비**
- GitHub에서 Personal Access Token 발급
- Settings → Developer settings → Personal access tokens → Generate new token
- 필요한 권한: `repo`, `user`
- **⚠️ 중요**: Token은 파일로 저장하지 마세요! 프로그램 실행 시 직접 입력합니다.

### 실행

#### 방법 1: 원클릭 실행 (권장) 🚀

```bash
./run.sh
```

이 스크립트는 자동으로:
- ✅ 가상환경 생성 (없는 경우)
- ✅ 의존성 설치 (처음 한 번만)
- ✅ 프로그램 실행
- ✅ 종료 후 정리

#### 방법 2: 수동 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 프로그램 실행
python main.py

# 종료 후 비활성화
deactivate
```

**실행 시:**
- 프로그램이 시작되면 GitHub Token을 입력하라는 메시지가 표시됩니다
- Token은 화면에 표시되지 않으며, 메모리에만 저장됩니다

### 가상환경 종료

```bash
deactivate
```

## 🔒 보안 특징

### Token 보안
- ✅ **파일 저장 없음**: Token을 .env나 다른 파일에 저장하지 않습니다
- ✅ **즉시 폐기**: Token은 받은 즉시 사용되고 메모리에서 제거됩니다
- ✅ **메모리 정리**: 사용 후 강제 가비지 컬렉션으로 완전히 제거됩니다
- ✅ **화면 숨김**: Token 입력 시 화면에 표시되지 않습니다 (getpass 사용)
- ✅ **추적 불가**: 컴퓨터에 Token 흔적이 남지 않습니다
- ✅ **작업 후 유출 방지**: 분석 완료 후에도 Token이 메모리에 남지 않습니다

### 파일 안전성
- ✅ **덮어쓰기 방지**: 같은 이름 파일 생성 시 자동으로 _1, _2 접미사 추가
- ✅ **Git 추적 제외**: 생성된 모든 분석 파일은 자동으로 gitignore에 포함

## 🎮 사용법

### 간단한 통합 분석

```bash
./run.sh
```

**메뉴 옵션:**
- `1` 📊 통합 분석 시작 (Start Analysis)
- `0` 🚪 종료 (Exit)

**분석 프로세스:**
1. GitHub 사용자명 입력
2. 리포지토리 타입 선택:
   - Public only (공개 리포지토리만)
   - Private only (비공개 리포지토리만)
   - Both (둘 다 - 기본값)
3. GitHub Token 입력 (화면에 표시되지 않음)
4. 자동 분석 및 통계 생성
5. JSON 파일 저장 옵션
6. HTML 시각화 생성 옵션

### 생성되는 파일

- `{username}_analysis.json` - 전체 분석 데이터
- `{username}_visualization.html` - 인터랙티브 HTML 리포트
  - Chart.js 기반 차트
  - 이미지로 Export 가능
  - Print/PDF 저장 가능

같은 사용자명으로 다시 분석하면 `{username}_analysis_1.json`, `{username}_analysis_2.json` 형태로 자동 저장됩니다.

## 📊 출력 정보

### 기본 통계
- 총 리포지토리 수 (Public/Private 분류)
- 총 커밋 수
- 총 스타 수
- 총 포크 수
- 총 이슈 수
- 총 코드량 (KB/MB/GB)
- 리포지토리당 평균 커밋/스타/포크

### 언어별 분포
- 모든 언어 사용 현황
- 각 언어별 사용 바이트 수 및 코드량
- 주요 언어 (Primary Language)
- 언어별 리포지토리 개수

### 시간 정보
- 가장 오래된 리포지토리 날짜
- 가장 최신 리포지토리 날짜
- 계정 활동 기간
- 각 리포지토리별 생성일/업데이트일/푸시일
- 리포지토리 나이 (일 단위)
- 마지막 업데이트 경과 시간

### 활동성 분석
- 최근 30일 내 업데이트된 리포지토리 수
- 90일 내 활동 중인 리포지토리 수
- 비활성 리포지토리 수

### 리포지토리 상세
- 리포지토리명, URL
- Public/Private 상태
- 설명 (Description)
- 커밋/스타/포크 수
- 기여자 수 (Contributors)
- 브랜치 수 (Branches)
- 태그/릴리스 수 (Tags)
- 라이선스 정보
- 생성일, 업데이트일, 푸시일
- 주요 사용 언어
- 모든 언어 및 바이트 수

## 📁 프로젝트 구조

```
gitscraper/
├── main.py                    # RICH TUI 메인 프로그램 (통합 분석)
├── run.sh                     # 원클릭 실행 스크립트
├── src/
│   ├── __init__.py
│   ├── unified_analyzer.py    # 통합 분석기 (Private/Public 선택)
│   ├── file_utils.py          # 파일 이름 중복 방지 유틸리티
│   ├── html_visualizer.py     # HTML 시각화 생성 (Chart.js)
│   ├── github_scraper.py      # 기본 분석기 (레거시)
│   ├── github_scraper_cli.py  # CLI 인터페이스 (레거시)
│   ├── advanced_analyzer.py   # 고급 분석 (레거시)
│   ├── visualizer.py          # 시각화 생성 (레거시)
│   ├── run_analysis.py        # 통합 실행 (레거시)
│   ├── compare_profiles.py    # 프로필 비교 (레거시)
│   └── export_report.py       # 리포트 내보내기 (레거시)
├── test_basic.py              # 기본 테스트
├── example_batch.sh           # 배치 분석
├── requirements.txt           # 의존성
├── setup.py                   # 설치 스크립트
├── .gitignore                 # Git 추적 제외 (분석 파일 포함)
├── LICENSE                    # MIT 라이선스
├── README.md                  # 문서 (이 파일)
├── USAGE.md                   # 상세 사용 가이드
└── CONTRIBUTING.md            # 기여 가이드
```

## 🛠️ 요구사항

- Python 3.7+
- GitHub Personal Access Token
- 패키지: 
  - PyGithub
  - matplotlib
  - rich
  - requests
  - numpy

## 📸 스크린샷

### 심플 라이트 테마 메인 화면
```
GitHub Profile Analyzer
Unified Analysis Tool

┌─────────── Main Menu ───────────┐
│ 1 Start Analysis                │
│ 0 Exit                           │
└──────────────────────────────────┘
```

### 분석 프로세스
```
GitHub Username: [입력]

Repository Type Selection:
1. Public only
2. Private only
3. Both (default)

Select type: [선택]

GitHub Personal Access Token Required
Token will be used immediately and discarded

Enter Token (hidden): [입력 - 화면에 표시되지 않음]

Token received
Token discarded from memory

Analyzing repositories... ████████████ 100%
```

### HTML 시각화 리포트
- 인터랙티브 Chart.js 차트
- 언어 분포 파이 차트
- 커밋 활동 바 차트
- 인기도 분석
- Export 버튼으로 이미지 저장 가능
- Print/PDF 저장 지원

## 💡 예제

### 예제 1: 빠른 분석
```bash
./run.sh
# 메뉴에서 1 선택
# 사용자명 입력: octocat
# 타입 선택: 3 (Both)
# Token 입력
# 결과: octocat_analysis.json, octocat_visualization.html
```

### 예제 2: Private 리포지토리만 분석
```bash
./run.sh
# 메뉴에서 1 선택
# 사용자명 입력: yourname
# 타입 선택: 2 (Private only)
# Token 입력 (Private 권한 필요)
```

### 예제 3: Public 리포지토리만 분석
```bash
./run.sh
# 메뉴에서 1 선택
# 사용자명 입력: torvalds
# 타입 선택: 1 (Public only)
# Token 입력
```

## 🐛 문제 해결

### Rate Limit 초과
GitHub API는 시간당 요청 제한이 있습니다. Personal Access Token을 사용하면 제한이 완화됩니다 (시간당 5,000건).

### Token 권한 부족
Private 리포지토리 분석을 위해서는 `repo` 권한이 필요합니다. Token 생성 시 다음 권한을 부여하세요:
- `repo` (전체 권한)
- `user` (읽기 권한)

### 생성된 파일 확인
분석 결과 파일은 프로그램 실행 디렉토리에 생성됩니다:
```bash
ls -la *_analysis*.json *_visualization*.html
```

### HTML 시각화가 열리지 않음
브라우저에서 직접 HTML 파일을 열어보세요:
```bash
# Linux
xdg-open {username}_visualization.html

# macOS
open {username}_visualization.html
```

### RICH 설치 오류
```bash
pip install rich --upgrade
```

## 📄 라이선스

MIT License

## 🤝 기여

이슈와 PR을 환영합니다! 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 🔗 링크

- GitHub: https://github.com/hslcrb/gitscraper
- 이슈 트래커: https://github.com/hslcrb/gitscraper/issues

---

⭐ 프로젝트가 마음에 드셨다면 Star를 눌러주세요!
