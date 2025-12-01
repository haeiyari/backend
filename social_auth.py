# 소셜 로그인 처리
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class KakaoAuth:
   
    
    def __init__(self, client_id: str, client_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://kauth.kakao.com/oauth/token"
        self.user_info_url = "https://kapi.kakao.com/v2/user/me"
    
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
            
            response = requests.post(self.token_url, data=data)
            
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                logger.error(f"카카오 토큰 발급 실패: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"카카오 토큰 발급 중 오류: {str(e)}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
       
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(self.user_info_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # 필요한 정보만 추출
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return {
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

