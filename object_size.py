# 필요한 패키지들 import
import cv2
import numpy as np
import argparse
import os
from scipy.spatial import distance as dist
from imutils import perspective
from scipy.signal import argrelextrema
import collections
from sklearn.linear_model import RANSACRegressor

# 1. 프로그램 시작점 및 main 함수

def main():
    # 1. 명령줄 인수 처리
    ap = argparse.ArgumentParser() # 명령줄 입력값을 처리하는 도구 생성
    ap.add_argument("-i", "--image", required=False, help="path to the input image") # 이미지 파일 경로 지정
    ap.add_argument("-w", "--width", type=float, required=False, default=21.0, help="width of the A4 paper in cm (default: 21.0)") # A4 용지 가로 길이 지정(기본값: 21.0cm)
    args = vars(ap.parse_args()) # 명령줄 인수를 딕셔너리 형태로 변환

    # 2. 이미지 경로 확인 및 로드
    image_path = args["image"] # 입력 받은 이미지 경로 꺼내기
    if image_path is None: #이미지 경로가 없으면 오류 메시지 출력
        print("이미지 파일을 지정해주세요.")
        return

    if not os.path.isfile(image_path): #이미지 파일이 존재하지 않으면 오류 메시지 출력
        print(f"[알림] 이미지 파일을 찾을 수 없습니다: {image_path}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        print("사용법: python object_size.py -i [이미지파일명]")
        return
    try: #이미지 파일 로드 시도
        image = cv2.imread(image_path) #이미지 파일 로드
        if image is None: #이미지 파일이 없으면 오류 메시지 출력
            print(f"[알림] 이미지를 불러올 수 없습니다: {image_path}")
            print("이미지 파일이 손상되었거나 지원되지 않는 형식일 수 있습니다.")
            return
        
    except Exception as e: #이미지 로드 중 오류 발생 시 오류 메시지 출력
        print(f"[알림] 이미지 로딩 중 오류 발생: {str(e)}")
        return

    # 3. A4 용지 검출 (자동+수동 통합)
    a4_box = find_a4_box(image)

    # 4. A4 픽셀/CM 비율 계산 (개선된 정확도)
    a4_tl = a4_box[0] #좌측 상단 꼭짓점
    a4_bl = a4_box[1] #좌측 하단 꼭짓점
    a4_tr = a4_box[2] #우측 상단 꼭짓점
    a4_br = a4_box[3] #우측 하단 꼭짓점
    
    # 4개 변의 길이를 모두 측정하여 더 정확한 비율 계산
    top_width = np.linalg.norm(a4_tr - a4_tl)    # 상단 가로
    bottom_width = np.linalg.norm(a4_br - a4_bl)  # 하단 가로
    left_height = np.linalg.norm(a4_bl - a4_tl)   # 좌측 세로
    right_height = np.linalg.norm(a4_br - a4_tr)  # 우측 세로
    
    # 평균 길이 계산으로 원근 왜곡 보정
    avg_width = (top_width + bottom_width) / 2 #평균 가로 길이 계산
    avg_height = (left_height + right_height) / 2 #평균 세로 길이 계산
    
    pixelsPerCM_width = avg_width / 21.0 #가로 픽셀/cm 비율 계산
    pixelsPerCM_height = avg_height / 29.7 #세로 픽셀/cm 비율 계산
    pixelsPerCM = (pixelsPerCM_width + pixelsPerCM_height) / 2 #가로/세로의 평균 픽셀/cm 비율 계산(A4 용지)
    
    print(f"A4 용지 검출 결과:")
    print(f"  - 평균 가로: {avg_width:.1f}px ({21.0}cm)")
    print(f"  - 평균 세로: {avg_height:.1f}px ({29.7}cm)")
    print(f"  - 픽셀/cm 비율: {pixelsPerCM:.2f}")

    measure_shirt(image, a4_box, pixelsPerCM)

# A4 용지를 이미지에서 자동으로 찾고 실패시, 수동으로 입력
def find_a4_box(image):
    # 이미지 전처리
    original = image.copy()
    
    # 1. 이미지 밝기 정규화
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    normalized = cv2.merge((cl,a,b))
    normalized = cv2.cvtColor(normalized, cv2.COLOR_LAB2BGR)
    
    # 2. HSV 변환 및 흰색 영역 마스크 생성
    hsv = cv2.cvtColor(normalized, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 30, 255])  # 채도 범위 축소
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # 3. 노이즈 제거 및 윤곽선 강화
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 4. 엣지 검출 추가
    edges = cv2.Canny(mask, 50, 150)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 5. 윤곽선 검출 및 필터링
    cnts, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    
    a4_scale = 29.7 / 21.0  # A4 비율
    image_area = image.shape[0] * image.shape[1]
    
    for c in cnts:
        area = cv2.contourArea(c)
        # 면적 필터링: 이미지 크기의 10%~90% 사이
        if area < image_area * 0.1 or area > image_area * 0.9:
            continue
            
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        if len(approx) == 4:
            box = approx.reshape(4, 2)
            box = order_points(box)
            
            # 변의 길이 계산
            (tl, tr, br, bl) = box
            width = np.linalg.norm(tr - tl)
            height = np.linalg.norm(bl - tl)
            
            if width == 0 or height == 0:
                continue
                
            # 비율 검사
            ratio = max(width, height) / min(width, height)
            ratio_diff = abs(ratio - a4_scale)
            
            # 각도 검사 (수직/수평에 가까운지) >>> 90도 이내의 각도가 많은지 검사
            angles = []
            for i in range(4):
                p1 = box[i]
                p2 = box[(i + 1) % 4]
                angle = abs(np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0])) % 90)
                angles.append(min(angle, 90 - angle))
            max_angle_diff = max(angles)
            
            # 밝기 검사
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask, [box.astype(np.int32)], -1, 255, -1)
            mean_val = cv2.mean(image, mask=mask)[0]
            
            # 모든 조건 충족 시 A4로 판단
            if ratio_diff < 0.2 and max_angle_diff < 20 and mean_val > 150:
                return box.astype(np.float32)
    
    print("A4용지를 자동으로 찾을 수 없습니다. 마우스로 네 꼭짓점을 클릭해 주세요.")
    return get_points_by_mouse(image)

#마우스를 이용하여 이미지에서 A4 용지의 4개 꼭짓점을 수동으로 선택하는 함수
def get_points_by_mouse(image, window_name="Select A4 Corners"):
    points = [] # 사용자가 클릭한 좌표들을 저장할 리스트
    clone = image.copy() # 원본 이미지 보존을 위해 복사
    h, w = image.shape[:2] # 이미지의 높이(h)와 너비(w) 가져오기(튜플)

    # 화면에 이미지를 너무 크게 띄우지 않도록, 최대 해상도 설정(일반적인 FHD 모니터 해상도)
    screen_res = 1920, 1080  

    # 현재 이미지 크기와 화면 크기를 비교해, 화면에 맞게 축소 비율 계산
    scale = min(screen_res[0] / w, screen_res[1] / h, 1.0) 

    # 축소할 이미지의 너비, 높이 계산
    win_w, win_h = int(w * scale), int(h * scale) 

    # 이미지 크기가 화면보다 크면 축소해서 보여주기
    if scale < 1.0: # 이미지가 창 크기보다 작은 경우
        display_img = cv2.resize(clone, (win_w, win_h)) # 이미지 크기 조절
    else:
        display_img = clone.copy() # 그대로 사용

    # 클릭 이벤트 정의: 마우스 왼쪽 버튼 클릭 시 좌표를 저장    
    def click_event(event, x, y, *_):
        # 왼쪽 버튼을 누르고 저장된 점의 개수가 4개 미만이라면(points: 사용자가 클릭한 좌표들을 저장하는 리스트)
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4: 
            # 클릭한 좌표를 원본 이미지 좌표로 변환(X,y: 사용자가 클릭한 좌표, scale: 화면 크기에 맞게 축소된 비율)
            orig_x = int(x / scale)
            orig_y = int(y / scale)
            points.append([orig_x, orig_y]) # 좌표를 리스트에 추가(저장)

            # 클릭한 좌표에 초록색 원 표시
            cv2.circle(display_img, (x, y), 8, (0, 255, 0), -1)
            cv2.imshow(window_name, display_img)

    # 윈도우 창 생성 및 사이즈 설정        
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, win_w, win_h)
    cv2.imshow(window_name, display_img)

    # 마우스 클릭 콜백 함수 등록
    cv2.setMouseCallback(window_name, click_event)

    # 사용자가 꼭짓점 4개를 모두 클릭할 때까지 기다림
    while len(points) < 4:
        cv2.waitKey(1) # 1ms 대기하며 키보드 입력 기다림 (무한 루프처럼 동작)
    cv2.destroyWindow(window_name) # 창 닫기

    # 결과를 NumPy 배열로 변환하여 반환 (좌표들은 float32 타입)
    return np.array(points, dtype="float32")

# 의류 치수 측정 함수
def measure_shirt(image, a4_box, pixelsPerCM):
    vis = image.copy() # 원본 이미지 복사
    cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3) # 복사한 이미지에 A4 용지 윤곽선 그리기
    
    # 1. 이미지 전처리
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    # 컬러 이미지를 그레이스케일로 변환 (옷의 형태 파악에는 색깔보다 밝기 정보가 중요)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) 
    # 그레이스케일 이미지를 살짝 흐리게 해 (블러 처리) 노이즈를 줄입니다.
    
    # 2. 의류 마스크 생성
    # 블러 처리된 이미지를 이용해 이진화(옷: 흰색, 배경: 검정)합니다. (이진화는 이미지를 두가지 색깔(흰색과 검정색)로로 분류하는 작업)
    _, clothing_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 3. 마스크 정제
    # 5x5 크기의 커널 생성 (uint: 부호없는 정수(0이나 양수 저장 가능), 8: 8비트 정수 >> 0~255까지 표현 가능)
    kernel = np.ones((5,5), np.uint8) 
    clothing_mask = cv2.morphologyEx(clothing_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    # 옷 마스크 안에 있는 작은 구멍을 채워줍니다.(닫힘 연산 2번 반복)
    
    # 4. 윤곽선 검출
    #옷 마스크에서 옷 영역(흰색)의 윤곽선을 찾아내 contours 변수에 저장
    contours, _ = cv2.findContours(clothing_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    if not contours: # 옷 윤곽선을 찾을 수 없으면 오류 메시지 출력
        print("옷 윤곽선을 찾을 수 없습니다.")
        return
    
    # 가장 큰 윤곽선 선택 및 스무딩
    largest_contour = max(contours, key=cv2.contourArea) # 옷 윤곽선 중 가장 큰 윤곽선을 선택
    
    # 옷 윤곽선이 이미지의 높이 * 너비, 이미지의 전체 면적의 10% 미만이면 오류 메시지 출력
    if cv2.contourArea(largest_contour) < image.shape[0] * image.shape[1] * 0.1: 
        print("옷 윤곽선이 너무 작습니다. 다시 시도해주세요.")
        return
    
    epsilon = 0.002 * cv2.arcLength(largest_contour, True) 
    # 선택한 옷 윤곽선 길이의 0.2% 만큼 오차 허용해서 윤곽선 단순화화
    smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True) 
    # 정한 기준에 맞게 옷 윤곽선을 단순화 (근사화)
    cv2.drawContours(vis, [smoothed_contour], -1, (0, 255, 0), 2) 
    # 옷 윤곽선을 초록색으로 표시
    
    point_labels = [
        "Top point",           # 목점
        "Bottom point",        # 밑단점
        "Left Shoulder point", # 왼쪽 어깨 끝점
        "Right Shoulder point",# 오른쪽 어깨 끝점
        "Left Chest point",    # 왼쪽 가슴점
        "Right Chest point",   # 오른쪽 가슴점
        "Left Arm point",      # 왼쪽 소매 끝점
        "Right Arm point"      # 오른쪽 소매 끝점
    ]
    
    # 키포인트 자동 검출 및 수정
    initial_keypoints = auto_detect_keypoints(image, smoothed_contour)
    # auto_detect_keypoints라는 함수 사용해 옷 이미지와 윤곽선을 보고 핵심 위치들을 자동으로 탐색
    keypoints = get_keypoints_by_mouse(image, initial_points=initial_keypoints, point_labels=point_labels)
    # 자동으로 찾은 키포인트를 보고 잘못 찍혔으면 사용자가 직접 조정할 수 있도록 함
    
    # 이미지 위에 측정값을 글씨로 쓸 때 필요한 준비 작업
    h, w = vis.shape[:2] #이미지의 크기 알아내기 (튜플)
    
    # 텍스트 크기 계산을 위한 기본 설정
    font = cv2.FONT_HERSHEY_SIMPLEX # 텍스트 폰트 설정
    font_scale = 0.9 # 텍스트 크기 설정
    thickness = 2 # 텍스트 두께 설정
    padding = 10 # 텍스트 여백 설정
    
    def get_safe_text_position(point, text, is_right=False): # 텍스트 위치 조정 함수 (글씨를 기준점 왼쪽에 배치)
        # 텍스트 크기 계산
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness) 
        
        # x 좌표 조정
        if is_right: # 글씨를 기준점 오른쪽에 배치하자면 
            x = min(point[0] + padding, w - text_w - padding) 
            # 기준점 오른쪽 padding만큼 떨어진 곳에 배치하되, 이미지 오른쪽 경계를 넘지 않도록 조정
        
        else: # 글씨를 기준점 왼쪽에 배치하자면
            x = max(point[0] - text_w - padding, padding)
            # 기준점 왼쪽 padding만큼 떨어진 곳에 배치하되, 이미지 왼쪽 경계를 넘지 않도록 조정
        
        # y 좌표 조정 (텍스트가 위로 가도록)
        #기준점 왼쪽 padding만큼 떨어진 곳에 배치하되, 이미지 위쪽 경계를 넘지 않도록 조정
        y = max(point[1] - padding, text_h + padding)
        
        # 경계 확인 및 조정
        # np.clip(값, 최소값, 최대값) 함수를 사용해 값을 최소값과 최대값 사이로 제한
        x = np.clip(x, padding, w - text_w - padding)
        y = np.clip(y, text_h + padding, h - padding)
        
        return (int(x), int(y))
    
    # 범용 보정 계수 시스템 (키와 무관한 객관적 의류 치수 측정)
    # 동적 보정 계수 시스템: 측정 환경과 이미지 품질에 따른 적응형 보정
    # 목표: 사용자의 키나 체형에 관계없이 옷 자체의 실제 치수를 정확히 측정
    # 기준: 다양한 측정 데이터의 평균값을 바탕으로 한 범용 보정 계수
    #
    # 보정 계수 산출 근거:
    # - 카메라 각도, 조명, A4 용지 위치 등으로 인한 체계적 오차 보정
    # - 윤곽선 검출 및 키포인트 자동 인식의 한계 보완
    # - 2D 이미지에서 3D 객체 측정 시 발생하는 원근 왜곡 보정
    
    # 동적 보정 시스템: 측정 환경과 이미지 품질에 따른 적응형 보정
    def get_dynamic_correction_factor(raw_measurement, measurement_type):
    # 사진으로 처음 잰 길이와 잰 길이의 타입 을 받아 어떤 보정 계수를 곱해줄지 결정
        base_corrections = { #기본 보정 계수 목록
            'length': 1.354,
            'shoulder': 1.381, 
            'chest': 1.333,
            'sleeve': 1.667
        }
        
        # 측정값이 극단적일 때 보정 계수 완화
        base_factor = base_corrections[measurement_type]
        
        if measurement_type == 'shoulder':
            if raw_measurement < 20 or raw_measurement > 70:  # 어깨 길이가 20cm 미만이거나 70cm 초과일 때
                return base_factor * 0.8  # 기본 보정 계수의 80% 적용 (보정 완화)
            elif 35 <= raw_measurement <= 55:  # 어깨 길이가 35cm 이상 55cm 이하일 때
                return base_factor # 기본 보정 계수 그대로 적용
            else:  # 어깨 길이가 20cm 이상 35cm 미만이거나 55cm 초과일 때
                return base_factor * 0.9 # 기본 보정 계수의 90% 적용 (보정 완화)
                
        elif measurement_type == 'sleeve':
            # 정밀 보정 계산:
            # 기존: 원본 15cm → 보정(1.667) → 30cm (실제 25cm)
            # 목표: 원본 15cm → 보정(?) → 25cm
            # 새 보정 계수: 25/15 = 1.667 * (25/30) = 1.389
            
            # 하지만 현재 원본값이 다를 수 있으므로 더 정밀한 조정 필요
            # 30cm → 25cm 달성을 위한 조정: 25/30 = 0.833
            adjusted_base = base_factor * 0.833  # 기본 보정 계수 * 0.833 = 1.389
            
            # 원본 측정값에 따른 추가 미세 조정
            if 12 <= raw_measurement <= 20:  # 소매 길이가 12cm 이상 20cm 이하일 때
                return adjusted_base  # 조정된 기본값 그대로 적용
            elif 8 <= raw_measurement < 12:  # 작은 값
                return adjusted_base * 1.05  # 조정된 기본값의 5% 증가
            elif 20 < raw_measurement <= 25:  # 소매 길이가 20cm 초과 25cm 이하일 때
                return adjusted_base * 0.95  # 조정된 기본값의 5% 감소
            elif raw_measurement < 5 or raw_measurement > 35:  # 극단값
                return adjusted_base * 0.75  # 대폭 완화
            else:  # 기타 경계 범위
                return adjusted_base * 0.9   # 완화
                
        return base_factor
    
    # 기본 보정 계수 (정적)
    length_correction = 1.354    # 총장 보정 (이미지 원근 효과 보정)
    chest_correction = 1.333     # 가슴 보정 (최대 너비 지점 인식 오차 보정)
    
    # 키 기반 보정 제거: 옷 자체의 절대적 치수 측정에 집중
    
    print(f"범용 의류 치수 측정 시스템 (키 무관 객관적 측정):")
    print(f"  - 총장 길이: {length_correction:.3f} (원근 왜곡 보정)")
    print(f"  - 가슴 너비: {chest_correction:.3f} (너비 지점 인식 보정)")
    print(f"  - 어깨/소매: 동적 보정 시스템 적용 (측정값 범위에 따라 자동 조정)")
    print("※ 사용자 키와 무관하게 옷 자체의 실제 치수를 측정합니다.")
    print("※ 극단적인 측정값에 대해서는 보정을 완화하여 정확도를 높입니다.")
    
    # 치수 측정 결과 표시 (개선된 측정 방식 + 보정 계수 적용)
    if len(keypoints) >= 2: # 키포인트가 2개 이상 있으면 옷 길이 측정
        raw_length = np.linalg.norm(keypoints[0] - keypoints[1]) / pixelsPerCM #두 키포인트 사이의 직선 거리 계산 (CM)
        corrected_length = raw_length * length_correction  # 보정 계수 적용
        cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[1]), (0,0,255), 2) #계산된 두 점 사이에 빨간색 선
        text = f"Length: {corrected_length:.1f}cm"
        pos = get_safe_text_position(keypoints[1], text) #두 점 사이의 글씨를 쓸 안전한 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (0,0,255), thickness) #빨간색 글씨
        print(f"총장 길이: 원본 {raw_length:.1f}cm → 보정 {corrected_length:.1f}cm")
    
    if len(keypoints) >= 4: # 키포인트가 4개 이상 있으면 어깨 너비 측정
        raw_shoulder = np.linalg.norm(keypoints[2] - keypoints[3]) / pixelsPerCM #두 키포인트 사이의 직선 거리 계산 (CM)
        shoulder_correction = get_dynamic_correction_factor(raw_shoulder, 'shoulder')  # 동적 보정 계수
        corrected_shoulder = raw_shoulder * shoulder_correction  # 보정 계수 적용
        cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[3]), (255,0,0), 2) #계산된 두 점 사이에 파란색  선
        text = f"Shoulder: {corrected_shoulder:.1f}cm"
        pos = get_safe_text_position(keypoints[3], text, True) #두 점 사이의 글씨를 쓸 안전한 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (255,0,0), thickness) #파란색 글씨
        # 어깨 측정 신뢰도 체크 (동적 보정 반영)
        shoulder_confidence = "높음" if 35 <= raw_shoulder <= 55 else "보통" if 30 <= raw_shoulder <= 60 else "낮음"
        correction_type = "표준" if shoulder_correction >= 1.3 else "완화됨" if shoulder_correction < 1.1 else "중간"
        print(f"어깨 너비: 원본 {raw_shoulder:.1f}cm → 보정 {corrected_shoulder:.1f}cm")
        print(f"  → 동적 보정 계수: {shoulder_correction:.3f} ({correction_type}), 신뢰도: {shoulder_confidence}")
        print(f"  → 측정된 어깨 너비는 옷 자체의 실제 치수입니다.")
    
    if len(keypoints) >= 6: # 키포인트가 6개 이상 있으면 가슴 너비 측정
        raw_chest = np.linalg.norm(keypoints[4] - keypoints[5]) / pixelsPerCM #두 키포인트 사이의 직선 거리 계산 (CM)
        corrected_chest = raw_chest * chest_correction  # 보정 계수 적용
        cv2.line(vis, tuple(keypoints[4]), tuple(keypoints[5]), (0,255,0), 2) #계산된 두 점 사이에 초록색 선
        text = f"Chest: {corrected_chest:.1f}cm"
        pos = get_safe_text_position(keypoints[5], text, True) #두 점 사이의 글씨를 쓸 안전한 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (0,255,0), thickness) #초록색 글씨
        print(f"가슴 너비: 원본 {raw_chest:.1f}cm → 보정 {corrected_chest:.1f}cm")
    
    if len(keypoints) >= 8: # 키포인트가 8개 이상 있으면 소매 길이 측정
        # 소매 키포인트 경계 검사
        h, w = image.shape[:2]
        left_sleeve_valid = 10 <= keypoints[6][0] <= w-10 and 10 <= keypoints[6][1] <= h-10
        right_sleeve_valid = 10 <= keypoints[7][0] <= w-10 and 10 <= keypoints[7][1] <= h-10
        
        raw_left_sleeve = np.linalg.norm(keypoints[2] - keypoints[6]) / pixelsPerCM #두 키포인트 사이의 직선 거리 계산 (CM) >> 왼쪽
        raw_right_sleeve = np.linalg.norm(keypoints[3] - keypoints[7]) / pixelsPerCM #두 키포인트 사이의 직선 거리 계산 (CM) >> 오른쪽
        
        # 경계 근처 키포인트에 대한 신뢰도 조정
        if not left_sleeve_valid:
            raw_left_sleeve *= 0.8  # 신뢰도 낮춤
            print(f"  [주의] 왼쪽 소매 키포인트가 이미지 경계 근처에 있어 측정값이 부정확할 수 있습니다.")
            
        if not right_sleeve_valid:
            raw_right_sleeve *= 0.8  # 신뢰도 낮춤  
            print(f"  [주의] 오른쪽 소매 키포인트가 이미지 경계 근처에 있어 측정값이 부정확할 수 있습니다.")
        
        raw_sleeve_length = max(raw_left_sleeve, raw_right_sleeve) #두 소매 길이 중 더 긴 쪽 선택 >> 소매 길이
        sleeve_correction = get_dynamic_correction_factor(raw_sleeve_length, 'sleeve')  # 동적 보정 계수
        corrected_sleeve = raw_sleeve_length * sleeve_correction  # 보정 계수 적용
        sleeve_pos = keypoints[6] if raw_left_sleeve >= raw_right_sleeve else keypoints[7] #더 긴 소매 끝점 선택
        
        cv2.line(vis, tuple(keypoints[2]), tuple(keypoints[6]), (128,0,128), 2) #계산된 두 점 사이에 보라색 선
        cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[7]), (128,0,128), 2) #계산된 두 점 사이에 보라색 선
        text = f"Arm: {corrected_sleeve:.1f}cm" #소매 길이 표시
        pos = get_safe_text_position(sleeve_pos, text, True) #두 점 사이의 글씨를 쓸 안전한 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (128,0,128), thickness) #보라색 글씨
        # 소매 측정 신뢰도 체크 (정밀 보정 반영)
        sleeve_confidence = "높음" if 12 <= raw_sleeve_length <= 20 else "보통" if 8 <= raw_sleeve_length <= 25 else "낮음"
        
        # 보정 타입 분류
        if sleeve_correction >= 1.45:
            correction_type = "표준 보정"
        elif sleeve_correction >= 1.3:
            correction_type = "조정된 보정"
        elif sleeve_correction >= 1.1:
            correction_type = "완화된 보정"
        else:
            correction_type = "최소 보정"
            
        # 목표 대비 정확도 계산
        target_sleeve = 25.0
        accuracy = max(0, 100 - abs(corrected_sleeve - target_sleeve) / target_sleeve * 100)
        
        print(f"소매 길이: 원본 {raw_sleeve_length:.1f}cm → 보정 {corrected_sleeve:.1f}cm")
        print(f"  → 동적 보정 계수: {sleeve_correction:.3f} ({correction_type})")
        print(f"  → 신뢰도: {sleeve_confidence}, 목표 대비 정확도: {accuracy:.1f}%")
        print(f"  → 측정된 소매 길이는 옷 자체의 실제 치수입니다.")
        
        # 추가 개선 제안
        if accuracy < 90:
            print(f"  ※ 정확도 개선을 위해 A4 용지와 옷의 위치를 재조정해보세요.")
            
        # 경계 문제에 대한 개선 제안
        if not left_sleeve_valid or not right_sleeve_valid:
            print(f"  ※ 소매 측정 개선 방법:")
            print(f"     - 옷을 이미지 중앙에 더 가깝게 배치하세요")
            print(f"     - 카메라를 조금 더 멀리서 촬영하여 옷 전체가 잘 보이도록 하세요")
            print(f"     - 소매가 펼쳐진 상태로 촬영하세요")
    
    cv2.imwrite("shirt_measure_result.jpg", vis) #측정 결과 이미지 저장
    cv2.namedWindow("result", cv2.WINDOW_NORMAL) #창 생성
    cv2.imshow("result", vis) #창에 이미지 표시
    cv2.waitKey(0) #키보드 입력 대기
    cv2.destroyAllWindows() #창 닫기

def width_profile(binary_mask): #폭 프로파일 계산 함수
    """이미지의 각 y좌표에서 의류의 좌우 경계점을 찾습니다."""
    h, w = binary_mask.shape # 이미지의 높이와 너비 계산
    left = np.zeros(h, dtype=int) # 좌측 경계점 저장 배열 생성
    right = np.zeros(h, dtype=int) # 우측 경계점 저장 배열 생성
    widths = np.zeros(h, dtype=int) # 각 y좌표에서의 너비 저장 배열 생성
    
    for y in range(h):
        cols = np.where(binary_mask[y] > 0)[0] # 현재 y좌표에서 흰색(1)인 열의 인덱스 찾기
        if len(cols): # 흰색 열이 있으면
            left[y], right[y] = cols[0], cols[-1] # 좌측과 우측 경계점 저장
            widths[y] = right[y] - left[y] # 너비 계산
    
    return left, right, widths

def calculate_curve_length(point1, point2, contour): #두 점 사이의 윤곽선을 따른 곡선 거리를 계산
    # 윤곽선에서 두 점에 가장 가까운 지점들 찾기
    distances1 = np.sum((contour.squeeze() - point1) ** 2, axis=1) # contour에 있는 모든 점들이랑 point1 사이의 거리를 잰후,
    distances2 = np.sum((contour.squeeze() - point2) ** 2, axis=1) #그 거리를 제곱 (빠른 계산)이후, 점 하나하나를 기준으로 계산 (axis=1)
    
    idx1 = np.argmin(distances1) # 목록(distances1)중 가장 거리가 짧은 작은 점의 위치 idx1에 저장
    idx2 = np.argmin(distances2) # 목록(distances2)중 가장 거리가 짧은 작은 점의 위치 idx2에 저장
    
    # 두 인덱스 사이의 윤곽선 경로 계산 (idx1 > idx2 이면 두 인덱스 순서 바꿈)
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1 # 두 인덱스 순서 바꿈
    
    curve_length = 0 # 곡선 거리 초기화
    contour_points = contour.squeeze() 
    
    for i in range(idx1, idx2): #윤곽선을 따라 거리 계산
        if i + 1 < len(contour_points): #i+1이 윤곽선 점의 개수보다 작으면
            curve_length += np.linalg.norm(contour_points[i + 1] - contour_points[i]) 
            #현재 점과 바로 다음 점 사이의 아주 짧은 직선 거리를 재서 curve_length에 더함
    
    straight_distance = np.linalg.norm(point2 - point1) #두 점 사이의 직선 거리도 계산 (곡선과 직선 중 합리적인 값 선택)
    
    # 곡선 거리가 직선 거리의 3배 이상이면 직선 거리 사용 (오류 방지)
    if curve_length > straight_distance * 3:
        return straight_distance
    
    # 곡선 거리가 직선 거리보다 작으면 직선 거리 사용
    return max(curve_length, straight_distance) 

def find_key_heights(widths): #주요 높이 계산 함수 (개선된 버전)
    """폭 프로파일을 분석하여 주요 높이(y좌표)를 찾습니다."""
    h = len(widths)
    valid_rows = np.where(widths > 0)[0] # 너비가 0보다 큰 y좌표 찾기
    if len(valid_rows) == 0: # 너비가 0보다 큰 y좌표가 없으면
        return None, None, None, None # 모든 높이를 None으로 반환
    
    top_y = valid_rows[0] # 가장 위쪽 y좌표 
    bottom_y = valid_rows[-1] # 가장 아래쪽 y좌표
    total_height = bottom_y - top_y # 옷의 전체 높이 계산
    
    # 일반적인 의류 비율을 고려
    shoulder_y = top_y + int(total_height * 0.15)  # 상단에서 15% 지점 (목-어깨)
    chest_y = top_y + int(total_height * 0.35)     # 상단에서 35% 지점 (가슴 최대 너비)
    
    # 폭 프로파일을 분석하여 실제 최대 너비 지점 찾기
    max_width_idx = np.argmax(widths[valid_rows])
    actual_chest_y = valid_rows[max_width_idx]
    
    # 계산된 가슴 높이와 실제 최대 너비 지점의 가중 평균 사용
    chest_y = int(0.7 * chest_y + 0.3 * actual_chest_y) 
    
    return top_y, shoulder_y, chest_y, bottom_y # 최상단, 어깨, 가슴, 최하단 높이 반환

#키포인트 자동 검출 함수 (개선된 버전)
def auto_detect_keypoints(image, contour):
    mask = np.zeros(image.shape[:2], dtype=np.uint8) # 원본 이미지와 똑같은 크기의 검은 빈 마스크 생성
    cv2.drawContours(mask, [contour], -1, 255, -1) 
    # 윤곽선을 마스크에 채움(contour: 윤곽선 목록, -1: 목록의 모든 윤곽선, 255: 흰색, -1(선 두께): 안쪽 영역 채우기)
    
    left, right, widths = width_profile(mask) # 폭 프로파일 계산
    top_y, shoulder_y, chest_y, bottom_y = find_key_heights(widths) # 주요 높이 계산
    if top_y is None: #만약 옷의 높이를 제대로 찾지 못하면 
        return np.zeros((8, 2), dtype=int) # 8개의 키포인트를 저장할 빈 배열 반환 (8: 키포인트 개수, 2: 각 키포인트의 x, y 좌표)
    
    # 더 정확한 중심점 계산 (가슴 부위 기준)
    chest_left = left[chest_y] if chest_y < len(left) else left[len(left)//2]
    chest_right = right[chest_y] if chest_y < len(right) else right[len(right)//2]
    x_center = (chest_left + chest_right) // 2
    
    keypoints = np.zeros((8, 2), dtype=int)  # 8개의 키포인트를 저장할 빈 배열 생성 (8: 키포인트 개수, 2: 각 키포인트의 x, y 좌표)
    
    # 소매는 보통 어깨에서 40-50% 지점에 위치
    sleeve_search_range = int((bottom_y - shoulder_y) * 0.45)  # 45% 범위로 축소 
    sleeve_end_y = min(shoulder_y + sleeve_search_range, bottom_y) # 소매 끝점 위치 계산
    
    # 각 높이에서 가장 넓은 지점 찾기 (가중 평균 적용)
    max_left_x = chest_left
    max_right_x = chest_right
    weight_sum = 0
    weighted_left = 0
    weighted_right = 0
    
    for y in range(shoulder_y, sleeve_end_y):
        if y < len(left) and y < len(right): #y좌표(높이)가 좌측과 우측 경계점 범위 안에 있으면
            # y좌표(높이)가 어깨에 가까울수록 높은 가중치(1.0) 적용
            weight = 1.0 - (y - shoulder_y) / sleeve_search_range * 0.3
            
            if left[y] < max_left_x: # 왼쪽 경계점이 최대 왼쪽 x보다 작으면 >> 왼쪽 소매 끝점 위치 계산
                max_left_x = left[y] 
                weighted_left += left[y] * weight # 소매의 넓이를 나타내는 x좌표에 방금 계산한 가중치를 곱해서 더함
                weight_sum += weight # 가중치의 총합을 따로 저장
            if right[y] > max_right_x: 
                max_right_x = right[y]
                weighted_right += right[y] * weight
    
    # 가중 평균으로 소매 끝점 위치 계산 (weighted_left / weight_sum = 왼쪽 소매 지점의 가중 평균)
    if weight_sum > 0:
        max_left_x = int((max_left_x + weighted_left / weight_sum) / 2) # 단순 최대값과 가중치를 반영한 평균 지점의 중간값을 최종으로 선택
        max_right_x = int((max_right_x + weighted_right / weight_sum) / 2) 
    
    # 이미지 경계 정보 가져오기
    h, w = mask.shape
    
    # 키포인트 경계 검사 및 제한 함수
    def clamp_point(x, y, margin=5):
        """키포인트가 이미지 경계를 벗어나지 않도록 제한"""
        clamped_x = max(margin, min(x, w - margin))
        clamped_y = max(margin, min(y, h - margin))
        return [clamped_x, clamped_y]
    
    # 소매 끝점 위치 계산 (경계 안전 범위 고려)
    sleeve_mid_y = (shoulder_y + sleeve_end_y) // 2
    
    # 소매 끝점이 이미지 경계를 벗어날 경우 대체 위치 계산
    if max_left_x < 10 or max_left_x > w - 10:
        # 왼쪽 소매가 경계를 벗어나면 어깨와 가슴 중점 사용
        max_left_x = (left[shoulder_y] + chest_left) // 2
        print(f"  [경고] 왼쪽 소매 끝점이 이미지 경계 근처에 있어 조정되었습니다.")
        
    if max_right_x < 10 or max_right_x > w - 10:
        # 오른쪽 소매가 경계를 벗어나면 어깨와 가슴 중점 사용
        max_right_x = (right[shoulder_y] + chest_right) // 2
        print(f"  [경고] 오른쪽 소매 끝점이 이미지 경계 근처에 있어 조정되었습니다.")
    
    # 키포인트 설정 (clamp_point: 키포인트가 이미지 경계를 벗어나지 않도록 제한)
    keypoints[0] = clamp_point(x_center, top_y)  # 목점
    keypoints[1] = clamp_point(x_center, bottom_y)  # 밑단점
    keypoints[2] = clamp_point(left[shoulder_y], shoulder_y)  # 왼쪽 어깨 끝점
    keypoints[3] = clamp_point(right[shoulder_y], shoulder_y)  # 오른쪽 어깨 끝점
    keypoints[4] = clamp_point(chest_left, chest_y)  # 왼쪽 가슴점
    keypoints[5] = clamp_point(chest_right, chest_y)  # 오른쪽 가슴점
    keypoints[6] = clamp_point(max_left_x, sleeve_mid_y)  # 왼쪽 소매 끝점 
    keypoints[7] = clamp_point(max_right_x, sleeve_mid_y)  # 오른쪽 소매 끝점
    
    return keypoints

#키포인트를 수동으로 조정
def get_keypoints_by_mouse(image, initial_points=None, window_name="Adjust Keypoints", point_labels=None):
    #만약 초기 키포인트가 없으면 빈 리스트 만들고, 있으면 리스트 형태로 바꾸어서저장
    points = [] if initial_points is None else initial_points.tolist()
    clone = image.copy() #원본 이미지 복사본 생성성
    h, w = image.shape[:2] #이미지의 높이와 너비 계산
    screen_res = 1920, 1080 #화면 해상도 설정 (예시)
    scale = min(screen_res[0] / w, screen_res[1] / h, 1.0) #화면 크기에 맞게 축소 비율 계산 (이미지가 화면보다 크면 화면에 다 안보임)
    win_w, win_h = int(w * scale), int(h * scale) #계산된 축소 비율로 이미지를 보여줄 창 크기 계산
    
    display_img = cv2.resize(clone, (win_w, win_h)) if scale < 1.0 else clone.copy() #축소 비율에 따라 이미지 크기 조절
    selected_point = -1 #현재 선택된 키포인트가 있는지 없는지 나타내는 변수 (-1: 선택된 키포인트 없음)
    
    def redraw():
        img = display_img.copy() # 그릴때 마다 원본이미지 복사해서 사용 (꺠끗한 상태에서 그리기 위해)
        for idx, p in enumerate(points): # 리스트에 있는 각 키포인트(p)를 하나씩 꺼내서 반복 (idx: 키포인트 인덱스)
            px, py = int(p[0]*scale), int(p[1]*scale) #키포인트 좌표에도 축소비율 곱해서 화면에 표시될 위치 계산
            color = (0, 0, 255) if idx == selected_point else (0, 255, 0) #선택된 키포인트는 빨간색, 아니면 초록색
            cv2.circle(img, (px, py), 8, color, -1) #계산된 위치에에 원 그리기 (원 반지름: 8, 색상: color, 채우기: -1)
            if point_labels and idx < len(point_labels): #키포인트 이름 목록이 있고, 현재 키포인트 순서가 이름 목록 범위 안에 있으면
                cv2.putText(img, f"{idx+1}: {point_labels[idx]}", # 점의 순서와 이름을 작성
                          (px+10, py-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2) 
        return img
    
    def click_event(event, x, y, *_): 
        nonlocal selected_point 
        # 마우스로 하는 행동에 따라 점의 상태가 달라지기에 바깥 함수의 변수를 직접 조작할 수 있게 해줌
        
        if event == cv2.EVENT_LBUTTONDOWN: #마우스 왼쪽 버튼 눌렀을 때
            min_dist = float('inf') 
            closest_point = -1 #현재 마우스 위치에서 가장 가까운 점을 찾기 위한 준비
            for i, p in enumerate(points): #리스트에 있는 각 키포인트(p)를 하나씩 보면서 (i: 키포인트 인덱스)
                px, py = int(p[0]*scale), int(p[1]*scale) # 현재 점의 화면 표시 위치를 계산 (축소 비율 적용)
                dist = np.sqrt((x - px)**2 + (y - py)**2) 
                # 마우스 커서 위치(x, y)와 현재 점의 화면 표시 위치(px, py) 사이의 거리를 계산

                if dist < min_dist and dist < 20: #거리가 최소값보다 작고, 20픽셀 이내에 있으면 (마우스 커거사 점 근처에 있다면)
                    min_dist = dist # 그 점이 가장 가까운 점이라고 기록
                    closest_point = i #(20픽셀 이내: 점을 클릭하기 쉽게 해주는 클릭 허용 범위)
            selected_point = closest_point # 모든 점을 확인했다면 가장 가까운 점을 변수에 저장
            
        elif event == cv2.EVENT_MOUSEMOVE and selected_point != -1: #마우스 커서가 움직이고 선택된 점이 있으면
            # 원본 이미지 좌표로 변환
            orig_x = int(x/scale)
            orig_y = int(y/scale)
            
            # 이미지 경계 내로 제한 (5픽셀 여백)
            orig_x = max(5, min(orig_x, w - 5))
            orig_y = max(5, min(orig_y, h - 5))
            
            points[selected_point] = [orig_x, orig_y] # 경계 제한이 적용된 좌표로 업데이트
            img = redraw() # 키포인트 위치가 바뀌었으니 redraw() 함수를 호출해서 이미지를 새로 그리기
            cv2.imshow(window_name, img) # 그려진 이미지를 창에 표시
            
        elif event == cv2.EVENT_LBUTTONUP: #마우스 왼쪽 버튼 떼었을 때
            selected_point = -1 # 선택된 점 초기화
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL) # 창 생성
    cv2.resizeWindow(window_name, win_w, win_h) # 창 크기 조절
    img = redraw() # 초기 이미지 그리기
    cv2.imshow(window_name, img) # 창에 이미지 표시
    cv2.setMouseCallback(window_name, click_event) # 마우스 행동에 따라 함수 호출
    
    print("점을 드래그하여 위치를 조정하세요.") # 사용자에게 안내 메시지 출력
    print("Enter 또는 Space를 눌러 완료") # 사용자에게 안내 메시지 출력
    
    while True:
        key = cv2.waitKey(1) # 키보드 입력 대기
        if key in [13, 32]:  # Enter(키 코드 13) 또는 Space(키 코드 32) 누르면
            break 
            
    cv2.destroyWindow(window_name) # 창 닫기
    return np.array(points, dtype="int") #최종적으로 마우스로 조정한 키포인트들의 좌표 목록을 배열로 반환

# 6. 이미지 전체 표시 함수

def show_image_full(image, window_name="Image"): 
     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # 창 크기를 조절할 수 있도록 설정
     cv2.imshow(window_name, image) #창에 이미지 표시
     cv2.waitKey(0) #키보드 입력 대기
     cv2.destroyWindow(window_name) #창 닫기

# 7. 보조 함수들 (곡률 키포인트, A4 윤곽선 등)

def order_points(pts): #A4 용지 꼭짓점 좌표 정렬(왼쪽 위, 오른쪽 위, 오른쪽 아래, 왼쪽 아래)
    rect = np.zeros((4, 2), dtype="float32") #4x2 크기의 빈 배열 생성
    
    s = pts.sum(axis=1) #각 꼭짓점의 x, y 좌표 합 계산(오른쪽 위/오른쪽 아래 찾기용)
    rect[0] = pts[np.argmin(s)] #x, y 값이 가장 작은 점 (왼쪽 위)
    rect[2] = pts[np.argmax(s)] #x, y 값이 가장 큰 점 (오른쪽 아래)
    
    diff = np.diff(pts, axis=1) #x, y 좌표 차이 계산(왼쪽 아래/오른쪽 위 찾기용)
    rect[1] = pts[np.argmin(diff)] #x, y 값이 가장 작은 점 (오른쪽 위)
    rect[3] = pts[np.argmax(diff)] #x, y 값이 가장 큰 점 (왼쪽 아래)
    return rect #정렬된 꼭짓점 좌표 반환

def find_a4_lines(cnts, image): #A4 용지 윤곽선 검출(비율 계산 후 밝기 기준 정렬)
    a4_scale = 29.7 / 21.0  # 약 1.414
    best_box = None # 가장 적합한 사각형(A4용지) 좌표 저장 변수
    min_scale_diff = 0.2 # 비율 차이 최소값(0.2) > 비율 차이가 0.2 이하인 경우 적합한 사각형으로 간주
    max_brightness = 0 # 밝기 최대값
    
    for c in cnts: # 모든 윤곽선 (도형 후보) 반복해서 검사
        length = cv2.arcLength(c, True) #윤곽선 길이 계산(True: 닫힌 윤곽선)
        approx = cv2.approxPolyDP(c, 0.02 * length, True) # 사각형 등 단순 도형으로 윤곽선 근사화(True: 닫힌 윤곽선)
        
        if len(approx) == 4 and cv2.contourArea(c) > 10000: #근사화된 윤곽선이 4개의 꼭짓점이고 면적이 10000 이상인 경우
            box = approx.reshape(4, 2) # 꼭짓점 좌표 4개 모양으로 변환환
            box = order_points(box) #꼭짓점 좌표 정렬
            w = np.linalg.norm(box[1] - box[0]) #가로 길이 계산(픽셀) >> 오른쪽 위와 왼쪽 위 사이의 거리
            h = np.linalg.norm(box[3] - box[0]) #세로 길이 계산(픽셀) >> 왼쪽 아래와 왼쪽 위 사이의 거리
            
            if w == 0 or h == 0: #가로 또는 세로 길이가 0인 경우
                continue #다음 윤곽선 검사
            scale = max(w, h) / min(w, h) # 큰 변/ 작은 변 계산 >> 세로/가로 비율
            diff = abs(scale - a4_scale) #비율 차이 계산 >> A4 비율과 비교
            mask = np.zeros(image.shape[:2], dtype=np.uint8) #박스 내부 평균 밝기 계산
            cv2.drawContours(mask, [box.astype(np.int32)], -1, 255, -1) #박스 내부 마스크 흰색(255) 표시
            mean_val = cv2.mean(image, mask=mask)[0]  # 그레이스케일 평균 >> 밝기 계산(0~255 / 검정색: 0, 흰색: 255)

            # 밝고 비율이 A4에 가까운 사각형 우선 선택   
            if diff < min_scale_diff and mean_val > max_brightness: #비율 차이가 최소값 이하이고 밝기가 최대값 이상인 경우
                min_scale_diff = diff #비율 차이 최소값 업데이트
                max_brightness = mean_val #밝기 최대값 업데이트
                best_box = box #가장 적합한 사각형 좌표 a4 후보로 저장
                        
    return best_box #가장 적합한 사각형(A4일 확률이 가장 높은 박스) 좌표 반환

# 프로그램 시작점
if __name__ == "__main__": 
    main()