# GitHub Profile Analyzer - 사용 가이드

## 빠른 시작

### 1단계: 설치
```bash
pip install -r requirements.txt
```

### 2단계: GitHub Token 설정
1. GitHub 웹사이트 로그인
2. Settings → Developer settings → Personal access tokens → Generate new token
3. 필요한 권한: `repo`, `user`
4. `.env` 파일 생성:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

### 3단계: 실행
```bash
python run_analysis.py YOUR_GITHUB_USERNAME
```

## 상세 사용법

### 모듈별 사용

#### 1. github_scraper.py - 기본 분석기
**용도**: 빠른 기본 통계 확인

```bash
# 대화형 모드
python github_scraper.py

# 입력 예시
GitHub 사용자명 또는 프로필 URL을 입력하세요: torvalds
```

**출력 내용**:
- 리포지토리 수
- 총 커밋, 스타, 포크 수
- 언어별 코드 분포
- 리포지토리 상세 정보

---

#### 2. github_scraper_cli.py - CLI 인터페이스
**용도**: 스크립트 자동화, JSON 출력

```bash
# 기본 사용
python github_scraper_cli.py torvalds

# JSON 파일로 저장
python github_scraper_cli.py torvalds -o torvalds_analysis.json

# 토큰 직접 지정
python github_scraper_cli.py torvalds -t ghp_YOUR_TOKEN

# 콘솔 출력 없이 JSON만 저장
python github_scraper_cli.py torvalds -o result.json --no-output

# JSON 형식으로 stdout 출력 (파이프 가능)
python github_scraper_cli.py torvalds --json-only | jq .
```

**옵션**:
- `-o FILE`: JSON 파일로 저장
- `-t TOKEN`: GitHub token 직접 지정
- `--no-output`: 콘솔 출력 억제
- `--json-only`: JSON만 출력

---

#### 3. advanced_analyzer.py - 고급 분석
**용도**: 코드 변경량, 활동 패턴 분석

```bash
# 기본 고급 분석
python advanced_analyzer.py torvalds

# JSON으로 저장
python advanced_analyzer.py torvalds -o advanced_result.json
```

**출력 내용**:
- 코드 추가/삭제량 (줄 단위)
- 순 변경량
- 시간대별 커밋 분포 (몇 시에 가장 활동적인지)
- 요일별 커밋 분포
- 리포지토리별 기여 역할
  - `owner`: 소유자
  - `main_contributor`: 주요 기여자 (50% 이상)
  - `major_contributor`: 주요 기여자 (20-50%)
  - `contributor`: 기여자 (5-20%)
  - `minor_contributor`: 소규모 기여자 (5% 미만)

---

#### 4. visualizer.py - 시각화
**용도**: 분석 결과를 차트로 생성

```bash
# 기본 시각화
python visualizer.py result.json

# 출력 파일명 접두어 지정
python visualizer.py result.json -p charts
```

**생성되는 차트**:
1. `{username}_language_distribution.png`: 언어 분포 파이 차트
2. `{username}_repo_commits.png`: 리포지토리별 커밋 수 바 차트
3. `{username}_repo_popularity.png`: 스타/포크 산점도

**요구사항**: matplotlib, numpy

---

#### 5. run_analysis.py - 통합 실행
**용도**: 모든 분석을 한 번에 실행

```bash
# 현재 디렉토리에 결과 저장
python run_analysis.py torvalds

# 특정 폴더에 결과 저장
python run_analysis.py torvalds -o analysis_results

# 토큰 지정
python run_analysis.py torvalds -t ghp_YOUR_TOKEN -o results
```

**실행 순서**:
1. 기본 분석 → JSON 저장
2. 고급 분석 → JSON 저장
3. 시각화 생성 → PNG 파일들

**생성 파일**:
- `{username}_basic_analysis.json`
- `{username}_advanced_analysis.json`
- `{username}_language_distribution.png`
- `{username}_repo_commits.png`
- `{username}_repo_popularity.png`

---

## 사용 시나리오

### 시나리오 1: 본인 프로필 빠른 확인
```bash
python github_scraper.py
# YOUR_USERNAME 입력
```

### 시나리오 2: 여러 개발자 비교 분석
```bash
# 각 개발자 분석
python github_scraper_cli.py developer1 -o dev1.json
python github_scraper_cli.py developer2 -o dev2.json
python github_scraper_cli.py developer3 -o dev3.json

# JSON 파일들을 비교 (별도 스크립트 작성 가능)
```

### 시나리오 3: 상세 리포트 생성
```bash
# 전체 분석 실행
python run_analysis.py username -o report_folder

# 결과물:
# - report_folder/username_basic_analysis.json
# - report_folder/username_advanced_analysis.json
# - report_folder/username_*.png
```

### 시나리오 4: CI/CD 통합
```bash
#!/bin/bash
# weekly_stats.sh
python github_scraper_cli.py $GITHUB_USER \
  -o "stats/$(date +%Y%m%d)_stats.json" \
  --no-output
```

### 시나리오 5: 대량 데이터 수집
```bash
#!/bin/bash
# analyze_multiple.sh
while IFS= read -r username; do
  echo "Analyzing $username..."
  python github_scraper_cli.py "$username" \
    -o "data/${username}.json" \
    --no-output
  sleep 2  # Rate limit 방지
done < usernames.txt
```

## 고급 기능

### JSON 데이터 활용

분석 결과는 JSON 형식으로 저장되므로, 다양한 방식으로 활용 가능:

```bash
# jq로 데이터 추출
cat result.json | jq '.statistics.total_commits'

# Python으로 추가 분석
python -c "
import json
with open('result.json') as f:
    data = json.load(f)
    print(f'Average stars: {data[\"statistics\"][\"avg_stars_per_repo\"]}')
"
```

### 환경 변수 설정

`.env` 파일 대신 환경 변수 직접 설정:

```bash
export GITHUB_TOKEN=ghp_your_token_here
python github_scraper.py
```

또는 명령줄에서:

```bash
GITHUB_TOKEN=ghp_your_token_here python github_scraper.py
```

## 문제 해결

### API Rate Limit 초과
**증상**: `API rate limit exceeded`

**해결책**:
1. Personal Access Token 사용 (시간당 5000 요청)
2. 요청 간 지연 추가
3. 캐싱 구현 (분석 결과 재사용)

### 한글 폰트 깨짐
**증상**: 차트에서 한글이 깨져 보임

**해결책**:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum fonts-nanum-coding

# macOS는 기본 지원

# Windows는 기본 지원
```

### 메모리 부족
**증상**: 대용량 리포지토리 분석 시 메모리 부족

**해결책**:
- 리포지토리 수 제한
- 커밋 분석 범위 제한 (최근 N개만)
- Swap 메모리 증가

### 느린 분석 속도
**증상**: 분석에 오래 걸림

**원인**:
- GitHub API 응답 시간
- 대량의 커밋 데이터

**해결책**:
- 기본 분석기 사용 (빠름)
- 고급 분석은 필요시에만 사용
- 병렬 처리 구현 (향후 업데이트)

## 추가 팁

### 1. 자동화 스크립트 만들기
```bash
#!/bin/bash
# auto_analyze.sh
python run_analysis.py $1 -o "reports/$(date +%Y%m%d)_$1"
echo "분석 완료: reports/$(date +%Y%m%d)_$1"
```

### 2. Crontab으로 주기적 실행
```bash
# 매주 월요일 9시에 실행
0 9 * * 1 cd /path/to/gitscraper && python github_scraper_cli.py myusername -o weekly_stats.json
```

### 3. 결과 이메일 전송
```bash
#!/bin/bash
python run_analysis.py username -o report
echo "분석 완료" | mail -s "GitHub Stats" -A report/*.png user@example.com
```

## 참고

- GitHub API 문서: https://docs.github.com/en/rest
- PyGithub 문서: https://pygithub.readthedocs.io/
- 프로젝트 이슈: [GitHub Issues 링크]
