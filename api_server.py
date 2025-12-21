# 치수 측정 API 서버
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect, Header
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # CORS 설정을 위해 CORSMiddleware 가져오기
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional, Dict, Set, List
import uvicorn # uvicorn 모듈을 가져오기 (FastAPI 앱을 실행하고 개발 서버를 실행하는 데 사용)
from measurement_service import MeasurementService
import logging # logging 모듈을 가져오기 (로깅 기능을 제공)
import json # json 모듈을 가져오기 (JSON 데이터를 처리하는 데 사용)
import uuid # uuid 모듈을 가져오기 (UUID 생성을 위해 사용)
import asyncio # asyncio 모듈을 가져오기 (비동기 작업을 위해 사용)
import mysql.connector
from mysql.connector import Error
import base64
import os
from datetime import datetime, timedelta
import hashlib
from fastapi.openapi.utils import get_openapi
import numpy as np
from dotenv import load_dotenv
import urllib.parse

# [추가된 함수] NumPy 데이터를 일반 파이썬 데이터로 변환해주는 청소기 함수
def make_serializable(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    return obj

# 현재 파일 기준 베이스 디렉토리 (어디서 실행해도 HTML/환경변수 경로가 안전하게 열리도록)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# .env 파일 로딩 (스크립트가 있는 디렉터리의 .env를 강제로 사용)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 새로 추가된 모듈들
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    verify_reset_token,
    decode_token,
)
from email_utils import send_password_reset_email, send_welcome_email
from social_auth import KakaoAuth, GoogleAuth, NaverAuth

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING,  # INFO → WARNING으로 변경 (로그 줄이기)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 본체 생성
app = FastAPI( # FastAPI 호출하여 'app' 이라는 이름의 메인 앱 객체를 생성
    title="의류 치수 측정 API",
    description="A4 용지 기준으로 의류 치수를 자동 측정하는 API 서비스", # 앱 설명
    version="1.0.0" # 앱 버전
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="의류 치수 측정 API",
        version="1.0.0",
        description="A4 용지 기준으로 의류 치수를 자동 측정하는 API 서비스",
        routes=app.routes,
    )
    
    # [Authorize] 버튼을 만드는 핵심 코드
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # 모든 API에 자물쇠 아이콘 표시
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS(Cross-origin Resource Sharing) 미들웨어 설정
app.add_middleware( # 앱 객체에 CORS 설정을 추가하는 메서드
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인(출처)에서의 요청을 허용 (* 는 모든 도메인을 의미, 주로 개발/테스트 단계에서 사용)
    allow_credentials=True, # 인증 정보(쿠키, 인증 헤더 등)를 포함한 요청을 허용 (예: 로그인 상태 유지)
    allow_methods=["*"], # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"], # 모든 HTTP 요청 헤더를 허용 (예: 쿠키, 인증 헤더 등)
)

# 이미지 저장 디렉토리 (업로드용)
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 정적 자원(샘플 이미지 등)이 들어있는 assets 경로
base_dir = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(base_dir, "assets", "images")

# 폴더가 없으면 서버가 죽지 않게, 빈 폴더라도 만들어줍니다.
if not os.path.exists(assets_path):
    os.makedirs(assets_path)

# 정적 파일 마운트
# 1) 기존 assets 이미지
app.mount("/images", StaticFiles(directory=assets_path), name="images")

# 2) 사용자가 업로드한 의류 사진
app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_DIR), name="uploaded_images")

# 서비스 클래스 인스턴스 생성 (치수 측정 서비스 객체 생성)
measurement_service = MeasurementService() # measurement_service 클래스의 인스턴스를 생성

# MySQL 데이터베이스 연결 설정 (환경변수 사용)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)), 
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'shopping_app'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def get_db_connection():

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"DB 연결 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 연결 실패: {str(e)}")

# WebSocket 세션 관리
class ConnectionManager:
    def __init__(self):
        
        self.sessions: Dict[str, Dict[str, WebSocket]] = {}
    
    def create_session(self) -> str:
     
        session_id = str(uuid.uuid4())[:8]
        self.sessions[session_id] = {}
        logger.info(f"새 세션 생성: {session_id}")
        return session_id
    
    async def connect_desktop(self, session_id: str, websocket: WebSocket):
     
        await websocket.accept()
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id]['desktop'] = websocket
        logger.info(f"데스크톱 연결: {session_id}")
    
    async def connect_mobile(self, session_id: str, websocket: WebSocket):
       
        await websocket.accept()
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id]['mobile'] = websocket
        logger.info(f"모바일 연결: {session_id}")
        
        # 데스크톱에 모바일 연결 알림
        if 'desktop' in self.sessions[session_id]:
            await self.sessions[session_id]['desktop'].send_json({
                'type': 'mobile_connected',
                'message': '모바일 기기가 연결되었습니다'
            })
    
    def disconnect(self, session_id: str, device_type: str):
      
        if session_id in self.sessions and device_type in self.sessions[session_id]:
            del self.sessions[session_id][device_type]
            logger.info(f"{device_type} 연결 해제: {session_id}")
            
            # 세션에 연결된 기기가 없으면 세션 삭제
            if not self.sessions[session_id]:
                del self.sessions[session_id]
                logger.info(f"세션 삭제: {session_id}")
    
    async def send_to_desktop(self, session_id: str, message: dict):
       
        if session_id in self.sessions and 'desktop' in self.sessions[session_id]:
            try:
                await self.sessions[session_id]['desktop'].send_json(message)
            except Exception as e:
                logger.error(f"데스크톱 전송 오류: {e}")
    
    async def send_to_mobile(self, session_id: str, message: dict):
       
        if session_id in self.sessions and 'mobile' in self.sessions[session_id]:
            try:
                await self.sessions[session_id]['mobile'].send_json(message)
            except Exception as e:
                logger.error(f"모바일 전송 오류: {e}")

manager = ConnectionManager()

# 소셜 로그인 인스턴스 (환경변수에서 키 가져오기)
kakao_auth = KakaoAuth(
    client_id=os.getenv("KAKAO_CLIENT_ID", ""),
    client_secret=os.getenv("KAKAO_CLIENT_SECRET")
)

google_auth = GoogleAuth(
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", "")
)

naver_auth = NaverAuth(
    client_id=os.getenv("NAVER_CLIENT_ID", ""),
    client_secret=os.getenv("NAVER_CLIENT_SECRET", "")
)

# 로그아웃된 토큰 블랙리스트 
token_blacklist: Set[str] = set()

# 응답 모델
class MeasurementResponse(BaseModel):
    type: str
    measurements: Dict[str, float]
    result_image: Optional[str] = None
    unit: str = "cm"
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# 회원가입 요청 이라는 이름의 데이터 설계도
class SignupRequest(BaseModel): # BaseModel로 인해 자동으로 데이터 검사 기능을 가짐
    name: str # 이름 필드
    email: str # 이메일 필드
    password: str # 비밀번호 필드

# 로그인 요청 이라는 이름의 데이터 설계도
class LoginRequest(BaseModel): # BaseModel로 인해 자동으로 데이터 검사 기능을 가짐
    email: str # 이메일 필드
    password: str # 비밀번호 필드

# 소셜 로그인 요청
class SocialLoginRequest(BaseModel):
    code: str  # 소셜 로그인 인가 코드
    redirect_uri: str  # 리다이렉트 URI
    provider: str  # 'kakao', 'google', 'naver'

# 비밀번호 재설정 요청
class PasswordResetRequest(BaseModel):
    email: str

# 비밀번호 변경 요청
class PasswordChangeRequest(BaseModel):
    token: str
    new_password: str

# 상품 검색 요청
class ProductSearchRequest(BaseModel):
    keyword: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

# 장바구니 아이템 생성 요청
class CartItemCreateRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


# 장바구니 아이템 수정 요청
class CartItemUpdateRequest(BaseModel):
    quantity: int


# 위시리스트 추가 요청
class WishlistCreateRequest(BaseModel):
    user_id: int
    product_id: int


# 장바구니 기반 주문 생성 요청
class OrderFromCartRequest(BaseModel):
    user_id: int
    receiver_name: str
    receiver_phone: str
    address: str
    payment_method: str = "카드"

# 리뷰 등록 요청
class ReviewCreateRequest(BaseModel):
    user_id: int
    product_id: int
    rating: int  # 1~5
    content: Optional[str] = None
    size_feedback: Optional[int] = None  # 1:작음, 2:적당함, 3:큼

# 사이즈 추천 요청
class SizeRecommendRequest(BaseModel):
    user_profile_id: int  # 내 옷장의 profile_id
    product_id: int  # 비교할 상품 ID

@app.get("/", response_class=HTMLResponse)
async def root():
    # 루트 경로에서 웹 시작 화면(index.html)을 제공
    try:
        index_path = os.path.join(BASE_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        # index.html이 없을 때 기존 JSON 안내 유지
        return HTMLResponse(
            content="""
            <html><body style='font-family:system-ui; padding:20px;'>
            <h2>의류 치수 측정 API</h2>
            <p>index.html 파일을 찾을 수 없습니다. <code>project/my-app/index.html</code>이 존재하는지 확인하세요.</p>
            <pre>{"message":"의류 치수 측정 API에 오신 것을 환영합니다!","version":"1.0.0","endpoints":{"POST /measure":"의류 치수 측정","GET /health":"서버 상태 확인","GET /docs":"API 문서"}}</pre>
            </body></html>
            """,
            status_code=200
        )

@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    # 명시적 경로(/index.html)로도 시작 화면 제공
    try:
        index_path = os.path.join(BASE_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return HTMLResponse(
            content="<html><body><h3>index.html 파일을 찾을 수 없습니다.</h3></body></html>",
            status_code=404,
        )

@app.get("/mobile_capture.html", response_class=HTMLResponse)
async def mobile_capture_page():
    # 모바일 촬영 페이지 제공
    try:
        html_path = os.path.join(BASE_DIR, "mobile_capture.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return HTMLResponse(
            content="<html><body><h3>mobile_capture.html 파일을 찾을 수 없습니다.</h3></body></html>",
            status_code=404,
        )

@app.get("/demo_with_keypoints.html", response_class=HTMLResponse)
async def demo_with_keypoints_page():
   
    try:
        html_path = os.path.join(BASE_DIR, "demo_with_keypoints.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return HTMLResponse(
            content="<html><body><h3>demo_with_keypoints.html 파일을 찾을 수 없습니다.</h3></body></html>",
            status_code=404,
        )

# 가입 요청 접수 API
# 클라이언트가 /signup 주소로 가입 신청서(SignupRequest)를 제출하면 실행되는 함수
@app.post("/signup")
async def signup(request: SignupRequest):

    # DB 창구 열기
    try:
        print(f"DEBUG: [1] 원본 데이터: {request}", flush=True)
        print(f"DEBUG: [2] 비밀번호 타입: {type(request.password)}", flush=True)
        print(f"DEBUG: [3] 비밀번호 값: {request.password}", flush=True)

        safe_password = str(request.password)

        connection = get_db_connection() # 회원 명부를 관리하는 데이터베이스에 접속
        cursor = connection.cursor(dictionary=True)

        # 이메일 중복 검사
        # 이미 같은 이메일로 가입한 사람이 있는지 DB를 살펴봄(SELECT)
        cursor.execute("SELECT id FROM users WHERE email = %s", (request.email,))
        existing = cursor.fetchone() 
        if existing: # 이미 같은 이메일로 가입한 사람이 있으면
            cursor.close() 
            connection.close() 
            raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.") # 즉시 에러(400)를 내고 가입을 거절

        # 비밀번호 암호화 (bcrypt 사용으로 변경)
        # 비밀번호를 그대로 저장하면 위험하므로, 알아볼 수 없는 문자열(해시)로 변환
        password_hash = hash_password(safe_password)

        # 신규 회원 등록
        # 이름, 이메일, 암호화된 비밀번호를 DB의 users 테이블에 추가 
        insert_sql = """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
        """
        values = (
            request.name,
            request.email,
            password_hash,
        )
        cursor.execute(insert_sql, values)
        connection.commit() # commit()을 해야 실제로 저장이 완료

        #회원 번호 발급 (DB가 자동으로 부여)
        user_id = cursor.lastrowid

        # DB 창구 닫기
        cursor.close()
        connection.close()

        # 가입 완료 통보
        #클라이언트에게 가입 성공 메시지와 함께 발급된 회원 번호를 보내줌
        return JSONResponse(
            content={
                "success": True,
                "user_id": user_id,
                "message": "회원가입이 완료되었습니다.",
            }
        )

    # 에러 처리
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"회원가입 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 로그인 요청 수신
# 클라이언트가 /login 주소로 이메일과 비밀번호를 보내면 이 함수가 실행
@app.post("/login")
async def login(request: LoginRequest): 

    # DB 연결
    # 사용자 정보를 확인하기 위해 데이터베이스에 접속
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 사용자 조회
        # 입력된 이메일과 일치하는 사용자가 있는지 DB에서 찾아봄 (이때 비밀번호도 같이 가져옴)
        cursor.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            (request.email,),
        )
        user = cursor.fetchone()

        # 존재 여부 확인
        # 만약 DB에서 가져온 데이터가 없다면
        if not user:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=401, detail="가입되지 않은 이메일입니다.") # 가입되지 않은 이메일이므로 401 에러를 냄

        # 비밀번호 검증 (bcrypt 사용으로 변경)
        if not verify_password(request.password, user["password"]): # DB에 저장된 암호문과 비교
            cursor.close()
            connection.close()
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.") # 비밀번호가 다르면 401 에러를 냄

        # 응답 데이터 준비
        # DB 연결을 끊고 클라이언트에게 돌려줄 사용자 정보 추림
        cursor.close()
        connection.close()

        # 이때 비밀번호는 절대 포함하지 않도록 주의해서 제외
        user_info = {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
        }

        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user["email"], "user_id": user["id"]})
        
        # 로그인 성공 응답
        # 성공 메시지와 함께 사용자 정보 및 토큰을 JSON 형태로 반환
        return JSONResponse(
            content={
                "success": True,
                "user": user_info,
                "access_token": access_token,
                "token_type": "bearer",
                "message": "로그인 성공",
            }
        )

    # 예외 처리
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"로그인 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/my_closet.html", response_class=HTMLResponse)
async def my_closet_page():
 
    try:
        html_path = os.path.join(BASE_DIR, "my_closet.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return HTMLResponse(
            content="<html><body><h3>my_closet.html 파일을 찾을 수 없습니다.</h3></body></html>",
            status_code=404,
        )

@app.get("/test_auth.html", response_class=HTMLResponse)
async def test_auth_page():
    # API 테스트 페이지 제공
    try:
        html_path = os.path.join(BASE_DIR, "test_auth.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return HTMLResponse(
            content="<html><body><h3>test_auth.html 파일을 찾을 수 없습니다.</h3></body></html>",
            status_code=404,
        )

@app.get("/health") # @app.get(): http get 요청을 받는 주소, "/health": 함수가 응답할 URL 주소
async def health_check(): # 서버가 현재 정상적으로 작동하고 있는지 확인하는 용도 (async: 비동기 작업임을 나타냄)
    return { # 서버 상태 정보를 JSON 형식으로 반환
        "status": "healthy", # 서버 상태 정보
        "service": "measurement-api", # 서비스 이름
        "version": "1.0.0" # 서버 버전
    }

@app.post("/measure", response_model=MeasurementResponse) 
# @app.post(): 클라이언트가 서버로 데이터를 제출할 떄 사용, "/measure": URL 주소
# response_model=MeasurementResponse: API에게 엔드포인트가 성공 시 어떤 데이터 구조로 응답할지 알려주는 역할
async def measure_clothing(
    image: UploadFile = File(..., description="측정할 의류 이미지 (A4 용지 포함)"), # 측정할 의류 이미지 파일형태로 업로드 받기
    clothing_type: str = Form(..., description="의류 타입: 'shirt' (상의) 또는 'pants' (하의)"), # 의류 타입 폼 데이터로 받기
    a4_box: str = Form(None, description="수동으로 지정한 A4 용지 박스 좌표 (JSON 배열, 선택사항)"), # A4 용지 좌표 폼 데이터로 받기
    scale_correction: float = Form(1.0, description="전체 치수에 곱해지는 보정계수 (기본 1.0)"), # 전체 치수에 곱해지는 보정계수 폼 데이터로 받기
    horiz_scale_correction: float = Form(1.0, description="가로(어깨/가슴) 보정 계수"), # 가로(어깨/가슴) 보정 계수 폼 데이터로 받기
    vert_scale_correction: float = Form(1.0, description="세로(총장) 보정 계수") # 세로(총장) 보정 계수 폼 데이터로 받기
):
    try: #메인 로직 시작 (try - except로 오류 처리)
        
        logger.info(f"측정 요청 수신 - 의류 타입: {clothing_type}, 파일명: {image.filename}") # 측정 요청 정보 기록 출력
        
        # 파일 형식 확인
        if not image.content_type.startswith('image/'): # 파일 형식이 이미지가 아닌 경우
            raise HTTPException( # 클라이언트 요청에 문제가 있다고 알리고
                status_code=400, # 400 오류 코드 반환과 함께
                detail="이미지 파일만 업로드 가능합니다." # 오류 메시지
            )
        
        # 의류 타입 검증
        if clothing_type not in ['shirt', 'pants']: # 의류 타입이 shirt 또는 pants가 아닌 경우
            raise HTTPException( # 클라이언트 요청에 문제가 있다고 알리고
                status_code=400, # 400 오류 코드 반환과 함께
                detail="clothing_type은 'shirt' 또는 'pants'여야 합니다." # 오류 메시지
            )
        
        # A4 좌표 파싱 (수동 선택된 경우)
        a4_box_list = None # A4 좌표 리스트 초기화
        if a4_box: # A4 좌표가 수동 선택된 경우라면
            try:
                a4_box_list = json.loads(a4_box) # A4 좌표 리스트로 변환
                logger.info(f"수동 선택된 A4 좌표 사용: {a4_box_list}") # 수동 선택된 A4 좌표 사용 정보 기록 출력
            except json.JSONDecodeError: # JSON 형식이 올바르지 않은 경우
                raise HTTPException(status_code=400, detail="a4_box의 JSON 형식이 올바르지 않습니다.") # 오류 발생
        
        # 다음으로 이미지 데이터 읽기
        image_data = await image.read() # 파일 읽기 작업은 시간이 걸릴 수 있으므로 await 사용해 비동기적 처리리
        
        if len(image_data) == 0: # 이미지 데이터가 비어있는 경우
            raise HTTPException( # 클라이언트 요청에 문제가 있다고 알리고
                status_code=400, # 400 오류 코드 반환과 함께
                detail="빈 이미지 파일입니다." # 오류 메시지
            )
        
        # API 엔드포인트 함수 (measure_clothing)는 요청을 받고 검증하는 역할만 하고
        result = measurement_service.measure_clothing( # 실제 치수 측정 작업은 measurement_service 라는 별도의 객체에게 위임
            image_data, clothing_type, a4_box_list,
            scale_correction, horiz_scale_correction, vert_scale_correction
        )
        
        # A4 수동 선택이 필요한 경우, 다음 단계로 넘어가기
        if result.get("need_manual_a4"):
            logger.info("A4 자동 검출 실패 - 수동 선택 필요")
            return JSONResponse(content=result)
        
        # 측정 서비스 자체에서 오류를 반환한 경우
        if "error" in result and not result.get("need_manual_a4"):
            logger.warning(f"측정 실패: {result['error']}")
            raise HTTPException( # 클라이언트 요청에 문제가 있다고 알리고
                status_code=422, # 요청 형식(400)은 맞으나 데이터에 문제가 있어 처리 불가로
                detail=result["error"] # 오류 메시지
            )
        
        logger.info(f"측정 완료 - {len(result.get('measurements', {}))}개 항목 측정됨") #모든 것이 성공한 경우
        
        return JSONResponse(content=result) # 측정 결과를 JSON 형식으로 반환
    
    except HTTPException: # 예외 처리 // 만약 try 블록 안에서 HTTPException(400, 422) 예외가 발생하면
        raise
    except Exception as e: 
        logger.error(f"측정 중 오류 발생: {str(e)}", exc_info=True) #오류의 상세 내역을 로그에만 남겨 보안 유지
        raise HTTPException(
            status_code=500, # 서버 내부에서 예상치 못한 오류 발생 시 500 오류 코드 반환과 함께
            detail=f"서버 오류가 발생했습니다: {str(e)}" # 오류 메시지
        )


# @app.post: HTTP POST 메서드로 작동하는 엔드포인트(주소)를 선언, "/detect-keypoints": 함수가 응답할 URL 주소
@app.post("/detect-keypoints")
async def detect_keypoints(
    image: UploadFile = File(..., description="측정할 의류 이미지 (A4 용지 포함)"), # image 라는 이름으로 파일 받기
    clothing_type: str = Form(..., description="의류 타입: 'shirt' (상의) 또는 'pants' (하의)"), # clothing_type 라는 이름으로 폼 데이터 받기
    a4_box: str = Form(None, description="수동으로 지정한 A4 용지 박스 좌표 (JSON 배열, 선택사항)"), # a4_box 라는 이름으로 폼 데이터 받기 (선택사항)
):
    # 1. 메인 로직 시작
    try:
        
        logger.info(f"키포인트 검출 요청 - 의류 타입: {clothing_type}, 파일명: {image.filename}") #서버 로그에 어떤 요청이 들어왔는지 기록
        
        # 2. 입력값 검증
        if not image.content_type.startswith('image/'): # 이미지 파일이 아닌 경우 차단
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
        if clothing_type not in ['shirt', 'pants']: # 약속된 의류 타입(shirt, pants)이 아닌 경우 차단
            raise HTTPException(status_code=400, detail="clothing_type은 'shirt' 또는 'pants'여야 합니다.")
        
        image_data = await image.read() # 비동기로 이미지 파일 데이터를 메모리로 읽어들임
        
        if len(image_data) == 0: # 이미지가 빈 파일 (용량이 0인 파일)이라면 차단
            raise HTTPException(status_code=400, detail="빈 이미지 파일입니다.")
        
        # 3.A4 박스 파싱 (수동 선택된 경우)
        a4_box_list = None # 기본값:None (자동검출 모드)
        if a4_box: # 만약 사용자가 a4_box 데이터를 보냈다면
            try:
                a4_box_list = json.loads(a4_box) # "[[x1,y1], ...]" 형태의 JSON 문자열을 파이썬 리스트로 변환합니다.
                logger.info(f"수동 선택된 A4 박스 사용: {a4_box_list}") # 수동 선택된 A4 박스 사용 정보 기록 출력
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="a4_box의 JSON 형식이 올바르지 않습니다.") # # JSON 형식이 잘못된 경우
        
        # 4. measurement_service 객체의 'detect_keypoints' 함수 호출
        # 이 함수는 측정은 하지 않고, 키포인트 검출까지만 수행
        result = measurement_service.detect_keypoints(image_data, clothing_type, a4_box_list)
        
        # 5. 서비스 결과 처리
        if result.get("need_manual_a4"): # A4 자동 검출에 실패한 경우
            logger.info("A4 자동 검출 실패 - 수동 선택 필요") 
            return JSONResponse(content=result)
        
        if "error" in result and not result.get("need_manual_a4"): # 옷 윤곽선과 같은 키포인트 검출에 실패한 경우
            logger.warning(f"키포인트 검출 실패: {result['error']}")
            raise HTTPException(status_code=422, detail=result["error"])
        
        logger.info(f"키포인트 검출 완료 - {len(result.get('keypoints', []))}개 키포인트") # 모든 것이 성공한 경우 
        
        return JSONResponse(content=result) # 프론트엔드에게 키포인트 정보와 미리보기 이미지를 반환
    # 6. 예외 처리
    except HTTPException: # 400, 422 오류 그대로 FastAPI가 처리하도록 다시 던짐 
        raise
    except Exception as e: # 예상치 못한 오류 발생 시, 사용자에게는 간단한 오류 메시지만 보내고, 서버는 다운되지 않도록 막기
        logger.error(f"키포인트 검출 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
# @app.post: HTTP POST 메서드로 작동하는 엔드포인트(주소)를 선언, "/measure-with-keypoints": 함수가 응답할 URL 주소
@app.post("/measure-with-keypoints")
async def measure_with_keypoints(
    image: UploadFile = File(..., description="측정할 의류 이미지"),
    clothing_type: str = Form(..., description="의류 타입: 'shirt' 또는 'pants'"),
    keypoints: str = Form(..., description="조정된 키포인트 좌표 (JSON 배열)"), # 사용자가 조정한 최종 키포인트 좌표
    a4_box: str = Form(..., description="A4 용지 박스 좌표 (JSON 배열)"), # 자동 / 수동으로 확정 되었던 A4 용지 좌표
    pixelsPerCM_w: float = Form(..., description="가로 픽셀/cm 비율"), # A4용지를 기반으로 계산되었던 픽셀/cm 비율
    pixelsPerCM_h: float = Form(..., description="세로 픽셀/cm 비율"),
    scale_correction: float = Form(1.0, description="전체 치수에 곱해지는 보정계수 (기본 1.0)"),
    horiz_scale_correction: float = Form(1.0, description="가로(어깨/가슴) 보정 계수"),
    vert_scale_correction: float = Form(1.0, description="세로(총장) 보정 계수")
):
    # 1. 메인 로직 시작 
    try:
        logger.info(f"키포인트 기반 측정 요청 - 의류 타입: {clothing_type}") # 서버 로그에 어떤 요청이 들어왔는지 기록
        
        # 2. 입력값 검증
        if not image.content_type.startswith('image/'): 
            raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
        if clothing_type not in ['shirt', 'pants']: 
            raise HTTPException(status_code=400, detail="clothing_type은 'shirt' 또는 'pants'여야 합니다.")
        
        # 3. 사용자가 보낸 텍스트형태의 좌표를 파이썬 리스트로 변환
        keypoints_list = json.loads(keypoints)
        a4_box_list = json.loads(a4_box)
        
        image_data = await image.read() # 이미지 데이터 읽기
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="빈 이미지 파일입니다.")
        
        # 4. measurement_service 객체의 'measure_with_keypoints' 함수 호출
        # 이 함수는 키포인트를 자동 검출 하지 않고 전달받은 keypoints_list를 사용하여 바로 측정을 시작
        result = measurement_service.measure_with_keypoints(
            image_data, clothing_type, keypoints_list, a4_box_list,
            pixelsPerCM_w, pixelsPerCM_h, scale_correction,
            horiz_scale_correction, vert_scale_correction
        )
        # 5. 결과 처리
        if "error" in result:
            logger.warning(f"측정 실패: {result['error']}")
            raise HTTPException(status_code=422, detail=result["error"])
        
        logger.info(f"측정 완료 - {len(result.get('measurements', {}))}개 항목 측정됨") # 성공 시, 최종 측정값을 로그로 남김
        
        return JSONResponse(content=make_serializable(result))

    # 6. 예외 처리
    except json.JSONDecodeError: # keypoints나 a4_box가 잘못된 텍스트(JSON) 형식일 때 발생하는 오류를 처리
        raise HTTPException(status_code=400, detail="keypoints 또는 a4_box의 JSON 형식이 올바르지 않습니다.")
    except HTTPException: # 400, 422 오류 그대로 FastAPI가 처리하도록 다시 던짐 
        raise
    except Exception as e: # 그 외 예상치 못한 모든 서버 오류 (500)
        logger.error(f"측정 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/supported-measurements")
async def get_supported_measurements():
    
    # 지원하는 측정 항목 조회
    
    return {
        "shirt": {
            "measurements": ["length", "shoulder", "chest", "sleeve"],
            "descriptions": {
                "length": "총장 (목~밑단)",
                "shoulder": "어깨 너비",
                "chest": "가슴 너비",
                "sleeve": "소매 길이"
            }
        },
        "pants": {
            "measurements": ["length", "waist", "hip", "crotch", "thigh", "hem"],
            "descriptions": {
                "length": "총장 (허리~밑단)",
                "waist": "허리 단면",
                "hip": "엉덩이 단면",
                "crotch": "밑위",
                "thigh": "허벅지 단면",
                "hem": "밑단 단면"
            }
        }
    }

# API 엔드포인트 정의
# 클라이언트가 '/save-to-closet' 주소로 데이터를 보내면 이 함수가 실행
@app.post("/save-to-closet")
async def save_to_closet(
    user_id: int = Form(...), #Form 데이터(글자)와 File(이미지)을 매개변수로 받아들임
    profile_name: str = Form(...),
    category: str = Form(...),
    measurements: str = Form(...),
    image: UploadFile = File(...) 
):

    try:
        logger.info(f"내 옷장 저장 요청 - user_id: {user_id}, profile_name: {profile_name}")
        
        # 데이터 해석
        # 클라이언트가 문자열 형태로 보낸 측정 데이터(measurements)를 딕셔너리 형태로 변환
        measurements_dict = json.loads(measurements)
        
        # 이미지 유무 확인
        # 업로드된 이미지 파일이 진짜 존재하는지, 파일명이 비어있지는 않은지 검사
        if not image or image.filename == "":
             raise HTTPException(status_code=400, detail="이미지 파일이 없습니다.") # 문제가 있다면 400 에러 보냄

        # 이미지 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # 파일 이름이 겹치지 않게 '사용자ID_시간' 형식으로 새 이름을 짓고
        file_extension = os.path.splitext(image.filename)[1] # (파일 확장자 추출)
        filename = f"user_{user_id}_{timestamp}{file_extension}" # (파일 이름 생성)
        file_path = os.path.join(UPLOAD_DIR, filename) # 서버의 하드디스크(UPLOAD_DIR)에
        
        with open(file_path, "wb") as f: 
            f.write(await image.read()) # 사진 파일을 실제로 저장
        
        # 이미지 URL 생성
        image_url = f"/{UPLOAD_DIR}/{filename}"
        logger.info(f"이미지 저장 완료: {image_url}")

        # 데이터베이스 연결
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 사용자 신원 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,)) # 데이터베이스에서 해당 user_id가 실제로 존재하는지 조회
        if not cursor.fetchone(): # 유령 회원이면 저장을 거부
            raise HTTPException(status_code=404, detail=f"사용자 ID {user_id}를 찾을 수 없습니다.")
        
        # 상의/하의에 따라 저장 양식 선택
        # 카테고리가 '상의'인지 '하의'인지에 따라 저장해야 할 DB 테이블의 컬럼(칸)이 다름
        # 상황에 맞는 SQL 문장(양식)을 선택
        if category == "상의":
            sql = """
                INSERT INTO user_measure_profile 
                (user_id, profile_name, profile_image_url, category, 
                 top_length, top_shoulder, top_chest, top_sleeve)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                user_id,
                profile_name,
                image_url,
                category,
                measurements_dict.get('length'),
                measurements_dict.get('shoulder'),
                measurements_dict.get('chest'),
                measurements_dict.get('sleeve')
            )
        else:  # 하의
            sql = """
                INSERT INTO user_measure_profile 
                (user_id, profile_name, profile_image_url, category,
                 bottom_length, bottom_waist, bottom_rise, bottom_hip, bottom_thigh, bottom_hem)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                user_id,
                profile_name,
                image_url,
                category,
                measurements_dict.get('length'),
                measurements_dict.get('waist'),
                measurements_dict.get('crotch'),
                measurements_dict.get('hip'),
                measurements_dict.get('thigh'),
                measurements_dict.get('hem')
            )
        
        # DB에 기록 (Commit)
        # 작성한 SQL 문을 실행하여 데이터베이스에 정보를 넣고
        cursor.execute(sql, values) 
        connection.commit() # commit을 통해 저장을 확정
        profile_id = cursor.lastrowid # 저장된 데이터의 고유 ID를 가져옴
        cursor.close() # (데이터베이스 연결 종료)
        connection.close() 
        logger.info(f"저장 완료 - profile_id: {profile_id}") 
        
        # 성공 응답 발송
        # 모든 작업이 성공했음을 클라이언트에게 알리고 새로 생성된 프로필 ID도 함께 전달
        return JSONResponse(content={
            "success": True,
            "profile_id": profile_id,
            "message": "내 옷장에 저장되었습니다."
        })

    # 에러 처리    
    # 작업 도중 예상치 못한 문제(DB 연결 끊김, 파일 오류 등)가 발생하면 서버가 멈추지 않게 막고 에러 내용을 상태 코드로 반환
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="measurements JSON 형식이 올바르지 않습니다.")
    except Error as e:
        logger.error(f"DB 저장 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"저장 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/my-closet/{user_id}")
async def get_my_closet(user_id: int, category: Optional[str] = None):
    """
    내 옷장 목록 조회 API
    
    사용자의 저장된 옷 목록을 조회합니다. 카테고리 필터 옵션 제공.
    """
    try:
        logger.info(f"내 옷장 조회 요청 - user_id: {user_id}, category: {category}")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 카테고리 필터링
        if category:
            sql = """
                SELECT 
                    profile_id,
                    profile_name,
                    profile_image_url,
                    category,
                    top_length, top_shoulder, top_chest, top_sleeve,
                    bottom_length, bottom_waist, bottom_rise, bottom_hip, bottom_thigh, bottom_hem,
                    created_at
                FROM user_measure_profile
                WHERE user_id = %s AND category = %s
                ORDER BY created_at DESC
            """
            cursor.execute(sql, (user_id, category))
        else:
            sql = """
                SELECT 
                    profile_id,
                    profile_name,
                    profile_image_url,
                    category,
                    top_length, top_shoulder, top_chest, top_sleeve,
                    bottom_length, bottom_waist, bottom_rise, bottom_hip, bottom_thigh, bottom_hem,
                    created_at
                FROM user_measure_profile
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            cursor.execute(sql, (user_id,))
        
        profiles = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # datetime을 문자열로 변환
        for profile in profiles:
            if profile['created_at']:
                profile['created_at'] = profile['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"조회 완료 - {len(profiles)}개 항목")
        
        # Decimal, datetime 등의 타입을 JSON 직렬화 가능한 형태로 변환
        payload = {
            "user_id": user_id,
            "category": category,
            "count": len(profiles),
            "profiles": profiles
        }
        return JSONResponse(content=jsonable_encoder(payload))
        
    except Error as e:
        logger.error(f"DB 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 삭제 요청 수신 (DELETE)
# 클라이언트가 '/my-closet/1'과 같이 특정 ID(profile_id)를 주면서 삭제를 요청하면 이 함수가 실행
@app.delete("/my-closet/{profile_id}")
async def delete_from_closet(profile_id: int):
   
   # DB 연결 및 준비
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 데이터 존재 확인
        # 삭제 명령을 내리기 전에 해당 ID의 옷이 실제로 존재하는지 먼저 조회(SELECT)
        cursor.execute("SELECT profile_id FROM user_measure_profile WHERE profile_id = %s", (profile_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail=f"profile_id {profile_id}를 찾을 수 없습니다.") # 없다면 404 에러 보냄
        
        # 삭제 실행 및 확정
        # 실제로 데이터를 지우는 SQL(DELETE)을 실행하고
        cursor.execute("DELETE FROM user_measure_profile WHERE profile_id = %s", (profile_id,)) 
        connection.commit() # commit을 통해 이 삭제는 되돌리지 않겠다고 확정

        #연결 종료
        cursor.close() 
        connection.close() 

        #성공 응답 반환
        return JSONResponse(content={"success": True, "profile_id": profile_id, "message": "삭제되었습니다."}) 

    # 에러 처리
    # DB 연결이 끊기거나 SQL 오류가 발생했을 때 서버가 죽지 않도록 에러를 잡아서(catch) 500 에러 메시지로 변환
    except Error as e:
        logger.error(f"DB 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"삭제 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# 서버 실행 함수
def start_server(host: str = "0.0.0.0", port: int = None, reload: bool = False): # start_server 라는 이름의 함수 정의
    # Render 등 클라우드 환경에서는 PORT 환경변수 사용
    if port is None:
        port = int(os.getenv('PORT', 8000))
    logger.info(f"서버 시작: http://{host}:{port}") # 서버 시작 정보 기록 출력 
    logger.info(f"API 문서: http://{host}:{port}/docs") # API 문서 정보 기록 출력
    uvicorn.run("api_server:app", host=host, port=port, reload=reload, log_level="info") # uvicorn 이라는 웹서버 프로그램을 실행하여 api_server.py 파일의 app 객체를 실행

# WebSocket(서버와 클라이언트 간 실시간 통신 통로를 열어두는 기술) 엔드포인트
@app.get("/create-session") # create-session 엔드포인트 정의
async def create_session():
    """새 세션 생성 (데스크톱용)""" # create_session 함수 설명
    session_id = manager.create_session() # manager 객체의 create_session 메서드를 호출하여 새로운 세션 ID를 생성
    return {"session_id": session_id} # 세션 ID를 JSON 형식으로 반환

@app.websocket("/ws/desktop/{session_id}")
async def websocket_desktop(websocket: WebSocket, session_id: str):
    """데스크톱 WebSocket 연결"""
    await manager.connect_desktop(session_id, websocket)
    logger.info(f"데스크톱 연결 성공: {session_id}")
    try:
        while True:
            # 데스크톱에서 오는 메시지 처리 (필요시)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 모바일로 메시지 전달
            if message.get('type') == 'command':
                await manager.send_to_mobile(session_id, message)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id, 'desktop')
        logger.info(f"데스크톱 연결 종료: {session_id}")

@app.websocket("/ws/mobile/{session_id}")
async def websocket_mobile(websocket: WebSocket, session_id: str):
    """모바일 WebSocket 연결"""
    await manager.connect_mobile(session_id, websocket)
    try:
        while True:
            # 모바일에서 오는 메시지 처리
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 이미지 데이터를 데스크톱으로 전송
            if message.get('type') == 'image_captured':
                await manager.send_to_desktop(session_id, message)
                logger.info(f"이미지 전송 완료: {session_id}")
            
            # 촬영 조건 상태를 데스크톱으로 전송
            elif message.get('type') == 'capture_status':
                await manager.send_to_desktop(session_id, message)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id, 'mobile')
        logger.info(f"모바일 연결 종료: {session_id}")

# 프론트엔드가 /auth/kakao/login-url로 GET 요청을 보내면 실행되는 함수
@app.get("/auth/kakao/login-url")
async def get_kakao_login_url():
    
    client_id = os.getenv("KAKAO_CLIENT_ID", "") # 서버 설정 파일(.env)에서 KAKAO_CLIENT_ID(앱 키)와
    redirect_uri = os.getenv( # KAKAO_REDIRECT_URI를 가져옴
        "KAKAO_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/kakao/callback" 
    )

    if not client_id: # 만약 client_id가 없다면
        raise HTTPException(
            status_code=500, # 500 에러 발생
            detail="KAKAO_CLIENT_ID가 설정되어 있지 않습니다. .env를 확인하세요.", # 에러 메시지
        )

    login_url = ( # 카카오 인증 서버 주소 뒤에 필요한 정보를 붙여 긴 URL을 만듦
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={client_id}" # (앱 키)
        f"&redirect_uri={redirect_uri}" # (돌아올 주소)
        "&response_type=code" # (인증 코드 받기)
    )

    return {"login_url": login_url} # 완성된 로그인 주소를 JSON 형태로 프론트엔드에 반환
    # 프론트엔드는 이 주소를 받아 사용자를 해당 페이지로 이동


@app.get("/auth/google/login-url")
async def get_google_login_url():
    
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/google/callback"
    )

    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID가 설정되어 있지 않습니다. .env를 확인하세요.",
        )

    login_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )

    return {"login_url": login_url}


@app.get("/auth/naver/login-url")
async def get_naver_login_url():
    
    client_id = os.getenv("NAVER_CLIENT_ID", "")
    redirect_uri = os.getenv(
        "NAVER_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/naver/callback"
    )

    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="NAVER_CLIENT_ID가 설정되어 있지 않습니다. .env를 확인하세요.",
        )

    login_url = (
        "https://nid.naver.com/oauth2.0/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&state=naver_login"
    )

    return {"login_url": login_url}


# ==================== 소셜 로그인 콜백 엔드포인트 ====================

@app.get("/oauth/kakao/callback") # 사용자가 카카오 로그인 창에서 로그인을 마치면 카카오가 사용자를 이 주소로 다시 보냄
async def kakao_callback(code: str = None, error: str = None): # 이때 인증 코드(code)와 에러 메시지(error)를 들고 옴
    
    try:
        logger.info("=" * 50)
        logger.info("카카오 콜백 엔드포인트 호출됨")
        logger.info(f"받은 code: {code[:20] if code else None}..." if code else "code 없음")
        logger.info(f"받은 error: {error}")
        logger.info("=" * 50)
        
        if error: # 사용자가 로그인을 취소했거나 오류가 생겨서 돌아온 경우
            logger.error(f"카카오 로그인 오류: {error}") # 에러 로그
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>로그인 실패</title>
                    </head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2>로그인 실패</h2>
                        <p>카카오 로그인 중 오류가 발생했습니다: {error}</p>
                        <button onclick="window.close()">창 닫기</button>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        if not code: # 인증 코드가 없다면
            logger.error("인증 코드가 없습니다.") # 에러 로그
            raise HTTPException(status_code=400, detail="인증 코드가 없습니다.") # 400 에러 발생
        
        # 1단계: 토큰 교환
        redirect_uri = os.getenv( # KAKAO_REDIRECT_URI를 가져옴
            "KAKAO_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/kakao/callback"
        )
        logger.info(f"토큰 발급 시도 - redirect_uri: {redirect_uri}") 
        access_token = kakao_auth.get_access_token(code, redirect_uri) # 가져온 임시 인증 코드를 카카오 서버에 주고, 진짜 사용할 수 있는 액세스 토큰으로 바꿈
        
        if not access_token: # 액세스 토큰이 없다면
            logger.error("카카오 액세스 토큰 발급 실패") # 에러 로그
            raise HTTPException(status_code=400, detail="카카오 토큰 발급 실패") # 400 에러 발생
        
        logger.info("✅ 카카오 액세스 토큰 발급 성공")
        
        # 2단계: 정보 조회
        user_info = kakao_auth.get_user_info(access_token) # 받은 토큰으로 카카오 서버에 사용자의 이름, 이메일 등의 정보를 받아옴
        if not user_info: # 사용자 정보가 없다면
            logger.error("카카오 사용자 정보 조회 실패")
            raise HTTPException(status_code=400, detail="사용자 정보 조회 실패") # 400 에러 발생
        
        logger.info(f"✅ 카카오 사용자 정보 조회 성공: {user_info.get('name', 'Unknown')}")
        
        # 카카오 계정에 이메일이 없거나 제공 동의를 안 한 경우
        email = user_info.get("email")
        if not email:
            social_id = user_info.get("id", "unknown")
            email = f"kakao_{social_id}@no-email.local" # 로그인 처리를 위해 'kakao_고유번호@...' 같은 가짜 이메일을 임시로 만듦
            logger.info(f"이메일 없음 - 임시 이메일 생성: {email}")
        
        # 사용자가 이미 회원이면 그 사람 정보를 씁니다. 그렇지 않으면 새로 회원가입 시킵니다.
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 사용자의 가입 여부 조회 부분
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # 이미 가입된 사람이면 -> 그 사람 정보를 씀
            logger.info(f"기존 회원 로그인: {email}")
            user = existing_user
            
        else:
            # 가입된 사람이 없으면 -> 새로 회원가입 시킴
            logger.info(f"신규 회원 가입: {email}")
            sql = """
                INSERT INTO users (email, name, social_provider, social_id, password, created_at)
                VALUES (%s, %s, %s, %s, '', NOW())
            """
            
            cursor.execute(sql, (email, user_info.get("name"), 'kakao', user_info.get("id")))
            connection.commit()
            
            # 방금 가입시킨 정보를 다시 가져옵니다.
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        cursor.close()
        connection.close()

        user_data = {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
        # 서비스 안에서 신분을 증명할 자체 토큰(JWT)을 발급
        jwt_token = create_access_token({
                "user_id": user_data["user_id"], 
                "email": user_data["email"]
            })
        
        # 로그인 성공 로그
        logger.info(f"🎉 로그인 성공! 사용자: {user_data.get('name')} (id: {user_data['user_id']})")

        user_name = user_data.get('name', '고객')
        encoded_name = urllib.parse.quote(user_name)
        user_email = user_data.get('email', '')
        
        # 모든 처리가 끝난 후, 발급한 토큰을 URL에 붙여서 사용자를 프론트엔드 홈 화면(home.html)으로 이동
        frontend_url = "http://127.0.0.1:5500/home.html"
        return RedirectResponse(url=f"{frontend_url}?token={jwt_token}&status=success&name={encoded_name}&email={user_email}")

    except Exception as e:
        logger.error(f"카카오 콜백 처리 오류: {str(e)}") 

        return {  # 에러 발생 시 에러 메시지를 반환
        "status": "error",
        "message": "로그인 처리 중 오류 발생",
        "detail": str(e)
        }


@app.get("/oauth/google/callback")
async def google_callback(code: str = None, error: str = None):
   
    try:
        logger.info("=" * 50)
        logger.info("구글 콜백 엔드포인트 호출됨")
        logger.info(f"받은 code: {code[:20] if code else None}..." if code else "code 없음")
        logger.info(f"받은 error: {error}")
        logger.info("=" * 50)
        
        if error:
            logger.error(f"구글 로그인 오류: {error}")
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>로그인 실패</title>
                    </head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2>로그인 실패</h2>
                        <p>구글 로그인 중 오류가 발생했습니다: {error}</p>
                        <button onclick="window.close()">창 닫기</button>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        if not code:
            raise HTTPException(status_code=400, detail="인증 코드가 없습니다.")
        
        # 구글 액세스 토큰 발급
        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/google/callback"
        )
        access_token = google_auth.get_access_token(code, redirect_uri)
        
        if not access_token:
            raise HTTPException(status_code=400, detail="구글 토큰 발급 실패")
        
        # 사용자 정보 조회
        user_info = google_auth.get_user_info(access_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="사용자 정보 조회 실패")
        
        # 이메일이 없는 경우 임시 이메일 생성
        email = user_info.get("email")
        if not email:
            social_id = user_info.get("id", "unknown")
            email = f"google_{social_id}@no-email.local"
        
        # DB 연결 및 사용자 확인/생성
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 1. 먼저 이메일로 가입된 회원이 있는지 찾아봅니다
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # [상황 A] 이미 가입된 사람이면 -> 그 사람 정보를 씀
            logger.info(f"기존 회원 로그인: {email}")
            user = existing_user
        
        else:
            # [상황 B] 가입된 사람이 없으면 -> 새로 회원가입 시킴
            logger.info(f"신규 회원 가입: {email}")
            sql = """
                INSERT INTO users (email, name, social_provider, social_id, password, created_at)
                VALUES (%s, %s, %s, %s, '', NOW())
            """
           
            cursor.execute(sql, (email, user_info.get("name"), 'google', user_info.get("id")))
            connection.commit()
            
            # 방금 가입시킨 정보를 다시 가져옵니다
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        cursor.close()
        connection.close()

        user_data = {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
        
        jwt_token = create_access_token({
                "user_id": user_data["user_id"], 
                "email": user_data["email"]
            })
        
        
        logger.info(f"🎉 로그인 성공! 사용자: {user_data.get('name')} (id: {user_data['user_id']})")
        
        user_name = user_data.get('name', '고객')
        encoded_name = urllib.parse.quote(user_name)
        user_email = user_data.get('email', '')
        
        frontend_url = "http://127.0.0.1:5500/home.html"
        return RedirectResponse(url=f"{frontend_url}?token={jwt_token}&status=success&name={encoded_name}&email={user_email}")
        
    except Exception as e:
        logger.error(f"카카오 콜백 처리 오류: {str(e)}")

        return {  
        "status": "error",
        "message": "로그인 처리 중 오류 발생",
        "detail": str(e)
        }


@app.get("/oauth/naver/callback")
async def naver_callback(code: str = None, state: str = None, error: str = None):
    
    try:
        logger.info("=" * 50)
        logger.info("네이버 콜백 엔드포인트 호출됨")
        logger.info(f"받은 code: {code[:20] if code else None}..." if code else "code 없음")
        logger.info(f"받은 state: {state}")
        logger.info(f"받은 error: {error}")
        logger.info("=" * 50)
        
        if error:
            logger.error(f"네이버 로그인 오류: {error}")
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>로그인 실패</title>
                    </head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h2>로그인 실패</h2>
                        <p>네이버 로그인 중 오류가 발생했습니다: {error}</p>
                        <button onclick="window.close()">창 닫기</button>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        if not code:
            raise HTTPException(status_code=400, detail="인증 코드가 없습니다.")
        
        # 네이버 액세스 토큰 발급
        redirect_uri = os.getenv(
            "NAVER_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/naver/callback"
        )
        access_token = naver_auth.get_access_token(code, redirect_uri)
        
        if not access_token:
            raise HTTPException(status_code=400, detail="네이버 토큰 발급 실패")
        
        # 사용자 정보 조회
        user_info = naver_auth.get_user_info(access_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="사용자 정보 조회 실패")
        
        # 이메일이 없는 경우 임시 이메일 생성
        email = user_info.get("email")
        if not email:
            social_id = user_info.get("id", "unknown")
            email = f"naver_{social_id}@no-email.local"
        
        # DB 연결 및 사용자 확인/생성
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 1. 먼저 이메일로 가입된 회원이 있는지 찾아봅니다
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # [상황 A] 이미 가입된 사람이면 -> 그 사람 정보를 씁니다
            logger.info(f"기존 회원 로그인: {email}")
            user = existing_user
            
        else:
            # [상황 B] 가입된 사람이 없으면 -> 새로 회원가입 시킵니다
            logger.info(f"신규 회원 가입: {email}")
            sql = """
                INSERT INTO users (email, name, social_provider, social_id, password, created_at)
                VALUES (%s, %s, %s, %s, '', NOW())
            """
          
            cursor.execute(sql, (email, user_info.get("name"), 'naver', user_info.get("id")))
            connection.commit()
            
            # 방금 가입시킨 정보를 다시 가져옵니다
            user_id = cursor.lastrowid
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        
        cursor.close()
        connection.close()

        user_data = {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
        
        # JWT 토큰 생성
        jwt_token = create_access_token({
                "user_id": user_data["user_id"], 
                "email": user_data["email"]
            })
        logger.info(f"🎉 로그인 성공! 사용자: {user_data.get('name')} (id: {user_data['user_id']})")
        
        user_name = user_data.get('name', '고객')
        encoded_name = urllib.parse.quote(user_name)
        user_email = user_data.get('email', '')
        
        frontend_url = "http://127.0.0.1:5500/home.html"
        return RedirectResponse(url=f"{frontend_url}?token={jwt_token}&status=success&name={encoded_name}&email={user_email}")
        
    except Exception as e:
        logger.error(f"카카오 콜백 처리 오류: {str(e)}") 

        return {  
        "status": "error",
        "message": "로그인 처리 중 오류 발생",
        "detail": str(e)
        }


# ==================== 1단계: 소셜 로그인 ====================

@app.post("/auth/social-login")
async def social_login(request: SocialLoginRequest):
    
    try:
        logger.info(f"소셜 로그인 요청 - provider: {request.provider}")
        
        # 1. 소셜 플랫폼에서 액세스 토큰 발급
        provider = request.provider.lower()
        if provider == "kakao":
            # redirect_uri를 요청 값이 있으면 그걸 쓰고,
            # 없으면 .env에 설정된 KAKAO_REDIRECT_URI 또는 기본값 사용
            redirect_uri = request.redirect_uri or os.getenv(
                "KAKAO_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/kakao/callback"
            )
            access_token = kakao_auth.get_access_token(request.code, redirect_uri)
            if not access_token:
                raise HTTPException(status_code=400, detail="카카오 토큰 발급 실패")
            user_info = kakao_auth.get_user_info(access_token)
        elif provider == "google":
            redirect_uri = request.redirect_uri or os.getenv(
                "GOOGLE_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/google/callback"
            )
            access_token = google_auth.get_access_token(request.code, redirect_uri)
            if not access_token:
                raise HTTPException(status_code=400, detail="구글 토큰 발급 실패")
            user_info = google_auth.get_user_info(access_token)
        elif provider == "naver":
            redirect_uri = request.redirect_uri or os.getenv(
                "NAVER_REDIRECT_URI", "https://backend-z01u.onrender.com/oauth/naver/callback"
            )
            access_token = naver_auth.get_access_token(request.code, redirect_uri)
            if not access_token:
                raise HTTPException(status_code=400, detail="네이버 토큰 발급 실패")
            user_info = naver_auth.get_user_info(access_token)
        else:
            raise HTTPException(
                status_code=400,
                detail="지원하지 않는 소셜 로그인 제공자입니다. (kakao, google, naver)",
            )
        
        if not user_info:
            raise HTTPException(status_code=400, detail="사용자 정보 조회 실패")

        # 카카오 등에서 이메일 제공 동의를 하지 않았을 때 email 이 None 인 경우가 있음
        # 우리 DB의 users.email 컬럼은 NOT NULL + UNIQUE 이므로,
        # 이메일이 없을 때는 소셜 ID 기반의 임시 이메일을 생성해서 저장한다
        if not user_info.get("email"):
            generated_email = f"{user_info['provider']}_{user_info['social_id']}@no-email.local"
            logger.warning(
                f"소셜 사용자 이메일 없음 - provider={user_info['provider']}, "
                f"social_id={user_info['social_id']}. "
                f"임시 이메일 {generated_email} 사용."
            )
            user_info["email"] = generated_email
        
        # 2. DB 연결
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 3. 소셜 계정으로 기존 사용자 찾기
        cursor.execute(
            "SELECT id, name, email FROM users WHERE social_id = %s AND social_provider = %s",
            (user_info["social_id"], user_info["provider"])
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            # [상황 A] 이미 소셜 연동이 되어있는 사람 -> 바로 로그인
            user_id = existing_user["id"]
            user_data = {
                "user_id": user_id,
                "name": existing_user["name"],
                "email": existing_user["email"]
            }
            logger.info(f"기존 소셜 사용자 로그인: {user_id}")
            
        else:
            # [상황 B] 소셜 연동은 안 되어있음. 하지만 '이메일'이 같은 사람이 있는지 확인!
            cursor.execute("SELECT * FROM users WHERE email = %s", (user_info["email"],))
            email_user = cursor.fetchone()
            
            if email_user:
                # [상황 B-1] 이미 가입된 이메일이 있음 -> 에러 내지 말고 로그인 시켜줌 (통합)
                logger.info(f"기존 이메일 계정으로 로그인 (소셜 연동): {email_user['email']}")
                user_id = email_user["id"]
                user_data = {
                    "user_id": user_id,
                    "name": email_user["name"],
                    "email": email_user["email"]
                }
                
                
            else:
                # [상황 B-2] 이메일도 없음 -> 진짜 신규 가입
                insert_sql = """
                    INSERT INTO users (name, email, social_id, social_provider, password, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """
                # 소셜 로그인 사용자는 비밀번호 없음 (빈 해시)
                cursor.execute(insert_sql, (
                    user_info["name"],
                    user_info["email"],
                    user_info["social_id"],
                    user_info["provider"],
                    ""  # 비밀번호 없음
                ))
                connection.commit()
                user_id = cursor.lastrowid
                
                user_data = {
                    "user_id": user_id,
                    "name": user_info["name"],
                    "email": user_info["email"]
                }
                logger.info(f"신규 소셜 사용자 가입: {user_id}")
        
        cursor.close()
        connection.close()
        
        # JWT 토큰 생성
        jwt_token = create_access_token({
                "user_id": user_data["user_id"], 
                "email": user_data["email"]
            })
        logger.info(f"🎉 로그인 성공! 사용자: {user_data.get('name')} (id: {user_data['user_id']})")
        
        return JSONResponse(content={
            "success": True,
            "user": user_data,
            "access_token": jwt_token,
            "token_type": "bearer",
            "message": "소셜 로그인 성공"
        })
        
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"소셜 로그인 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"소셜 로그인 처리 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 1단계: 로그아웃 ====================
# 로그아웃 요청 수신
@app.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    
    try: # 요청에 Bearer 토큰값 형태의 인증 정보가 제대로 들어있는지 검사
        if not authorization or not authorization.startswith("Bearer "): # 토큰이 없으면 로그아웃 처리를 할 수 없으므로
            raise HTTPException(status_code=401, detail="인증 토큰이 없습니다.") # 401 에러 발생
        
        token = authorization.split(" ")[1] # 토큰 값을 추출
        
        # 추출한 토큰을 서버의 블랙리스트에 등록
        token_blacklist.add(token) 
        
        logger.info("로그아웃 성공") # 로그아웃 처리가 완료되었음을 알림
        
        return JSONResponse(content={ 
            "success": True,
            "message": "로그아웃되었습니다."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그아웃 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 1단계: 비밀번호 재설정 이메일 발송 ====================
# 비밀번호 재설정 요청
@app.post("/auth/password-reset/request")
async def request_password_reset(request: PasswordResetRequest):
   
    try:
        logger.info(f"비밀번호 재설정 요청: {request.email}")
        
        # 데이터베이스에 접속하여 작업을 준비 
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 입력받은 이메일이 우리 서비스에 가입된 이메일인지 확인
        cursor.execute("SELECT id, email FROM users WHERE email = %s", (request.email,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # 보안을 위해 만약 가입되지 않은 이메일이라도 없는 회원입니다라고 알려주지 않음 
        if not user:
            logger.warning(f"존재하지 않는 이메일로 재설정 요청: {request.email}")
            return JSONResponse(content={
                "success": True,
                "message": "비밀번호 재설정 링크가 이메일로 발송되었습니다."
            })
        
        # 비밀번호 변경 권한이 담긴 재설정 토큰을 생성
        reset_token = create_reset_token(request.email)
        
        # 생성된 토큰을 포함한 비밀번호 재설정 링크(URL)를 사용자의 이메일로 전송
        app_url = os.getenv("APP_URL", "https://backend-z01u.onrender.com")
        email_sent = send_password_reset_email(request.email, reset_token, app_url)
        
        if not email_sent:
            logger.warning("이메일 발송 실패")
        
        return JSONResponse(content={ # 이메일 발송 작업이 끝났음을 알림
            "success": True,
            "message": "비밀번호 재설정 링크가 이메일로 발송되었습니다."
        })
        
    except Error as e:
        logger.error(f"비밀번호 재설정 요청 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"비밀번호 재설정 요청 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
# 비밀번호 변경 확정 함수
@app.post("/auth/password-reset/confirm")
async def confirm_password_reset(request: PasswordChangeRequest):
   
    try:
        # 가져온 토큰이 유효한지 확인하고 그 안에 담긴 이메일 주소를 추출
        email = verify_reset_token(request.token)
        if not email:
            raise HTTPException(status_code=400, detail="유효하지 않거나 만료된 토큰입니다.") #  실패하면 400 에러 발생
        
        logger.info(f"비밀번호 재설정 확정: {email}")
        
        # 사용자가 입력한 새 비밀번호를 그대로 저장하지 않고
        new_password_hash = hash_password(request.new_password) # hash_password 함수를 통해 안전하게 암호화
        
        # DB에서 해당 이메일을 가진 사용자를 찾아
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute( # 비밀번호 칸을 방금 만든 새 암호문으로 바꿔치기
            "UPDATE users SET password = %s WHERE email = %s",
            (new_password_hash, email)
        )
        connection.commit() # commit()을 통해 변경 확정
        
        cursor.close()
        connection.close()
        
        return JSONResponse(content={ # 모든 절차가 끝났음을 알리는 메시지를 반환
            "success": True,
            "message": "비밀번호가 성공적으로 변경되었습니다."
        })
        
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"비밀번호 변경 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"비밀번호 변경 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 2단계: 회원 탈퇴 ====================
# 탈퇴 요청 수신 (DELETE)
@app.delete("/auth/withdraw/{user_id}")
async def withdraw_user(user_id: int, authorization: Optional[str] = Header(None)):
    
    try:
        #  토큰 유무 확인
        if not authorization or not authorization.startswith("Bearer "): # 요청에 인증 토큰이 붙어있는지 확인
            raise HTTPException(status_code=401, detail="인증 토큰이 없습니다.") # 토큰이 없거나 형식이 잘못되었다면 401 에러 발생
        
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        
        # 토큰 속의 주인(user_id)과 탈퇴하려는 대상(user_id)이 일치하는지 확인
        if not payload or payload.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="본인만 탈퇴할 수 있습니다.")
        
        logger.info(f"회원 탈퇴 요청: user_id={user_id}")
        
        # 데이터베이스에 접속해서
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 사용자가 실제로 존재하는지 다시 한번 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone(): # 이미 탈퇴했거나 없는 계정이면
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.") # 404 에러 발생
        
        # 사용자를 지우기 전에 사용자가 저장했던 옷 치수 데이터를 먼저 지움
        cursor.execute("DELETE FROM user_measure_profile WHERE user_id = %s", (user_id,))
        
        # 그 다음 사용자 테이블에서 사용자를 완전히 지움
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit() # commit()을 통해 삭제 확정
        
        cursor.close()
        connection.close()
        
        # 탈퇴한 사용자가 갖고 있던 토큰을 블랙리스트에 등록
        token_blacklist.add(token)
        
        logger.info(f"회원 탈퇴 완료: user_id={user_id}")
        
        return JSONResponse(content={ # 모든 절차가 끝났음을 알리는 메시지를 반환
            "success": True,
            "message": "회원 탈퇴가 완료되었습니다."
        })
        
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"회원 탈퇴 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"회원 탈퇴 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 카테고리 목록 조회 ====================
# 카테고리 조회 API
@app.get("/categories")
async def get_categories():
    
    try:
        logger.info("카테고리 목록 조회 요청")

        connection = get_db_connection() # 데이터베이스에 접속하고
        cursor = connection.cursor(dictionary=True) # 결과를 딕셔너리 형태(Key: Value)로 받기 위한 커서를 준비

        # SELECT * FROM categories` 명령어로 카테고리 테이블의 모든 데이터를 가져옴
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()

        cursor.close()
        connection.close()

        logger.info(f"카테고리 목록 조회 완료: {len(categories)}개")

        return JSONResponse(content={ # 가져온 목록을 JSON 형식으로 변환해서 프론트엔드에 보냄
            "success": True,
            "count": len(categories),
            "categories": jsonable_encoder(categories) # jsonable_encoder: DB 데이터를 JSON으로 바꿀 때 생기는 호환성 문제 해결
        })

    except Error as e:
        logger.error(f"카테고리 목록 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"카테고리 목록 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


# ==================== 2단계: 상품 검색 ====================
# 상품 검색 API
@app.get("/products/search")
async def search_products(
    keyword: str, # 검색 키워드
    category: Optional[str] = None, # 카테고리 필터
    min_price: Optional[float] = None, # 최소 가격 필터
    max_price: Optional[float] = None, # 최대 가격 필터
    limit: int = 20 # 결과 개수 제한
):
    
    try:
        logger.info(f"상품 검색 요청: keyword={keyword}, category={category}")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 동적 SQL 쿼리 생성
        sql = "SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s)"
        params = [f"%{keyword}%", f"%{keyword}%"]
        
        if category:
            sql += " AND category = %s"
            params.append(category)
        
        if min_price is not None:
            sql += " AND price >= %s"
            params.append(min_price)
        
        if max_price is not None:
            sql += " AND price <= %s"
            params.append(max_price)
        
        sql += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, tuple(params))
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        logger.info(f"검색 완료: {len(products)}개 상품")
        
        return JSONResponse(content={
            "success": True,
            "keyword": keyword,
            "count": len(products),
            "products": jsonable_encoder(products)
        })
        
    except Error as e:
        logger.error(f"상품 검색 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"상품 검색 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 상품 목록 조회 ====================
# 상품 목록 조회 API
@app.get("/products")
async def get_products(
    page: int = 1, # 페이지 번호
    limit: int = 20, # 페이지당 상품 개수
    category_id: Optional[int] = None, # 전체상품 보여주기
    sort_by: str = "created_at", # 정렬 기준 (날짜순)
    order: str = "desc" # 정렬 기준 (내림차순)
):
    
    try:
        logger.info(f"상품 목록 조회: page={page}, limit={limit}, category_id={category_id}")
        
        # 페이지 검증
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        # 정렬 기준 검증
        allowed_sort_fields = ["created_at", "price", "name", "id"]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"
        
        # 정렬 순서 검증
        order = order.lower()
        if order not in ["asc", "desc"]:
            order = "desc"
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 전체 상품 개수 조회
        count_sql = "SELECT COUNT(*) as total FROM products"
        count_params = []
        
        if category_id:
            count_sql += " WHERE category_id = %s"
            count_params.append(category_id)
        
        cursor.execute(count_sql, tuple(count_params))
        total_count = cursor.fetchone()["total"]
        
        # 상품 목록 조회
        offset = (page - 1) * limit
        
        sql = "SELECT * FROM products"
        params = []
        
        if category_id:
            sql += " WHERE category_id = %s"
            params.append(category_id)
        
        sql += f" ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(sql, tuple(params))
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # 페이지 정보 계산
        total_pages = (total_count + limit - 1) // limit  # 올림 계산
        
        logger.info(f"상품 목록 조회 완료: {len(products)}개 (전체 {total_count}개)")
        
        return JSONResponse(content={
            "success": True,
            "products": jsonable_encoder(products),
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "limit": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })
        
    except Error as e:
        logger.error(f"상품 목록 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"상품 목록 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 상품 상세 조회 ====================
# 상품 상세 조회 API
@app.get("/products/{product_id}")
async def get_product_detail(product_id: int): # 상품 아이디
    
    try:
        logger.info(f"상품 상세 조회: product_id={product_id}") # 상품 상세 조회 로그
        
        connection = get_db_connection() # 데이터베이스에 접속하고
        cursor = connection.cursor(dictionary=True) # 결과를 딕셔너리 형태(Key: Value)로 받기 위한 커서를 준비
        
        # 상품 테이블에서 해당 상품 아이디를 가진 상품의 정보를 조회
        cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """, (product_id,))
        
        product = cursor.fetchone() # 조회된 상품 정보를 변수에 저장
        
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.") # 상품이 없으면 404 에러 발생
        
        # 상품 사이즈 옵션 테이블에서 해당 상품 아이디를 가진 상품의 사이즈 옵션 정보를 조회
        cursor.execute("""
            SELECT size_option_id, option_name, stock_quantity
            FROM product_size_option
            WHERE product_id = %s
            ORDER BY size_option_id
        """, (product_id,))
        
        size_options = cursor.fetchall()
        
        # 3. 실측 정보 조회 (사이즈 옵션별)
        measurements = []
        for size_option in size_options:
            cursor.execute("""
                SELECT *
                FROM product_real_measure
                WHERE size_option_id = %s
            """, (size_option['size_option_id'],))
            
            measure = cursor.fetchone()
            if measure:
                measurements.append({
                    "size_option_id": size_option['size_option_id'],
                    "size_name": size_option['option_name'],
                    "measurements": measure
                })
        
        # 4. 상품 이미지 조회
        cursor.execute("""
            SELECT image_url, image_type
            FROM product_images
            WHERE product_id = %s
            ORDER BY image_type, product_image_id
        """, (product_id,))
        
        images = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # 응답 데이터 구성
        result = {
            "success": True,
            "product": jsonable_encoder(product),
            "size_options": jsonable_encoder(size_options),
            "measurements": jsonable_encoder(measurements),
            "images": jsonable_encoder(images)
        }
        
        logger.info(f"상품 상세 조회 완료: {product['name']}")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"상품 상세 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"상품 상세 조회 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ==================== 장바구니(Cart) ====================
# 장바구니 담기 API
@app.post("/cart") # 프론트엔드가 상품 ID와 수량을 보내면 이 함수가 실행
async def add_to_cart(request: CartItemCreateRequest):
    
    try:
        logger.info(
            f"장바구니 추가 요청 - user_id={request.user_id}, "
            f"product_id={request.product_id}, quantity={request.quantity}"
        )

        if request.quantity < 1: # 수량이 1개 미만인지 확인
            raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

        connection = get_db_connection() 
        cursor = connection.cursor(dictionary=True)

        # DB에서 해당 사용자가 진짜 회원인지
        cursor.execute("SELECT id FROM users WHERE id = %s", (request.user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 해당 상품이 실제로 존재하고 판매 중인지 확인
        cursor.execute("SELECT id, stock_quantity, price, name FROM products WHERE id = %s", (request.product_id,))
        product = cursor.fetchone()
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

        # 이미 장바구니에 똑같은 상품을 담아뒀는지 확인
        cursor.execute(
            "SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s", 
            (request.user_id, request.product_id),
        )
        existing = cursor.fetchone()

        if existing: # 이미 담긴 상품이라면
            new_quantity = existing["quantity"] + request.quantity # 기존 수량에 더해서 총수량을 계산
            if new_quantity > product["stock_quantity"]:
                cursor.close()
                connection.close()
                raise HTTPException( # 이때 재고보다 많이 담게 되면 에러 발생
                    status_code=400,
                    detail=f"재고 부족: 최대 {product['stock_quantity']}개까지 담을 수 있습니다.",
                )

            cursor.execute(
                "UPDATE cart SET quantity = %s WHERE id = %s",
                (new_quantity, existing["id"]),
            )
            cart_id = existing["id"]
            quantity = new_quantity
        else: # 처음 담는 상품이라면
            if request.quantity > product["stock_quantity"]: 
                cursor.close()
                connection.close()
                raise HTTPException( 
                    status_code=400,
                    detail=f"재고 부족: 최대 {product['stock_quantity']}개까지 담을 수 있습니다.",
                )

            cursor.execute( # 장바구니 테이블에 새로운 항목 추가
                """
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (request.user_id, request.product_id, request.quantity),
            )
            cart_id = cursor.lastrowid
            quantity = request.quantity

        connection.commit()

        # 장바구니 항목 조회용 응답 데이터
        line_total = float(product["price"]) * quantity

        cursor.close()
        connection.close()

        logger.info(f"장바구니 추가/수정 완료 - cart_id={cart_id}, quantity={quantity}")

        return JSONResponse(
            content={
                "success": True,
                "cart_item": {
                    "cart_id": cart_id,
                    "user_id": request.user_id,
                    "product_id": request.product_id,
                    "product_name": product["name"],
                    "price": float(product["price"]),
                    "quantity": quantity,
                    "line_total": line_total,
                },
                "message": "장바구니에 상품이 추가되었습니다.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"장바구니 추가 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"장바구니 추가 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/cart")
async def get_cart(user_id: int):
    
    try:
        logger.info(f"장바구니 조회 요청 - user_id={user_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 사용자 존재 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 장바구니 + 상품 정보 조인
        cursor.execute(
            """
            SELECT 
                c.id AS cart_id,
                c.quantity,
                p.id AS product_id,
                p.name,
                p.price,
                p.stock_quantity,
                p.category_id
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
            ORDER BY c.id DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        items = []
        total_amount = 0.0

        for row in rows:
            price = float(row["price"])
            qty = row["quantity"]
            line_total = price * qty
            total_amount += line_total

            items.append(
                {
                    "cart_id": row["cart_id"],
                    "product_id": row["product_id"],
                    "product_name": row["name"],
                    "price": price,
                    "quantity": qty,
                    "line_total": line_total,
                    "stock_quantity": row["stock_quantity"],
                    "category_id": row["category_id"],
                }
            )

        logger.info(f"장바구니 조회 완료 - {len(items)}개 항목, total_amount={total_amount}")

        return JSONResponse(
            content={
                "success": True,
                "user_id": user_id,
                "items": items,
                "total_amount": total_amount,
                "count": len(items),
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"장바구니 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"장바구니 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.patch("/cart/{cart_id}")
async def update_cart_item(cart_id: int, request: CartItemUpdateRequest):
    
    try:
        logger.info(f"장바구니 수량 변경 요청 - cart_id={cart_id}, quantity={request.quantity}")

        if request.quantity < 1:
            raise HTTPException(status_code=400, detail="수량은 1 이상이어야 합니다.")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 장바구니 항목 + 상품 정보 조회
        cursor.execute(
            """
            SELECT c.id, c.user_id, c.product_id, c.quantity, p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.id = %s
            """,
            (cart_id,),
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")

        if request.quantity > row["stock_quantity"]:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=400,
                detail=f"재고 부족: 최대 {row['stock_quantity']}개까지 설정할 수 있습니다.",
            )

        cursor.execute(
            "UPDATE cart SET quantity = %s WHERE id = %s", (request.quantity, cart_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        logger.info("장바구니 수량 변경 완료")

        return JSONResponse(
            content={
                "success": True,
                "cart_id": cart_id,
                "quantity": request.quantity,
                "message": "장바구니 수량이 변경되었습니다.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"장바구니 수량 변경 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"장바구니 수량 변경 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.delete("/cart/{cart_id}")
async def delete_cart_item(cart_id: int):
    
    try:
        logger.info(f"장바구니 삭제 요청 - cart_id={cart_id}")

        connection = get_db_connection()
        cursor = connection.cursor()

        # 존재 여부 확인
        cursor.execute("SELECT id FROM cart WHERE id = %s", (cart_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")

        cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
        connection.commit()

        cursor.close()
        connection.close()

        logger.info("장바구니 항목 삭제 완료")

        return JSONResponse(
            content={
                "success": True,
                "cart_id": cart_id,
                "message": "장바구니 항목이 삭제되었습니다.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"장바구니 삭제 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"장바구니 삭제 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


# ==================== 위시리스트(Wishlist) ====================
# 위시리스트 추가 API
@app.post("/wishlist") # 사용자가 상품 페이지에서 찜 버튼을 누르면 이 함수가 실행
async def add_to_wishlist(request: WishlistCreateRequest):
    
    try:
        logger.info(
            f"위시리스트 추가 요청 - user_id={request.user_id}, "
            f"product_id={request.product_id}"
        )

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # DB에서 해당 회원이 존재하는지
        cursor.execute("SELECT id FROM users WHERE id = %s", (request.user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 찜하려는 상품이 실제로 존재하는지 확인
        cursor.execute(
            "SELECT id, name, price FROM products WHERE id = %s",
            (request.product_id,),
        )
        product = cursor.fetchone() 
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

        # 이미 위시리스트에 담아둔 상품인지 확인
        cursor.execute(
            "SELECT id FROM wishlist WHERE user_id = %s AND product_id = %s",
            (request.user_id, request.product_id),
        )
        existing = cursor.fetchone()

        if existing: # 이미 찜한 상품이라면 아무것도 하지 않고
            wishlist_id = existing["id"]
            created_new = False
        else:
            cursor.execute( # 처음 찜하는 상품이라면 DB에 새로 저장
                """
                INSERT INTO wishlist (user_id, product_id)
                VALUES (%s, %s)
                """,
                (request.user_id, request.product_id),
            )
            wishlist_id = cursor.lastrowid
            connection.commit()
            created_new = True

        cursor.close()
        connection.close()

        logger.info(f"위시리스트 추가/유지 완료 - wishlist_id={wishlist_id}")

        return JSONResponse( # 처리가 완료되었음을 알림
            content={
                "success": True,
                "wishlist_id": wishlist_id,
                "product": {
                    "product_id": product["id"],
                    "name": product["name"],
                    "price": float(product["price"]),
                },
                "created": created_new,
                "message": "위시리스트에 추가되었습니다."
                if created_new
                else "이미 위시리스트에 있는 상품입니다.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"위시리스트 추가 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"위시리스트 추가 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/wishlist")
async def get_wishlist(user_id: int):
    
    try:
        logger.info(f"위시리스트 조회 요청 - user_id={user_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 사용자 존재 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        cursor.execute(
            """
            SELECT 
                w.id AS wishlist_id,
                p.id AS product_id,
                p.name,
                p.price,
                p.category_id
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            WHERE w.user_id = %s
            ORDER BY w.id DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        items = []
        for row in rows:
            items.append(
                {
                    "wishlist_id": row["wishlist_id"],
                    "product_id": row["product_id"],
                    "product_name": row["name"],
                    "price": float(row["price"]),
                    "category_id": row["category_id"],
                }
            )

        logger.info(f"위시리스트 조회 완료 - {len(items)}개 항목")

        return JSONResponse(
            content={
                "success": True,
                "user_id": user_id,
                "items": items,
                "count": len(items),
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"위시리스트 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"위시리스트 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.delete("/wishlist/{wishlist_id}")
async def delete_wishlist_item(wishlist_id: int):
    
    try:
        logger.info(f"위시리스트 삭제 요청 - wishlist_id={wishlist_id}")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM wishlist WHERE id = %s", (wishlist_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="위시리스트 항목을 찾을 수 없습니다.")

        cursor.execute("DELETE FROM wishlist WHERE id = %s", (wishlist_id,))
        connection.commit()

        cursor.close()
        connection.close()

        logger.info("위시리스트 항목 삭제 완료")

        return JSONResponse(
            content={
                "success": True,
                "wishlist_id": wishlist_id,
                "message": "위시리스트에서 삭제되었습니다.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"위시리스트 삭제 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"위시리스트 삭제 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


# ==================== 주문(Orders) ====================

@app.post("/orders/from-cart")
async def create_order_from_cart(request: OrderFromCartRequest):
    
    try:
        logger.info(f"주문 생성 요청(from cart) - user_id={request.user_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. 사용자 존재 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (request.user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 2. 장바구니 조회
        cursor.execute(
            """
            SELECT 
                c.id AS cart_id,
                c.quantity,
                p.id AS product_id,
                p.name,
                p.price,
                p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
            """,
            (request.user_id,),
        )
        cart_rows = cursor.fetchall()

        if not cart_rows:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=400, detail="장바구니에 담긴 상품이 없습니다.")

        # 3. 재고 및 총액 계산
        total_price = 0.0
        for row in cart_rows:
            if row["quantity"] > row["stock_quantity"]:
                cursor.close()
                connection.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"재고 부족: '{row['name']}' 상품의 재고가 부족합니다.",
                )
            total_price += float(row["price"]) * row["quantity"]

        # 4. 주문 테이블에 삽입
        cursor.execute(
            """
            INSERT INTO orders (user_id, total_price, status)
            VALUES (%s, %s, %s)
            """,
            (request.user_id, total_price, "결제대기"),
        )
        order_id = cursor.lastrowid

        # 5. 주문 상품(orderitems) 삽입
        for row in cart_rows:
            cursor.execute(
                """
                INSERT INTO orderitems (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, row["product_id"], row["quantity"], float(row["price"])),
            )

            # 재고 차감 (선택적; 필요하다면 사용)
            cursor.execute(
                """
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE id = %s
                """,
                (row["quantity"], row["product_id"]),
            )

        # 6. 결제 레코드(임시) 삽입 - 실제 결제 연동 전까지는 '대기' 상태
        cursor.execute(
            """
            INSERT INTO payments (order_id, method, amount, status)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, request.payment_method, total_price, "대기"),
        )

        # 7. 배송 정보 삽입
        cursor.execute(
            """
            INSERT INTO shipping (order_id, address, receiver_name, receiver_phone, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                order_id,
                request.address,
                request.receiver_name,
                request.receiver_phone,
                "준비중",
            ),
        )

        # 8. 장바구니 비우기
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (request.user_id,))

        connection.commit()

        cursor.close()
        connection.close()

        logger.info(f"주문 생성 완료 - order_id={order_id}, total_price={total_price}")

        return JSONResponse(
            content={
                "success": True,
                "order_id": order_id,
                "total_price": total_price,
                "status": "결제대기",
                "message": "주문이 생성되었습니다. 결제를 진행해주세요.",
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"주문 생성 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"주문 생성 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/orders/my")
async def get_my_orders(user_id: int):
   
    try:
        logger.info(f"주문 목록 조회 요청 - user_id={user_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 사용자 존재 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        cursor.execute(
            """
            SELECT 
                o.id AS order_id,
                o.total_price,
                o.status,
                o.created_at,
                s.status AS shipping_status,
                s.address
            FROM orders o
            LEFT JOIN shipping s ON o.id = s.order_id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
            """,
            (user_id,),
        )

        orders = cursor.fetchall()
        cursor.close()
        connection.close()

        # 날짜 문자열로 변환
        for order in orders:
            if order.get("created_at"):
                order["created_at"] = order["created_at"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            order["total_price"] = float(order["total_price"])

        logger.info(f"주문 목록 조회 완료 - {len(orders)}건")

        return JSONResponse(
            content={
                "success": True,
                "user_id": user_id,
                "orders": jsonable_encoder(orders),
                "count": len(orders),
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"주문 목록 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"주문 목록 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/orders/{order_id}")
async def get_order_detail(order_id: int):
   
    ##주문 상세 조회

    #주문 기본 정보
    #주문 상품 목록
    #결제 정보
    #배송 정보
    
    try:
        logger.info(f"주문 상세 조회 요청 - order_id={order_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. 주문 기본 정보
        cursor.execute(
            """
            SELECT 
                o.id AS order_id,
                o.user_id,
                o.total_price,
                o.status,
                o.created_at
            FROM orders o
            WHERE o.id = %s
            """,
            (order_id,),
        )
        order = cursor.fetchone()

        if not order:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")

        # 2. 주문 상품 목록
        cursor.execute(
            """
            SELECT 
                oi.id AS order_item_id,
                oi.product_id,
                oi.quantity,
                oi.unit_price,
                p.name
            FROM orderitems oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
            """,
            (order_id,),
        )
        items = cursor.fetchall()

        # 3. 결제 정보
        cursor.execute(
            """
            SELECT 
                id AS payment_id,
                method,
                amount,
                status,
                paid_at
            FROM payments
            WHERE order_id = %s
            """,
            (order_id,),
        )
        payment = cursor.fetchone()

        # 4. 배송 정보
        cursor.execute(
            """
            SELECT 
                id AS shipping_id,
                address,
                receiver_name,
                receiver_phone,
                status,
                shipped_at,
                delivered_at
            FROM shipping
            WHERE order_id = %s
            """,
            (order_id,),
        )
        shipping = cursor.fetchone()

        cursor.close()
        connection.close()

        # 타입/날짜 정리
        order["total_price"] = float(order["total_price"])
        if order.get("created_at"):
            order["created_at"] = order["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        for item in items:
            item["unit_price"] = float(item["unit_price"])

        if payment:
            payment["amount"] = float(payment["amount"])
            if payment.get("paid_at"):
                payment["paid_at"] = payment["paid_at"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        for dt_field in ["shipped_at", "delivered_at"]:
            if shipping and shipping.get(dt_field):
                shipping[dt_field] = shipping[dt_field].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        logger.info(f"주문 상세 조회 완료 - order_id={order_id}")

        return JSONResponse(
            content={
                "success": True,
                "order": jsonable_encoder(order),
                "items": jsonable_encoder(items),
                "payment": jsonable_encoder(payment) if payment else None,
                "shipping": jsonable_encoder(shipping) if shipping else None,
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"주문 상세 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"주문 상세 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


# ==================== 사이즈 추천 ====================

@app.post("/products/{product_id}/recommend-size")
async def recommend_size(product_id: int, user_profile_id: int):
    """
    사이즈 추천 API
    
    사용자의 옷장에 저장된 옷 치수와 상품의 실측 치수를 비교하여
    가장 적합한 사이즈를 추천합니다.
    """
    try:
        logger.info(
            f"사이즈 추천 요청 - product_id={product_id}, "
            f"user_profile_id={user_profile_id}"
        )

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. 사용자의 옷 치수 정보 가져오기
        cursor.execute(
            """
            SELECT 
                profile_id,
                profile_name,
                category,
                top_length, top_shoulder, top_chest, top_sleeve,
                bottom_length, bottom_waist, bottom_rise, bottom_hip, bottom_thigh, bottom_hem
            FROM user_measure_profile
            WHERE profile_id = %s
            """,
            (user_profile_id,)
        )
        user_profile = cursor.fetchone()

        if not user_profile:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=404, 
                detail="사용자 프로필을 찾을 수 없습니다."
            )

        # 2. 상품 정보 및 카테고리 확인
        cursor.execute(
            """
            SELECT p.id, p.name, p.category_id, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
            """,
            (product_id,)
        )
        product = cursor.fetchone()

        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=404, 
                detail="상품을 찾을 수 없습니다."
            )

        # 3. 상품의 모든 사이즈 옵션 및 실측 정보 가져오기
        cursor.execute(
            """
            SELECT 
                pso.size_option_id,
                pso.option_name,
                pso.stock_quantity,
                prm.category,
                prm.top_length, prm.top_shoulder, prm.top_chest, prm.top_sleeve,
                prm.bottom_length, prm.bottom_waist, prm.bottom_rise, 
                prm.bottom_hip, prm.bottom_thigh, prm.bottom_hem
            FROM product_size_option pso
            LEFT JOIN product_real_measure prm ON pso.size_option_id = prm.size_option_id
            WHERE pso.product_id = %s
            ORDER BY pso.size_option_id
            """,
            (product_id,)
        )
        size_options = cursor.fetchall()

        cursor.close()
        connection.close()

        if not size_options:
            raise HTTPException(
                status_code=404, 
                detail="해당 상품의 사이즈 정보를 찾을 수 없습니다."
            )

        # 4. 카테고리 일치 여부 확인
        user_category = user_profile['category']
        product_category = size_options[0]['category'] if size_options[0].get('category') else None

        if not product_category:
            raise HTTPException(
                status_code=400,
                detail="상품의 카테고리 정보가 없습니다."
            )

        if user_category != product_category:
            raise HTTPException(
                status_code=400,
                detail=f"카테고리가 일치하지 않습니다. 사용자: {user_category}, 상품: {product_category}"
            )

        # 5. 각 사이즈별로 적합도 계산
        recommendations = []
        
        for size_option in size_options:
            score_details = {}
            total_score = 0
            count = 0

            if user_category == "상의":
                # 상의 비교 항목
                measurements = [
                    ('length', 'top_length', '총장', 3.0),      # 가중치 3.0
                    ('shoulder', 'top_shoulder', '어깨', 2.5),  # 가중치 2.5
                    ('chest', 'top_chest', '가슴', 3.0),        # 가중치 3.0
                    ('sleeve', 'top_sleeve', '소매', 2.0)       # 가중치 2.0
                ]
            else:  # 하의
                measurements = [
                    ('length', 'bottom_length', '총장', 2.5),
                    ('waist', 'bottom_waist', '허리', 3.5),
                    ('rise', 'bottom_rise', '밑위', 2.0),
                    ('hip', 'bottom_hip', '엉덩이', 3.0),
                    ('thigh', 'bottom_thigh', '허벅지', 2.5),
                    ('hem', 'bottom_hem', '밑단', 1.5)
                ]

            # 각 치수 항목별 비교
            for key, field, label, weight in measurements:
                user_value = user_profile.get(field)
                product_value = size_option.get(field)

                if user_value and product_value:
                    user_value = float(user_value)
                    product_value = float(product_value)
                    
                    # 차이 계산
                    diff = abs(product_value - user_value)
                    
                    # 점수 계산 (차이가 적을수록 높은 점수)
                    # 0cm 차이: 100점, 1cm: 90점, 2cm: 80점, 3cm: 70점...
                    item_score = max(0, 100 - (diff * 10))
                    
                    # 가중치 적용
                    weighted_score = item_score * weight
                    
                    total_score += weighted_score
                    count += weight
                    
                    score_details[label] = {
                        "user_measurement": round(user_value, 1),
                        "product_measurement": round(product_value, 1),
                        "difference": round(diff, 1),
                        "score": round(item_score, 1),
                        "weight": weight
                    }

            # 평균 점수 계산
            final_score = (total_score / count) if count > 0 else 0

            # 재고 여부 확인
            in_stock = size_option['stock_quantity'] > 0

            recommendations.append({
                "size_option_id": size_option['size_option_id'],
                "size_name": size_option['option_name'],
                "fit_score": round(final_score, 1),
                "fit_level": _get_fit_level(final_score),
                "score_details": score_details,
                "in_stock": in_stock,
                "stock_quantity": size_option['stock_quantity']
            })

        # 6. 점수순으로 정렬
        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)

        # 7. 최고 점수 사이즈를 추천으로 표시
        if recommendations:
            recommendations[0]['is_recommended'] = True
            for rec in recommendations[1:]:
                rec['is_recommended'] = False

        logger.info(
            f"사이즈 추천 완료 - {len(recommendations)}개 사이즈 분석, "
            f"추천: {recommendations[0]['size_name'] if recommendations else 'N/A'}"
        )

        return JSONResponse(
            content={
                "success": True,
                "product_id": product_id,
                "product_name": product['name'],
                "user_profile_id": user_profile_id,
                "user_profile_name": user_profile['profile_name'],
                "category": user_category,
                "recommendations": recommendations,
                "message": f"총 {len(recommendations)}개의 사이즈를 분석했습니다."
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"사이즈 추천 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"사이즈 추천 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


def _get_fit_level(score: float) -> str:
    """적합도 점수를 텍스트로 변환"""
    if score >= 90:
        return "매우 적합"
    elif score >= 80:
        return "적합"
    elif score >= 70:
        return "보통"
    elif score >= 60:
        return "약간 작음/큼"
    else:
        return "맞지 않음"


# ==================== 리뷰(Reviews) ====================

@app.post("/reviews")
async def create_review(request: ReviewCreateRequest):
    """
    리뷰 등록 API
    
    사용자가 구매한 상품에 대한 리뷰를 작성합니다.
    """
    try:
        logger.info(
            f"리뷰 등록 요청 - user_id={request.user_id}, "
            f"product_id={request.product_id}, rating={request.rating}"
        )

        # 입력값 검증
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(
                status_code=400, 
                detail="별점은 1~5 사이의 값이어야 합니다."
            )

        if request.size_feedback and (request.size_feedback < 1 or request.size_feedback > 3):
            raise HTTPException(
                status_code=400,
                detail="사이즈 체감은 1(작음), 2(적당함), 3(큼) 중 하나여야 합니다."
            )

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 사용자 존재 확인
        cursor.execute("SELECT id FROM users WHERE id = %s", (request.user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 상품 존재 확인
        cursor.execute(
            "SELECT id, name FROM products WHERE id = %s", 
            (request.product_id,)
        )
        product = cursor.fetchone()
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

        # 리뷰 등록
        cursor.execute(
            """
            INSERT INTO reviews (user_id, product_id, rating, content, size_feedback)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                request.user_id,
                request.product_id,
                request.rating,
                request.content,
                request.size_feedback
            )
        )
        connection.commit()
        review_id = cursor.lastrowid

        cursor.close()
        connection.close()

        logger.info(f"리뷰 등록 완료 - review_id={review_id}")

        return JSONResponse(
            content={
                "success": True,
                "review_id": review_id,
                "message": "리뷰가 등록되었습니다.",
                "product_name": product["name"]
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"리뷰 등록 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"리뷰 등록 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/reviews")
async def get_reviews(
    product_id: Optional[int] = None,
    user_id: Optional[int] = None,
    rating: Optional[int] = None,
    page: int = 1,
    limit: int = 20
):
    """
    리뷰 조회 API
    
    특정 상품의 리뷰 목록 또는 특정 사용자가 작성한 리뷰를 조회합니다.
    """
    try:
        logger.info(
            f"리뷰 조회 요청 - product_id={product_id}, "
            f"user_id={user_id}, rating={rating}, page={page}"
        )

        # 페이지 검증
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 동적 SQL 쿼리 생성
        where_conditions = []
        params = []

        if product_id:
            where_conditions.append("r.product_id = %s")
            params.append(product_id)

        if user_id:
            where_conditions.append("r.user_id = %s")
            params.append(user_id)

        if rating:
            where_conditions.append("r.rating = %s")
            params.append(rating)

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # 전체 리뷰 개수 조회
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM reviews r
            WHERE {where_clause}
        """
        cursor.execute(count_sql, tuple(params))
        total_count = cursor.fetchone()["total"]

        # 리뷰 목록 조회 (사용자명, 상품명 JOIN)
        offset = (page - 1) * limit

        sql = f"""
            SELECT 
                r.id AS review_id,
                r.user_id,
                u.name AS user_name,
                r.product_id,
                p.name AS product_name,
                r.rating,
                r.content,
                r.size_feedback,
                r.created_at
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN products p ON r.product_id = p.id
            WHERE {where_clause}
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        cursor.execute(sql, tuple(params))
        reviews = cursor.fetchall()

        cursor.close()
        connection.close()

        # 날짜 문자열로 변환
        for review in reviews:
            if review.get("created_at"):
                review["created_at"] = review["created_at"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            
            # 사이즈 체감 텍스트 추가
            size_feedback_map = {1: "작음", 2: "적당함", 3: "큼"}
            if review.get("size_feedback"):
                review["size_feedback_text"] = size_feedback_map.get(
                    review["size_feedback"], ""
                )

        # 페이지 정보 계산
        total_pages = (total_count + limit - 1) // limit

        logger.info(f"리뷰 조회 완료 - {len(reviews)}개 (전체 {total_count}개)")

        return JSONResponse(
            content={
                "success": True,
                "reviews": jsonable_encoder(reviews),
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "limit": limit,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters": {
                    "product_id": product_id,
                    "user_id": user_id,
                    "rating": rating
                }
            }
        )

    except Error as e:
        logger.error(f"리뷰 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"리뷰 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/reviews/{review_id}")
async def get_review_detail(review_id: int):
    """
    리뷰 상세 조회 API
    
    특정 리뷰의 상세 정보를 조회합니다.
    """
    try:
        logger.info(f"리뷰 상세 조회 요청 - review_id={review_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                r.id AS review_id,
                r.user_id,
                u.name AS user_name,
                r.product_id,
                p.name AS product_name,
                p.price,
                r.rating,
                r.content,
                r.size_feedback,
                r.created_at
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN products p ON r.product_id = p.id
            WHERE r.id = %s
            """,
            (review_id,)
        )

        review = cursor.fetchone()

        if not review:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")

        cursor.close()
        connection.close()

        # 날짜 문자열로 변환
        if review.get("created_at"):
            review["created_at"] = review["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        # 사이즈 체감 텍스트 추가
        size_feedback_map = {1: "작음", 2: "적당함", 3: "큼"}
        if review.get("size_feedback"):
            review["size_feedback_text"] = size_feedback_map.get(
                review["size_feedback"], ""
            )

        # 가격 변환
        if review.get("price"):
            review["price"] = float(review["price"])

        logger.info(f"리뷰 상세 조회 완료 - review_id={review_id}")

        return JSONResponse(
            content={
                "success": True,
                "review": jsonable_encoder(review)
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"리뷰 상세 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"리뷰 상세 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.delete("/reviews/{review_id}")
async def delete_review(review_id: int, user_id: int):
    """
    리뷰 삭제 API
    
    본인이 작성한 리뷰를 삭제합니다.
    """
    try:
        logger.info(f"리뷰 삭제 요청 - review_id={review_id}, user_id={user_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 리뷰 존재 및 소유자 확인
        cursor.execute(
            "SELECT id, user_id FROM reviews WHERE id = %s",
            (review_id,)
        )
        review = cursor.fetchone()

        if not review:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")

        # 본인 확인
        if review["user_id"] != user_id:
            cursor.close()
            connection.close()
            raise HTTPException(
                status_code=403, 
                detail="본인이 작성한 리뷰만 삭제할 수 있습니다."
            )

        # 리뷰 삭제
        cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        connection.commit()

        cursor.close()
        connection.close()

        logger.info(f"리뷰 삭제 완료 - review_id={review_id}")

        return JSONResponse(
            content={
                "success": True,
                "review_id": review_id,
                "message": "리뷰가 삭제되었습니다."
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"리뷰 삭제 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"리뷰 삭제 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@app.get("/products/{product_id}/reviews/summary")
async def get_product_review_summary(product_id: int):
    """
    상품 리뷰 요약 API
    
    특정 상품의 평균 평점, 리뷰 개수, 별점별 분포, 사이즈 체감 통계를 제공합니다.
    """
    try:
        logger.info(f"상품 리뷰 요약 조회 - product_id={product_id}")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 상품 존재 확인
        cursor.execute("SELECT id, name FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

        # 평균 평점 및 리뷰 개수
        cursor.execute(
            """
            SELECT 
                COUNT(*) as review_count,
                AVG(rating) as avg_rating
            FROM reviews
            WHERE product_id = %s
            """,
            (product_id,)
        )
        summary = cursor.fetchone()

        # 별점별 분포
        cursor.execute(
            """
            SELECT 
                rating,
                COUNT(*) as count
            FROM reviews
            WHERE product_id = %s
            GROUP BY rating
            ORDER BY rating DESC
            """,
            (product_id,)
        )
        rating_distribution = cursor.fetchall()

        # 사이즈 체감 통계
        cursor.execute(
            """
            SELECT 
                size_feedback,
                COUNT(*) as count
            FROM reviews
            WHERE product_id = %s AND size_feedback IS NOT NULL
            GROUP BY size_feedback
            ORDER BY size_feedback
            """,
            (product_id,)
        )
        size_feedback_stats = cursor.fetchall()

        cursor.close()
        connection.close()

        # 평균 평점 소수점 처리
        avg_rating = float(summary["avg_rating"]) if summary["avg_rating"] else 0.0
        avg_rating = round(avg_rating, 1)

        # 별점별 분포를 딕셔너리로 변환
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for item in rating_distribution:
            rating_dist[item["rating"]] = item["count"]

        # 사이즈 체감 통계 딕셔너리로 변환
        size_feedback_map = {1: "작음", 2: "적당함", 3: "큼"}
        size_stats = []
        for item in size_feedback_stats:
            size_stats.append({
                "value": item["size_feedback"],
                "text": size_feedback_map.get(item["size_feedback"], ""),
                "count": item["count"]
            })

        logger.info(
            f"상품 리뷰 요약 조회 완료 - "
            f"평균 평점: {avg_rating}, 리뷰 수: {summary['review_count']}"
        )

        return JSONResponse(
            content={
                "success": True,
                "product_id": product_id,
                "product_name": product["name"],
                "review_count": summary["review_count"],
                "avg_rating": avg_rating,
                "rating_distribution": rating_dist,
                "size_feedback_stats": size_stats
            }
        )

    except HTTPException:
        raise
    except Error as e:
        logger.error(f"리뷰 요약 조회 DB 오류: {e}")
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except Exception as e:
        logger.error(f"리뷰 요약 조회 중 오류: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


if __name__ == "__main__":
    # 서버 실행
    start_server(
        host="0.0.0.0",
        port=8000,
        reload=True  # 개발 모드
    )

