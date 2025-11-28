# 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1단계: 패키지 설치
```bash
cd project/my-app
pip install -r requirements.txt
```

### 2단계: 서버 시작
**Windows:**
```bash
.\start_server.bat
```

**Linux/Mac:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**또는 직접 실행:**
```bash
python api_server.py

##ngrok
ngrok http 8000
```

### 3단계: API 테스트

#### 방법 1: 웹 브라우저에서 테스트
1. 브라우저에서 http://localhost:8000/docs 접속
2. `/measure` 엔드포인트 클릭
3. "Try it out" 버튼 클릭
4. 이미지 업로드 및 clothing_type 선택
5. "Execute" 버튼 클릭

#### 방법 2: 테스트 클라이언트 사용
```bash
# 상의 측정
python test_client.py shirt_image.jpg shirt

# 하의 측정
python test_client.py pants_image.jpg pants
```

#### 방법 3: cURL 사용
```bash
curl -X POST "http://localhost:8000/measure" \
  -F "image=@your_image.jpg" \
  -F "clothing_type=shirt"
```

## 📸 이미지 준비 팁

### ✅ 좋은 예시
- A4 용지가 이미지에 완전히 보임
- 의류가 평평하게 펼쳐짐
- 배경이 단색 (흰색, 회색 등)
- 조명이 고르게 비춤
- 카메라가 정면에서 수직으로 촬영

### ❌ 나쁜 예시
- A4 용지가 잘림
- 의류가 구겨짐
- 복잡한 배경 (무늬, 다른 물체)
- 그림자가 많음
- 각도가 기울어짐

## 📊 응답 예시

### 상의 (shirt) 측정 결과
```json
{
  "type": "shirt",
  "measurements": {
    "length": 72.5,      // 총장 (cm)
    "shoulder": 48.3,    // 어깨 너비 (cm)
    "chest": 56.8,       // 가슴 너비 (cm)
    "sleeve": 24.2       // 소매 길이 (cm)
  },
  "unit": "cm",
  "result_image": "base64_encoded_string..."
}
```

### 하의 (pants) 측정 결과
```json
{
  "type": "pants",
  "measurements": {
    "length": 98.5,      // 총장 (cm)
    "waist": 42.3,       // 허리 단면 (cm)
    "hip": 54.2,         // 엉덩이 단면 (cm)
    "crotch": 32.8,      // 밑위 (cm)
    "thigh": 31.5,       // 허벅지 단면 (cm)
    "hem": 22.1          // 밑단 단면 (cm)
  },
  "unit": "cm",
  "result_image": "base64_encoded_string..."
}
```

## 🔧 문제 해결

### 서버가 시작되지 않음
```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# 패키지 재설치
pip install --upgrade -r requirements.txt
```

### "A4 용지를 찾을 수 없습니다" 오류
- A4 용지가 이미지에 완전히 보이는지 확인
- 조명을 밝게 하여 A4 용지가 잘 보이도록 촬영
- A4 용지와 배경의 대비를 높임

### "옷 윤곽선을 찾을 수 없습니다" 오류
- 배경을 단색으로 변경
- 의류를 평평하게 펼침
- 조명 개선

### 측정값이 부정확함
- 카메라를 정면에서 수직으로 촬영
- A4 용지와 의류가 같은 평면에 있도록 배치
- 의류의 주름을 펴서 촬영

## 🌐 프론트엔드 연동 예시

### HTML + JavaScript
```html
<!DOCTYPE html>
<html>
<head>
    <title>의류 치수 측정</title>
</head>
<body>
    <h1>의류 치수 측정</h1>
    <input type="file" id="imageInput" accept="image/*">
    <select id="typeSelect">
        <option value="shirt">상의</option>
        <option value="pants">하의</option>
    </select>
    <button onclick="measure()">측정하기</button>
    <div id="result"></div>

    <script>
        async function measure() {
            const file = document.getElementById('imageInput').files[0];
            const type = document.getElementById('typeSelect').value;
            
            const formData = new FormData();
            formData.append('image', file);
            formData.append('clothing_type', type);

            const response = await fetch('http://localhost:8000/measure', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            document.getElementById('result').innerHTML = 
                JSON.stringify(data.measurements, null, 2);
        }
    </script>
</body>
</html>
```

## 📚 더 많은 정보

- 상세 문서: [README_API.md](README_API.md)
- API 문서: http://localhost:8000/docs
- 측정 항목: http://localhost:8000/supported-measurements

## ❓ 자주 묻는 질문

**Q: A4 용지 대신 다른 크기를 사용할 수 있나요?**  
A: 현재는 A4 용지만 지원합니다. 다른 크기를 사용하려면 코드 수정이 필요합니다.

**Q: 여러 의류를 한 번에 측정할 수 있나요?**  
A: `/measure/batch` 엔드포인트를 사용하면 가능합니다.

**Q: 결과 이미지는 어디에 저장되나요?**  
A: 결과 이미지는 base64 인코딩되어 응답에 포함됩니다. 클라이언트에서 디코딩하여 사용하세요.

**Q: API 인증이 필요한가요?**  
A: 현재 버전은 인증이 없습니다. 운영 환경에서는 인증 추가를 권장합니다.

