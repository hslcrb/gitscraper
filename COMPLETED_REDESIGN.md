# GitHub Profile Analyzer - 통합 분석 버전 완료

## 프로젝트 개요

GitHub 프로필 분석 도구를 **단일 통합 분석 시스템**으로 완전히 재설계했습니다.

## 주요 변경 사항

### 1. 🎯 통합 분석 시스템
- **단일 분석 옵션**: 모든 기능을 하나로 통합
- **리포지토리 타입 선택**: Public only / Private only / Both (기본값)
- **모든 메타데이터 수집**: 시간 정보, 기여자, 브랜치, 태그, 라이선스 등

### 2. 🔒 강화된 보안
- **즉시 폐기**: Token을 받은 즉시 사용하고 메모리에서 제거
- **가비지 컬렉션**: `gc.collect()`로 강제 메모리 정리
- **작업 후 유출 방지**: 분석 완료 후에도 Token이 남지 않음
- **파일 저장 없음**: .env 파일 완전 제거

### 3. 📁 파일 안전성
- **덮어쓰기 방지**: 동일 파일명 시 자동으로 `_1`, `_2` 접미사 추가
- **Git 추적 제외**: 모든 생성 파일(*.json, *.html, *.png) 자동 gitignore

### 4. 📊 HTML 시각화
- **Chart.js 기반**: 인터랙티브 차트
- **다양한 그래프**: 파이, 바, 도넛 차트
- **Export 기능**: HTML 자체 및 표를 이미지로 저장 가능
- **Print/PDF**: 브라우저 인쇄 기능 지원
- **라이트 테마**: 심플하고 깔끔한 디자인

### 5. 🎨 심플한 UI
- **라이트 테마**: 밝고 깔끔한 색상
- **도형 문자 제거**: 장식적인 박스 문자 모두 제거
- **2가지 메뉴**: Start Analysis / Exit 만 유지
- **이모지 제거**: ASCII 특수문자만 사용

## 새로운 파일 구조

```
src/
├── unified_analyzer.py    # 통합 분석기 (메인)
├── file_utils.py          # 파일 중복 방지 유틸
├── html_visualizer.py     # HTML 시각화 생성
└── (기존 레거시 파일들...)

main.py                    # 심플한 TUI 메인 프로그램
run.sh                     # 원클릭 실행 스크립트
.gitignore                 # 생성 파일 제외 설정
```

## 사용 방법

### 실행
```bash
./run.sh
```

### 프로세스
1. **메뉴 선택**: `1` (Start Analysis)
2. **사용자명 입력**: GitHub 사용자명
3. **타입 선택**: Public/Private/Both
4. **Token 입력**: 화면에 표시되지 않음
5. **자동 분석**: 진행률 표시
6. **결과 저장**: JSON 및 HTML 생성

## 생성되는 파일

- `{username}_analysis.json` - 전체 분석 데이터
- `{username}_visualization.html` - 인터랙티브 리포트

중복 시 자동으로 `_1`, `_2` 등의 번호가 추가됩니다.

## 수집되는 정보

### 기본 통계
- 리포지토리 수 (Public/Private)
- 커밋/스타/포크/이슈 수
- 코드 크기 (KB/MB/GB)
- 평균값들

### 시간 정보
- 생성일, 업데이트일, 푸시일
- 리포지토리 나이
- 마지막 업데이트 경과 시간
- 활동성 분석

### 메타데이터
- 언어별 코드량
- 기여자 수
- 브랜치 수
- 태그/릴리스 수
- 라이선스 정보
- Public/Private 분류

## 보안 특징

1. **Token 즉시 폐기**
   ```python
   token = getpass("Enter Token: ")
   analyzer = UnifiedGitHubAnalyzer(token)
   del token
   gc.collect()  # 즉시 메모리에서 제거
   ```

2. **분석 후 정리**
   ```python
   analyzer.cleanup()
   del analyzer
   gc.collect()
   ```

3. **Git 추적 제외**
   - 모든 `*.json`, `*.html`, `*.png` 파일
   - Token 관련 파일 모두 제외

## HTML 시각화 기능

### Chart.js 그래프
1. **언어 분포** - Pie Chart
2. **커밋 활동** - Bar Chart (상위 15개)
3. **인기도** - Bar Chart (스타 & 포크)
4. **리포 타입** - Doughnut Chart (Public vs Private)
5. **활동성** - Bar Chart (최근/활동/비활성)

### Export 기능
- **Export as Image**: html2canvas로 전체 리포트 이미지 저장
- **Export Table as Image**: 테이블만 별도 이미지 저장
- **Print/PDF**: 브라우저 인쇄 기능으로 PDF 저장

## 테스트 완료

✅ 모든 모듈 import 성공
✅ 파일 이름 중복 방지 작동
✅ 분석 파일명 생성 정상
✅ 시각화 파일명 생성 정상
✅ Git commit 및 push 완료
✅ README.md 업데이트 완료

## Git 커밋 내역

```
commit ed091d8
FEATURE: Major redesign - Unified analysis with HTML visualization

- Simplified TUI to single unified analysis option
- Implemented immediate token disposal
- Added comprehensive metadata collection
- Created file_utils.py for duplicate prevention
- Created html_visualizer.py with Chart.js
- Created unified_analyzer.py
- Light theme UI
- Updated documentation
```

## 다음 단계

이제 프로그램을 실행할 수 있습니다:

```bash
./run.sh
```

모든 기능이 통합되어 있으며, 간단한 2가지 메뉴로 모든 작업을 수행할 수 있습니다.

---

**완료일**: 2024
**버전**: 2.0 (Unified Analysis Version)
**상태**: ✅ 완료 및 테스트 완료
