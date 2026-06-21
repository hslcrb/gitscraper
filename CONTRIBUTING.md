# Contributing to GitHub Profile Analyzer

이 프로젝트에 기여해주셔서 감사합니다! 🎉

## 개발 환경 설정

### 1. 저장소 포크 및 클론
```bash
# 저장소 포크 (GitHub 웹사이트에서)
# 그 후 클론
git clone https://github.com/YOUR_USERNAME/gitscraper.git
cd gitscraper
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 개발 브랜치 생성
```bash
git checkout -b feature/your-feature-name
```

## 코딩 스타일

### Python 코드
- PEP 8 스타일 가이드 준수
- 함수와 클래스에 docstring 작성
- 타입 힌팅 사용 권장

```python
def analyze_repository(self, repo: Repository.Repository) -> Dict[str, Any]:
    """
    개별 리포지토리 분석
    
    Args:
        repo: GitHub 리포지토리 객체
        
    Returns:
        분석 결과 딕셔너리
    """
    pass
```

### 커밋 메시지
```
<type>: <한글 설명> - <영문 설명>

Types:
- feat: 새로운 기능
- fix: 버그 수정
- docs: 문서 수정
- style: 코드 포맷팅
- refactor: 코드 리팩토링
- test: 테스트 추가
- chore: 빌드/설정 변경

예시:
feat: 캐싱 기능 추가 - Add caching feature
fix: Rate limit 처리 개선 - Improve rate limit handling
docs: README 업데이트 - Update README
```

## 테스트

### 테스트 실행
```bash
# 기본 테스트
python test_basic.py

# 특정 기능 테스트
python -m pytest tests/  # pytest 설치 시
```

### 테스트 작성
- 새 기능 추가 시 관련 테스트도 함께 작성
- `test_*.py` 형식으로 파일명 작성

## Pull Request 프로세스

1. **브랜치 업데이트**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **변경사항 커밋**
   ```bash
   git add .
   git commit -m "feat: 기능 설명 - Feature description"
   ```

3. **테스트 확인**
   ```bash
   python test_basic.py
   ```

4. **푸시**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Pull Request 생성**
   - GitHub에서 Pull Request 생성
   - 변경사항 설명 작성
   - 관련 이슈 링크

## PR 체크리스트

- [ ] 코드가 PEP 8 스타일을 따릅니다
- [ ] 새로운 기능에 대한 테스트를 추가했습니다
- [ ] 모든 테스트가 통과합니다
- [ ] 문서를 업데이트했습니다 (해당하는 경우)
- [ ] 커밋 메시지가 규칙을 따릅니다

## 기여 아이디어

### 기능 추가
- [ ] 더 많은 통계 지표
- [ ] 웹 대시보드
- [ ] 데이터베이스 저장 기능
- [ ] 비교 분석 기능
- [ ] 팀/조직 분석
- [ ] 타임라인 시각화
- [ ] PDF 리포트 생성

### 성능 개선
- [ ] 병렬 처리
- [ ] 캐싱 시스템
- [ ] 증분 업데이트
- [ ] 메모리 최적화

### 문서 개선
- [ ] 튜토리얼 영상
- [ ] API 문서
- [ ] 다국어 지원
- [ ] 사용 예제 추가

## 이슈 리포팅

버그를 발견하셨나요? 이슈를 생성해주세요!

### 버그 리포트 템플릿
```markdown
**버그 설명**
명확하고 간결한 버그 설명

**재현 방법**
1. '...'로 이동
2. '...'를 클릭
3. '...'까지 스크롤
4. 오류 확인

**예상 동작**
무엇이 일어나길 기대했는지

**실제 동작**
실제로 무엇이 일어났는지

**스크린샷**
해당하는 경우 스크린샷 추가

**환경**
- OS: [예: Ubuntu 20.04]
- Python 버전: [예: 3.9.5]
- 프로젝트 버전: [예: 1.0.0]

**추가 컨텍스트**
버그에 대한 기타 컨텍스트
```

## 질문이나 도움이 필요하신가요?

- 이슈를 생성하세요
- 디스커션에 참여하세요
- 이메일: [연락처]

## 행동 강령

### 우리의 약속

우리는 다음을 약속합니다:
- 모든 기여자를 존중합니다
- 건설적인 피드백을 제공합니다
- 다양성을 환영합니다
- 포용적인 환경을 유지합니다

### 용납되지 않는 행동

- 괴롭힘이나 모욕적인 언어
- 개인 정보 공개
- 트롤링이나 정치적/종교적 공격
- 기타 비전문적인 행동

---

다시 한 번 기여에 감사드립니다! 🙏
