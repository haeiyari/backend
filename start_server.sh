#!/bin/bash
# API 서버 시작 스크립트

echo "========================================"
echo "의류 치수 측정 API 서버 시작"
echo "========================================"
echo ""

# Python 버전 확인
python_version=$(python --version 2>&1)
echo "Python 버전: $python_version"

# 필요한 패키지 확인
echo ""
echo "필요한 패키지 확인 중..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI가 설치되어 있지 않습니다."
    echo "설치를 시작합니다: pip install -r requirements.txt"
    pip install -r requirements.txt
else
    echo "✅ 필요한 패키지가 설치되어 있습니다."
fi

echo ""
echo "========================================"
echo "서버 시작 중..."
echo "========================================"
echo ""
echo "접속 주소:"
echo "  - API 서버: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

# 서버 실행
python api_server.py

