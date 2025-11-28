# GitHub 업로드 가이드

## 🎯 목표
백엔드 코드를 GitHub에 업로드하여 Render에서 배포할 수 있도록 준비합니다.

---

## 방법 1: GitHub Desktop 사용 (가장 쉬움) ⭐ 추천

### 1단계: GitHub Desktop 설치
1. https://desktop.github.com/ 접속
2. "Download for Windows" 클릭하여 설치
3. 설치 후 GitHub 계정으로 로그인

### 2단계: GitHub 저장소 생성
1. GitHub 웹사이트 (https://github.com) 접속
2. 우측 상단 "+" 버튼 → "New repository" 클릭
3. 저장소 설정:
   ```
   Repository name: shopping-app-backend (또는 원하는 이름)
   Description: Backend API for shopping app
   Public 또는 Private 선택
   ⚠️ "Initialize this repository with a README" 체크 해제!
   ```
4. "Create repository" 클릭

### 3단계: GitHub Desktop으로 코드 업로드
1. GitHub Desktop 실행
2. "File" → "Add Local Repository" 클릭
3. 폴더 선택: `C:\Users\rehan\Desktop\project\my-app`
4. "Add repository" 클릭
5. 왼쪽 패널에서 변경된 파일 확인:
   - ✅ 업로드될 파일들 (Python 코드, requirements.txt 등)
   - ❌ `.env` 파일이 목록에 없어야 함 (자동 제외됨)
6. 하단에 커밋 메시지 입력:
   ```
   Initial commit: Backend API
   ```
7. "Commit to main" 클릭
8. "Publish repository" 클릭
9. 저장소 이름 확인 후 "Publish repository" 클릭

✅ 완료! GitHub에서 코드 확인 가능

---

## 방법 2: Git 명령어 사용 (터미널)

### 1단계: Git 설치 확인
```powershell
git --version
```
- 설치되어 있지 않으면: https://git-scm.com/download/win 에서 다운로드

### 2단계: GitHub 저장소 생성
1. GitHub 웹사이트 (https://github.com) 접속
2. 우측 상단 "+" 버튼 → "New repository" 클릭
3. 저장소 설정:
   ```
   Repository name: shopping-app-backend
   Description: Backend API for shopping app
   Public 또는 Private 선택
   ⚠️ "Initialize this repository with a README" 체크 해제!
   ```
4. "Create repository" 클릭
5. 저장소 URL 복사 (예: `https://github.com/your-username/shopping-app-backend.git`)

### 3단계: 코드 업로드
프로젝트 폴더에서 다음 명령어 실행:

```powershell
# 1. Git 초기화
git init

# 2. 모든 파일 추가 (자동으로 .gitignore에 따라 제외됨)
git add .

# 3. 커밋
git commit -m "Initial commit: Backend API"

# 4. main 브랜치로 변경
git branch -M main

# 5. 원격 저장소 연결 (your-username과 your-repo-name을 실제 값으로 변경)
git remote add origin https://github.com/your-username/your-repo-name.git

# 6. 코드 업로드
git push -u origin main
```

### 업로드 전 확인사항
```powershell
# 어떤 파일들이 추가될지 확인
git status

# .env 파일이 제외되었는지 확인
git status | Select-String ".env"
# 결과가 없어야 함 (제외됨)
```

---

## 방법 3: GitHub 웹 인터페이스 사용 (간단한 파일만)

⚠️ 이 방법은 파일이 많을 때 비효율적입니다.

1. GitHub 저장소 생성 (방법 1 또는 2의 2단계 참고)
2. "uploading an existing file" 클릭
3. 파일들을 드래그 앤 드롭
4. "Commit changes" 클릭

---

## ✅ 업로드 후 확인

### GitHub에서 확인할 파일들
- ✅ `api_server.py`
- ✅ `requirements.txt`
- ✅ `env_example.txt`
- ✅ `.gitignore`
- ✅ `Dump20251114.sql`
- ✅ 모든 Python 코드 파일들
- ❌ `.env` 파일이 없어야 함!

### 확인 방법
1. GitHub 저장소 페이지 접속
2. 파일 목록 확인
3. `.env` 파일이 보이면 안 됨!

---

## 🚨 문제 해결

### `.env` 파일이 업로드된 경우
1. GitHub에서 `.env` 파일 삭제
2. `.gitignore`에 `.env`가 있는지 확인
3. 로컬에서 `.env` 파일 내용 변경 (비밀번호 등)
4. 다시 커밋 및 푸시

### Git 명령어 오류
- `git: command not found` → Git 설치 필요
- `Permission denied` → GitHub 인증 확인
- `Repository not found` → 저장소 URL 확인

---

## 다음 단계

GitHub 업로드 완료 후:
1. `DEPLOYMENT_GUIDE.md`의 "2단계: Render에서 Web Service 생성" 진행
2. Render 대시보드에서 GitHub 저장소 연결
3. 환경변수 설정

