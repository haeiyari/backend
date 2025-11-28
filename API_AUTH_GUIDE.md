# 인증 및 사용자 관리 API 가이드

## 📋 목차

1. [소셜 로그인 (카카오/구글)](#1-소셜-로그인)
2. [로그아웃](#2-로그아웃)
3. [비밀번호 재설정](#3-비밀번호-재설정)
4. [회원 탈퇴](#4-회원-탈퇴)
5. [상품 검색](#5-상품-검색)

---

## 1. 소셜 로그인

### 1-1. 카카오 로그인

#### 사전 준비
1. [카카오 개발자 센터](https://developers.kakao.com/) 접속
2. 애플리케이션 생성
3. REST API 키 발급
4. 리다이렉트 URI 설정

#### API 엔드포인트
```
POST /auth/social-login
```

#### 요청 예시
```json
{
  "code": "카카오에서_받은_인가_코드",
  "redirect_uri": "http://localhost:8000/callback",
  "provider": "kakao"
}
```

#### 응답 예시
```json
{
  "success": true,
  "user": {
    "user_id": 1,
    "name": "홍길동",
    "email": "user@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "소셜 로그인 성공"
}
```

#### 프론트엔드 구현 예시 (JavaScript)
```javascript
// 1. 카카오 로그인 버튼 클릭 시
function loginWithKakao() {
    const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code`;
    window.location.href = kakaoAuthUrl;
}

// 2. 리다이렉트 후 인가 코드 처리
async function handleKakaoCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    const response = await fetch('http://localhost:8000/auth/social-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            redirect_uri: REDIRECT_URI,
            provider: 'kakao'
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // 토큰 저장
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // 메인 페이지로 이동
        window.location.href = '/';
    }
}
```

### 1-2. 구글 로그인

#### 사전 준비
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성
3. OAuth 2.0 클라이언트 ID 발급
4. 승인된 리디렉션 URI 추가

#### API 엔드포인트
```
POST /auth/social-login
```

#### 요청 예시
```json
{
  "code": "구글에서_받은_인가_코드",
  "redirect_uri": "http://localhost:8000/callback",
  "provider": "google"
}
```

---

## 2. 로그아웃

### API 엔드포인트
```
POST /auth/logout
```

### 요청 헤더
```
Authorization: Bearer {access_token}
```

### 응답 예시
```json
{
  "success": true,
  "message": "로그아웃되었습니다."
}
```

### 프론트엔드 구현 예시
```javascript
async function logout() {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/auth/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    
    if (data.success) {
        // 로컬 스토리지 정리
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        
        // 로그인 페이지로 이동
        window.location.href = '/login';
    }
}
```

---

## 3. 비밀번호 재설정

### 3-1. 재설정 요청 (이메일 발송)

#### API 엔드포인트
```
POST /auth/password-reset/request
```

#### 요청 예시
```json
{
  "email": "user@example.com"
}
```

#### 응답 예시
```json
{
  "success": true,
  "message": "비밀번호 재설정 링크가 이메일로 발송되었습니다."
}
```

### 3-2. 비밀번호 변경 확정

#### API 엔드포인트
```
POST /auth/password-reset/confirm
```

#### 요청 예시
```json
{
  "token": "이메일에서_받은_토큰",
  "new_password": "new_password123"
}
```

#### 응답 예시
```json
{
  "success": true,
  "message": "비밀번호가 성공적으로 변경되었습니다."
}
```

### 프론트엔드 구현 예시
```javascript
// 1. 비밀번호 재설정 요청
async function requestPasswordReset(email) {
    const response = await fetch('http://localhost:8000/auth/password-reset/request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    });
    
    const data = await response.json();
    alert(data.message);
}

// 2. 비밀번호 변경
async function confirmPasswordReset(token, newPassword) {
    const response = await fetch('http://localhost:8000/auth/password-reset/confirm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            new_password: newPassword
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        alert('비밀번호가 변경되었습니다. 다시 로그인해주세요.');
        window.location.href = '/login';
    }
}
```

---

## 4. 회원 탈퇴

### API 엔드포인트
```
DELETE /auth/withdraw/{user_id}
```

### 요청 헤더
```
Authorization: Bearer {access_token}
```

### 응답 예시
```json
{
  "success": true,
  "message": "회원 탈퇴가 완료되었습니다."
}
```

### 프론트엔드 구현 예시
```javascript
async function withdrawUser(userId) {
    if (!confirm('정말로 탈퇴하시겠습니까? 모든 데이터가 삭제됩니다.')) {
        return;
    }
    
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`http://localhost:8000/auth/withdraw/${userId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    const data = await response.json();
    
    if (data.success) {
        // 로컬 스토리지 정리
        localStorage.clear();
        
        alert('회원 탈퇴가 완료되었습니다.');
        window.location.href = '/';
    }
}
```

---

## 5. 상품 검색

### API 엔드포인트
```
GET /products/search
```

### 쿼리 파라미터
- `keyword` (필수): 검색 키워드
- `category` (선택): 카테고리 필터
- `min_price` (선택): 최소 가격
- `max_price` (선택): 최대 가격
- `limit` (선택): 결과 개수 (기본값: 20)

### 요청 예시
```
GET /products/search?keyword=티셔츠&category=상의&min_price=10000&max_price=50000&limit=10
```

### 응답 예시
```json
{
  "success": true,
  "keyword": "티셔츠",
  "count": 3,
  "products": [
    {
      "product_id": 1,
      "name": "기본 면 티셔츠",
      "description": "편안한 착용감의 기본 면 티셔츠",
      "category": "상의",
      "price": 15000,
      "stock": 100,
      "image_url": "/images/tshirt1.jpg",
      "created_at": "2025-01-01T00:00:00"
    }
  ]
}
```

### 프론트엔드 구현 예시
```javascript
async function searchProducts(keyword, filters = {}) {
    const params = new URLSearchParams({
        keyword: keyword,
        ...filters
    });
    
    const response = await fetch(`http://localhost:8000/products/search?${params}`);
    const data = await response.json();
    
    if (data.success) {
        displayProducts(data.products);
    }
}

function displayProducts(products) {
    const container = document.getElementById('product-list');
    container.innerHTML = '';
    
    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'product-item';
        item.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <p class="price">${product.price.toLocaleString()}원</p>
        `;
        container.appendChild(item);
    });
}
```

---

## 🔐 환경변수 설정

`env_example.txt` 파일을 `.env`로 복사하고 실제 값을 입력하세요:

```bash
# 카카오 로그인
KAKAO_CLIENT_ID=your-kakao-rest-api-key

# 구글 로그인
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# SendGrid 이메일
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourapp.com

# JWT 시크릿 키
SECRET_KEY=your-secret-key-here

# 앱 URL
APP_URL=http://localhost:8000
```

---

## 📦 패키지 설치

```bash
pip install -r requirements.txt
```

---

## 🗄️ 데이터베이스 업데이트

```bash
mysql -u root -p shopping_app < database_update.sql
```

---

## 🚀 서버 실행

```bash
python api_server.py
```

---

## ⚠️ 주의사항

1. **보안**: 프로덕션 환경에서는 반드시 HTTPS 사용
2. **토큰 관리**: 실제 운영에서는 Redis 등을 사용한 토큰 블랙리스트 관리 권장
3. **이메일 발송**: SendGrid API 키가 없으면 콘솔에 링크만 출력됨
4. **소셜 로그인**: 각 플랫폼에서 앱 등록 및 키 발급 필요

---

## 📞 문의

문제가 발생하면 로그를 확인하거나 API 문서를 참조하세요:
- API 문서: http://localhost:8000/docs

