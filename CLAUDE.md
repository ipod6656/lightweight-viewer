# 프로젝트 가이드

## 개발 환경
- 개발: Mac
- 배포 대상: Windows 11
- 언어: Python

## 빌드 명령

### Windows .exe 빌드
```bash
./build-win.sh main.py
```
- Docker 필요 (cdrx/pyinstaller-windows:python3 이미지 사용)
- 결과물: `dist/` 폴더 + VMware 공유폴더 (`/Volumes/shared/`)

### 엔트리 포인트
- main.py (필요시 변경)

## 폴더 구조
```
프로젝트/
├── main.py              # 메인 실행 파일
├── requirements.txt     # 의존성 패키지
├── build-win.sh         # Windows 빌드 스크립트
├── CLAUDE.md            # 이 파일
└── dist/                # 빌드 결과물
```

## Claude Code에게 요청 시

### 빌드 요청
- "윈도우 빌드해줘" 또는 "./build-win.sh 실행해줘"

### 새 기능 개발 후
1. 코드 수정
2. "윈도우 빌드해줘"
3. VMware에서 `/Volumes/shared/` 확인 후 테스트
