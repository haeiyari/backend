# 백엔드 배포 가이드 (Render)

## 📋 배포에 필요한 파일 목록

### ✅ 필수 파일 (GitHub에 업로드)

#### 1. Python 코드 파일
```
api_server.py              # FastAPI 메인 서버
measurement_service.py     # 치수 측정 서비스
auth_utils.py              # 인증 유틸리티 (JWT, 비밀번호 해싱)
email_utils.py             # 이메일 발송 유틸리티
social_auth.py             # 소셜 로그인 처리 (카카오/구글/네이버)
object_size.py             # 상의 측정 로직
pants_size.py              # 하의 측정 로직
```

#### 2. 설정 파일
```
requirements.txt           # Python 패키지 의존성
.gitignore                 # Git 제외 파일 목록 (필수!)
env_example.txt           # 환경변수 예시 (실제 값은 Render에서 설정)
render.yaml               # Render 배포 설정 (선택적 - 있으면 자동 설정됨)
```

#### 3. 데이터베이스
```
Dump20251114.sql          # 데이터베이스 스키마 (초기 설정용)
```

#### 4. HTML 파일 (선택적 - 프론트엔드가 사용할 수도 있음)
```
index.html
demo_with_keypoints.html
mobile_capture.html
my_closet.html
test_auth.html
```

#### 5. 문서 파일 (선택적)
```
README_API.md
API_AUTH_GUIDE.md
QUICKSTART.md
```

### ❌ 제외할 파일 (GitHub에 업로드하지 않음)

```
.env                       # 민감한 정보 포함 (절대 업로드 금지!)
__pycache__/              # Python 캐시
*.pyc                      # 컴파일된 Python 파일
node_modules/             # Node.js 모듈 (프론트엔드용)
uploaded_images/           # 사용자 업로드 이미지
*.jpg, *.png              # 테스트용 이미지 파일들
test_*.py                 # 테스트 파일들 (선택적)
```

---

## 🚀 Render 배포 단계

### 1단계: GitHub에 코드 업로드

1. **GitHub 저장소 생성**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Backend API"
   git branch -M main
   git remote add origin https://github.com/your-username/your-repo-name.git
   git push -u origin main
   ```

2. **업로드 전 확인사항**
   - ✅ `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
   - ✅ `__pycache__/` 폴더가 제외되었는지 확인
   - ✅ 민감한 정보가 코드에 하드코딩되지 않았는지 확인

### 2단계: Render에서 Web Service 생성

1. **Render 대시보드 접속**
   - https://dashboard.render.com 접속
   - "New +" → "Web Service" 클릭

2. **GitHub 저장소 연결**
   - GitHub 저장소 선택
   - 저장소 연결

3. **서비스 설정**
   ```
   Name: shopping-app-backend (또는 원하는 이름)
   Region: Singapore (또는 가장 가까운 지역)
   Branch: main
   Root Directory: (비워두기 - 루트에 있으면)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

### 3단계: 환경변수 설정 (Render 대시보드)

Render 대시보드 → Environment 탭에서 다음 환경변수들을 설정:

#### 데이터베이스 설정
```
DB_HOST=your-render-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=shopping_app
```

#### JWT 설정
```
SECRET_KEY=your-random-secret-key-here-change-in-production
```

#### 카카오 로그인
```
KAKAO_CLIENT_ID=your-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=https://your-app.onrender.com/oauth/kakao/callback
```

#### 구글 로그인
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app.onrender.com/oauth/google/callback
```

#### 네이버 로그인
```
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
NAVER_REDIRECT_URI=https://your-app.onrender.com/oauth/naver/callback
```

#### Gmail SMTP
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=your-gmail@gmail.com
```

#### 앱 URL
```
APP_URL=https://your-app.onrender.com
```

### 4단계: 데이터베이스 설정

1. **Render에서 PostgreSQL 생성**
   - "New +" → "PostgreSQL" 클릭
   - 데이터베이스 생성
   - **주의**: 현재 코드는 MySQL을 사용하므로, PostgreSQL을 사용하려면 코드 수정 필요
   - 또는 Render에서 MySQL을 사용할 수 있는 다른 서비스 사용

2. **데이터베이스 초기화**
   - Render의 PostgreSQL에 연결하여 `Dump20251114.sql` 실행
   - 또는 Render의 MySQL 서비스 사용

### 5단계: 소셜 로그인 리다이렉트 URI 업데이트

각 소셜 로그인 플랫폼의 개발자 콘솔에서:
- 카카오: https://developers.kakao.com/
- 구글: https://console.cloud.google.com/
- 네이버: https://developers.naver.com/

**리다이렉트 URI를 Render URL로 변경:**
```
https://your-app.onrender.com/oauth/kakao/callback
https://your-app.onrender.com/oauth/google/callback
https://your-app.onrender.com/oauth/naver/callback
```

---

## ⚠️ 중요 사항

### 1. 데이터베이스 연결 설정 변경 필요

현재 `api_server.py`의 `DB_CONFIG`가 하드코딩되어 있습니다.
환경변수를 사용하도록 수정해야 합니다:

```python
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'shopping_app'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

### 2. 포트 설정

Render는 `$PORT` 환경변수를 제공하므로, `api_server.py`의 `start_server` 함수를 수정하거나
Start Command에서 `--port $PORT`를 사용해야 합니다.

### 3. CORS 설정

프로덕션 환경에서는 `allow_origins=["*"]` 대신 프론트엔드 도메인만 허용하도록 변경:

```python
allow_origins=[
    "https://your-frontend-domain.com",
    "http://localhost:3000"  # 개발 환경용
]
```

### 4. 정적 파일 (uploaded_images)

Render는 임시 파일 시스템을 사용하므로, 업로드된 이미지는:
- AWS S3 같은 외부 스토리지 사용 권장
- 또는 Render의 디스크 볼륨 사용 (유료 플랜)

---

## 📝 체크리스트

배포 전 확인사항:

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있음
- [ ] 모든 환경변수가 Render에 설정됨
- [ ] 데이터베이스 연결 설정이 환경변수 사용하도록 수정됨
- [ ] 소셜 로그인 리다이렉트 URI가 Render URL로 업데이트됨
- [ ] CORS 설정이 프로덕션 환경에 맞게 수정됨
- [ ] `requirements.txt`에 모든 필요한 패키지가 포함됨
- [ ] 데이터베이스 스키마가 초기화됨

---

## 🔍 배포 후 확인

1. **서버 상태 확인**
   ```
   https://your-app.onrender.com/health
   ```

2. **API 문서 확인**
   ```
   https://your-app.onrender.com/docs
   ```

3. **소셜 로그인 테스트**
   - 각 소셜 로그인 플랫폼에서 로그인 테스트
   - 리다이렉트 URI가 올바르게 작동하는지 확인

---

## 🆘 문제 해결

### 서버가 시작되지 않는 경우
- Render 로그 확인: Dashboard → Logs
- 환경변수가 올바르게 설정되었는지 확인
- `requirements.txt`의 패키지 버전 확인

### 데이터베이스 연결 실패
- DB_HOST, DB_USER, DB_PASSWORD 환경변수 확인
- 데이터베이스가 생성되고 실행 중인지 확인
- 방화벽 설정 확인 (Render는 자동으로 처리)

### 소셜 로그인 실패
- 리다이렉트 URI가 Render URL과 정확히 일치하는지 확인
- CLIENT_ID, CLIENT_SECRET이 올바른지 확인
- 각 플랫폼의 개발자 콘솔에서 앱 상태 확인

