#!/bin/bash
# GitHub Profile Analyzer - Batch Analysis Example
# 여러 사용자를 한 번에 분석하는 배치 스크립트

# 사용법: ./example_batch.sh

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================================"
echo "GitHub Profile Analyzer - Batch Analysis"
echo "======================================================================"
echo ""

# 출력 디렉토리 생성
OUTPUT_DIR="batch_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}출력 디렉토리: $OUTPUT_DIR${NC}"
echo ""

# 분석할 사용자 목록
# 예제: 유명한 오픈소스 기여자들
USERS=(
    "torvalds"
    "gvanrossum"
    "matz"
    "DHH"
    "taylorotwell"
)

# 각 사용자 분석
TOTAL=${#USERS[@]}
SUCCESS=0
FAILED=0

for i in "${!USERS[@]}"; do
    USER="${USERS[$i]}"
    NUM=$((i + 1))
    
    echo -e "${YELLOW}[$NUM/$TOTAL] 분석 중: $USER${NC}"
    
    # 기본 분석 실행
    python3 github_scraper_cli.py "$USER" \
        -o "$OUTPUT_DIR/${USER}_analysis.json" \
        --no-output
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $USER 분석 완료${NC}"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}❌ $USER 분석 실패${NC}"
        FAILED=$((FAILED + 1))
    fi
    
    # Rate limit 방지를 위한 대기
    if [ $NUM -lt $TOTAL ]; then
        echo "대기 중 (2초)..."
        sleep 2
    fi
    
    echo ""
done

echo "======================================================================"
echo "배치 분석 완료"
echo "======================================================================"
echo -e "${GREEN}성공: $SUCCESS${NC}"
echo -e "${RED}실패: $FAILED${NC}"
echo -e "결과 위치: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""

# 요약 리포트 생성
SUMMARY_FILE="$OUTPUT_DIR/summary.txt"
echo "GitHub Profile Analyzer - Batch Summary" > "$SUMMARY_FILE"
echo "Generated: $(date)" >> "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

for USER in "${USERS[@]}"; do
    JSON_FILE="$OUTPUT_DIR/${USER}_analysis.json"
    if [ -f "$JSON_FILE" ]; then
        echo "User: $USER" >> "$SUMMARY_FILE"
        
        # jq가 설치되어 있으면 상세 정보 추출
        if command -v jq &> /dev/null; then
            REPOS=$(jq -r '.statistics.total_repositories // "N/A"' "$JSON_FILE")
            COMMITS=$(jq -r '.statistics.total_commits // "N/A"' "$JSON_FILE")
            STARS=$(jq -r '.statistics.total_stars // "N/A"' "$JSON_FILE")
            
            echo "  Repositories: $REPOS" >> "$SUMMARY_FILE"
            echo "  Total Commits: $COMMITS" >> "$SUMMARY_FILE"
            echo "  Total Stars: $STARS" >> "$SUMMARY_FILE"
        fi
        
        echo "" >> "$SUMMARY_FILE"
    fi
done

echo -e "${GREEN}요약 리포트 생성: $SUMMARY_FILE${NC}"
echo ""

# 요약 출력
if command -v jq &> /dev/null; then
    echo "빠른 요약:"
    echo "----------------------------------------"
    for USER in "${USERS[@]}"; do
        JSON_FILE="$OUTPUT_DIR/${USER}_analysis.json"
        if [ -f "$JSON_FILE" ]; then
            COMMITS=$(jq -r '.statistics.total_commits // 0' "$JSON_FILE")
            echo "  $USER: $COMMITS commits"
        fi
    done
else
    echo -e "${YELLOW}팁: 'jq'를 설치하면 더 상세한 요약을 볼 수 있습니다.${NC}"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
fi

echo ""
echo "완료!"
