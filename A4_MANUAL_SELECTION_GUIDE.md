# A4 용지 수동 선택 가이드

## 📌 개요

의류 치수 측정 API는 A4 용지를 자동으로 검출하여 치수를 계산합니다. 그러나 다음과 같은 경우 자동 검출이 실패할 수 있습니다:

- 조명이 불균일한 경우
- A4 용지가 구겨지거나 그림자가 있는 경우
- 배경과 A4 용지의 대비가 낮은 경우
- A4 용지가 부분적으로 가려진 경우

이런 경우, 사용자가 수동으로 A4 용지의 4개 꼭짓점을 지정할 수 있습니다.

## 🎯 작동 방식

### 1단계: 자동 검출 시도
API 호출 시 먼저 A4 용지 자동 검출을 시도합니다.

### 2단계: 검출 실패 시 응답
자동 검출이 실패하면 다음과 같은 응답을 받습니다:

```json
{
  "error": "A4 용지를 찾을 수 없습니다.",
  "need_manual_a4": true,
  "preview_image": "base64_encoded_image...",
  "image_size": {"width": 1920, "height": 1080}
}
```

### 3단계: 사용자가 4개 꼭짓점 선택
사용자는 이미지에서 A4 용지의 4개 꼭짓점을 다음 순서로 선택합니다:

1. **좌측 상단** (왼쪽 위 모서리)
2. **우측 상단** (오른쪽 위 모서리)
3. **우측 하단** (오른쪽 아래 모서리)
4. **좌측 하단** (왼쪽 아래 모서리)

### 4단계: A4 박스와 함께 재요청
선택한 좌표를 `a4_box` 파라미터에 포함하여 API를 다시 호출합니다.

## 💻 사용 예제

### Python 예제

```python
import requests
import json

# 1단계: 초기 요청
with open("shirt.jpg", "rb") as f:
    files = {"image": f}
    data = {"clothing_type": "shirt"}
    
    response = requests.post("http://localhost:8000/detect-keypoints", 
                           files=files, data=data)
    result = response.json()

# 2단계: A4 수동 선택이 필요한지 확인
if result.get("need_manual_a4"):
    print("A4 용지를 수동으로 선택해야 합니다.")
    print(f"이미지 크기: {result['image_size']}")
    
    # 사용자로부터 좌표 입력받기 (예시)
    # 실제로는 GUI에서 클릭으로 입력받음
    a4_box = [
        [150, 200],  # 좌측 상단
        [550, 200],  # 우측 상단
        [550, 900],  # 우측 하단
        [150, 900]   # 좌측 하단
    ]
    
    # 3단계: A4 박스와 함께 재요청
    with open("shirt.jpg", "rb") as f:
        files = {"image": f}
        data = {
            "clothing_type": "shirt",
            "a4_box": json.dumps(a4_box)
        }
        
        response = requests.post("http://localhost:8000/detect-keypoints",
                               files=files, data=data)
        result = response.json()

# 4단계: 키포인트 사용
print("검출된 키포인트:", result['keypoints'])
```

### JavaScript 예제

```javascript
// 1단계: 초기 요청
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('clothing_type', 'shirt');

const response = await fetch('http://localhost:8000/detect-keypoints', {
    method: 'POST',
    body: formData
});

const result = await response.json();

// 2단계: A4 수동 선택이 필요한지 확인
if (result.need_manual_a4) {
    console.log('A4 용지를 수동으로 선택해야 합니다.');
    
    // 사용자가 캔버스에서 4개 점을 클릭하여 좌표 수집
    const a4Points = await collectA4Points(result.preview_image);
    
    // 3단계: A4 박스와 함께 재요청
    const retryFormData = new FormData();
    retryFormData.append('image', fileInput.files[0]);
    retryFormData.append('clothing_type', 'shirt');
    retryFormData.append('a4_box', JSON.stringify(a4Points));
    
    const retryResponse = await fetch('http://localhost:8000/detect-keypoints', {
        method: 'POST',
        body: retryFormData
    });
    
    const retryResult = await retryResponse.json();
    console.log('키포인트:', retryResult.keypoints);
}
```

## 🖼️ 웹 UI에서 사용하기

### 데모 페이지
프로젝트에는 A4 수동 선택과 키포인트 조정을 지원하는 데모 페이지가 포함되어 있습니다:

- **demo_with_keypoints.html**: 키포인트 조정 기능 + A4 수동 선택 (권장)

### 주요 구현 사항

1. **캔버스 표시**: A4 검출 실패 시 이미지를 캔버스에 표시
2. **클릭 이벤트**: 사용자가 4개 점을 순서대로 클릭
3. **시각적 피드백**: 선택된 점을 원으로 표시하고 선으로 연결
4. **재요청**: 4개 점이 모두 선택되면 자동으로 API 재요청

## ⚠️ 주의사항

### 좌표 순서
A4 박스 좌표는 **반드시 시계방향**으로 입력해야 합니다:
1. 좌측 상단 → 2. 우측 상단 → 3. 우측 하단 → 4. 좌측 하단

잘못된 순서로 입력하면 측정 결과가 부정확할 수 있습니다.

### 좌표 단위
- 좌표는 **픽셀 단위**입니다
- 원본 이미지 크기 기준입니다 (캔버스 크기가 아님)
- 캔버스를 사용하는 경우 스케일 변환이 필요합니다

### JSON 형식
API 요청 시 `a4_box` 파라미터는 **JSON 문자열** 형태로 전달해야 합니다:

```python
# Python
data = {
    "a4_box": json.dumps([[100, 100], [500, 100], [500, 800], [100, 800]])
}
```

```javascript
// JavaScript
formData.append('a4_box', JSON.stringify([[100, 100], [500, 100], [500, 800], [100, 800]]));
```

## 🔧 API 엔드포인트

A4 수동 선택 기능은 다음 엔드포인트에서 사용할 수 있습니다:

### 1. `/measure`
기본 측정 엔드포인트
```bash
POST /measure
- image: 이미지 파일
- clothing_type: 'shirt' 또는 'pants'
- a4_box: (선택사항) A4 박스 좌표 JSON 문자열
```

### 2. `/detect-keypoints`
키포인트 검출 엔드포인트
```bash
POST /detect-keypoints
- image: 이미지 파일
- clothing_type: 'shirt' 또는 'pants'
- a4_box: (선택사항) A4 박스 좌표 JSON 문자열
```

## 📝 FAQ

### Q: A4 자동 검출 성공률을 높이려면?
**A:** 
- 밝고 균일한 조명 사용
- A4 용지를 평평하게 펴기
- 단색 배경 사용
- A4 용지가 이미지에 완전히 보이도록 촬영

### Q: 수동 선택 시 정확도가 떨어지는 경우?
**A:**
- A4 용지의 정확한 모서리 점을 클릭
- 확대하여 더 정확하게 선택
- 순서를 정확히 지키기 (좌상 → 우상 → 우하 → 좌하)

### Q: 수동 선택을 기본으로 사용할 수 있나요?
**A:**
네, 초기 요청 시부터 `a4_box` 파라미터를 포함하면 자동 검출을 건너뛰고 수동 좌표를 바로 사용합니다.

## 🎉 마무리

A4 수동 선택 기능을 사용하면 자동 검출이 어려운 환경에서도 정확한 치수 측정이 가능합니다. 
웹 데모를 통해 직접 체험해보세요!

**웹 데모 실행:**
```bash
cd project/my-app
python api_server.py
# 브라우저에서 demo_with_keypoints.html 열기
```

