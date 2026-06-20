# GitHub Profile Analyzer

GitHub 프로필의 오픈소스 리포지토리를 분석하여 커밋 수, 코드량, 언어 분포 등의 통계를 제공하는 Python 도구

## 기능

- 📊 GitHub 프로필의 모든 공개 리포지토리 분석
- 📈 총 커밋 수, 스타 수, 포크 수 집계
- 💻 언어별 코드 분포 분석
- 📦 리포지토리별 상세 정보 제공
- 📋 종합 통계 리포트 생성

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

```bash
python github_scraper.py
```

프로그램 실행 후 GitHub 사용자명 또는 프로필 URL을 입력하세요.

### 예시

```
GitHub 사용자명 또는 프로필 URL을 입력하세요: torvalds
```

또는

```
GitHub 사용자명 또는 프로필 URL을 입력하세요: https://github.com/torvalds
```

## 출력 정보

### 종합 통계
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

## 요구사항

- Python 3.7+
- GitHub Personal Access Token

## 라이선스

MIT License