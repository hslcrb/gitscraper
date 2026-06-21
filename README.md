# GitHub Profile Analyzer

🎨 **RICH TUI 기반** GitHub 프로필 오픈소스 리포지토리 분석 도구

아름다운 터미널 UI로 GitHub 프로필의 커밋 수, 코드량, 언어 분포 등의 통계를 제공합니다.

## ✨ 주요 특징

### 🎨 **RICH TUI 인터페이스**
- 아름다운 터미널 사용자 인터페이스
- 인터랙티브한 메뉴 시스템
- 실시간 프로그레스 바
- 컬러풀한 테이블과 트리 뷰

### 📊 **기본 분석**
- GitHub 프로필의 모든 공개 리포지토리 분석
- 총 커밋 수, 스타 수, 포크 수 집계
- 💻 언어별 코드 분포 분석
- 📦 리포지토리별 상세 정보 제공
- 📋 종합 통계 리포트 생성

### 🔬 **고급 분석**
- 📝 코드 추가/삭제량 상세 분석
- ⏰ 시간대별/요일별 커밋 패턴 분석
- 🎯 리포지토리별 기여도 및 역할 분석
- 📊 활동 통계 및 트렌드

### 📈 **시각화**
- 언어별 코드 분포 파이 차트
- 리포지토리별 커밋 수 바 차트
- 스타/포크 인기도 산점도

### 🔄 **추가 기능**
- 프로필 비교 분석
- Markdown, HTML, CSV 리포트 내보내기
- 배치 분석 스크립트

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

```bash
# 가상환경이 활성화된 상태에서
python main.py

# 프로그램이 시작되면 GitHub Token을 입력하라는 메시지가 표시됩니다
# Token은 화면에 표시되지 않으며, 메모리에만 저장됩니다
```

### 가상환경 종료

```bash
deactivate
```

## 🔒 보안 특징

### Token 보안
- ✅ **파일 저장 없음**: Token을 .env나 다른 파일에 저장하지 않습니다
- ✅ **메모리만 사용**: Token은 프로그램 실행 중에만 메모리에 존재합니다
- ✅ **자동 제거**: 프로그램 종료 시 Token이 메모리에서 자동으로 제거됩니다
- ✅ **화면 숨김**: Token 입력 시 화면에 표시되지 않습니다 (getpass 사용)
- ✅ **추적 불가**: 컴퓨터에 Token 흔적이 남지 않습니다

## 🎮 사용법

### 1. RICH TUI 메인 프로그램 (권장)

```bash
python main.py
```

**메뉴 옵션:**
- `1` 📊 프로필 기본 분석
- `2` 🔬 프로필 고급 분석
- `3` 📈 시각화 생성
- `4` 🔄 프로필 비교
- `5` 📄 리포트 내보내기
- `6` ⚙️  설정
- `0` 🚪 종료

### 2. CLI 도구 (고급 사용자용)

```bash
# 기본 분석
python src/github_scraper.py

# CLI 인터페이스
python src/github_scraper_cli.py USERNAME -o result.json

# 고급 분석
python src/advanced_analyzer.py USERNAME

# 시각화 생성
python src/visualizer.py result.json

# 프로필 비교
python src/compare_profiles.py user1.json user2.json

# 리포트 내보내기
python src/export_report.py result.json --html report.html
```

## 📊 출력 정보

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
- 시각적 프로그레스 바

### 리포지토리 상세
- 리포지토리명, URL
- 설명
- 커밋/스타/포크 수
- 생성일 및 업데이트일
- 주요 사용 언어

## 📁 프로젝트 구조

```
gitscraper/
├── main.py                    # RICH TUI 메인 프로그램
├── src/
│   ├── __init__.py
│   ├── github_scraper.py      # 기본 분석기
│   ├── github_scraper_cli.py  # CLI 인터페이스
│   ├── advanced_analyzer.py   # 고급 분석
│   ├── visualizer.py          # 시각화 생성
│   ├── run_analysis.py        # 통합 실행
│   ├── compare_profiles.py    # 프로필 비교
│   └── export_report.py       # 리포트 내보내기
├── test_basic.py              # 기본 테스트
├── example_batch.sh           # 배치 분석
├── requirements.txt           # 의존성
├── setup.py                   # 설치 스크립트
├── .env.example              # 환경 변수 예제
├── LICENSE                   # MIT 라이선스
├── README.md                 # 문서 (이 파일)
├── USAGE.md                  # 상세 사용 가이드
└── CONTRIBUTING.md           # 기여 가이드
```

## 🛠️ 요구사항

- Python 3.7+
- GitHub Personal Access Token
- 패키지: 
  - PyGithub
  - python-dotenv
  - matplotlib
  - rich (RICH TUI)

## 📸 스크린샷

### RICH TUI 메인 화면
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           GitHub Profile Analyzer                             ║
║                                                               ║
║          RICH TUI 기반 프로필 분석 도구                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

┌─────────────── 메인 메뉴 ───────────────┐
│ 1 📊 프로필 기본 분석                    │
│ 2 🔬 프로필 고급 분석                    │
│ 3 📈 시각화 생성                         │
│ 4 🔄 프로필 비교                         │
│ 5 📄 리포트 내보내기                     │
│ 6 ⚙️  설정                              │
│ 0 🚪 종료                               │
└─────────────────────────────────────────┘
```

## 💡 예제

### 예제 1: 빠른 분석
```bash
python main.py
# 메뉴에서 1 선택
# 사용자명 입력
```

### 예제 2: 배치 분석
```bash
./example_batch.sh
```

### 예제 3: 프로필 비교
```bash
python src/compare_profiles.py user1.json user2.json --csv comparison.csv
```

## 🐛 문제 해결

### Rate Limit 초과
GitHub API는 시간당 요청 제한이 있습니다. Personal Access Token을 사용하면 제한이 완화됩니다.

### 한글 폰트 깨짐 (Linux)
```bash
sudo apt-get install fonts-nanum
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
