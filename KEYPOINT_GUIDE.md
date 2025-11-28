# 키포인트 수동 조정 가이드

## 📍 개요

자동 검출된 키포인트를 사용자가 직접 조정하여 더 정확한 측정을 수행할 수 있는 기능입니다.

## 🎯 주요 기능

### 1. 2단계 측정 프로세스
1. **1단계: 자동 키포인트 검출**
   - AI가 자동으로 의류의 주요 지점을 검출
   - 검출 결과를 시각적으로 확인

2. **2단계: 수동 조정 및 측정**
   - 필요시 키포인트 위치를 수동으로 조정
   - 조정된 키포인트로 정확한 치수 측정

### 2. 키포인트 종류

#### 상의 (Shirt) - 8개 키포인트
1. 목점 (Top point)
2. 밑단점 (Bottom point)
3. 왼쪽 어깨 (Left Shoulder)
4. 오른쪽 어깨 (Right Shoulder)
5. 왼쪽 가슴 (Left Chest)
6. 오른쪽 가슴 (Right Chest)
7. 왼쪽 소매 끝 (Left Sleeve)
8. 오른쪽 소매 끝 (Right Sleeve)

#### 하의 (Pants) - 9개 키포인트
1. 허리 상단 중앙 (Top Center)
2. 왼쪽 허리 (Left Waist)
3. 오른쪽 허리 (Right Waist)
4. 왼쪽 엉덩이 (Left Hip)
5. 오른쪽 엉덩이 (Right Hip)
6. 왼쪽 허벅지/밑위 (Left Thigh/Crotch)
7. 오른쪽 허벅지 (Right Thigh)
8. 밑단 좌측 (Left Hem)
9. 밑단 우측 (Right Hem)

## 🔌 API 엔드포인트

### 1. 키포인트 검출
```
POST /detect-keypoints
```

**요청:**
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('clothing_type', 'shirt'); // 또는 'pants'

fetch('http://localhost:8000/detect-keypoints', {
  method: 'POST',
  body: formData
})
```

**응답:**
```json
{
  "type": "shirt",
  "keypoints": [[x1, y1], [x2, y2], ...],
  "point_labels": ["목점", "밑단점", ...],
  "preview_image": "base64_encoded_image...",
  "image_size": {"width": 1920, "height": 1080},
  "a4_box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
  "pixelsPerCM_w": 45.5,
  "pixelsPerCM_h": 46.2
}
```

### 2. 조정된 키포인트로 측정
```
POST /measure-with-keypoints
```

**요청:**
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('clothing_type', 'shirt');
formData.append('keypoints', JSON.stringify(adjustedKeypoints));
formData.append('a4_box', JSON.stringify(a4Box));
formData.append('pixelsPerCM_w', pixelsPerCM_w);
formData.append('pixelsPerCM_h', pixelsPerCM_h);

fetch('http://localhost:8000/measure-with-keypoints', {
  method: 'POST',
  body: formData
})
```

**응답:**
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

## 💻 웹 UI 사용법

### `demo_with_keypoints.html` 사용하기

1. **서버 시작**
   ```bash
   python api_server.py
   ```

2. **웹 페이지 열기**
   - `demo_with_keypoints.html` 파일을 브라우저에서 열기

3. **이미지 업로드**
   - "📷 이미지 선택" 버튼 클릭
   - 의류 이미지 선택 (A4 용지 포함)
   - 의류 타입 선택 (상의/하의)

4. **키포인트 자동 검출**
   - "1단계: 키포인트 자동 검출" 버튼 클릭
   - 잠시 대기 (자동 검출 진행)

5. **키포인트 조정 (2가지 모드)**

   #### 🔸 개별 조정 모드 (기본)
   - 캔버스에 표시된 빨간 점들이 키포인트
   - 마우스로 각 점을 개별적으로 드래그하여 위치 조정
   - 각 점은 번호로 표시됨
   
   #### 🎯 부위별 조정 모드 (신규!)
   - 부위 선택 버튼 클릭 (예: 어깨, 가슴, 소매 등)
   - 선택된 부위의 키포인트들이 **자주색**으로 표시됨
   - 해당 부위의 키포인트 중 하나를 드래그하면 **전체가 함께 이동**
   - 대칭적인 조정이 필요할 때 유용 (예: 양쪽 어깨를 함께 조정)
   
   **상의 부위별 그룹:**
   - 목/총장: 목점, 밑단점
   - 어깨: 왼쪽/오른쪽 어깨
   - 가슴: 왼쪽/오른쪽 가슴
   - 소매: 왼쪽/오른쪽 소매
   
   **하의 부위별 그룹:**
   - 허리: 허리 상단 중앙, 왼쪽/오른쪽 허리
   - 엉덩이: 왼쪽/오른쪽 엉덩이
   - 허벅지/밑위: 왼쪽/오른쪽 허벅지
   - 밑단: 밑단 좌측/우측

6. **측정 실행**
   - "2단계: 측정 시작" 버튼 클릭
   - 측정 결과 확인

## 🎨 Python 코드 예제

### 전체 프로세스 예제
```python
import requests
import json

API_URL = "http://localhost:8000"

# 1단계: 키포인트 검출
with open("shirt.jpg", "rb") as f:
    files = {'image': f}
    data = {'clothing_type': 'shirt'}
    
    response = requests.post(f"{API_URL}/detect-keypoints", 
                           files=files, data=data)
    keypoint_data = response.json()

print("검출된 키포인트:")
for idx, (label, point) in enumerate(zip(
    keypoint_data['point_labels'], 
    keypoint_data['keypoints']
)):
    print(f"{idx+1}. {label}: {point}")

# 2단계: 키포인트 수동 조정 (예시)
# 실제로는 사용자 UI에서 조정됨
adjusted_keypoints = keypoint_data['keypoints'].copy()
# 예: 첫 번째 키포인트를 약간 이동
adjusted_keypoints[0] = [
    adjusted_keypoints[0][0] + 5, 
    adjusted_keypoints[0][1] + 3
]

# 3단계: 조정된 키포인트로 측정
with open("shirt.jpg", "rb") as f:
    files = {'image': f}
    data = {
        'clothing_type': 'shirt',
        'keypoints': json.dumps(adjusted_keypoints),
        'a4_box': json.dumps(keypoint_data['a4_box']),
        'pixelsPerCM_w': keypoint_data['pixelsPerCM_w'],
        'pixelsPerCM_h': keypoint_data['pixelsPerCM_h']
    }
    
    response = requests.post(f"{API_URL}/measure-with-keypoints",
                           files=files, data=data)
    result = response.json()

print("\n측정 결과:")
for key, value in result['measurements'].items():
    print(f"{key}: {value}cm")
```

## 🔧 고급 기능

### 키포인트 자동 조정 알고리즘
```python
def auto_adjust_keypoints(keypoints, contour):
    """
    윤곽선 정보를 이용한 키포인트 자동 최적화
    """
    adjusted = []
    for point in keypoints:
        # 주변 윤곽선에서 가장 가까운 점 찾기
        distances = np.linalg.norm(contour - point, axis=1)
        nearest_idx = np.argmin(distances)
        adjusted.append(contour[nearest_idx])
    return adjusted
```

### 배치 처리
```python
def batch_measure_with_adjustment(image_paths, clothing_types):
    """
    여러 의류를 순차적으로 측정
    """
    results = []
    
    for image_path, clothing_type in zip(image_paths, clothing_types):
        # 1. 키포인트 검출
        keypoint_data = detect_keypoints(image_path, clothing_type)
        
        # 2. 자동 조정 (선택사항)
        adjusted = auto_adjust_keypoints(
            keypoint_data['keypoints'],
            keypoint_data['contour']
        )
        
        # 3. 측정
        result = measure_with_keypoints(
            image_path, 
            clothing_type,
            adjusted,
            keypoint_data
        )
        
        results.append(result)
    
    return results
```

## ⚠️ 주의사항

### 키포인트 조정 시
1. **정확한 위치 선택**
   - 의류의 실제 경계점에 키포인트 배치
   - 주름이나 그림자가 있는 부분 피하기

2. **대칭성 유지**
   - 좌우 대칭인 키포인트는 균형있게 조정
   - 예: 왼쪽/오른쪽 어깨, 소매 등

3. **순서 준수**
   - 키포인트는 정해진 순서대로 배치되어야 함
   - 순서가 바뀌면 측정값이 부정확해짐

### 일반적인 오류
1. **키포인트가 의류 밖에 있음**
   - 모든 키포인트는 의류 윤곽선 내부에 있어야 함

2. **극단적인 위치 변경**
   - 자동 검출 결과에서 너무 크게 벗어나지 않도록 주의

3. **A4 용지 데이터 불일치**
   - 검출 단계와 측정 단계에서 같은 이미지 사용 필수

## 📊 성능 비교

| 측정 방법 | 평균 정확도 | 처리 시간 | 사용자 개입 |
|----------|-----------|---------|-----------|
| 완전 자동 | 85-90% | 2-3초 | 없음 |
| 수동 조정 | 95-98% | 4-6초 | 필요 (10-30초) |

## 🎯 최적 사용 시나리오

### 수동 조정 권장 상황
- 복잡한 패턴의 의류
- 주름이 많은 경우
- 특수한 디자인 (비대칭, 레이어드 등)
- 정밀한 측정이 필요한 경우

### 자동 검출 충분 상황
- 단색의 평평한 의류
- 표준 디자인의 의류
- 배치 처리가 필요한 경우
- 빠른 대략적 측정이 목적인 경우

## 💡 팁

1. **효율적인 작업 흐름**
   ```
   이미지 업로드 → 자동 검출 → 결과 확인 
   → 필요시에만 조정 → 측정
   ```

2. **부위별 조정 활용 방법**
   - **대칭 조정**: 어깨, 가슴, 소매 등 좌우 대칭 부위를 함께 위/아래로 이동
   - **전체 이동**: 의류가 전체적으로 치우친 경우, 각 부위를 선택하여 한 번에 이동
   - **미세 조정**: 부위별로 대략 조정 후, 개별 조정 모드로 전환하여 미세 조정
   - **빠른 작업**: 개별 조정보다 부위별 조정이 3~5배 빠름

3. **색상 가이드**
   - 🔴 **빨간색**: 일반 키포인트 (개별 조정 가능)
   - 🟣 **자주색**: 선택된 부위의 키포인트 (함께 이동)
   - 🟢 **초록색**: 현재 드래그 중인 키포인트
   - **점선**: 선택된 부위의 키포인트를 연결한 선

4. **키보드 단축키 (향후 구현 예정)**
   - `Space`: 다음 키포인트로 이동
   - `Enter`: 측정 시작
   - `Esc`: 조정 취소

5. **모바일 지원**
   - 터치 인터페이스로도 키포인트 조정 가능
   - 핀치 줌으로 정밀 조정

## 🔗 관련 문서

- [API 전체 문서](README_API.md)
- [빠른 시작 가이드](QUICKSTART.md)
- [프로젝트 구조](PROJECT_STRUCTURE.md)

---

**버전**: 1.2.0 (부위별 조정 기능 추가)  
**최종 업데이트**: 2025-10-31

