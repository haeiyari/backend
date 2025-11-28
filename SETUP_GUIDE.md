# 내 옷장 기능 설정 가이드

## 📋 개요

사용자가 의류를 측정한 후, 결과를 **내 옷장**에 저장하고 나중에 확인할 수 있는 기능이 추가되었습니다.

## 🗄️ 데이터베이스 설정

### 1. MySQL 데이터베이스 준비

`Dump20251114.sql` 파일이 이미 제공되어 있으며, 다음 테이블들이 포함되어 있습니다:
- `users`: 사용자 정보
- `user_measure_profile`: 사용자별 측정 프로필 (내 옷장 데이터)

### 2. 데이터베이스 import

```bash
# MySQL에 로그인
mysql -u root -p

# 데이터베이스 생성 (이미 있다면 생략)
CREATE DATABASE shopping_app;

# SQL 파일 import
mysql -u root -p shopping_app < Dump20251114.sql
```

### 3. api_server.py의 DB 설정 수정

`api_server.py` 파일의 45-53번째 줄에서 DB 연결 정보를 수정하세요:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # ← 본인의 MySQL 사용자명
    'password': '',  # ← 본인의 MySQL 비밀번호
    'database': 'shopping_app',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

## 📦 Python 패키지 설치

```bash
# 프로젝트 디렉토리로 이동
cd project/my-app

# 필수 패키지 설치 (mysql-connector-python 포함)
pip install -r requirements.txt
```

## 🚀 서버 실행

```bash
# API 서버 실행
python api_server.py
```

서버가 실행되면 다음 주소에서 접근할 수 있습니다:
- 메인 페이지: http://localhost:8000/
- API 문서: http://localhost:8000/docs
- 내 옷장: http://localhost:8000/my_closet.html

## 📂 주요 파일 및 기능

### 1. **demo_with_keypoints.html** (측정 페이지)
- 의류 이미지를 업로드하고 치수를 측정
- 측정 완료 후 **"내 옷장에 저장하기"** 섹션이 자동으로 표시됨
- 의류 이름과 사용자 ID를 입력하고 저장

### 2. **my_closet.html** (내 옷장 페이지)
- 사용자 ID를 입력하면 저장된 모든 의류 목록 조회
- 각 의류의 이미지, 이름, 측정값, 저장일 표시
- 카드 형태로 깔끔하게 정리

### 3. **index.html** (시작 페이지)
- "시작하기" 버튼: 측정 페이지로 이동
- **"내 옷장 보기 👔" 버튼**: 내 옷장 페이지로 바로 이동

### 4. **api_server.py** (백엔드 API)

#### 새로 추가된 API 엔드포인트:

##### POST `/save-to-closet`
- 측정 결과를 DB에 저장
- 요청 파라미터:
  - `user_id`: 사용자 ID
  - `profile_name`: 의류 이름 (예: "내 최애 후드티")
  - `category`: "상의" 또는 "하의"
  - `measurements`: JSON 형식의 측정값
  - `image`: 의류 이미지 파일 (선택사항)

##### GET `/my-closet/{user_id}`
- 특정 사용자의 옷장 목록 조회
- 응답: 사용자의 모든 측정 프로필 리스트

## 🔄 전체 흐름

```
1. 사용자가 의류를 촬영/업로드
   ↓
2. demo_with_keypoints.html에서 측정 진행
   ↓
3. 측정 완료 후 "내 옷장에 저장" 섹션이 나타남
   ↓
4. 의류 이름 입력 + 저장 버튼 클릭
   ↓
5. API 서버가 DB에 저장 (user_measure_profile 테이블)
   ↓
6. my_closet.html에서 저장된 목록 확인
```

## 📊 데이터베이스 스키마

### user_measure_profile 테이블

| 필드 | 타입 | 설명 |
|------|------|------|
| profile_id | INT | 자동 증가 PK |
| user_id | INT | 사용자 ID (FK) |
| profile_name | VARCHAR(100) | 의류 이름 |
| profile_image_url | VARCHAR(255) | 이미지 경로 |
| category | VARCHAR(50) | "상의" 또는 "하의" |
| top_length | DECIMAL(5,1) | 상의 총장 |
| top_shoulder | DECIMAL(5,1) | 상의 어깨 너비 |
| top_chest | DECIMAL(5,1) | 상의 가슴 너비 |
| top_sleeve | DECIMAL(5,1) | 상의 소매 길이 |
| bottom_length | DECIMAL(5,1) | 하의 총장 |
| bottom_waist | DECIMAL(5,1) | 하의 허리 단면 |
| bottom_rise | DECIMAL(5,1) | 하의 밑위 |
| bottom_hip | DECIMAL(5,1) | 하의 엉덩이 단면 |
| bottom_thigh | DECIMAL(5,1) | 하의 허벅지 단면 |
| bottom_hem | DECIMAL(5,1) | 하의 밑단 단면 |
| created_at | DATETIME | 저장 일시 |

## 🧪 테스트 방법

### 1. 기존 테스트 데이터 확인

DB에 이미 3개의 샘플 데이터가 들어있습니다:
- user_id 3: "내 최애 후드티 (L)", "자주 입는 청바지 (30)"
- user_id 4: "딱 맞는 반팔티 (M)"

```bash
# my_closet.html에서 user_id 3 입력 → 2개 항목 확인
# my_closet.html에서 user_id 4 입력 → 1개 항목 확인
```

### 2. 새로운 측정 결과 저장

1. `demo_with_keypoints.html`에서 의류 측정 진행
2. 측정 완료 후 나타나는 "내 옷장에 저장" 폼에서:
   - 의류 이름: "내가 좋아하는 셔츠"
   - 사용자 ID: 3
3. "내 옷장에 저장" 버튼 클릭
4. `my_closet.html`에서 user_id 3으로 조회 → 새 항목 추가 확인

## ⚠️ 주의사항

1. **MySQL 비밀번호 설정**: `api_server.py`의 `DB_CONFIG`에서 본인의 MySQL 비밀번호를 입력하세요.

2. **이미지 저장 디렉토리**: 서버 실행 시 자동으로 `uploaded_images` 폴더가 생성됩니다.

3. **User ID**: 현재는 임시로 수동 입력하지만, 추후 로그인 시스템과 연동할 예정입니다.

4. **이미지 URL**: 저장된 이미지는 `/uploaded_images/user_{user_id}_{timestamp}.jpg` 형식으로 저장됩니다.

## 🐛 문제 해결

### DB 연결 오류
```
데이터베이스 연결 실패: Access denied for user 'root'@'localhost'
```
→ `api_server.py`의 `DB_CONFIG`에서 MySQL 비밀번호 확인

### 패키지 import 오류
```
Import "mysql.connector" could not be resolved
```
→ `pip install mysql-connector-python`

### 이미지가 표시되지 않음
→ 서버가 `uploaded_images` 폴더를 정적 파일로 서빙하는지 확인
→ `api_server.py` 44번째 줄 확인: `app.mount("/uploaded_images", ...)`

## 📝 향후 개선 사항

- [ ] 로그인 시스템 연동 (user_id 자동 설정)
- [ ] 측정 프로필 삭제/수정 기능
- [ ] 측정 프로필 상세 보기 모달
- [ ] 프로필별 메모/태그 기능
- [ ] 이미지 썸네일 최적화
- [ ] 측정값 기반 상품 추천 기능

