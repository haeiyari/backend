# 프로젝트 구조

## 📁 디렉토리 구조

```
project/my-app/
├── 📄 API 서버 (핵심 파일)
│   ├── api_server.py              # FastAPI 서버 메인 파일
│   ├── measurement_service.py     # 치수 측정 서비스 로직
│   └── requirements.txt           # Python 패키지 의존성
│
├── 📄 원본 측정 스크립트
│   ├── object_size.py             # 상의 치수 측정 (원본)
│   └── pants_size.py              # 하의 치수 측정 (원본)
│
├── 🚀 실행 스크립트
│   ├── start_server.bat           # 서버 시작 (Windows)
│   ├── start_server.sh            # 서버 시작 (Linux/Mac)
│   └── test_client.py             # API 테스트 클라이언트
│
├── 📚 문서
│   ├── README_API.md              # API 상세 문서
│   ├── QUICKSTART.md              # 빠른 시작 가이드
│   └── PROJECT_STRUCTURE.md       # 프로젝트 구조 (이 파일)
│
├── 🌐 웹 인터페이스
│   ├── demo_with_keypoints.html   # 웹 데모 페이지(키포인트 조정 포함)
│   └── postman_collection.json    # Postman API 컬렉션
│
└── 🔧 설정 파일
    └── .gitignore                 # Git 무시 파일 목록
```

## 📋 파일 설명

### 핵심 API 파일

#### `api_server.py`
- **역할**: FastAPI 기반 REST API 서버
- **주요 기능**:
  - `/measure` - 단일 의류 측정
  - `/measure/batch` - 여러 의류 일괄 측정
  - `/health` - 서버 상태 확인
  - `/supported-measurements` - 측정 항목 조회
- **포트**: 8000 (기본값)

#### `measurement_service.py`
- **역할**: 의류 치수 측정 핵심 로직
- **주요 클래스**: `MeasurementService`
- **주요 기능**:
  - A4 용지 자동 검출
  - 의류 윤곽선 검출
  - 키포인트 자동 추출
  - 치수 계산 및 보정

### 원본 스크립트

#### `object_size.py`
- 상의(티셔츠, 셔츠 등) 치수 측정
- 측정 항목: 총장, 어깨, 가슴, 소매

#### `pants_size.py`
- 하의(바지, 반바지 등) 치수 측정
- 측정 항목: 총장, 허리, 엉덩이, 밑위, 허벅지, 밑단

### 실행 및 테스트 도구

#### `start_server.bat` / `start_server.sh`
- API 서버 간편 실행 스크립트
- 패키지 설치 상태 확인
- 자동으로 서버 시작

#### `test_client.py`
- 커맨드라인 API 테스트 도구
- 사용법:
  ```bash
  python test_client.py image.jpg shirt
  ```

### 문서

#### `README_API.md`
- API 전체 문서
- 엔드포인트 상세 설명
- 코드 예제 (Python, JavaScript, cURL)
- 문제 해결 가이드

#### `QUICKSTART.md`
- 5분 빠른 시작 가이드
- 이미지 준비 팁
- 간단한 예제

### 웹 인터페이스

#### `demo_with_keypoints.html`
- 브라우저 기반 데모 페이지
- 드래그 앤 드롭으로 이미지 업로드
- A4 수동 선택 + 키포인트 조정 + 실시간 측정 결과 표시

#### `postman_collection.json`
- Postman API 테스트 컬렉션
- 모든 엔드포인트 사전 설정

## 🔄 데이터 흐름

```
[사용자] → [이미지 업로드]
    ↓
[API 서버] (api_server.py)
    ↓
[측정 서비스] (measurement_service.py)
    ↓
    ├─→ [A4 용지 검출]
    ├─→ [의류 윤곽선 검출]
    ├─→ [키포인트 추출]
    └─→ [치수 계산]
    ↓
[JSON 응답] + [결과 이미지]
    ↓
[사용자]
```

## 🛠 기술 스택

### 백엔드
- **FastAPI**: 고성능 웹 프레임워크
- **OpenCV**: 이미지 처리 및 컴퓨터 비전
- **NumPy**: 수치 계산
- **SciPy**: 과학 계산
- **Uvicorn**: ASGI 서버

### 프론트엔드 (데모)
- **HTML5**: 구조
- **CSS3**: 스타일링
- **JavaScript (Fetch API)**: API 통신

## 📦 의존성

### Python 패키지
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
opencv-python==4.9.0.80
numpy==1.26.3
scipy==1.11.4
scikit-learn==1.4.0
pydantic==2.5.3
```

### 시스템 요구사항
- Python 3.8 이상
- 최소 4GB RAM
- 1GB 여유 디스크 공간

## 🚀 배포 아키텍처

### 개발 환경
```
[개발자 PC]
    ↓
python api_server.py
    ↓
http://localhost:8000
```

### 프로덕션 환경 (예시)
```
[클라이언트] → [로드밸런서]
                    ↓
            [API 서버 인스턴스 1]
            [API 서버 인스턴스 2]
            [API 서버 인스턴스 3]
                    ↓
            [공유 스토리지]
```

## 🔐 보안 고려사항

### 현재 구현
- ✅ 파일 타입 검증
- ✅ 이미지 크기 제한
- ✅ 에러 핸들링

### 프로덕션 권장사항
- 🔒 API 인증 (JWT, OAuth2)
- 🔒 Rate Limiting
- 🔒 HTTPS 필수
- 🔒 CORS 설정 강화
- 🔒 입력 데이터 검증 강화

## 📊 성능 최적화

### 현재 성능
- 단일 이미지 처리: ~2-5초
- 동시 요청 처리: 가능 (비동기)

### 최적화 방안
1. **캐싱**: Redis를 사용한 결과 캐싱
2. **큐잉**: Celery를 사용한 백그라운드 처리
3. **이미지 리사이징**: 대용량 이미지 자동 축소
4. **GPU 가속**: CUDA 활성화 OpenCV 사용

## 🧪 테스트

### 수동 테스트
```bash
# 1. 단일 이미지 테스트
python test_client.py test.jpg shirt

# 2. 웹 브라우저 테스트
# demo_with_keypoints.html을 브라우저에서 열기

# 3. Postman 테스트
# postman_collection.json 임포트
```

### 자동 테스트 (TODO)
```bash
# pytest를 사용한 단위 테스트
pytest tests/

# API 통합 테스트
pytest tests/test_api.py
```

## 📈 향후 개발 계획

### v1.1
- [ ] API 인증 추가
- [ ] 사용자별 측정 이력 저장
- [ ] 측정 정확도 개선

### v2.0
- [ ] 실시간 비디오 측정
- [ ] 3D 측정 지원
- [ ] 모바일 앱 (React Native)
- [ ] 다국어 지원

## 🤝 기여 가이드

1. Fork 후 브랜치 생성
2. 기능 개발 및 테스트
3. 코드 스타일 준수 (PEP 8)
4. Pull Request 생성

## 📞 지원

- **이슈 등록**: GitHub Issues
- **문서**: README_API.md
- **API 문서**: http://localhost:8000/docs

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-10-31

