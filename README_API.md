# 의류 치수 측정 API

A4 용지를 기준으로 의류 치수를 자동으로 측정하는 REST API 서비스입니다.

## 📋 목차
- [기능 소개](#기능-소개)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [API 엔드포인트](#api-엔드포인트)
- [예제 코드](#예제-코드)
- [측정 가능한 항목](#측정-가능한-항목)

## 🎯 기능 소개

### 상의 (Shirt) 측정
- **총장**: 목에서 밑단까지의 길이
- **어깨 너비**: 양쪽 어깨 끝점 사이의 거리
- **가슴 너비**: 가슴 가장 넓은 부분의 단면
- **소매 길이**: 어깨 끝에서 소매 끝까지의 길이

### 하의 (Pants) 측정
- **총장**: 허리에서 밑단까지의 길이
- **허리 단면**: 허리 가장 좁은 부분의 단면
- **엉덩이 단면**: 엉덩이 가장 넓은 부분의 단면
- **밑위**: 허리에서 허벅지 분기점까지의 길이
- **허벅지 단면**: 허벅지 가장 넓은 부분의 단면
- **밑단 단면**: 바지 밑단 부분의 단면

## 🚀 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- pip

### 2. 패키지 설치
```bash
# 프로젝트 디렉토리로 이동
cd project/my-app

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
# 개발 모드로 실행 (자동 재시작 활성화)
python api_server.py

# 또는 직접 uvicorn으로 실행
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

서버가 시작되면 다음 주소로 접근할 수 있습니다:
- **API 서버**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc

## 📖 사용 방법

### 촬영 가이드

1. **A4 용지 배치**
   - 흰색 A4 용지를 의류 옆에 배치합니다
   - A4 용지가 이미지에 완전히 보이도록 합니다

2. **의류 준비**
   - 의류를 평평하게 펼칩니다
   - 주름을 최대한 펴줍니다
   - 배경은 단색이 좋습니다

3. **촬영**
   - 의류와 A4 용지가 모두 보이도록 촬영합니다
   - 카메라는 정면에서 수직으로 촬영합니다
   - 조명이 고르게 비추도록 합니다

## 🔌 API 엔드포인트

### 1. 루트 엔드포인트
```
GET /
```
API 기본 정보를 반환합니다.

**응답 예시:**
```json
{
  "message": "의류 치수 측정 API에 오신 것을 환영합니다!",
  "version": "1.0.0",
  "endpoints": {
    "POST /measure": "의류 치수 측정",
    "GET /health": "서버 상태 확인"
  }
}
```

### 2. 상태 확인
```
GET /health
```
서버 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "service": "measurement-api",
  "version": "1.0.0"
}
```

### 3. 치수 측정 (단일)
```
POST /measure
```

**요청 파라미터:**
- `image` (file, required): 측정할 의류 이미지 파일
- `clothing_type` (string, required): 의류 타입 (`shirt` 또는 `pants`)
- `a4_box` (string, optional): 수동으로 지정한 A4 용지 박스 좌표 (JSON 배열)

**A4 수동 선택 기능:**
- A4 용지 자동 검출 실패 시, 응답에 `need_manual_a4: true`가 포함됩니다
- 사용자가 이미지에서 A4 용지의 4개 꼭짓점을 선택한 후, `a4_box` 파라미터에 좌표를 전달하여 재요청합니다
- 좌표 형식: `[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]` (좌상단, 우상단, 우하단, 좌하단 순)

**응답 예시 (상의):**
```json
{
  "type": "shirt",
  "measurements": {
    "length": 72.5,
    "shoulder": 48.3,
    "chest": 56.8,
    "sleeve": 24.2
  },
  "result_image": "base64_encoded_image_string...",
  "unit": "cm"
}
```

**응답 예시 (하의):**
```json
{
  "type": "pants",
  "measurements": {
    "length": 98.5,
    "waist": 42.3,
    "hip": 54.2,
    "crotch": 32.8,
    "thigh": 31.5,
    "hem": 22.1
  },
  "result_image": "base64_encoded_image_string...",
  "unit": "cm"
}
```

### 4. 배치 측정 (여러 개)
```
POST /measure/batch
```

**요청 파라미터:**
- `images` (files, required): 측정할 여러 이미지 파일
- `clothing_types` (string, required): 각 이미지의 의류 타입 (쉼표로 구분, 예: "shirt,pants,shirt")

**응답 예시:**
```json
{
  "results": [
    {
      "index": 0,
      "filename": "shirt1.jpg",
      "result": {
        "type": "shirt",
        "measurements": {...}
      }
    },
    {
      "index": 1,
      "filename": "pants1.jpg",
      "result": {
        "type": "pants",
        "measurements": {...}
      }
    }
  ],
  "total": 2
}
```

### 5. 키포인트 자동 검출 (신규! ⭐)
```
POST /detect-keypoints
```

**설명:**
자동으로 키포인트를 검출한 후, 사용자가 수동으로 조정할 수 있도록 키포인트 정보와 미리보기 이미지를 반환합니다.

**주요 기능:**
- **개별 조정**: 각 키포인트를 개별적으로 드래그하여 위치 조정
- **부위별 조정** (신규!): 부위를 선택하면 해당 부위의 모든 키포인트가 함께 이동
  - 상의: 목/총장, 어깨, 가슴, 소매
  - 하의: 허리, 엉덩이, 허벅지/밑위, 밑단

**요청 파라미터:**
- `image` (file, required): 측정할 의류 이미지 파일
- `clothing_type` (string, required): 의류 타입 (`shirt` 또는 `pants`)
- `a4_box` (string, optional): 수동으로 지정한 A4 용지 박스 좌표 (JSON 배열)

**A4 수동 선택 기능:**
- A4 용지 자동 검출 실패 시, 응답에 `need_manual_a4: true`와 함께 이미지가 반환됩니다
- 사용자가 4개 꼭짓점을 선택한 후, `a4_box` 파라미터와 함께 재요청하면 키포인트가 검출됩니다

**응답 예시 (성공):**
```json
{
  "type": "shirt",
  "keypoints": [[450, 120], [450, 680], ...],
  "point_labels": ["목점", "밑단점", "왼쪽 어깨", ...],
  "preview_image": "base64_encoded_image...",
  "image_size": {"width": 1920, "height": 1080},
  "a4_box": [[100, 100], [500, 100], [500, 800], [100, 800]],
  "pixelsPerCM_w": 45.5,
  "pixelsPerCM_h": 46.2
}
```

**응답 예시 (A4 자동 검출 실패):**
```json
{
  "error": "A4 용지를 찾을 수 없습니다.",
  "need_manual_a4": true,
  "preview_image": "base64_encoded_image...",
  "image_size": {"width": 1920, "height": 1080}
}
```

### 6. 조정된 키포인트로 측정 (신규! ⭐)
```
POST /measure-with-keypoints
```

**요청 파라미터:**
- `image` (file, required): 측정할 의류 이미지 파일
- `clothing_type` (string, required): 의류 타입
- `keypoints` (string, required): 조정된 키포인트 좌표 (JSON 배열 문자열)
- `a4_box` (string, required): A4 용지 박스 좌표 (JSON 배열 문자열)
- `pixelsPerCM_w` (float, required): 가로 픽셀/cm 비율
- `pixelsPerCM_h` (float, required): 세로 픽셀/cm 비율

**응답 예시:**
```json
{
  "type": "shirt",
  "measurements": {
    "length": 72.5,
    "shoulder": 48.3,
    "chest": 56.8,
    "sleeve": 24.2
  },
  "result_image": "base64_encoded_image...",
  "unit": "cm"
}
```

### 7. 지원 항목 조회
```
GET /supported-measurements
```
측정 가능한 항목 목록을 반환합니다.

## 💻 예제 코드

### 키포인트 조정 기능 (신규!)

#### 기본 사용법 (A4 자동 검출 성공 시)
```python
import requests
import json

# 1단계: 키포인트 자동 검출
with open("shirt.jpg", "rb") as f:
    files = {"image": f}
    data = {"clothing_type": "shirt"}
    
    response = requests.post("http://localhost:8000/detect-keypoints", 
                           files=files, data=data)
    keypoint_data = response.json()

# A4 수동 선택이 필요한 경우 처리
if keypoint_data.get("need_manual_a4"):
    print("A4 용지를 수동으로 선택해야 합니다.")
    print(f"이미지 크기: {keypoint_data['image_size']}")
    # 사용자로부터 4개 꼭짓점 좌표 입력받기
    a4_box = [[100, 100], [500, 100], [500, 800], [100, 800]]  # 예시
    
    # A4 박스와 함께 재요청
    with open("shirt.jpg", "rb") as f:
        files = {"image": f}
        data = {
            "clothing_type": "shirt",
            "a4_box": json.dumps(a4_box)
        }
        response = requests.post("http://localhost:8000/detect-keypoints",
                               files=files, data=data)
        keypoint_data = response.json()

print("검출된 키포인트:")
for idx, (label, point) in enumerate(zip(
    keypoint_data['point_labels'], 
    keypoint_data['keypoints']
)):
    print(f"{idx+1}. {label}: {point}")

# 2단계: 키포인트 수동 조정 (필요시)
adjusted_keypoints = keypoint_data['keypoints'].copy()
# 예: 첫 번째 키포인트를 약간 이동
adjusted_keypoints[0] = [
    adjusted_keypoints[0][0] + 5, 
    adjusted_keypoints[0][1] + 3
]

# 3단계: 조정된 키포인트로 측정
with open("shirt.jpg", "rb") as f:
    files = {"image": f}
    data = {
        "clothing_type": "shirt",
        "keypoints": json.dumps(adjusted_keypoints),
        "a4_box": json.dumps(keypoint_data['a4_box']),
        "pixelsPerCM_w": keypoint_data['pixelsPerCM_w'],
        "pixelsPerCM_h": keypoint_data['pixelsPerCM_h']
    }
    
    response = requests.post("http://localhost:8000/measure-with-keypoints",
                           files=files, data=data)
    result = response.json()

print("측정 결과:", result['measurements'])
```

### Python (requests)

#### 기본 측정 (A4 자동 검출)
```python
import requests
import json

# 서버 URL
url = "http://localhost:8000/measure"

# 이미지 파일과 의류 타입 전송
with open("shirt_with_a4.jpg", "rb") as image_file:
    files = {"image": image_file}
    data = {"clothing_type": "shirt"}
    
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    # A4 수동 선택이 필요한 경우
    if result.get("need_manual_a4"):
        print("A4 용지를 수동으로 선택해야 합니다.")
        # 사용자로부터 4개 꼭짓점 좌표 입력받기
        a4_box = [[100, 100], [500, 100], [500, 800], [100, 800]]  # 예시
        
        # A4 박스와 함께 재요청
        with open("shirt_with_a4.jpg", "rb") as image_file:
            files = {"image": image_file}
            data = {
                "clothing_type": "shirt",
                "a4_box": json.dumps(a4_box)
            }
            response = requests.post(url, files=files, data=data)
            result = response.json()
    
    print("측정 결과:")
    print(f"총장: {result['measurements']['length']}cm")
    print(f"어깨: {result['measurements']['shoulder']}cm")
    print(f"가슴: {result['measurements']['chest']}cm")
    print(f"소매: {result['measurements']['sleeve']}cm")
```

### cURL
```bash
# 상의 측정
curl -X POST "http://localhost:8000/measure" \
  -F "image=@shirt_with_a4.jpg" \
  -F "clothing_type=shirt"

# 하의 측정
curl -X POST "http://localhost:8000/measure" \
  -F "image=@pants_with_a4.jpg" \
  -F "clothing_type=pants"
```

### JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('clothing_type', 'shirt');

fetch('http://localhost:8000/measure', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('측정 결과:', data.measurements);
  // 결과 이미지 표시
  const img = document.createElement('img');
  img.src = `data:image/jpeg;base64,${data.result_image}`;
  document.body.appendChild(img);
})
.catch(error => console.error('오류:', error));
```

### React 예제
```jsx
import React, { useState } from 'react';

function MeasurementUpload() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);
    formData.append('clothing_type', 'shirt');

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/measure', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('측정 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleUpload} accept="image/*" />
      {loading && <p>측정 중...</p>}
      {result && (
        <div>
          <h3>측정 결과</h3>
          <ul>
            {Object.entries(result.measurements).map(([key, value]) => (
              <li key={key}>{key}: {value}cm</li>
            ))}
          </ul>
          <img 
            src={`data:image/jpeg;base64,${result.result_image}`} 
            alt="측정 결과"
            style={{maxWidth: '100%'}}
          />
        </div>
      )}
    </div>
  );
}
```

## 📊 측정 가능한 항목

### 상의 (shirt)
| 항목 | 키 | 설명 |
|------|-----|------|
| 총장 | `length` | 목 중앙에서 밑단까지 |
| 어깨 너비 | `shoulder` | 양쪽 어깨 끝점 사이 |
| 가슴 너비 | `chest` | 가슴 가장 넓은 부분 단면 |
| 소매 길이 | `sleeve` | 어깨 끝에서 소매 끝까지 |

### 하의 (pants)
| 항목 | 키 | 설명 |
|------|-----|------|
| 총장 | `length` | 허리 상단에서 밑단까지 |
| 허리 단면 | `waist` | 허리 가장 좁은 부분 |
| 엉덩이 단면 | `hip` | 엉덩이 가장 넓은 부분 |
| 밑위 | `crotch` | 허리에서 다리 분기점까지 |
| 허벅지 단면 | `thigh` | 허벅지 가장 넓은 부분 |
| 밑단 단면 | `hem` | 바지 밑단 부분 |

## 🔧 고급 설정

### 환경 변수
서버 동작을 커스터마이징하려면 환경 변수를 설정할 수 있습니다:

```bash
# 포트 변경
export API_PORT=9000

# 호스트 변경
export API_HOST=127.0.0.1

# 서버 실행
python api_server.py
```

### Docker 배포
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# OpenCV 의존성 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py"]
```

빌드 및 실행:
```bash
docker build -t measurement-api .
docker run -p 8000:8000 measurement-api
```

## 📝 에러 처리

### 일반적인 오류

1. **A4 용지를 찾을 수 없음**
   ```json
   {
     "error": "A4 용지를 찾을 수 없습니다."
   }
   ```
   **해결방법**: A4 용지가 이미지에 명확하게 보이는지 확인하세요.

2. **옷 윤곽선을 찾을 수 없음**
   ```json
   {
     "error": "옷 윤곽선을 찾을 수 없습니다."
   }
   ```
   **해결방법**: 배경과 의류의 대비를 높이거나 조명을 개선하세요.

3. **지원하지 않는 의류 타입**
   ```json
   {
     "error": "지원하지 않는 의류 타입입니다. 'shirt' 또는 'pants'를 사용하세요."
   }
   ```
   **해결방법**: clothing_type을 'shirt' 또는 'pants'로 설정하세요.

## 🤝 기여 방법

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙋 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.

---

**버전**: 1.0.0  
**최종 업데이트**: 2025-10-31

