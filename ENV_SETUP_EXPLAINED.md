# 환경변수 설정 방법 설명

## 🤔 왜 `.env` 파일을 업로드하지 않나요?

### `.env` 파일의 역할

`.env` 파일은 **로컬 개발 환경**에서만 사용하는 설정 파일입니다.

```
로컬 개발 환경 (내 컴퓨터)
├── .env 파일 사용 ✅
└── 실제 값들이 들어있음 (비밀번호, API 키 등)
```

```
배포 환경 (Render 클라우드)
├── .env 파일 사용 ❌ (업로드 안 함)
└── Render 대시보드에서 환경변수 직접 설정 ✅
```

---

## 📍 환경변수 설정 방법

### 1️⃣ 로컬 개발 환경 (내 컴퓨터)

**방법: `.env` 파일 사용**

1. `env_example.txt` 파일을 복사해서 `.env` 파일 생성
   ```bash
   cp env_example.txt .env
   ```

2. `.env` 파일을 열어서 실제 값 입력
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=root
   DB_NAME=shopping_app
   SECRET_KEY=my-secret-key-123
   KAKAO_CLIENT_ID=실제_카카오_키
   # ... 등등
   ```

3. 코드에서 자동으로 읽어옴
   ```python
   # api_server.py에서
   load_dotenv(os.path.join(BASE_DIR, ".env"))  # .env 파일 읽기
   DB_CONFIG = {
       'host': os.getenv('DB_HOST', 'localhost'),  # .env에서 값 가져오기
       # ...
   }
   ```

---

### 2️⃣ 배포 환경 (Render 클라우드)

**방법: Render 대시보드에서 직접 설정**

`.env` 파일을 업로드하지 않고, Render 웹사이트에서 직접 환경변수를 설정합니다.

#### Render에서 환경변수 설정하는 방법:

1. **Render 대시보드 접속**
   - https://dashboard.render.com
   - 생성한 Web Service 클릭

2. **Environment 탭 클릭**
   ```
   Dashboard
   ├── Your Service
   │   ├── Settings
   │   ├── Environment  ← 여기 클릭!
   │   ├── Logs
   │   └── ...
   ```

3. **환경변수 추가**
   - "Add Environment Variable" 버튼 클릭
   - Key와 Value 입력
   - 저장

   예시:
   ```
   Key: DB_HOST
   Value: your-render-db-host.render.com
   
   Key: DB_USER
   Value: your-db-user
   
   Key: DB_PASSWORD
   Value: your-secure-password
   
   Key: SECRET_KEY
   Value: your-random-secret-key-here
   
   ... (나머지도 동일하게 추가)
   ```

4. **코드에서 자동으로 읽어옴**
   ```python
   # api_server.py에서
   # Render에 설정한 환경변수를 자동으로 읽어옴
   DB_CONFIG = {
       'host': os.getenv('DB_HOST'),  # Render 환경변수에서 가져옴
       'user': os.getenv('DB_USER'),
       'password': os.getenv('DB_PASSWORD'),
       # ...
   }
   ```

---

## 🔄 전체 흐름 비교

### 로컬 개발 환경

```
1. .env 파일 생성 (로컬에만 존재)
   ↓
2. .env 파일에 실제 값 입력
   ↓
3. 코드 실행 시 .env 파일 읽기
   load_dotenv(".env")
   ↓
4. 환경변수 사용
   os.getenv('DB_HOST') → localhost
```

### 배포 환경 (Render)

```
1. GitHub에 코드 업로드 (.env 제외)
   ↓
2. Render에서 Web Service 생성
   ↓
3. Render 대시보드에서 환경변수 설정
   (웹사이트에서 직접 입력)
   ↓
4. 코드 실행 시 Render 환경변수 읽기
   os.getenv('DB_HOST') → render-db-host
   (load_dotenv는 .env가 없어도 괜찮음)
```

---

## ⚠️ 중요한 차이점

### `.env` 파일 (로컬용)
- ✅ 내 컴퓨터에만 존재
- ✅ GitHub에 업로드하지 않음 (보안)
- ✅ `env_example.txt`를 복사해서 사용

### Render 환경변수 (배포용)
- ✅ Render 웹사이트에서 설정
- ✅ 코드와 분리되어 안전함
- ✅ `env_example.txt`를 참고해서 설정

---

## 📝 실제 예시

### 로컬에서 개발할 때

```bash
# 1. .env 파일 생성
cp env_example.txt .env

# 2. .env 파일 편집 (텍스트 에디터로)
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=root
# ...

# 3. 서버 실행
python api_server.py
# → .env 파일에서 설정값 읽어옴
```

### Render에 배포할 때

```bash
# 1. GitHub에 코드 업로드 (.env 제외)
git add .
git commit -m "Deploy"
git push origin main

# 2. Render 대시보드에서:
#    - Web Service 생성
#    - Environment 탭 클릭
#    - 환경변수 추가:
#      * DB_HOST = your-db-host
#      * DB_USER = your-user
#      * DB_PASSWORD = your-password
#      * ... (env_example.txt 참고)

# 3. Render가 자동으로 배포
# → Render 환경변수에서 설정값 읽어옴
```

---

## 🎯 요약

| 환경 | 설정 방법 | 파일 위치 |
|------|----------|----------|
| **로컬 개발** | `.env` 파일 사용 | 내 컴퓨터 (GitHub 업로드 ❌) |
| **Render 배포** | Render 대시보드에서 설정 | Render 클라우드 (웹사이트) |

**결론**: `.env` 파일은 로컬에서만 사용하고, Render에서는 웹사이트에서 직접 환경변수를 설정합니다!

