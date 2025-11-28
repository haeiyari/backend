# 배포 체크리스트

## 📦 GitHub 업로드 전 확인

### 필수 파일 확인
- [x] `api_server.py` - 메인 서버 파일
- [x] `measurement_service.py` - 측정 서비스
- [x] `auth_utils.py` - 인증 유틸리티
- [x] `email_utils.py` - 이메일 유틸리티
- [x] `social_auth.py` - 소셜 로그인
- [x] `object_size.py` - 상의 측정
- [x] `pants_size.py` - 하의 측정
- [x] `requirements.txt` - 패키지 의존성
- [x] `.gitignore` - Git 제외 파일
- [x] `env_example.txt` - 환경변수 예시
- [x] `Dump20251114.sql` - 데이터베이스 스키마

### 제외할 파일 확인
- [x] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [x] `__pycache__/` 폴더 제외 확인
- [x] `node_modules/` 제외 확인
- [x] `uploaded_images/` 제외 확인
- [x] 테스트 이미지 파일들 제외 확인

### 코드 수정 확인
- [x] `DB_CONFIG`가 환경변수 사용하도록 수정됨
- [x] `start_server` 함수가 `PORT` 환경변수 사용하도록 수정됨
- [x] 하드코딩된 민감한 정보 제거됨

---

## 🚀 Render 배포 설정

### 1. Web Service 생성
- [ ] GitHub 저장소 연결
- [ ] 서비스 이름 설정
- [ ] Region 선택
- [ ] Branch 선택 (main)

### 2. Build & Start Command 설정
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### 3. 환경변수 설정
- [ ] `DB_HOST` 설정
- [ ] `DB_USER` 설정
- [ ] `DB_PASSWORD` 설정
- [ ] `DB_NAME` 설정 (shopping_app)
- [ ] `SECRET_KEY` 설정 (랜덤 문자열)
- [ ] `APP_URL` 설정 (Render URL)
- [ ] `KAKAO_CLIENT_ID` 설정
- [ ] `KAKAO_CLIENT_SECRET` 설정
- [ ] `KAKAO_REDIRECT_URI` 설정 (Render URL 기반)
- [ ] `GOOGLE_CLIENT_ID` 설정
- [ ] `GOOGLE_CLIENT_SECRET` 설정
- [ ] `GOOGLE_REDIRECT_URI` 설정 (Render URL 기반)
- [ ] `NAVER_CLIENT_ID` 설정
- [ ] `NAVER_CLIENT_SECRET` 설정
- [ ] `NAVER_REDIRECT_URI` 설정 (Render URL 기반)
- [ ] `SMTP_HOST` 설정 (smtp.gmail.com)
- [ ] `SMTP_PORT` 설정 (587)
- [ ] `SMTP_USER` 설정
- [ ] `SMTP_PASSWORD` 설정
- [ ] `FROM_EMAIL` 설정

### 4. 데이터베이스 설정
- [ ] PostgreSQL 또는 MySQL 데이터베이스 생성
- [ ] 데이터베이스 연결 정보 확인
- [ ] `Dump20251114.sql` 실행하여 스키마 초기화

### 5. 소셜 로그인 설정
- [ ] 카카오 개발자 콘솔에서 리다이렉트 URI 업데이트
- [ ] 구글 클라우드 콘솔에서 리다이렉트 URI 업데이트
- [ ] 네이버 개발자 센터에서 리다이렉트 URI 업데이트

---

## ✅ 배포 후 테스트

### 기본 기능 테스트
- [ ] `/health` 엔드포인트 응답 확인
- [ ] `/docs` API 문서 접근 확인
- [ ] `/` 루트 엔드포인트 응답 확인

### 인증 기능 테스트
- [ ] 일반 회원가입 테스트
- [ ] 일반 로그인 테스트
- [ ] 카카오 소셜 로그인 테스트
- [ ] 구글 소셜 로그인 테스트
- [ ] 네이버 소셜 로그인 테스트
- [ ] 로그아웃 테스트
- [ ] 비밀번호 재설정 이메일 발송 테스트

### 상품 기능 테스트
- [ ] 상품 목록 조회 테스트
- [ ] 상품 검색 테스트
- [ ] 상품 상세 조회 테스트

### 장바구니 기능 테스트
- [ ] 장바구니 추가 테스트
- [ ] 장바구니 조회 테스트
- [ ] 장바구니 수량 변경 테스트
- [ ] 장바구니 삭제 테스트

### 위시리스트 기능 테스트
- [ ] 위시리스트 추가 테스트
- [ ] 위시리스트 조회 테스트
- [ ] 위시리스트 삭제 테스트

### 주문 기능 테스트
- [ ] 주문 생성 테스트
- [ ] 주문 목록 조회 테스트
- [ ] 주문 상세 조회 테스트

---

## 🔧 문제 해결

### 서버가 시작되지 않는 경우
- [ ] Render 로그 확인
- [ ] 환경변수 확인
- [ ] `requirements.txt` 패키지 버전 확인

### 데이터베이스 연결 실패
- [ ] DB 환경변수 확인
- [ ] 데이터베이스 상태 확인
- [ ] 네트워크 연결 확인

### 소셜 로그인 실패
- [ ] 리다이렉트 URI 일치 확인
- [ ] CLIENT_ID, CLIENT_SECRET 확인
- [ ] 각 플랫폼 개발자 콘솔 확인

