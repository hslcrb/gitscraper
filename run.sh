#!/bin/bash
# GitHub Profile Analyzer - 원클릭 실행 스크립트

set -e  # 오류 발생 시 중단

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}║           ${GREEN}GitHub Profile Analyzer${BLUE}                             ║${NC}"
echo -e "${BLUE}║                                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 가상환경이 없습니다. 생성 중...${NC}"
    
    # python3-venv 확인
    if ! dpkg -l | grep -q python3.*-venv; then
        echo -e "${RED}⚠️  python3-venv가 설치되지 않았습니다.${NC}"
        echo -e "${YELLOW}다음 명령어로 설치하세요:${NC}"
        echo -e "${GREEN}sudo apt install python3.12-venv${NC}"
        exit 1
    fi
    
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상환경 생성 완료!${NC}"
    echo ""
fi

# 가상환경 활성화
echo -e "${BLUE}🔄 가상환경 활성화 중...${NC}"
source venv/bin/activate

# 의존성 확인 및 설치
if [ ! -f "venv/dependencies_installed.flag" ]; then
    echo -e "${YELLOW}📥 의존성 패키지 설치 중...${NC}"
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    # 설치 완료 플래그 생성
    touch venv/dependencies_installed.flag
    
    echo -e "${GREEN}✅ 의존성 설치 완료!${NC}"
    echo ""
fi

# 프로그램 실행
echo -e "${GREEN}🚀 프로그램 실행 중...${NC}"
echo ""

python main.py

# 종료 후 정리
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 프로그램이 정상적으로 종료되었습니다.${NC}"
else
    echo ""
    echo -e "${RED}❌ 프로그램이 오류와 함께 종료되었습니다. (종료 코드: $EXIT_CODE)${NC}"
fi

# 가상환경 비활성화
deactivate

exit $EXIT_CODE
