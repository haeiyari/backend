# 소셜 로그인 API 연동 가이드

이 문서는 프론트엔드 개발자가 백엔드의 소셜 로그인 API를 연동하는 방법을 설명합니다.

---

## 📋 목차

1. [지원하는 소셜 로그인](#지원하는-소셜-로그인)
2. [API 엔드포인트](#api-엔드포인트)
3. [연동 흐름](#연동-흐름)
4. [코드 예제](#코드-예제)
5. [에러 처리](#에러-처리)

---

## 지원하는 소셜 로그인

- **카카오 (Kakao)**
- **구글 (Google)**
- **네이버 (Naver)**

---

## API 엔드포인트

### 기본 URL
```
로컬: http://localhost:8000
배포: https://backend-z01u.onrender.com
```

### 1. 로그인 URL 생성 API

각 소셜 로그인 제공자의 인증 URL을 생성합니다.

#### 카카오 로그인 URL
```http
GET /auth/kakao/login-url
```

**응답 예시:**
```json
{
  "login_url": "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code"
}
```

#### 구글 로그인 URL
```http
GET /auth/google/login-url
```

**응답 예시:**
```json
{
  "login_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&response_type=code&scope=..."
}
```

#### 네이버 로그인 URL
```http
GET /auth/naver/login-url
```

**응답 예시:**
```json
{
  "login_url": "https://nid.naver.com/oauth2.0/authorize?client_id=...&redirect_uri=...&response_type=code&state=..."
}
```

---

### 2. 소셜 로그인 처리 API

소셜 로그인 제공자로부터 받은 인증 코드로 로그인/회원가입을 처리합니다.

```http
POST /auth/social-login
Content-Type: application/json
```

**요청 본문:**
```json
{
  "provider": "kakao",  // "kakao", "google", "naver" 중 하나
  "code": "인증_코드",
  "redirect_uri": "http://localhost:3000/callback"  // 선택사항
}
```

**성공 응답 (200):**
```json
{
  "success": true,
  "message": "로그인 성공",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 123,
    "email": "user@example.com",
    "name": "홍길동",
    "social_provider": "kakao",
    "social_id": "1234567890"
  }
}
```

**실패 응답 (400/500):**
```json
{
  "detail": "카카오 토큰 발급 실패: invalid_grant"
}
```

---

## 연동 흐름

### 전체 프로세스

```
1. 사용자가 "카카오 로그인" 버튼 클릭
   ↓
2. 프론트엔드: GET /auth/kakao/login-url 호출
   ↓
3. 백엔드: 카카오 로그인 URL 반환
   ↓
4. 프론트엔드: 해당 URL로 리다이렉트 (새 창 또는 현재 창)
   ↓
5. 사용자: 카카오 로그인 페이지에서 로그인
   ↓
6. 카카오: redirect_uri로 리다이렉트 (code 포함)
   ↓
7. 프론트엔드: URL에서 code 추출
   ↓
8. 프론트엔드: POST /auth/social-login 호출 (code 전달)
   ↓
9. 백엔드: 토큰 발급 및 사용자 정보 반환
   ↓
10. 프론트엔드: access_token 저장 및 로그인 완료
```

---

## 코드 예제

### React 예제

#### 1. 소셜 로그인 버튼 컴포넌트

```jsx
import React, { useState } from 'react';
import axios from 'axios';

// 개발 환경에 따라 변경
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://backend-z01u.onrender.com';

function SocialLogin() {
  const [loading, setLoading] = useState(false);

  // 카카오 로그인 시작
  const handleKakaoLogin = async () => {
    try {
      setLoading(true);
      
      // 1. 로그인 URL 가져오기
      const response = await axios.get(`${API_BASE_URL}/auth/kakao/login-url`);
      const loginUrl = response.data.login_url;
      
      // 2. 카카오 로그인 페이지로 이동
      window.location.href = loginUrl;
      
    } catch (error) {
      console.error('카카오 로그인 URL 생성 실패:', error);
      alert('로그인 URL 생성에 실패했습니다.');
      setLoading(false);
    }
  };

  // 구글 로그인 시작
  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/auth/google/login-url`);
      window.location.href = response.data.login_url;
    } catch (error) {
      console.error('구글 로그인 URL 생성 실패:', error);
      alert('로그인 URL 생성에 실패했습니다.');
      setLoading(false);
    }
  };

  // 네이버 로그인 시작
  const handleNaverLogin = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/auth/naver/login-url`);
      window.location.href = response.data.login_url;
    } catch (error) {
      console.error('네이버 로그인 URL 생성 실패:', error);
      alert('로그인 URL 생성에 실패했습니다.');
      setLoading(false);
    }
  };

  return (
    <div className="social-login-container">
      <h2>소셜 로그인</h2>
      
      <button 
        onClick={handleKakaoLogin} 
        disabled={loading}
        style={{ backgroundColor: '#FEE500', color: '#000' }}
      >
        카카오 로그인
      </button>
      
      <button 
        onClick={handleGoogleLogin} 
        disabled={loading}
        style={{ backgroundColor: '#4285F4', color: '#fff' }}
      >
        구글 로그인
      </button>
      
      <button 
        onClick={handleNaverLogin} 
        disabled={loading}
        style={{ backgroundColor: '#03C75A', color: '#fff' }}
      >
        네이버 로그인
      </button>
    </div>
  );
}

export default SocialLogin;
```

#### 2. 콜백 페이지 컴포넌트

```jsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

// 개발 환경에 따라 변경
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://backend-z01u.onrender.com';

function SocialLoginCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState(null);

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    try {
      // URL에서 code와 state 파라미터 추출
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const state = params.get('state');
      
      if (!code) {
        throw new Error('인증 코드가 없습니다.');
      }

      // provider 판별 (state 또는 localStorage에서)
      let provider = localStorage.getItem('social_login_provider');
      
      // 네이버의 경우 state로 판별 가능
      if (state && state.includes('naver')) {
        provider = 'naver';
      }

      if (!provider) {
        throw new Error('소셜 로그인 제공자를 확인할 수 없습니다.');
      }

      // 백엔드에 인증 코드 전달
      const response = await axios.post(`${API_BASE_URL}/auth/social-login`, {
        provider: provider,
        code: code,
        redirect_uri: window.location.origin + '/callback'
      });

      const { access_token, user } = response.data;

      // 토큰 저장
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.removeItem('social_login_provider');

      // 메인 페이지로 이동
      alert(`${user.name}님, 환영합니다!`);
      navigate('/');

    } catch (error) {
      console.error('소셜 로그인 처리 실패:', error);
      setError(error.response?.data?.detail || error.message);
      
      // 3초 후 로그인 페이지로 이동
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    }
  };

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h2>로그인 실패</h2>
        <p style={{ color: 'red' }}>{error}</p>
        <p>잠시 후 로그인 페이지로 이동합니다...</p>
      </div>
    );
  }

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h2>로그인 처리 중...</h2>
      <p>잠시만 기다려주세요.</p>
    </div>
  );
}

export default SocialLoginCallback;
```

#### 3. 개선된 버전 (provider 자동 저장)

```jsx
// SocialLogin.jsx (개선)
const handleKakaoLogin = async () => {
  try {
    setLoading(true);
    localStorage.setItem('social_login_provider', 'kakao');
    const response = await axios.get(`${API_BASE_URL}/auth/kakao/login-url`);
    window.location.href = response.data.login_url;
  } catch (error) {
    console.error('카카오 로그인 실패:', error);
    localStorage.removeItem('social_login_provider');
    setLoading(false);
  }
};

const handleGoogleLogin = async () => {
  try {
    setLoading(true);
    localStorage.setItem('social_login_provider', 'google');
    const response = await axios.get(`${API_BASE_URL}/auth/google/login-url`);
    window.location.href = response.data.login_url;
  } catch (error) {
    console.error('구글 로그인 실패:', error);
    localStorage.removeItem('social_login_provider');
    setLoading(false);
  }
};

const handleNaverLogin = async () => {
  try {
    setLoading(true);
    localStorage.setItem('social_login_provider', 'naver');
    const response = await axios.get(`${API_BASE_URL}/auth/naver/login-url`);
    window.location.href = response.data.login_url;
  } catch (error) {
    console.error('네이버 로그인 실패:', error);
    localStorage.removeItem('social_login_provider');
    setLoading(false);
  }
};
```

---

### Vanilla JavaScript 예제

#### HTML
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>소셜 로그인</title>
    <style>
        .social-btn {
            padding: 15px 30px;
            margin: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .kakao { background: #FEE500; color: #000; }
        .google { background: #4285F4; color: #fff; }
        .naver { background: #03C75A; color: #fff; }
    </style>
</head>
<body>
    <div style="text-align: center; padding: 50px;">
        <h1>소셜 로그인</h1>
        <button class="social-btn kakao" onclick="loginKakao()">카카오 로그인</button>
        <button class="social-btn google" onclick="loginGoogle()">구글 로그인</button>
        <button class="social-btn naver" onclick="loginNaver()">네이버 로그인</button>
    </div>

    <script src="social-login.js"></script>
</body>
</html>
```

#### JavaScript (social-login.js)
```javascript
// 개발 환경에 따라 변경
const API_BASE_URL = 'https://backend-z01u.onrender.com';

// 카카오 로그인
async function loginKakao() {
    try {
        localStorage.setItem('social_login_provider', 'kakao');
        const response = await fetch(`${API_BASE_URL}/auth/kakao/login-url`);
        const data = await response.json();
        window.location.href = data.login_url;
    } catch (error) {
        console.error('카카오 로그인 실패:', error);
        alert('로그인에 실패했습니다.');
    }
}

// 구글 로그인
async function loginGoogle() {
    try {
        localStorage.setItem('social_login_provider', 'google');
        const response = await fetch(`${API_BASE_URL}/auth/google/login-url`);
        const data = await response.json();
        window.location.href = data.login_url;
    } catch (error) {
        console.error('구글 로그인 실패:', error);
        alert('로그인에 실패했습니다.');
    }
}

// 네이버 로그인
async function loginNaver() {
    try {
        localStorage.setItem('social_login_provider', 'naver');
        const response = await fetch(`${API_BASE_URL}/auth/naver/login-url`);
        const data = await response.json();
        window.location.href = data.login_url;
    } catch (error) {
        console.error('네이버 로그인 실패:', error);
        alert('로그인에 실패했습니다.');
    }
}
```

#### 콜백 페이지 (callback.html)
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>로그인 처리 중...</title>
</head>
<body>
    <div style="text-align: center; padding: 50px;">
        <h2>로그인 처리 중...</h2>
        <p id="status">잠시만 기다려주세요.</p>
    </div>

    <script>
        // 개발 환경에 따라 변경
        const API_BASE_URL = 'https://backend-z01u.onrender.com';

        async function handleCallback() {
            try {
                // URL에서 code 추출
                const urlParams = new URLSearchParams(window.location.search);
                const code = urlParams.get('code');
                const state = urlParams.get('state');

                if (!code) {
                    throw new Error('인증 코드가 없습니다.');
                }

                // provider 확인
                let provider = localStorage.getItem('social_login_provider');
                if (state && state.includes('naver')) {
                    provider = 'naver';
                }

                if (!provider) {
                    throw new Error('소셜 로그인 제공자를 확인할 수 없습니다.');
                }

                // 백엔드에 인증 코드 전달
                const response = await fetch(`${API_BASE_URL}/auth/social-login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        provider: provider,
                        code: code,
                        redirect_uri: window.location.origin + '/callback.html'
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || '로그인 실패');
                }

                const data = await response.json();
                
                // 토큰 저장
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.removeItem('social_login_provider');

                // 성공 메시지
                document.getElementById('status').innerHTML = 
                    `<span style="color: green;">${data.user.name}님, 환영합니다!</span><br>메인 페이지로 이동합니다...`;

                // 메인 페이지로 이동
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);

            } catch (error) {
                console.error('로그인 처리 실패:', error);
                document.getElementById('status').innerHTML = 
                    `<span style="color: red;">로그인 실패: ${error.message}</span><br>로그인 페이지로 이동합니다...`;
                
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 3000);
            }
        }

        // 페이지 로드 시 실행
        handleCallback();
    </script>
</body>
</html>
```

---

## 에러 처리

### 주요 에러 코드

| HTTP 코드 | 설명 | 해결 방법 |
|-----------|------|-----------|
| 400 | 잘못된 요청 (code 누락, provider 오류 등) | 요청 파라미터 확인 |
| 401 | 인증 실패 (토큰 발급 실패) | 새로운 code로 재시도 |
| 500 | 서버 오류 | 서버 로그 확인 또는 관리자 문의 |

### 에러 메시지 예시

```json
{
  "detail": "카카오 토큰 발급 실패: invalid_grant"
}
```

```json
{
  "detail": "구글 사용자 정보 조회 실패"
}
```

```json
{
  "detail": "provider는 'kakao', 'google', 'naver' 중 하나여야 합니다."
}
```

### 에러 처리 예제

```javascript
try {
  const response = await axios.post(`${API_BASE_URL}/auth/social-login`, {
    provider: 'kakao',
    code: code
  });
  
  // 성공 처리
  const { access_token, user } = response.data;
  localStorage.setItem('access_token', access_token);
  
} catch (error) {
  if (error.response) {
    // 서버가 응답을 반환한 경우
    const status = error.response.status;
    const message = error.response.data.detail;
    
    if (status === 400) {
      alert('잘못된 요청입니다: ' + message);
    } else if (status === 401) {
      alert('인증에 실패했습니다. 다시 시도해주세요.');
      // 로그인 페이지로 리다이렉트
      window.location.href = '/login';
    } else if (status === 500) {
      alert('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
  } else if (error.request) {
    // 요청은 보냈지만 응답을 받지 못한 경우
    alert('서버에 연결할 수 없습니다. 네트워크를 확인해주세요.');
  } else {
    // 요청 설정 중 오류가 발생한 경우
    alert('오류가 발생했습니다: ' + error.message);
  }
}
```

---

## 중요 사항

### 1. Redirect URI 설정

각 소셜 로그인 제공자의 개발자 콘솔에서 Redirect URI를 등록해야 합니다.

**현재 배포된 백엔드 주소:**
- **Render URL**: https://backend-z01u.onrender.com

**로컬 개발:**
```
http://localhost:3000/callback
http://localhost:8000/oauth/kakao/callback
http://localhost:8000/oauth/google/callback
http://localhost:8000/oauth/naver/callback
```

**배포 환경:**
```
https://your-frontend.com/callback
https://backend-z01u.onrender.com/oauth/kakao/callback
https://backend-z01u.onrender.com/oauth/google/callback
https://backend-z01u.onrender.com/oauth/naver/callback
```

### 2. CORS 설정

백엔드에서 프론트엔드 도메인을 CORS에 허용해야 합니다.

```python
# api_server.py에 이미 설정되어 있음
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 특정 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 토큰 저장 및 사용

로그인 성공 후 받은 `access_token`을 저장하고, 이후 API 요청 시 헤더에 포함시킵니다.

```javascript
// 토큰 저장
localStorage.setItem('access_token', access_token);

// API 요청 시 사용
const response = await axios.get(`${API_BASE_URL}/api/user/profile`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### 4. 보안 고려사항

- **access_token은 localStorage보다 httpOnly 쿠키 사용 권장** (XSS 공격 방지)
- **HTTPS 사용 필수** (배포 환경)
- **code는 1회용이므로 재사용 불가**
- **state 파라미터 검증** (CSRF 공격 방지)

---

## 테스트 방법

### 1. Swagger UI에서 테스트

**로컬:**
```
http://localhost:8000/docs
```

**배포 환경:**
```
https://backend-z01u.onrender.com/docs
```

1. `GET /auth/kakao/login-url` 실행
2. 반환된 `login_url`을 브라우저에 복사
3. 카카오 로그인 후 리다이렉트된 URL에서 `code` 추출
4. `POST /auth/social-login`에 `provider`와 `code` 입력하여 실행

### 2. 프론트엔드에서 테스트

1. 로그인 버튼 클릭
2. 소셜 로그인 페이지에서 로그인
3. 콜백 페이지로 리다이렉트
4. 개발자 도구 콘솔에서 토큰 확인
5. localStorage에 토큰 저장 확인

---

## 문의

API 연동 중 문제가 발생하면 다음을 확인하세요:

1. **백엔드 서버 실행 여부** (`python api_server.py`)
2. **환경변수 설정 확인** (`.env` 파일)
3. **Redirect URI 일치 여부** (콘솔 설정 vs 코드)
4. **네트워크 요청 로그** (개발자 도구 Network 탭)
5. **백엔드 로그** (터미널 출력)

추가 지원이 필요하면 백엔드 개발자에게 문의하세요.

