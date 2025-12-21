# 인증 관련 유틸리티 함수들
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")  # 환경변수로 관리 권장
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24시간

# 비밀번호 재설정 토큰 유효시간
RESET_TOKEN_EXPIRE_MINUTES = 30  # 30분
# 비밀번호 길이가 너무 길어서 생길 수 있는 문제를 예방하기 위해 미리 길이를 조절해주는 도우미 함수
def _normalize_password(password: str) -> str:

    # 글자 상태의 비밀번호를 컴퓨터가 계산할 수 있는 바이트 형태로 변환
    pw_bytes = password.encode("utf-8")
    if len(pw_bytes) > 72: # 우리가 사용하는 암호화 도구는 최대 72바이트까지만 처리할 수 있으므로
        pw_bytes = pw_bytes[:72] # 72바이트 이상이면 72바이트까지만 잘라서 사용
        password = pw_bytes.decode("utf-8", errors="ignore") 
    return password # 길이가 조절된 비밀번호를 다시 글자 형태로 복구해서 돌려줌

# 회원가입 시 사용자가 입력한 비밀번호를 알아볼 수 없는 문자열로 바꾸는 함수
def hash_password(password: str) -> str:
    normalized = _normalize_password(password) # 먼저 _normalize_password로 길이를 맞춘 뒤
    return pwd_context.hash(normalized) # pwd_context.hash를 사용해 진짜 암호화를 수행

# 로그인 시 사용자가 입력한 비밀번호가 DB에 저장된 암호문과 일치하는지 확인하는 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    
    normalized = _normalize_password(plain_password) # 입력받은 비밀번호도 똑같이 길이를 맞춘 뒤
    return pwd_context.verify(normalized, hashed_password) # 저장된 암호문과 수학적으로 일치하는지 비교

# 로그인한 사용자에게 발급할 정식 출입증을 만드는 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None): # 사용자 ID 등의 정보(data)를 받아서 암호화된 토큰으로 제작
    
    to_encode = data.copy() # 토큰이 언제까지 유효한지 계산
    if expires_delta: # 만약 토큰 만료 시간이 지정되어 있다면
        expire = datetime.utcnow() + expires_delta # 그 시간을 사용
    else: # 지정되어 있지 않다면
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # 24시간 후 만료
    
    to_encode.update({"exp": expire}) # exp 필드에 만료 시간을 기록
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # 정보와 만료 시간을 합친 뒤, 서버만 아는 SECRET_KEY로 서명하여
    return encoded_jwt # 암호화된 문자열(JWT)로 반환

def create_reset_token(email: str) -> str: # 비밀번호를 잃어버린 사용자에게 발급하는 임시 토큰 생성 함수
   
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES) 
    to_encode = { 
        "email": email, 
        "exp": expire, 
        "type": "password_reset" # 토큰 안에 이것은 비밀번호 재설정용입니다라는 표식을 남겨둠
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) 

def verify_reset_token(token: str) -> Optional[str]: # 사용자가 가져온 토큰이 유효한 비밀번호 재설정 토큰인지 확인
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # 비밀키를 사용해 암호화된 문자열을 다시 원래의 정보로 되돌림
        email: str = payload.get("email") # (이메일 정보 추출)
        token_type: str = payload.get("type") # (토큰 유형 추출)
        
        if email is None or token_type != "password_reset": # 해독된 정보에 이메일이 있는지, 토큰 타입이 'password_reset'이 맞는지 확인
            return None # 조건이 안 맞으면 무효 처리
        return email  
    except JWTError: 
        return None 

def decode_token(token: str) -> Optional[dict]: # 로그인 유지 등 일반적인 용도로 토큰의 내용을 확인할 때 쓰는 함수
   
    try: # 해독에 성공하면 정보를 담은 딕셔너리를 반환
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError: # 해독에 실패하면 None을 반환
        return None

