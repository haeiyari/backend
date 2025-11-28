# 치수 측정 서비스 모듈
import cv2
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import base64

class MeasurementService:
    """의류 치수 측정 서비스 클래스"""
    
    def __init__(self):
        self.a4_width_cm = 21.0
        self.a4_height_cm = 29.7
    # measure_clothing 함수가 API로부터 이미지 데이터 (bytes)와 의류 타입 (shirt 또는 pants)을 받음
    def measure_clothing(self, image_data: bytes, clothing_type: str, a4_box: Optional[List] = None,
                         scale_correction: float = 1.0, horiz_scale_correction: float = 1.0, vert_scale_correction: float = 1.0,
                         waist_corr: float = 1.0, hip_corr: float = 1.0, thigh_corr: float = 1.0) -> Dict:

        # 전달받은 이미지 데이터를 OPEN CV 라이브러리가 처리할 수 있는 numpy 배열로 변환(디코딩)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"error": "이미지를 불러올 수 없습니다."}
        
        # A4 용지 검출 (수동 또는 자동)
        if a4_box is not None:
            # 사용자가 수동으로 지정한 A4 박스 좌표 사용
            a4_box_array = np.array(a4_box, dtype=np.float32) # 사용자가 지정한 A4 박스 좌표를 numpy 배열로 변환
            a4_box_array = self._order_points(a4_box_array) # 4개의 꼭짓점 좌표를 정렬
        else:
            # 자동 검출 시도
            a4_box_array = self._find_a4_box(image) 

            if a4_box_array is None:
                # A4 검출 실패 시 이미지 정보만 반환 (수동 선택 유도)
                _, buffer = cv2.imencode('.jpg', image)
                preview_image = base64.b64encode(buffer).decode('utf-8')
                return {
                    "error": "A4 용지를 찾을 수 없습니다.",
                    "need_manual_a4": True, #A4 용지를 수동으로 지정해야 한다는 신호와 함께 
                    "preview_image": preview_image, # 원본 이미지를 base64로 인코딩 하여 즉시 반환
                    "image_size": {"width": image.shape[1], "height": image.shape[0]}
                }
        
        # 찾아낸 A4용지 4개의 꼭짓점(a4_box_array)을 _calculate_pixel_ratio 함수로 넘김
        pixelsPerCM_w, pixelsPerCM_h = self._calculate_pixel_ratio(a4_box_array)
        
        # 의류 타입에 따라 측정
        # 유효 보정값 (단일 스케일과 축 보정을 함께 지원)
        scale_w = scale_correction * horiz_scale_correction
        scale_h = scale_correction * vert_scale_correction
        # 바지 전용 과도한 기본 보정은 제거하고, 동적 보정 로직만 사용
        if clothing_type == "pants":
            pass

        if clothing_type == "shirt":
            result = self._measure_shirt(image, a4_box_array, pixelsPerCM_w, pixelsPerCM_h, scale_w=scale_w, scale_h=scale_h)
        elif clothing_type == "pants":
            result = self._measure_pants(image, a4_box_array, pixelsPerCM_w, pixelsPerCM_h, scale_w=scale_w, scale_h=scale_h,
                                         waist_corr=waist_corr, hip_corr=hip_corr, thigh_corr=thigh_corr)
        else:
            return {"error": "지원하지 않는 의류 타입입니다. 'shirt' 또는 'pants'를 사용하세요."}
        
        return result
    # 앱이 /detect-keypoints 같은 별도 엔드포인트를 호출하면 API 는 서비스의 detect_keypoints 함수를 호출
    def detect_keypoints(self, image_data: bytes, clothing_type: str, a4_box: Optional[List] = None) -> Dict:
        #... (A4 용지를 먼저 검출 -> measure_clothing과 동일) ...

        # 이미지 디코딩
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"error": "이미지를 불러올 수 없습니다."}
        
        # A4 용지 검출 (수동 또는 자동)
        if a4_box is not None:
            # 수동으로 지정된 A4 박스 사용
            a4_box_array = np.array(a4_box, dtype=np.float32)
            a4_box_array = self._order_points(a4_box_array)
        else:
            # 자동 검출 시도
            a4_box_array = self._find_a4_box(image)
            if a4_box_array is None:
                # A4 검출 실패 시 이미지 정보만 반환 (수동 선택 유도)
                _, buffer = cv2.imencode('.jpg', image)
                preview_image = base64.b64encode(buffer).decode('utf-8')
                return {
                    "error": "A4 용지를 찾을 수 없습니다.",
                    "need_manual_a4": True,
                    "preview_image": preview_image,
                    "image_size": {"width": image.shape[1], "height": image.shape[0]}
                }
        
        # 픽셀/cm 비율 계산
        pixelsPerCM_w, pixelsPerCM_h = self._calculate_pixel_ratio(a4_box_array)
        
        # 이미지 전처리 및 윤곽선 검출
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        if clothing_type == "shirt":
            _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        elif clothing_type == "pants":
            _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
        else:
            return {"error": "지원하지 않는 의류 타입입니다. 'shirt' 또는 'pants'를 사용하세요."}
        
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"error": "의류 윤곽선을 찾을 수 없습니다."}
        
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < image.shape[0] * image.shape[1] * 0.1:
            return {"error": "의류 윤곽선이 너무 작습니다."}
        
        epsilon = 0.002 * cv2.arcLength(largest_contour, True)
        smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        # 1. _auto_detect_keypoints_shirt/pants를 호출해 키포인트 자동 검출
        if clothing_type == "shirt":
            keypoints = self._auto_detect_keypoints_shirt(image, smoothed_contour)
            point_labels = ["목점", "밑단점", "왼쪽 어깨", "오른쪽 어깨", 
                          "왼쪽 가슴", "오른쪽 가슴", "왼쪽 소매", "오른쪽 소매"]
        else:  # pants
            keypoints = self._auto_detect_keypoints_pants(image, smoothed_contour)
            point_labels = ["바지 상단(총장거리)", "왼쪽 허리", "오른쪽 허리",
                          "왼쪽 엉덩이", "오른쪽 엉덩이", "밑위",
                          "오른쪽 허벅지", "밑단 좌측(총장거리)", "밑단 우측"]
        
        # 2.키포인트가 그려진 시각화 이미지 (vis) 생성
        vis = image.copy()
        cv2.drawContours(vis, [a4_box_array.astype(np.int32)], -1, (255, 0, 0), 3)
        cv2.drawContours(vis, [smoothed_contour], -1, (0, 255, 0), 2)
        
        for idx, point in enumerate(keypoints):
            cv2.circle(vis, tuple(point), 8, (0, 0, 255), -1)
            cv2.putText(vis, str(idx+1), (point[0]+10, point[1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # 3. 이미지 인코딩
        _, buffer = cv2.imencode('.jpg', vis)
        preview_image = base64.b64encode(buffer).decode('utf-8')
        # 4. 측정이 아닌, 찾은 키포인트 정보와 키포인트가 그려진 preview_image를 반환
        return {
            "type": clothing_type,
            "keypoints": keypoints.tolist(),
            "point_labels": point_labels,
            "preview_image": preview_image,
            "image_size": {"width": image.shape[1], "height": image.shape[0]},
            "a4_box": a4_box_array.tolist(),
            "pixelsPerCM_w": float(pixelsPerCM_w),
            "pixelsPerCM_h": float(pixelsPerCM_h)
        }
    
    def measure_with_keypoints(self, image_data: bytes, clothing_type: str, 
                               keypoints: List, a4_box: List,
                               pixelsPerCM_w: float, pixelsPerCM_h: float,
                               scale_correction: float = 1.0,
                               horiz_scale_correction: float = 1.0,
                               vert_scale_correction: float = 1.0,
                               waist_corr: float = 1.0, hip_corr: float = 1.0, thigh_corr: float = 1.0) -> Dict:
        """
        사용자가 조정한 키포인트로 측정
        
        Args:
            image_data: 이미지 바이트 데이터
            clothing_type: 'shirt' 또는 'pants'
            keypoints: 조정된 키포인트 좌표 리스트
            a4_box: A4 용지 박스 좌표
            pixelsPerCM_w: 가로 픽셀/cm 비율
            pixelsPerCM_h: 세로 픽셀/cm 비율
            
        Returns:
            측정 결과 딕셔너리
        """
        # 이미지 디코딩
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"error": "이미지를 불러올 수 없습니다."}
        
        # 리스트를 numpy 배열로 변환
        keypoints_array = np.array(keypoints, dtype=int)
        a4_box_array = np.array(a4_box, dtype=np.float32)
        
        # 측정 수행
        # 유효 보정값 계산
        scale_w = scale_correction * horiz_scale_correction
        scale_h = scale_correction * vert_scale_correction
        # 바지 전용 과도한 기본 보정은 제거하고, 동적 보정 로직만 사용
        if clothing_type == "pants":
            pass
        # 의류 타입에 따라 _measure_shirt 또는 _measure_pants 함수를 호출
        if clothing_type == "shirt":
            result = self._measure_shirt_with_keypoints(
                image, a4_box_array, keypoints_array, pixelsPerCM_w, pixelsPerCM_h, scale_w=scale_w, scale_h=scale_h
            )
        elif clothing_type == "pants":
            result = self._measure_pants_with_keypoints(
                image, a4_box_array, keypoints_array, pixelsPerCM_w, pixelsPerCM_h, scale_w=scale_w, scale_h=scale_h,
                waist_corr=waist_corr, hip_corr=hip_corr, thigh_corr=thigh_corr
            )
        else:
            return {"error": "지원하지 않는 의류 타입입니다."}
        
        return result
    
    def _find_a4_box(self, image: np.ndarray) -> Optional[np.ndarray]:
        # ... (이미지 전처리: LAB, HSV, 노이즈 제거 등) ...
        # 이미지 전처리
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        normalized = cv2.merge((cl,a,b))
        normalized = cv2.cvtColor(normalized, cv2.COLOR_LAB2BGR)
        
        # HSV 변환 및 흰색 영역 마스크 생성
        hsv = cv2.cvtColor(normalized, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 180])
        # 채도 상한 완화(반사/난반사 환경 대응)
        upper_white = np.array([180, 60, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # 노이즈 제거 및 윤곽선 강화
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # 윤곽선 검출
        # 엣지 임계 완화
        edges = cv2.Canny(mask, 40, 120)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        
        cnts, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        
        a4_scale = 29.7 / 21.0
        image_area = image.shape[0] * image.shape[1]
        
        for c in cnts: #윤곽선 (cnts)을 찾아서 A4 비율과 비교
            area = cv2.contourArea(c) # 윤곽선의 면적을 계산
            # 면적 하한 완화: 7% 이상이면 후보
            if area < image_area * 0.07 or area > image_area * 0.9: # 면적이 이미지 면적의 7% 미만 또는 90% 초과인 경우 무시
                continue
                
            peri = cv2.arcLength(c, True) # 윤곽선의 길이를 계산
            approx = cv2.approxPolyDP(c, 0.02 * peri, True) # 윤곽선을 다각형으로 변환
            
            if len(approx) == 4: # 사각형인 경우
                #...(비율, 각도, 밝기 검사) ...
                box = approx.reshape(4, 2) # 4개의 꼭짓점 좌표를 2차원 배열로 변환
                box = self._order_points(box) # 4개의 꼭짓점 좌표를 정렬
                
                (tl, tr, br, bl) = box
                width = np.linalg.norm(tr - tl)
                height = np.linalg.norm(bl - tl)
                
                if width == 0 or height == 0:
                    continue
                    
                ratio = max(width, height) / min(width, height)
                ratio_diff = abs(ratio - a4_scale)
                
                # 각도 검사
                angles = []
                for i in range(4):
                    p1 = box[i]
                    p2 = box[(i + 1) % 4]
                    angle = abs(np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0])) % 90)
                    angles.append(min(angle, 90 - angle))
                max_angle_diff = max(angles)
                
                # 밝기 검사
                temp_mask = np.zeros(image.shape[:2], dtype=np.uint8)
                cv2.drawContours(temp_mask, [box.astype(np.int32)], -1, 255, -1)
                mean_val = cv2.mean(image, mask=temp_mask)[0]
                
                # 각도/밝기 조건 완화
                if ratio_diff < 0.2 and max_angle_diff < 25 and mean_val > 140: # 모든 조건을 충족하면 A4 용지로 판단
                    return box.astype(np.float32) # 찾음
        
        return None # 못 찾음
    #A4용지가 가로로 있는지 세로로 있는지 판단한 뒤, cm 당 몇 픽셀인지 가로 / 세로 비율을 계산
    def _calculate_pixel_ratio(self, a4_box: np.ndarray) -> Tuple[float, float]:
        #...(A4의 픽셀 가로 / 세로 길이 계산)...
        a4_tl = a4_box[0]
        a4_tr = a4_box[1]
        a4_br = a4_box[2]
        a4_bl = a4_box[3]

        # 픽셀 길이 계산
        top_width_px = np.linalg.norm(a4_tr - a4_tl)
        bottom_width_px = np.linalg.norm(a4_br - a4_bl)
        left_height_px = np.linalg.norm(a4_bl - a4_tl)
        right_height_px = np.linalg.norm(a4_br - a4_tr)

        avg_width_px = (top_width_px + bottom_width_px) / 2.0
        avg_height_px = (left_height_px + right_height_px) / 2.0

        # 물리적 A4 변 길이(cm)
        short_cm = min(self.a4_width_cm, self.a4_height_cm)   # 21.0
        long_cm = max(self.a4_width_cm, self.a4_height_cm)    # 29.7

        # A4가 가로로 긴지 세로로 긴지 판단
        if avg_width_px >= avg_height_px:
            physical_width_cm = long_cm #29.7cm
            physical_height_cm = short_cm #21.0cm
        else:
            physical_width_cm = short_cm #21.0cm
            physical_height_cm = long_cm #29.7cm

        # 1cm 당 픽셀 수 계산
        pixelsPerCM_width = avg_width_px / float(physical_width_cm)
        pixelsPerCM_height = avg_height_px / float(physical_height_cm)

        return pixelsPerCM_width, pixelsPerCM_height

    def _get_homography_for_a4(self, a4_box: np.ndarray, scale_px_per_cm: float = 30.0) -> Tuple[np.ndarray, Tuple[int, int], float]:
        """A4 박스를 기준으로 평면 보정을 위한 호모그래피와 출력 크기 반환.
        반환된 출력 크기는 (width_px, height_px)이며, scale_px_per_cm는 1cm당 픽셀 수.
        """
        # 점 순서 정리 (tl, tr, br, bl)
        box = self._order_points(a4_box.astype(np.float32))

        # 현재 이미지에서 A4의 가로/세로 픽셀 길이
        top_width_px = np.linalg.norm(box[1] - box[0])
        left_height_px = np.linalg.norm(box[3] - box[0])

        # 실제 A4 변 길이(cm)
        short_cm = min(self.a4_width_cm, self.a4_height_cm)  # 21.0
        long_cm = max(self.a4_width_cm, self.a4_height_cm)   # 29.7

        # 이미지에서 가로가 더 길면 가로=긴 변(29.7), 세로=짧은 변(21.0)
        if top_width_px >= left_height_px:
            width_cm, height_cm = long_cm, short_cm
        else:
            width_cm, height_cm = short_cm, long_cm

        W = int(round(width_cm * scale_px_per_cm))
        H = int(round(height_cm * scale_px_per_cm))

        dst = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], dtype=np.float32)
        Hmat = cv2.getPerspectiveTransform(box.astype(np.float32), dst)
        return Hmat, (W, H), scale_px_per_cm

    @staticmethod
    def _warp_points(points: np.ndarray, H: np.ndarray) -> np.ndarray:
        pts = points.astype(np.float32).reshape(-1, 1, 2)
        warped = cv2.perspectiveTransform(pts, H)
        return warped.reshape(-1, 2)
    
    def _measure_shirt(self, image: np.ndarray, a4_box: np.ndarray, 
                       pixelsPerCM_w: float, pixelsPerCM_h: float, scale_w: float = 1.0, scale_h: float = 1.0) -> Dict:
        """상의 치수 측정"""
        vis = image.copy()
        cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3)
        
        # 이미지 전처리
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, clothing_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = np.ones((5,5), np.uint8)
        clothing_mask = cv2.morphologyEx(clothing_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(clothing_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"error": "옷 윤곽선을 찾을 수 없습니다."}
        
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < image.shape[0] * image.shape[1] * 0.1:
            return {"error": "옷 윤곽선이 너무 작습니다."}
        
        epsilon = 0.002 * cv2.arcLength(largest_contour, True)
        smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
        cv2.drawContours(vis, [smoothed_contour], -1, (0, 255, 0), 2)
        
        # 키포인트 자동 검출
        keypoints = self._auto_detect_keypoints_shirt(image, smoothed_contour)

        # A4 기반 평면 보정으로 왜곡 최소화 후 측정
        Hmat, (W, H), scale = self._get_homography_for_a4(a4_box)
        warped_keypoints = self._warp_points(keypoints.astype(np.float32), Hmat).astype(np.float32)
        warped_contour = cv2.perspectiveTransform(smoothed_contour.astype(np.float32), Hmat).reshape(-1, 2)

        def width_px_at_y(contour_pts: np.ndarray, y: float) -> float:
            xs = []
            n = contour_pts.shape[0]
            for i in range(n):
                x1, y1 = contour_pts[i]
                x2, y2 = contour_pts[(i + 1) % n]
                if (y1 <= y <= y2) or (y2 <= y <= y1):
                    if y1 == y2:
                        xs.extend([float(x1), float(x2)])
                    else:
                        t = (y - y1) / (y2 - y1)
                        x = x1 + t * (x2 - x1)
                        xs.append(float(x))
            if len(xs) < 2:
                return 0.0
            xs.sort()
            return xs[-1] - xs[0]

        def horiz_cm_warp(p1, p2):
            return abs(p1[0] - p2[0]) / float(scale)

        def euclid_cm_warp(p1, p2):
            dx = (p1[0] - p2[0]) / float(scale)
            dy = (p1[1] - p2[1]) / float(scale)
            return (dx*dx + dy*dy) ** 0.5

        # 측정값 계산
        measurements = {}

        if len(keypoints) >= 2:
            dx_cm = (warped_keypoints[0][0] - warped_keypoints[1][0]) / float(scale)
            dy_cm = (warped_keypoints[0][1] - warped_keypoints[1][1]) / float(scale)
            corrected_length = ((dx_cm * scale_w) ** 2 + (dy_cm * scale_h) ** 2) ** 0.5
            measurements["length"] = round(corrected_length, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[1]), (0,0,255), 2)
            cv2.putText(vis, f"{measurements['length']}cm", ((keypoints[0][0]+keypoints[1][0])//2, (keypoints[0][1]+keypoints[1][1])//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        if len(keypoints) >= 4:
            raw_shoulder = horiz_cm_warp(warped_keypoints[2], warped_keypoints[3])
            corrected_shoulder = raw_shoulder * scale_w
            measurements["shoulder"] = round(corrected_shoulder, 1)
            cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[3]), (255,0,0), 2)
            cv2.putText(vis, f"{measurements['shoulder']}cm", ((keypoints[2][0]+keypoints[3][0])//2, (keypoints[2][1]+keypoints[3][1])//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        if len(keypoints) >= 6:
            raw_chest = horiz_cm_warp(warped_keypoints[4], warped_keypoints[5])
            corrected_chest = raw_chest * scale_w
            measurements["chest"] = round(corrected_chest, 1)
            cv2.line(vis, tuple(keypoints[4]), tuple(keypoints[5]), (0,255,0), 2)
            cv2.putText(vis, f"{measurements['chest']}cm", ((keypoints[4][0]+keypoints[5][0])//2, (keypoints[4][1]+keypoints[5][1])//2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        if len(keypoints) >= 8:
            raw_left_dx = (warped_keypoints[2][0] - warped_keypoints[6][0]) / float(scale)
            raw_left_dy = (warped_keypoints[2][1] - warped_keypoints[6][1]) / float(scale)
            raw_right_dx = (warped_keypoints[3][0] - warped_keypoints[7][0]) / float(scale)
            raw_right_dy = (warped_keypoints[3][1] - warped_keypoints[7][1]) / float(scale)
            left_corr = ((raw_left_dx * scale_w) ** 2 + (raw_left_dy * scale_h) ** 2) ** 0.5
            right_corr = ((raw_right_dx * scale_w) ** 2 + (raw_right_dy * scale_h) ** 2) ** 0.5
            corrected_sleeve = max(left_corr, right_corr)
            measurements["sleeve"] = round(corrected_sleeve, 1)
            cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[6]), (128,0,128), 2)
            cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[7]), (128,0,128), 2)
            # 텍스트는 긴 쪽 선의 중간에 표시
            if left_corr >= right_corr:
                midx = (keypoints[2][0] + keypoints[6][0]) // 2
                midy = (keypoints[2][1] + keypoints[6][1]) // 2
            else:
                midx = (keypoints[3][0] + keypoints[7][0]) // 2
                midy = (keypoints[3][1] + keypoints[7][1]) // 2
            cv2.putText(vis, f"{measurements['sleeve']}cm", (midx, midy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128,0,128), 2)
        
        # 결과 이미지 인코딩
        _, buffer = cv2.imencode('.jpg', vis)
        result_image = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "type": "shirt",
            "measurements": measurements,
            "result_image": result_image,
            "unit": "cm"
        }
    
    def _measure_pants(self, image: np.ndarray, a4_box: np.ndarray,
                       pixelsPerCM_w: float, pixelsPerCM_h: float,
                       scale_w: float = 1.0, scale_h: float = 1.0,
                       waist_corr: float = 1.0, hip_corr: float = 1.0, thigh_corr: float = 1.0) -> Dict:
    #...(옷 윤곽선 찾기) ...
        vis = image.copy()
        cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3)
        
        # 이미지 전처리
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, pants_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = np.ones((5,5), np.uint8)
        pants_mask = cv2.morphologyEx(pants_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        pants_mask = cv2.dilate(pants_mask, kernel, iterations=1)
        
        contours, _ = cv2.findContours(pants_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return {"error": "바지 윤곽선을 찾을 수 없습니다."}
        
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < image.shape[0] * image.shape[1] * 0.1:
            return {"error": "바지 윤곽선이 너무 작습니다."}
        
        epsilon = 0.002 * cv2.arcLength(largest_contour, True)
        smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
        cv2.drawContours(vis, [smoothed_contour], -1, (0, 255, 0), 2)
        
        # _measure_shirt/pants 함수 내부에서 _auto_detect_keypoints_shirt/pants를 호출해 옷의 주요 지점 자동
        keypoints = self._auto_detect_keypoints_pants(image, smoothed_contour)

        # 기울어진 이미지를 바로잡기 위해 _get_homography_for_a4로 평면 보정(Warping)을 수행
        Hmat, (W, H), scale = self._get_homography_for_a4(a4_box)
        warped_keypoints = self._warp_points(keypoints.astype(np.float32), Hmat).astype(np.float32) #키포인트들을 보정된 평면으로 이동
        warped_contour = cv2.perspectiveTransform(smoothed_contour.astype(np.float32), Hmat).reshape(-1, 2) #윤곽선을 보정된 평면으로 이동
        # 마스크 자체를 워핑하여 최하단 픽셀을 안정적으로 탐색
        warped_mask = cv2.warpPerspective(pants_mask, Hmat, (W, H), flags=cv2.INTER_NEAREST)

        def width_px_at_y(contour_pts: np.ndarray, y: float) -> float:
            xs = []
            n = contour_pts.shape[0]
            for i in range(n):
                x1, y1 = contour_pts[i]
                x2, y2 = contour_pts[(i + 1) % n]
                if (y1 <= y <= y2) or (y2 <= y <= y1):
                    if y1 == y2:
                        xs.extend([float(x1), float(x2)])
                    else:
                        t = (y - y1) / (y2 - y1)
                        x = x1 + t * (x2 - x1)
                        xs.append(float(x))
            if len(xs) < 2:
                return 0.0
            xs.sort()
            return xs[-1] - xs[0]

        # 측정값 계산
        measurements = {}

        def horiz_cm_warp(p1, p2):
            return abs(p1[0] - p2[0]) / float(scale)

        def vert_cm_warp(p1, p2):
            return abs(p1[1] - p2[1]) / float(scale)

        def euclid_cm_warp(p1, p2):
            dx = (p1[0] - p2[0]) / float(scale)
            dy = (p1[1] - p2[1]) / float(scale)
            return (dx*dx + dy*dy) ** 0.5
        
        if len(keypoints) >= 9:
            # 총장은 좌/우 밑단과 윤곽 최하단까지의 후보 중 최대값을 사용
            candidates = []
            candidates.append(vert_cm_warp(warped_keypoints[0], warped_keypoints[7]))
            candidates.append(vert_cm_warp(warped_keypoints[0], warped_keypoints[8]))
            if warped_contour.size > 0:
                bottom_y_px = float(np.max(warped_contour[:, 1]))
                top_y_px = float(warped_keypoints[0][1])
                if bottom_y_px > top_y_px:
                    candidates.append((bottom_y_px - top_y_px) / float(scale))
            raw_length = max(candidates) if len(candidates) else 0.0
            length_correction = self._get_pants_correction_factor(raw_length, 'length')
            corrected_length = raw_length * length_correction * scale_h
            measurements["length"] = round(corrected_length, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[7]), (0,0,255), 2)
        
        if len(keypoints) >= 3:
            raw_waist = horiz_cm_warp(warped_keypoints[1], warped_keypoints[2])
            waist_correction = self._get_pants_correction_factor(raw_waist, 'waist')
            corrected_waist = raw_waist * waist_correction * scale_w * waist_corr
            measurements["waist"] = round(corrected_waist, 1)
            cv2.line(vis, tuple(keypoints[1]), tuple(keypoints[2]), (255,0,0), 2)
        
        if len(keypoints) >= 5:
            raw_hip = horiz_cm_warp(warped_keypoints[3], warped_keypoints[4])
            hip_correction = self._get_pants_correction_factor(raw_hip, 'hip')
            corrected_hip = raw_hip * hip_correction * scale_w * hip_corr
            measurements["hip"] = round(corrected_hip, 1)
            cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[4]), (255,128,0), 2)
        
        if len(keypoints) >= 6:
            # 축 보정을 반영한 유클리드 길이
            dx_cm = (warped_keypoints[0][0] - warped_keypoints[5][0]) / float(scale)
            dy_cm = (warped_keypoints[0][1] - warped_keypoints[5][1]) / float(scale)
            raw_crotch = (dx_cm**2 + dy_cm**2) ** 0.5
            crotch_correction = self._get_pants_correction_factor(raw_crotch, 'crotch')
            corrected_crotch = ((dx_cm * scale_w) ** 2 + (dy_cm * scale_h) ** 2) ** 0.5
            corrected_crotch *= crotch_correction
            measurements["crotch"] = round(corrected_crotch, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[5]), (255,255,0), 2)
        
        if len(keypoints) >= 7:
            raw_thigh = horiz_cm_warp(warped_keypoints[5], warped_keypoints[6])
            thigh_correction = self._get_pants_correction_factor(raw_thigh, 'thigh')
            corrected_thigh = raw_thigh * thigh_correction * scale_w * thigh_corr
            measurements["thigh"] = round(corrected_thigh, 1)
            cv2.line(vis, tuple(keypoints[5]), tuple(keypoints[6]), (0,255,0), 2)
        
        if len(keypoints) >= 9:
            raw_hem = horiz_cm_warp(warped_keypoints[7], warped_keypoints[8])
            hem_correction = 1.0  # 과도 보정 제거
            corrected_hem = raw_hem * hem_correction * scale_w
            measurements["hem"] = round(corrected_hem, 1)
            cv2.line(vis, tuple(keypoints[7]), tuple(keypoints[8]), (128,0,128), 2)
        
        # 결과 이미지 인코딩
        _, buffer = cv2.imencode('.jpg', vis)
        result_image = base64.b64encode(buffer).decode('utf-8')
        
        # 측정 결과를 반환
        return {
            "type": "pants",
            "measurements": measurements,
            "result_image": result_image,
            "unit": "cm"
        }
    
    def _auto_detect_keypoints_shirt(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """상의 키포인트 자동 검출"""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        
        left, right, widths = self._width_profile(mask)
        top_y, shoulder_y, chest_y, bottom_y = self._find_key_heights_shirt(widths)
        
        if top_y is None:
            return np.zeros((8, 2), dtype=int)
        
        chest_left = left[chest_y] if chest_y < len(left) else left[len(left)//2]
        chest_right = right[chest_y] if chest_y < len(right) else right[len(right)//2]
        x_center = (chest_left + chest_right) // 2
        
        keypoints = np.zeros((8, 2), dtype=int)
        h, w = mask.shape
        
        def clamp_point(x, y, margin=5):
            return [max(margin, min(x, w - margin)), max(margin, min(y, h - margin))]
        
        sleeve_search_range = int((bottom_y - shoulder_y) * 0.45)
        sleeve_end_y = min(shoulder_y + sleeve_search_range, bottom_y)
        
        max_left_x = chest_left
        max_right_x = chest_right
        
        for y in range(shoulder_y, sleeve_end_y):
            if y < len(left) and y < len(right):
                if left[y] < max_left_x:
                    max_left_x = left[y]
                if right[y] > max_right_x:
                    max_right_x = right[y]
        
        sleeve_mid_y = (shoulder_y + sleeve_end_y) // 2
        
        keypoints[0] = clamp_point(x_center, top_y)
        keypoints[1] = clamp_point(x_center, bottom_y)
        keypoints[2] = clamp_point(left[shoulder_y], shoulder_y)
        keypoints[3] = clamp_point(right[shoulder_y], shoulder_y)
        keypoints[4] = clamp_point(chest_left, chest_y)
        keypoints[5] = clamp_point(chest_right, chest_y)
        keypoints[6] = clamp_point(max_left_x, sleeve_mid_y)
        keypoints[7] = clamp_point(max_right_x, sleeve_mid_y)
        
        return keypoints
    
    def _auto_detect_keypoints_pants(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """바지 키포인트 자동 검출"""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        
        left, right, widths = self._width_profile(mask)
        result = self._find_key_heights_pants(widths)
        
        if result[0] is None:
            return np.zeros((9, 2), dtype=int)
        
        top_y, waist_y, crotch_y, hip_y, thigh_y, hem_y, bottom_y = result
        
        waist_left = left[waist_y] if waist_y < len(left) else left[len(left)//4]
        waist_right = right[waist_y] if waist_y < len(right) else right[len(right)//4]
        x_center = (waist_left + waist_right) // 2
        
        keypoints = np.zeros((9, 2), dtype=int)
        h, w = mask.shape
        
        def clamp_point(x, y, margin=5):
            return [max(margin, min(x, w - margin)), max(margin, min(y, h - margin))]
        
        # 엉덩이 폭은 crotch_y가 아닌 hip_y에서 계산해야 정확함
        hip_left_at_crotch = left[hip_y] if hip_y < len(left) else left[len(left)//3]
        hip_right_at_crotch = right[hip_y] if hip_y < len(right) else right[len(right)//3]
        thigh_left = left[thigh_y] if thigh_y < len(left) else left[len(left)//2]
        thigh_right = right[thigh_y] if thigh_y < len(right) else right[len(right)//2]
        hem_left = left[hem_y] if hem_y < len(left) else left[-10]
        hem_right = right[hem_y] if hem_y < len(right) else right[-10]
        
        keypoints[0] = clamp_point(x_center, top_y)
        keypoints[1] = clamp_point(waist_left, waist_y)
        keypoints[2] = clamp_point(waist_right, waist_y)
        keypoints[3] = clamp_point(hip_left_at_crotch, crotch_y)
        keypoints[4] = clamp_point(hip_right_at_crotch, crotch_y)
        keypoints[5] = clamp_point(thigh_left, thigh_y)
        keypoints[6] = clamp_point(thigh_right, thigh_y)
        keypoints[7] = clamp_point(hem_left, hem_y)
        keypoints[8] = clamp_point(hem_right, hem_y)
        
        return keypoints
    
    def _width_profile(self, binary_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """폭 프로파일 계산
        - 세로 방향 작은 구멍/하이라이트로 폭이 깎이지 않도록 5행 윈도우(최대값)로 합성 후 좌우 경계를 산출한다.
        """
        h, w = binary_mask.shape
        left = np.zeros(h, dtype=int)
        right = np.zeros(h, dtype=int)
        widths = np.zeros(h, dtype=int)

        window_half = 2  # 총 5행 윈도우
        for y in range(h):
            y0 = max(0, y - window_half)
            y1 = min(h - 1, y + window_half)
            rows = binary_mask[y0:y1+1]
            merged_row = (rows.max(axis=0) > 0)
            cols = np.where(merged_row)[0]
            if len(cols):
                left[y], right[y] = int(cols[0]), int(cols[-1])
                widths[y] = right[y] - left[y]

        return left, right, widths
    
    def _find_key_heights_shirt(self, widths: np.ndarray) -> Tuple:
        """상의 주요 높이 계산"""
        h = len(widths)
        valid_rows = np.where(widths > 0)[0]
        if len(valid_rows) == 0:
            return None, None, None, None
        
        top_y = valid_rows[0]
        bottom_y = valid_rows[-1]
        total_height = bottom_y - top_y
        
        shoulder_y = top_y + int(total_height * 0.15)
        chest_y = top_y + int(total_height * 0.35)
        
        max_width_idx = np.argmax(widths[valid_rows])
        actual_chest_y = valid_rows[max_width_idx]
        chest_y = int(0.7 * chest_y + 0.3 * actual_chest_y)
        
        return top_y, shoulder_y, chest_y, bottom_y
    
    def _find_key_heights_pants(self, widths: np.ndarray) -> Tuple:
        """바지 주요 높이 계산
        - hip_y: 고정 비율이 아닌 폭 프로파일의 지역 최대를 이용해 동적으로 결정
        """
        h = len(widths)
        valid_rows = np.where(widths > 0)[0]
        if len(valid_rows) == 0:
            return None, None, None, None, None, None, None
        
        top_y = valid_rows[0]
        bottom_y = valid_rows[-1]
        total_height = bottom_y - top_y
        
        waist_y = top_y + int(total_height * 0.05)
        crotch_y = top_y + int(total_height * 0.25)
        thigh_y = top_y + int(total_height * 0.40)
        hem_y = bottom_y - int(total_height * 0.05)

        # hip 후보 구간: 허리 아래 ~ 허벅지 위 사이(대략 25%~70%)
        start = top_y + int(total_height * 0.25)
        end = top_y + int(total_height * 0.70)
        start = max(start, top_y)
        end = min(end, bottom_y)

        if end <= start:
            hip_y = top_y + int(total_height * 0.32)
        else:
            # 간단한 이동평균으로 노이즈 완화 (바지 길이에 비례해 완만하게)
            k = max(13, (total_height // 35) * 2 + 1)  # 홀수 보장, 조금 더 넓게 평활화
            pad = k // 2
            padded = np.pad(widths.astype(float), (pad, pad), mode='edge')
            kernel = np.ones(k) / float(k)
            smoothed = np.convolve(padded, kernel, mode='valid')
            window = smoothed[start:end+1]
            if len(window) > 0:
                # 극단치 대신 상위 95퍼센타일에 가장 가까운 행을 선택
                target = np.percentile(window, 95)
                hip_rel = int(np.argmin(np.abs(window - target)))
                hip_y = start + hip_rel
            else:
                hip_y = top_y + int(total_height * 0.32)
        
        return top_y, waist_y, crotch_y, hip_y, thigh_y, hem_y, bottom_y
    
    def _get_dynamic_correction_factor(self, raw_measurement: float, measurement_type: str) -> float:
        """상의 동적 보정 계수"""
        base_corrections = {
            'length': 1.354,
            'shoulder': 1.381,
            'chest': 1.333,
            'sleeve': 1.667
        }
        
        base_factor = base_corrections[measurement_type]
        
        if measurement_type == 'shoulder':
            if raw_measurement < 20 or raw_measurement > 70:
                return base_factor * 0.8
            elif 35 <= raw_measurement <= 55:
                return base_factor
            else:
                return base_factor * 0.9
        
        elif measurement_type == 'sleeve':
            adjusted_base = base_factor * 0.833
            if 12 <= raw_measurement <= 20:
                return adjusted_base
            elif 8 <= raw_measurement < 12:
                return adjusted_base * 1.05
            elif 20 < raw_measurement <= 25:
                return adjusted_base * 0.95
            elif raw_measurement < 5 or raw_measurement > 35:
                return adjusted_base * 0.75
            else:
                return adjusted_base * 0.9
        
        return base_factor
    
    def _get_pants_correction_factor(self, raw_measurement: float, measurement_type: str) -> float:
        """하의 동적 보정 계수"""
        if measurement_type == 'length':
            if raw_measurement > 105:
                return 0.90
            elif raw_measurement > 100:
                return 0.95
            elif raw_measurement < 85:
                return 1.05
            else:
                return 1.00
        
        elif measurement_type == 'waist':
            if raw_measurement > 48:
                return 0.90
            elif raw_measurement > 45:
                return 0.95
            elif raw_measurement < 36:
                return 1.05
            else:
                return 1.00
        
        elif measurement_type == 'hip':
            if raw_measurement > 60:
                return 0.90
            elif raw_measurement > 56:
                return 0.95
            elif raw_measurement < 46:
                return 1.05
            else:
                return 1.00
        
        elif measurement_type == 'thigh':
            if raw_measurement > 36:
                return 0.90
            elif raw_measurement > 34:
                return 0.95
            elif raw_measurement < 26:
                return 1.05
            else:
                return 1.00
        
        elif measurement_type == 'hem':
            if raw_measurement > 27:
                return 0.95
            elif raw_measurement < 22:
                return 1.05
            else:
                return 1.00
        
        elif measurement_type == 'crotch':
            if raw_measurement > 40:
                return 0.92
            elif raw_measurement > 38:
                return 0.96
            elif raw_measurement < 30:
                return 1.05
            else:
                return 1.00
        
        return 1.00
    
    def _measure_shirt_with_keypoints(self, image: np.ndarray, a4_box: np.ndarray,
                                      keypoints: np.ndarray, pixelsPerCM_w: float, 
                                      pixelsPerCM_h: float, scale_w: float = 1.0, scale_h: float = 1.0) -> Dict:
        """사용자가 조정한 키포인트로 상의 측정"""
        vis = image.copy()
        cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3)
        
        # A4 기반 평면 보정으로 왜곡 최소화 후 측정
        Hmat, (W, H), scale = self._get_homography_for_a4(a4_box)
        warped_keypoints = self._warp_points(keypoints.astype(np.float32), Hmat).astype(np.float32)

        def horiz_cm_warp(p1, p2):
            return abs(p1[0] - p2[0]) / float(scale)

        def euclid_cm_warp(p1, p2):
            dx = (p1[0] - p2[0]) / float(scale)
            dy = (p1[1] - p2[1]) / float(scale)
            return (dx*dx + dy*dy) ** 0.5

        measurements = {}
        
        if len(warped_keypoints) >= 2:
            dx_cm = (warped_keypoints[0][0] - warped_keypoints[1][0]) / float(scale)
            dy_cm = (warped_keypoints[0][1] - warped_keypoints[1][1]) / float(scale)
            corrected_length = ((dx_cm * scale_w) ** 2 + (dy_cm * scale_h) ** 2) ** 0.5
            measurements["length"] = round(corrected_length, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[1]), (0,0,255), 2)
        
        if len(warped_keypoints) >= 4:
            raw_shoulder = horiz_cm_warp(warped_keypoints[2], warped_keypoints[3])
            corrected_shoulder = raw_shoulder * scale_w
            measurements["shoulder"] = round(corrected_shoulder, 1)
            cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[3]), (255,0,0), 2)
        
        if len(warped_keypoints) >= 6:
            raw_chest = horiz_cm_warp(warped_keypoints[4], warped_keypoints[5])
            corrected_chest = raw_chest * scale_w
            measurements["chest"] = round(corrected_chest, 1)
            cv2.line(vis, tuple(keypoints[4]), tuple(keypoints[5]), (0,255,0), 2)
        
        if len(warped_keypoints) >= 8:
            left_dx = (warped_keypoints[2][0] - warped_keypoints[6][0]) / float(scale)
            left_dy = (warped_keypoints[2][1] - warped_keypoints[6][1]) / float(scale)
            right_dx = (warped_keypoints[3][0] - warped_keypoints[7][0]) / float(scale)
            right_dy = (warped_keypoints[3][1] - warped_keypoints[7][1]) / float(scale)
            left_len = ((left_dx * scale_w) ** 2 + (left_dy * scale_h) ** 2) ** 0.5
            right_len = ((right_dx * scale_w) ** 2 + (right_dy * scale_h) ** 2) ** 0.5
            corrected_sleeve = max(left_len, right_len)
            measurements["sleeve"] = round(corrected_sleeve, 1)
            cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[6]), (128,0,128), 2)
            cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[7]), (128,0,128), 2)
        
        _, buffer = cv2.imencode('.jpg', vis)
        result_image = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "type": "shirt",
            "measurements": measurements,
            "result_image": result_image,
            "unit": "cm"
        }
    
    def _measure_pants_with_keypoints(self, image: np.ndarray, a4_box: np.ndarray,
                                      keypoints: np.ndarray, pixelsPerCM_w: float,
                                      pixelsPerCM_h: float, scale_w: float = 1.0, scale_h: float = 1.0,
                                      waist_corr: float = 1.0, hip_corr: float = 1.0, thigh_corr: float = 1.0) -> Dict:
        """사용자가 조정한 키포인트로 하의 측정"""
        vis = image.copy()
        cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3)
        
        # A4 기반 평면 보정: 키포인트를 보정 평면으로 변환하고 단일 scale(px/cm) 사용
        Hmat, (W, H), scale = self._get_homography_for_a4(a4_box)
        warped_keypoints = self._warp_points(keypoints.astype(np.float32), Hmat).astype(np.float32)

        # 키포인트 경계 외에도 윤곽 최하단을 이용하기 위해, 동일한 전처리로 윤곽을 추정하고 워핑한다
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, pants_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((5,5), np.uint8)
        pants_mask = cv2.morphologyEx(pants_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        pants_mask = cv2.dilate(pants_mask, kernel, iterations=1)
        contours, _ = cv2.findContours(pants_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        warped_contour = None
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            epsilon = 0.002 * cv2.arcLength(largest_contour, True)
            smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
            warped_contour = cv2.perspectiveTransform(smoothed_contour.astype(np.float32), Hmat).reshape(-1, 2)
        # 마스크 워핑: 최하단 픽셀 추정에 활용
        warped_mask = cv2.warpPerspective(pants_mask, Hmat, (W, H), flags=cv2.INTER_NEAREST)

        measurements = {}
        
        def horiz_cm_warp(p1, p2):
            return abs(p1[0] - p2[0]) / float(scale)
        
        def vert_cm_warp(p1, p2):
            return abs(p1[1] - p2[1]) / float(scale)
        
        if len(keypoints) >= 9:
            candidates = []
            candidates.append(vert_cm_warp(warped_keypoints[0], warped_keypoints[7]))
            candidates.append(vert_cm_warp(warped_keypoints[0], warped_keypoints[8]))
            # 윤곽/마스크 최하단까지의 수직거리도 후보로 사용
            top_y_px = float(warped_keypoints[0][1])
            if warped_contour is not None and warped_contour.size > 0:
                bottom_y_px = float(np.max(warped_contour[:, 1]))
                if bottom_y_px > top_y_px:
                    candidates.append((bottom_y_px - top_y_px) / float(scale))
            ys = np.where(warped_mask > 0)[0]
            if ys.size > 0:
                bottom_y_px2 = float(np.max(ys))
                if bottom_y_px2 > top_y_px:
                    candidates.append((bottom_y_px2 - top_y_px) / float(scale))
            raw_length = max(candidates) if len(candidates) else 0.0
            length_correction = self._get_pants_correction_factor(raw_length, 'length')
            corrected_length = raw_length * length_correction * scale_h
            measurements["length"] = round(corrected_length, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[7]), (0,0,255), 2)
        
        if len(keypoints) >= 3:
            raw_waist = horiz_cm_warp(warped_keypoints[1], warped_keypoints[2])
            waist_correction = self._get_pants_correction_factor(raw_waist, 'waist')
            corrected_waist = raw_waist * waist_correction * scale_w * waist_corr
            measurements["waist"] = round(corrected_waist, 1)
            cv2.line(vis, tuple(keypoints[1]), tuple(keypoints[2]), (255,0,0), 2)
        
        if len(keypoints) >= 5:
            raw_hip = horiz_cm_warp(warped_keypoints[3], warped_keypoints[4])
            hip_correction = self._get_pants_correction_factor(raw_hip, 'hip')
            corrected_hip = raw_hip * hip_correction * scale_w * hip_corr
            measurements["hip"] = round(corrected_hip, 1)
            cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[4]), (255,128,0), 2)
        
        if len(keypoints) >= 6:
            dx_cm = (warped_keypoints[0][0] - warped_keypoints[5][0]) / float(scale)
            dy_cm = (warped_keypoints[0][1] - warped_keypoints[5][1]) / float(scale)
            raw_crotch = (dx_cm**2 + dy_cm**2) ** 0.5
            crotch_correction = self._get_pants_correction_factor(raw_crotch, 'crotch')
            corrected_crotch = ((dx_cm * scale_w) ** 2 + (dy_cm * scale_h) ** 2) ** 0.5
            corrected_crotch *= crotch_correction
            measurements["crotch"] = round(corrected_crotch, 1)
            cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[5]), (255,255,0), 2)
        
        if len(keypoints) >= 7:
            raw_thigh = horiz_cm_warp(warped_keypoints[5], warped_keypoints[6])
            thigh_correction = self._get_pants_correction_factor(raw_thigh, 'thigh')
            corrected_thigh = raw_thigh * thigh_correction * scale_w * thigh_corr
            measurements["thigh"] = round(corrected_thigh, 1)
            cv2.line(vis, tuple(keypoints[5]), tuple(keypoints[6]), (0,255,0), 2)
        
        if len(keypoints) >= 9:
            raw_hem = horiz_cm_warp(warped_keypoints[7], warped_keypoints[8])
            hem_correction = 1.0
            corrected_hem = raw_hem * hem_correction * scale_w
            measurements["hem"] = round(corrected_hem, 1)
            cv2.line(vis, tuple(keypoints[7]), tuple(keypoints[8]), (128,0,128), 2)
        
        _, buffer = cv2.imencode('.jpg', vis)
        result_image = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "type": "pants",
            "measurements": measurements,
            "result_image": result_image,
            "unit": "cm"
        }
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """꼭짓점 좌표 정렬"""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

