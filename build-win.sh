#!/bin/bash

# Windows .exe 빌드 스크립트
# 사용법: ./build-win.sh
# build.spec 파일을 사용하여 빌드합니다

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 기본값 설정
SPEC_FILE="build.spec"
PYTHON_FILE="src/main.py"
SHARED_FOLDER="/Volumes/shared"

echo -e "${YELLOW}🔨 Windows .exe 빌드 시작${NC}"
echo "spec 파일: $SPEC_FILE"
echo ""

# spec 파일 존재 확인
if [ ! -f "$SPEC_FILE" ]; then
    echo -e "${RED}❌ 오류: $SPEC_FILE 파일을 찾을 수 없습니다${NC}"
    exit 1
fi

# 파이썬 파일 존재 확인
if [ ! -f "$PYTHON_FILE" ]; then
    echo -e "${RED}❌ 오류: $PYTHON_FILE 파일을 찾을 수 없습니다${NC}"
    exit 1
fi

# Docker 실행 확인
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ 오류: Docker가 실행되고 있지 않습니다${NC}"
    echo "Docker Desktop을 먼저 실행해주세요"
    exit 1
fi

# 공유폴더 존재 확인
if [ ! -d "$SHARED_FOLDER" ]; then
    echo -e "${RED}❌ 오류: VMware 공유폴더를 찾을 수 없습니다${NC}"
    echo "VMware에서 공유폴더를 마운트해주세요: $SHARED_FOLDER"
    exit 1
fi

# 앱 이름
APP_NAME="LightweightViewer"

echo -e "${YELLOW}📦 Docker로 PyInstaller 실행 중...${NC}"
echo "(처음 실행 시 이미지 다운로드로 시간이 걸릴 수 있습니다)"
echo ""

# Docker로 Windows용 빌드 (build.spec 사용)
docker run --rm -v "$(pwd):/src" cdrx/pyinstaller-windows:python3 \
    "pip install PySide6 Pillow pillow-heif 2>/dev/null; pyinstaller --clean build.spec"

# 빌드 결과 확인
if [ -f "dist/$APP_NAME.exe" ]; then
    echo ""
    echo -e "${GREEN}✅ 빌드 성공!${NC}"

    # VMware 공유폴더로 복사
    cp "dist/$APP_NAME.exe" "$SHARED_FOLDER/"

    echo ""
    echo -e "${GREEN}📁 파일 위치:${NC}"
    echo "  로컬: $(pwd)/dist/$APP_NAME.exe"
    echo "  공유폴더: $SHARED_FOLDER/$APP_NAME.exe"
    echo ""
    echo -e "${YELLOW}💡 VMware Windows에서 실행하세요:${NC}"
    echo "  경로: \\\\vmware-host\\Shared Folders\\$APP_NAME.exe"
else
    echo ""
    echo -e "${RED}❌ 빌드 실패${NC}"
    echo "에러 로그를 확인해주세요"
    exit 1
fi
