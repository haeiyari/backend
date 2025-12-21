# 소셜 로그인 처리
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# 카카오 로그인과 관련된 모든 통신 기능을 담고 있음, 앱 키(ID)와 비밀 키(Secret)를 가지고 일을 처리
class KakaoAuth:
   
    # 카카오 API를 쓰기 위해 필요한 앱 ID, 비밀키, 그리고 카카오 서버 주소(URL)들을 미리 변수에 저장
    def __init__(self, client_id: str, client_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.user_info_url = "https://kapi.kakao.com/v2/user/me"
    
    # 1단계: 토큰 교환 시작
    # 사용자가 로그인하고 받아온 임시 인증 코드(code)를 진짜 사용할 수 있는 Access Token으로 교환
    def get_access_token(self, code: str, redirect_uri: str) -> Optional[str]:
        
        try:
            data = {
                "grant_type": "authorization_code", 
                "client_id": self.client_id,
                "redirect_uri": redirect_uri, 
                "code": code 
            }
            
            if self.client_secret: 
                data["client_secret"] = self.client_secret 
            
            response = requests.post(self.token_url, data=data) # 카카오 인증 서버(token_url)에 코드를 토큰으로 바꿔달라는 요청을 보냄
            
            if response.status_code == 200: # 카카오가 200 (OK) 응답을 주면
                return response.json().get("access_token") # 그 안에 들어있는 `access_token`을 꺼내서 반환
            else:
                logger.error(f"카카오 토큰 발급 실패: {response.text}") # 실패하면 에러 로그
                return None
                
        except Exception as e:
            logger.error(f"카카오 토큰 발급 중 오류: {str(e)}")
            return None
    
    # 2단계: 사용자 정보 조회
    # 방금 받은 액세스 토큰을 이용해서 카카오에 저장된 사용자의 프로필 정보(이름, 이메일 등)를 달라고 요청하는 함수
    def get_user_info(self, access_token: str) -> Optional[Dict]:
       
        try:
            headers = { # Header의 Authorization: Bearer 토큰 형식으로 토큰을 붙여서
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(self.user_info_url, headers=headers) # 카카오 API 서버(user_info_url)에 요청을 보냄

            if response.status_code == 200: # 카카오가 200 (OK) 응답을 주면
                data = response.json() # 그 안에 들어있는 데이터를 꺼내서 변수에 저장
                
                
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return { # 카카오가 보내준 복잡한 데이터 중에서 서비스에 필요한 핵심 정보만 골라내어 딕셔너리로 만듦
                    "social_id": str(data.get("id")),
                    "provider": "kakao",
                    "email": kakao_account.get("email"),
                    "name": profile.get("nickname"),
                    "profile_image": profile.get("profile_image_url")
                }
            else:
                logger.error(f"카카오 사용자 정보 조회 실패: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"카카오 사용자 정보 조회 중 오류: {str(e)}")
            return None


class GoogleAuth:
   
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_access_token(self, code: str, redirect_uri: str) -> Optional[str]:
       
        try:
            data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": redirect_uri,
                "code": code
            }
            
            response = requests.post(self.token_url, data=data)
            
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"구글 토큰 발급 실패: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"구글 토큰 발급 중 오류: {str(e)}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
       
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(self.user_info_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "social_id": data.get("id"),
                    "provider": "google",
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "profile_image": data.get("picture")
                }
            else:
                logger.error(f"구글 사용자 정보 조회 실패: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"구글 사용자 정보 조회 중 오류: {str(e)}")
            return None


class NaverAuth:


    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://nid.naver.com/oauth2.0/token"
        self.user_info_url = "https://openapi.naver.com/v1/nid/me"

    def get_access_token(self, code: str, redirect_uri: str) -> Optional[str]:
       
        try:
            params = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }

            response = requests.post(self.token_url, params=params)

            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"네이버 토큰 발급 실패: {response.text}")
                return None

        except Exception as e:
            logger.error(f"네이버 토큰 발급 중 오류: {str(e)}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict]:
       
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
            }

            response = requests.get(self.user_info_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # 네이버 응답 구조: { "resultcode": "00", "message": "success", "response": { ... } }
                resp = data.get("response", {})

                return {
                    "social_id": resp.get("id"),
                    "provider": "naver",
                    "email": resp.get("email"),
                    "name": resp.get("name"),
                    "profile_image": resp.get("profile_image"),
                }
            else:
                logger.error(f"네이버 사용자 정보 조회 실패: {response.text}")
                return None

        except Exception as e:
            logger.error(f"네이버 사용자 정보 조회 중 오류: {str(e)}")
            return None

