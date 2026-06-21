# GitHub Profile Analyzer

GitHub 프로필의 오픈소스 리포지토리를 분석하여 커밋 수, 코드량, 언어 분포 등의 통계를 제공하는 Python 도구

## 기능

### 기본 분석
- 📊 GitHub 프로필의 모든 공개 리포지토리 분석
- 📈 총 커밋 수, 스타 수, 포크 수 집계
- 💻 언어별 코드 분포 분석
- 📦 리포지토리별 상세 정보 제공
- 📋 종합 통계 리포트 생성

### 고급 분석
- 📝 코드 추가/삭제량 상세 분석
- ⏰ 시간대별/요일별 커밋 패턴 분석
- 🎯 리포지토리별 기여도 및 역할 분석
- 📊 활동 통계 및 트렌드

### 시각화
- 📊 언어별 코드 분포 파이 차트
- 📈 리포지토리별 커밋 수 바 차트
- 🎯 스타/포크 인기도 산점도

## 설치

1. 저장소 클론
```bash
git clone <repository-url>
cd gitscraper
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. GitHub Token 설정
- GitHub에서 Personal Access Token 발급 (Settings > Developer settings > Personal access tokens)
- `.env` 파일 생성:
```bash
cp .env.example .env
```
- `.env` 파일에 토큰 입력:
```
GITHUB_TOKEN=your_github_token_here
```

## 사용법

### 1. 기본 분석 (빠른 실행)
```bash
python github_scraper.py
```

대화형으로 사용자명을 입력받아 기본 분석을 수행합니다.

### 2. CLI 인터페이스 (고급 옵션)
```bash
# 기본 사용
python github_scraper_cli.py torvalds

# JSON 파일로 저장
python github_scraper_cli.py torvalds -o result.json

# JSON만 출력 (리포트 없음)
python github_scraper_cli.py torvalds --json-only -o result.json

# 콘솔 출력 없이 파일만 저장
python github_scraper_cli.py torvalds -o result.json --no-output
```

### 3. 고급 분석 (코드 변경량, 활동 패턴)
```bash
# 고급 분석 실행
python advanced_analyzer.py torvalds

# JSON으로 저장
python advanced_analyzer.py torvalds -o advanced_result.json
```

### 4. 시각화 생성
```bash
# 분석 결과 JSON에서 차트 생성
python visualizer.py result.json

# 출력 파일명 접두어 지정
python visualizer.py result.json -p charts
```

### 5. 완전 분석 (모든 기능 한번에)
```bash
# 기본 + 고급 + 시각화 모두 실행
python run_analysis.py torvalds

# 결과를 특정 폴더에 저장
python run_analysis.py torvalds -o results
```

## 출력 정보

### 기본 통계
- 총 리포지토리 수
- 총 커밋 수
- 총 스타 수
- 총 포크 수
- 총 코드량 (MB/KB)
- 리포지토리당 평균 커밋/스타

### 언어별 분포
- 상위 10개 언어
- 각 언어별 사용 비율 및 코드량

### 리포지토리 상세
- 리포지토리명, URL
- 설명
- 커밋/스타/포크 수
- 생성일 및 업데이트일
- 주요 사용 언어

### 고급 분석 (advanced_analyzer)
- 총 코드 추가/삭제량
- 순 변경량
- 시간대별 커밋 분포
- 요일별 커밋 분포
- 리포지토리별 기여 역할 (owner, main_contributor, contributor 등)
- 활동 기간 및 평균 커밋 빈도

### 시각화 파일
- `{username}_language_distribution.png`: 언어 분포 파이 차트
- `{username}_repo_commits.png`: 리포지토리별 커밋 수
- `{username}_repo_popularity.png`: 스타/포크 인기도

### 6. 프로필 비교
```bash
# 여러 사용자 비교
python compare_profiles.py user1.json user2.json user3.json

# CSV로 저장
python compare_profiles.py user1.json user2.json --csv comparison.csv
```

### 7. 리포트 내보내기
```bash
# Markdown 리포트 생성
python export_report.py result.json --markdown report.md

# HTML 리포트 생성
python export_report.py result.json --html report.html

# CSV 리포트 생성
python export_report.py result.json --csv repos.csv

# 모든 형식으로 내보내기
python export_report.py result.json --all output
```

## 프로젝트 구조

```
gitscraper/
├── github_scraper.py          # 기본 분석기
├── github_scraper_cli.py      # CLI 인터페이스
├── advanced_analyzer.py       # 고급 분석 (코드 변경량, 패턴)
├── visualizer.py              # 시각화 생성
├── run_analysis.py            # 통합 실행 스크립트
├── compare_profiles.py        # 프로필 비교 도구
├── export_report.py           # 리포트 내보내기
├── test_basic.py              # 기본 테스트
├── example_batch.sh           # 배치 분석 예제
├── requirements.txt           # 의존성
├── setup.py                   # 설치 스크립트
├── .env.example              # 환경 변수 예제
├── .gitignore                # Git 무시 파일
├── LICENSE                   # 라이선스
├── README.md                 # 문서
├── USAGE.md                  # 사용 가이드
└── CONTRIBUTING.md           # 기여 가이드
```

## 요구사항

- Python 3.7+
- GitHub Personal Access Token
- 패키지: PyGithub, python-dotenv, matplotlib

## 예제

### 예제 1: 빠른 분석
```bash
python github_scraper.py
# 입력: torvalds
```

### 예제 2: JSON 저장 후 시각화
```bash
python github_scraper_cli.py torvalds -o torvalds.json
python visualizer.py torvalds.json
```

### 예제 3: 전체 분석
```bash
python run_analysis.py torvalds -o analysis_results
```

## 문제 해결

### Rate Limit 초과
GitHub API는 시간당 요청 제한이 있습니다. Personal Access Token을 사용하면 제한이 완화됩니다.

### 한글 폰트 깨짐 (Linux)
```bash
sudo apt-get install fonts-nanum
```

### matplotlib 설치 오류
```bash
pip install matplotlib --upgrade
```

## 라이선스

MIT License

## 기여

이슈와 PR을 환영합니다!