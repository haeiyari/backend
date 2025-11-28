# 🚀 인증 기능 설치 및 설정 가이드

## 📋 구현된 기능

### ✅ 1단계 (완료)
- [x] 소셜 로그인 (카카오)
- [x] 소셜 로그인 (구글)
- [x] 로그아웃
- [x] 비밀번호 재설정 이메일 발송

### ✅ 2단계 (완료)
- [x] 회원 탈퇴
- [x] 상품 검색 (기본 SQL)

---

## 🔧 설치 단계

### 1. 패키지 설치

```bash
cd C:\Users\rehan\Desktop\project\my-app
pip install -r requirements.txt
```

새로 추가된 패키지:
- `python-jose[cryptography]` - JWT 토큰
- `passlib[bcrypt]` - 비밀번호 해싱
- `sendgrid` - 이메일 발송
- `requests` - 소셜 로그인 API 호출

---

### 2. 데이터베이스 업데이트

```bash
# MySQL에 접속
mysql -u root -p

# 스키마 업데이트 실행
source C:\Users\rehan\Desktop\project\my-app\database_update.sql
```

또는 MySQL Workbench에서 `database_update.sql` 파일을 열어서 실행하세요.

**업데이트 내용:**
- `users` 테이블에 소셜 로그인 컬럼 추가
- `products` 테이블 생성
- 샘플 상품 데이터 추가

---

### 3. 환경변수 설정

#### 3-1. `.env` 파일 생성

`env_example.txt`를 복사하여 `.env` 파일을 만드세요:

```bash
copy env_example.txt .env
```

#### 3-2. 카카오 로그인 설정

1. [카카오 개발자 센터](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 애플리케이션 추가하기
3. 앱 설정 > 앱 키 > REST API 키 복사
4. 제품 설정 > 카카오 로그인 > 활성화 설정
5. Redirect URI 등록: `http://localhost:8000/callback`
6. `.env` 파일에 추가:
   ```
   KAKAO_CLIENT_ID=your-rest-api-key
   ```

#### 3-3. 구글 로그인 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성
3. API 및 서비스 > OAuth 동의 화면 설정
4. 사용자 인증 정보 > OAuth 2.0 클라이언트 ID 만들기
5. 승인된 리디렉션 URI 추가: `http://localhost:8000/callback`
6. 클라이언트 ID와 클라이언트 보안 비밀 복사
7. `.env` 파일에 추가:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

#### 3-4. SendGrid 이메일 설정 (선택사항)

1. [SendGrid](https://sendgrid.com/) 가입 (무료 플랜: 하루 100통)
2. Settings > API Keys > Create API Key
3. Full Access 권한으로 생성
4. API 키 복사
5. `.env` 파일에 추가:
   ```
   SENDGRID_API_KEY=your-api-key
   FROM_EMAIL=noreply@yourapp.com
   ```

**참고:** SendGrid 설정을 하지 않으면 이메일은 발송되지 않고 콘솔에 링크만 출력됩니다.

#### 3-5. JWT 시크릿 키 설정

```
SECRET_KEY=your-very-long-random-secret-key-change-this
```

랜덤 문자열 생성 (Python):
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

### 4. 서버 실행

```bash
python api_server.py
```

서버가 정상적으로 시작되면:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 🧪 테스트

### 1. API 문서에서 테스트

브라우저에서 http://localhost:8000/docs 접속하여 각 엔드포인트를 테스트할 수 있습니다.

### 2. 소셜 로그인 테스트

#### 카카오 로그인 테스트 URL
```
https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri=http://localhost:8000/callback&response_type=code
```

#### 구글 로그인 테스트 URL
```
https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/callback&response_type=code&scope=openid%20email%20profile
```

### 3. Postman으로 테스트

`postman_collection.json`에 새로운 엔드포인트를 추가하여 테스트할 수 있습니다.

---

## 📁 생성된 파일 목록

```
my-app/
├── auth_utils.py              # 인증 유틸리티 (JWT, 비밀번호 해싱)
├── email_utils.py             # 이메일 발송 유틸리티
├── social_auth.py             # 소셜 로그인 처리
├── database_update.sql        # DB 스키마 업데이트
├── env_example.txt            # 환경변수 예시
├── API_AUTH_GUIDE.md          # API 사용 가이드
├── SETUP_AUTH.md              # 이 파일
└── requirements.txt           # 업데이트됨
```

---

## 🔗 API 엔드포인트 요약

### 인증
- `POST /auth/social-login` - 소셜 로그인 (카카오/구글)
- `POST /auth/logout` - 로그아웃
- `POST /auth/password-reset/request` - 비밀번호 재설정 요청
- `POST /auth/password-reset/confirm` - 비밀번호 변경
- `DELETE /auth/withdraw/{user_id}` - 회원 탈퇴

### 상품
- `GET /products/search` - 상품 검색

### 기존 기능
- `POST /signup` - 회원가입
- `POST /login` - 로그인
- `POST /measure` - 의류 치수 측정
- `GET /my-closet/{user_id}` - 내 옷장 조회
- 기타 등등...

---

## ⚠️ 주의사항

### 보안
1. **프로덕션 환경**에서는 반드시:
   - HTTPS 사용
   - 강력한 SECRET_KEY 설정
   - 환경변수를 `.env` 파일로 관리 (Git에 커밋하지 말 것)
   - CORS 설정 강화

2. **토큰 블랙리스트**:
   - 현재는 메모리에 저장 (서버 재시작 시 초기화)
   - 실제 운영에서는 Redis 사용 권장

3. **비밀번호 해싱**:
   - 기존 MD5 → bcrypt로 변경됨
   - 기존 사용자는 다음 로그인 시 비밀번호 재설정 필요할 수 있음

### 데이터베이스
- 기존 `users` 테이블의 `password` 컬럼이 NULL 허용으로 변경됨
- 소셜 로그인 사용자는 `password`가 빈 문자열

---

## 🐛 문제 해결

### 1. 패키지 설치 오류
```bash
# 가상환경 사용 권장
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 데이터베이스 연결 오류
- `api_server.py`의 `DB_CONFIG` 확인
- MySQL 서버 실행 여부 확인

### 3. 소셜 로그인 오류
- 환경변수 설정 확인
- 리다이렉트 URI가 정확히 일치하는지 확인
- 각 플랫폼의 개발자 콘솔에서 앱 상태 확인

### 4. 이메일 발송 안 됨
- SendGrid API 키 확인
- 무료 플랜 제한 (하루 100통) 확인
- 콘솔 로그에서 링크 확인 가능

---

## 📚 추가 문서

- **API 사용 가이드**: `API_AUTH_GUIDE.md`
- **기존 API 문서**: `README_API.md`
- **프로젝트 구조**: `PROJECT_STRUCTURE.md`

---

## 🎉 완료!

이제 다음 기능들을 사용할 수 있습니다:
- ✅ 카카오/구글 소셜 로그인
- ✅ 로그아웃
- ✅ 비밀번호 재설정 이메일
- ✅ 회원 탈퇴
- ✅ 상품 검색

궁금한 점이 있으면 `API_AUTH_GUIDE.md`를 참조하세요!

