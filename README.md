# Lightweight Viewer

Windows 11용 초경량 로컬 사진 뷰어

> 백그라운드 상주 없이 1초 안에 사진을 보여주는 가장 가벼운 뷰어

## 특징

- **빠른 실행**: 콜드 스타트 1초 이내
- **작은 용량**: 50~80MB (단일 exe)
- **낮은 메모리**: idle 시 50MB 이하
- **심플한 UI**: 미니멀 디자인, Windows 11 다크/라이트 테마 지원
- **오프라인 전용**: 클라우드 연동, 계정, 텔레메트리 없음

## 지원 포맷

### 이미지
- JPG, JPEG, PNG, BMP, WebP, GIF
- HEIC, HEIF (pillow-heif 라이브러리)

### 동영상 (예정)
- MP4 (H.264/H.265)

## 주요 기능

### 뷰어
- 좌우 방향키로 이전/다음 파일 탐색
- 마우스 휠 확대/축소
- 드래그로 이미지 이동
- 더블클릭 또는 F11 전체화면
- EXIF 회전 정보 자동 반영

### 썸네일 스트립
- 하단 가로 썸네일 스트립
- 비동기 로딩 (가상 스크롤)
- 1,000개 파일 폴더에서도 원활한 스크롤

### 이미지 압축
- 품질 선택 (90/80/70%)
- 해상도 축소 옵션
- JPEG, WebP, PNG 출력

## 설치

### 릴리스 다운로드
[Releases](../../releases) 페이지에서 최신 exe 파일 다운로드

### 직접 빌드

```bash
# 저장소 클론
git clone https://github.com/your-username/lightweight-viewer.git
cd lightweight-viewer

# 의존성 설치
pip install -r requirements.txt

# 개발 실행
python src/main.py

# exe 빌드
pyinstaller build.spec
```

## 단축키

| 키 | 동작 |
|---|------|
| ← / → | 이전/다음 이미지 |
| + / - | 확대/축소 |
| 0 | 창에 맞춤 |
| 1 | 실제 크기 (100%) |
| F11 | 전체 화면 토글 |
| ESC | 전체 화면 해제 |
| Ctrl+O | 파일 열기 |
| Ctrl+Shift+S | 이미지 압축 |

## 기술 스택

- **GUI**: PySide6 (Qt6)
- **이미지 처리**: Pillow
- **HEIC 지원**: pillow-heif
- **패키징**: PyInstaller

## 프로젝트 구조

```
lightweight-viewer/
├── src/
│   ├── main.py              # 앱 진입점
│   ├── viewer/
│   │   ├── main_window.py   # 메인 윈도우
│   │   ├── image_viewer.py  # 이미지 뷰어 위젯
│   │   └── thumbnail_strip.py # 썸네일 스트립
│   └── utils/
│       ├── image_loader.py  # 이미지 로딩 (HEIC 포함)
│       ├── compressor.py    # 이미지 압축
│       └── theme.py         # 테마 관리
├── .github/workflows/
│   └── build.yml            # GitHub Actions 빌드
├── requirements.txt
├── build.spec               # PyInstaller 설정
└── README.md
```

## 개발 → 테스트 흐름

```
1. 로컬에서 개발/커밋
2. git push origin main (또는 태그)
3. GitHub Actions 자동 빌드
4. Actions → Artifacts에서 exe 다운로드
5. 테스트 환경에서 exe 실행
```

## 성능 목표

| 항목 | 목표 |
|------|------|
| 콜드 스타트 → 창 표시 | 500ms 이내 |
| 콜드 스타트 → 첫 이미지 표시 | 1초 이내 |
| 50MB HEIC 파일 로드 | 3초 이내 |
| 1,000개 파일 폴더 썸네일 스크롤 | 60fps |

## 라이선스

MIT License
