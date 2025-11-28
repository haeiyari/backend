# 필요한 패키지들 import
import cv2
import numpy as np
import argparse
import os

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
        print("사용법: python pants_size.py -i [이미지파일명]")
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

    # 4. A4 픽셀/CM 비율 계산
    
    a4_tl = a4_box[0] # 좌측 상단 꼭짓점
    a4_tr = a4_box[1] # 우측 상단 꼭짓점
    a4_br = a4_box[2] # 우측 하단 꼭짓점
    a4_bl = a4_box[3] # 좌측 하단 꼭짓점
    
    # 4개 변의 길이를 측정(np.linalg.norm: 두 점 사이의 거리를 구하는 수학 공식)
    top_width = np.linalg.norm(a4_tr - a4_tl)     # 윗변 픽셀 길이
    bottom_width = np.linalg.norm(a4_br - a4_bl)  # 아랫변 픽셀 길이
    left_height = np.linalg.norm(a4_bl - a4_tl)   # 왼쪽 세로 픽셀 길이
    right_height = np.linalg.norm(a4_br - a4_tr)  # 오른쪽 세로 픽셀 길이
    
    # 평균 길이 계산으로 원근 왜곡 보정
    avg_width = (top_width + bottom_width) / 2 #평균 가로 길이 계산(상단가로 + 하단가로 / 2)
    avg_height = (left_height + right_height) / 2 #평균 세로 길이 계산(좌측세로 + 우측세로 / 2)
    
    pixelsPerCM_width = avg_width / 21.0 # 가로 비율 계산(A4 용지 가로길이 / 21.0cm)
    pixelsPerCM_height = avg_height / 29.7 # 세로 비율 계산(A4 용지 세로길이 / 29.7cm)
    pixelsPerCM = (pixelsPerCM_width + pixelsPerCM_height) / 2 # 두 비율의 전체 평균값 (A4 용지)
    
    print(f"A4 용지 검출 결과:")
    print(f"  - 평균 가로: {avg_width:.1f}px ({21.0}cm)")
    print(f"  - 평균 세로: {avg_height:.1f}px ({29.7}cm)")
    print(f"  - 픽셀/cm 비율(가로, 세로): {pixelsPerCM_width:.2f}, {pixelsPerCM_height:.2f} (평균 {pixelsPerCM:.2f})")
 
    measure_pants(image, a4_box, pixelsPerCM_width, pixelsPerCM_height)

# A4 용지를 이미지에서 자동으로 찾고 실패시, 수동으로 입력
def find_a4_box(image):
    # 이미지 전처리
    original = image.copy() # 원본 이미지 복사
    
    # 1. 이미지 밝기 정규화
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB) # 이미지를 LAB 색상 공간으로 변환
    l, a, b = cv2.split(lab) # 밝기와 색상 정보를 분리
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)) # 밝기 보정 도구(clahe) 준비
    cl = clahe.apply(l) # 밝기 정보만 보정 적용(색상 정보는 유지)
    normalized = cv2.merge((cl,a,b)) # 보정된 밝기와 원본 색상 합침
    normalized = cv2.cvtColor(normalized, cv2.COLOR_LAB2BGR) # LAB 색상 공간을 BGR 색상 공간으로 변환
    
    # 2. HSV 변환 및 흰색 영역 마스크 생성
    hsv = cv2.cvtColor(normalized, cv2.COLOR_BGR2HSV) # 이미지를 HSV 색상 공간으로 변환(무채색이면서 밝은 픽셀을 골라내는 것).
    lower_white = np.array([0, 0, 180]) # 흰색 영역 하한 값
    upper_white = np.array([180, 30, 255])  # 채도 범위 축소
    mask = cv2.inRange(hsv, lower_white, upper_white) # HSV 색상 공간에서 흰색 영역 마스크 생성
    
    # 3. 노이즈 제거 및 윤곽선 강화
    kernel = np.ones((5,5), np.uint8) # 5x5 크기의 커널 생성
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2) # A4 용지 내부 노이즈 제거를 위해 Morphology(형태학) 연산을 통해
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1) # 구멍들을 메우고(close) 작은 점들을 지워서(open), A4 용지를 깔끔한 단일 객체로.
    
    # 4. 윤곽선 검출
    edges = cv2.Canny(mask, 50, 150) # canny로 엣지 검출
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 5. 윤곽선 검출 및 필터링
    cnts, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # findContours로 외곽선 수집
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True) #A4용지 후보 목록 확보(면적 기준 정렬)
    
    a4_scale = 29.7 / 21.0  # A4 비율
    image_area = image.shape[0] * image.shape[1]
    
    for c in cnts:
        area = cv2.contourArea(c) # A4 용지 후보 면적 픽셀 단위로 계산 (1차 필터링: 크기 검사)
        # 이미지 전체의 10% 미만 또는 이미지 전체의 90% 초과하는 경우 건너뜀
        if area < image_area * 0.1 or area > image_area * 0.9:
            continue
            
        peri = cv2.arcLength(c, True) # A4 용지 후보 윤곽선 길이 계산 (2차 필터링: 모양 검사)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True) # approxPolyDP 이용해 윤곽선을 단순화 (둘레 길이의 2% 오차는 무시)
        
        if len(approx) == 4: # 꼭짓점이 4개인 경우(3차 필터링: 비율 검사)
            box = approx.reshape(4, 2) # 4개의 꼭짓점 좌표를 사용하기 쉽게 (4,2) 형태로 변환
            box = order_points(box) # 꼭짓점을 (왼쪽-위, 오른쪽-위, 오른쪽-아래, 왼쪽-아래) 순서로 정렬
            
            # 정렬된 꼭짓점을 이용해 사각형의 윗변과 왼쪽 변 길이 계산
            (tl, tr, br, bl) = box 
            width = np.linalg.norm(tr - tl) # 윗변의 픽셀 길이
            height = np.linalg.norm(bl - tl) # 왼쪽 변의 픽셀 길이
            
            if width == 0 or height == 0: # 변의 길이가 0인 경우, 해당 후보 무시
                continue
                
            # A4 용지 후보 비율 검사
            ratio = max(width, height) / min(width, height) # 우리가 찾은 사각형의 (긴변 / 짧은 변) 비율 계산
            ratio_diff = abs(ratio - a4_scale) # 실제 A4 비율과의 차이 계산
            
            # A4 용지 후보 각도 검사 (수직/수평에 가까운지)
            angles = [] # 각도 저장 리스트 (4차 필터링: 각도 검사)
            for i in range(4):
                p1 = box[i] 
                p2 = box[(i + 1) % 4] 
                angle = abs(np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0])) % 90) # 두 꼭짓점이 이루는 선분의 수평 대비 각도 계산
                angles.append(min(angle, 90 - angle)) # 각도가 수평 또는 수직(90도)를 얼마나 벗어났는지 계산
            max_angle_diff = max(angles) # 4개의 변 중 가장 찌그러진 각도 찾기
            
            # 5차 필터링: 실제 밝기 검사사
            mask = np.zeros(image.shape[:2], dtype=np.uint8) # 검은 도화지 생성
            cv2.drawContours(mask, [box.astype(np.int32)], -1, 255, -1) # 우리가 찾은 사각형 내부만 흰색(255) 표시
            mean_val = cv2.mean(image, mask=mask)[0] # 원본 이미지지에서 흰색으로 칠한 영역에 해당하는 픽셀의 평균 밝기 계산(검정색: 0, 흰색: 255)
            
            # 모든 조건 충족 시 A4로 판단
            if ratio_diff < 0.2 and max_angle_diff < 20 and mean_val > 150: # A4 비율 차이가 0.2 이하이고 각도 차이가 20도 이내이고 밝기가 150 이상인 경우
                return box.astype(np.float32) # 실제 A4용지로 확정 >> 꼭짓점 좌표 반환 후, 함수 즉시 종료
    
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
        # 왼쪽 버튼을 누르고 저장된 점의 개수가 4개 미만이라면
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4: 
            # 클릭한 좌표를 원본 이미지 좌표로 변환
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
        cv2.waitKey(1) # 1ms 대기하며 키보드 입력 기다림
    cv2.destroyWindow(window_name) # 창 닫기

    # 결과를 NumPy 배열로 변환하여 반환 (좌표들은 float32 타입)
    return np.array(points, dtype="float32")

# 하의(바지) 치수 측정 함수
def measure_pants(image, a4_box, pixelsPerCM_w, pixelsPerCM_h):
    vis = image.copy() # 원본 이미지 복사
    cv2.drawContours(vis, [a4_box.astype(np.int32)], -1, (255, 0, 0), 3) # A4 용지 확인을 위해 파란색으로 윤곽선 그리기
    
    # 1. 이미지 전처리 (바지를 찾기 쉽게 만들기 위해)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # 그레이스케일(흑백)로 변환하여 처리를 단순화
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) # 블러 처리로 노이즈 줄이고 다음 단계 이진화가 잘 보이도록 가우시안 블러 적용
    
    # 2. 바지 마스크 생성 (배경과 바지 분리)
    # 이진화: 이미지를 검은색(0) 과 흰색 (255)으로만 구분하는 작업업
    _, pants_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 3. 마스크 정제 (바지 모양 다듬기)
    kernel = np.ones((5,5), np.uint8) # 5x5 크기의 커널 생성 (uint: 부호없는 정수(0이나 양수 저장 가능))
    pants_mask = cv2.morphologyEx(pants_mask, cv2.MORPH_CLOSE, kernel, iterations=2) # 바지(흰색) 영역 내부에 생긴 구멍들을 채워줌
    pants_mask = cv2.dilate(pants_mask, kernel, iterations=1) # dilate 연산: 바지 영역을 살짝 팽창 >> 바지의 끊어진 외곽선은 이어주고 윤곽선을 확실하게
    
    # 4. 윤곽선 검출 (바지의 최종 외곽선 찾기)
    contours, _ = cv2.findContours(pants_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #바지 마스크에서 윤곽선 좌표 리스트 찾아내기
    if not contours: # 바지 윤곽선을 찾을 수 없으면 오류 메시지 출력
        print("바지 윤곽선을 찾을 수 없습니다.")
        return
    
    # 찾은 외곽선 중 면적이 가장 큰 윤곽선 선택 (바지일 확률이 가장 높기에)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 만약 가장 큰 외곽선 조차 이미지 전체 면적의 10%보다 작다면 
    if cv2.contourArea(largest_contour) < image.shape[0] * image.shape[1] * 0.1: 
        print("바지 윤곽선이 너무 작습니다. 다시 시도해주세요.")
        return
    
    epsilon = 0.002 * cv2.arcLength(largest_contour, True) 
    # 전체 윤곽선 길이의 0.2% 정도로 매우 작게 설정하여 원본 형태를 거의 유지하도록
    smoothed_contour = cv2.approxPolyDP(largest_contour, epsilon, True) 
    # approxPolyDP 를 사용해 윤곽선을 더 작은 점을 가진 매끈한 다각형 형태로 단순화
    cv2.drawContours(vis, [smoothed_contour], -1, (0, 255, 0), 2) 
    # 시각화 이미지(vis)에 최종적으로 찾은 바지 윤곽선을 초록색으로 표시
    
    point_labels = [
        "Top",                    # 허리 상단 중앙점 (총장 측정용)
        "Left Waist",             # 왼쪽 허리점 (허리 단면 측정용)
        "Right Waist",            # 오른쪽 허리점 (허리 단면 측정용)
        "Left Hip",               # 왼쪽 엉덩이점 (엉덩이 단면 측정용)
        "Right Hip",              # 오른쪽 엉덩이점 (엉덩이 단면 측정용)
        "Crotch / center",        # 허벅지/밑위 기준점 (밑위 측정용)
        "Right Thigh",            # 오른쪽 허벅지점 (허벅지 단면 측정용)
        "Bottom",                 # 밑단 좌측점 (밑단 단면, 총장 측정용)
        "Ankel Opening"           # 밑단 우측점 (밑단 단면 측정용)
    ]
    
    # 키포인트 자동 검출 및 수정
    initial_keypoints = auto_detect_keypoints_pants(image, smoothed_contour)
    # auto_detect_keypoints_pants 함수 사용해 바지의 핵심 위치들을 자동으로 탐색
    keypoints = get_keypoints_by_mouse(image, initial_points=initial_keypoints, point_labels=point_labels)
    # 자동으로 찾은 키포인트를 보고 잘못 찍혔으면 사용자가 직접 조정할 수 있도록 함
    
    # 이미지 위에 측정값을 글씨로 쓸 때 필요한 준비 작업
    h, w = vis.shape[:2] #이미지의 크기 알아내기
    
    # 텍스트 크기 계산을 위한 기본 설정
    font = cv2.FONT_HERSHEY_SIMPLEX # 텍스트 폰트 설정
    font_scale = 0.9 # 텍스트 크기 설정
    thickness = 2 # 텍스트 두께 설정
    padding = 10 # 텍스트 여백 설정
    
    def get_safe_text_position(point, text, is_right=False): # 텍스트 위치 조정 함수
        # 텍스트 크기 계산
        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness) 
        
        # x 좌표 조정
        if is_right: # 글씨를 기준점 오른쪽에 배치
            x = min(point[0] + padding, w - text_w - padding) 
        else: # 글씨를 기준점 왼쪽에 배치
            x = max(point[0] - text_w - padding, padding)
        
        # y 좌표 조정 (텍스트가 위로 가도록)
        y = max(point[1] - padding, text_h + padding)
        
        # 경계 확인 및 조정
        x = np.clip(x, padding, w - text_w - padding)
        y = np.clip(y, text_h + padding, h - padding)
        
        return (int(x), int(y))
    
    # 하의 보정 계수 시스템 (1차 측정 원본 값이 일반적인 바지 치수를 벗어날 경우, 데이터를 바탕으로 미세 조정 해주는 보정 배율 반환)
    def get_dynamic_correction_factor_pants(raw_measurement, measurement_type):
        # raw_measurement: 1차 측정 원본 값 / measurement_type: 측정 항목 (length, waist, hip, thigh, hem, crotch)
        if measurement_type == 'length': # 총장 길이 보정
            if raw_measurement > 105: #1차 측정 값이 105를 초과한 경우 >> 10% 줄여서 (0.90배) 보정 
                return 0.90
            elif raw_measurement > 100: #1차 측정 값이 100를 초과한 경우 >> 5% 줄여서 (0.95배) 보정 
                return 0.95
            elif raw_measurement < 85: #1차 측정 값이 85를 미만인 경우 >> 5% 늘려서 (1.05배) 보정 
                return 1.05
            else: #85 ~ 100 사이 경우, 보정 없음
                return 1.00
        
        if measurement_type == 'waist': # 허리 단면 보정
            if raw_measurement > 48:
                return 0.90
            elif raw_measurement > 45:
                return 0.95
            elif raw_measurement < 36:
                return 1.05
            else:
                return 1.00
        
        if measurement_type == 'hip': # 엉덩이 단면 보정
            if raw_measurement > 60:
                return 0.90
            elif raw_measurement > 56:
                return 0.95
            elif raw_measurement < 46:
                return 1.05
            else:
                return 1.00
        
        if measurement_type == 'thigh': # 허벅지 단면 보정
            if raw_measurement > 36:
                return 0.90
            elif raw_measurement > 34:
                return 0.95
            elif raw_measurement < 26:
                return 1.05
            else:
                return 1.00
        
        if measurement_type == 'hem': # 밑단 단면 보정
            if raw_measurement > 27:
                return 0.95
            elif raw_measurement < 22:
                return 1.05
            else:
                return 1.00
        
        if measurement_type == 'crotch': # 밑위 보정
            if raw_measurement > 40:
                return 0.92 # 8% 줄여서 (0.92배) 보정 
            elif raw_measurement > 38:
                return 0.96 # 4% 줄여서 (0.96배) 보정 
            elif raw_measurement < 30:
                return 1.05 # 5% 늘려서 (1.05배) 보정 
            else:
                return 1.00 # 보정 없음
        
        return 1.00 # 혹시 모를 예외 상황에서는 보정 없음
    
    print(f"\n범용 하의 치수 측정 시스템 (키 무관 객관적 측정):")
    print(f"※ 바지 자체의 실제 치수를 측정합니다.")
    print(f"※ 극단적인 측정값에 대해서는 보정을 완화하여 정확도를 높입니다.")
    print(f"※ 최적화된 9개 키포인트로 6가지 부위를 측정합니다.\n")
    
    # 해당 함수들은 픽셀 거리를 cm로 변화하며, 원근 왜곡 보정을 위해 가로와 세로에 서로 다른 비율을 적용용
    def horiz_dist(p1, p2): # 두 점 (p1, p2) 사이의 수평 거리를 계산 (허리 단면이나 엉덩이 단면 등 수평 길이 잴 때)
        return abs(p1[0] - p2[0]) / float(pixelsPerCM_w) #p1[0] = p1의 x좌표, p2[0] = p2의 x좌표
    def vert_dist(p1, p2): # 두 점 (p1, p2) 사이의 수직 거리를 계산 (총장 처럼 수직 길이 잴 때)
        return abs(p1[1] - p2[1]) / float(pixelsPerCM_h) #p1[1] = p1의 y좌표, p2[1] = p2의 y좌표
    def euclid_cm(p1, p2): # 두 점 (p1, p2) 사이의 대각선 거리를 계산 (밑위 처럼 대각선 길이 잴 때)
        dx = (p1[0] - p2[0]) / float(pixelsPerCM_w) # 가로(dx)와 세로(dy)의 축소 비율이 다르기에 (원근 왜곡 때매)
        dy = (p1[1] - p2[1]) / float(pixelsPerCM_h) # 각각의 픽셀 거리를 먼저 가로/세로 cm 로 변환
        return (dx*dx + dy*dy) ** 0.5 # 피타고라스 정리를 사용해 두 점 사이의 대각선 거리를 계산
    
    # 치수 측정 결과 표시 (9개 키포인트 기반)
    if len(keypoints) >= 9: # 총장 길이 (거의 수직): vert_dist 함수 사용
        raw_length = vert_dist(keypoints[0], keypoints[7]) # keypoints[0] = 허리 상단 중앙점, keypoints[7] = 밑단 중앙점 >> 수직 거리 계산
        length_correction = get_dynamic_correction_factor_pants(raw_length, 'length') # length 타입의 보정 계수 받기
        corrected_length = raw_length * length_correction # 최종 치수 계산: 원본 치수 * 보정 계수
        cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[7]), (0,0,255), 2) # 빨간 선 긋기
        text = f"Length: {corrected_length:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[7], text) # 텍스트가 이미지 밖으로 나가지 않게 안전 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (0,0,255), thickness) # 계산된 위치에 빨간색 텍스트 표시
        print(f"총장 길이: 원본 {raw_length:.1f}cm → 보정 {corrected_length:.1f}cm")
    
    if len(keypoints) >= 3: # 허리 단면 (수평): horiz_dist 함수 사용
        raw_waist = horiz_dist(keypoints[1], keypoints[2]) # keypoints[1] = 왼쪽 허리점, keypoints[2] = 오른쪽 허리점 >> 수평 거리 계산
        waist_correction = get_dynamic_correction_factor_pants(raw_waist, 'waist') # waist 타입의 보정 계수 받기
        corrected_waist = raw_waist * waist_correction # 최종 치수 계산: 원본 치수 * 보정 계수
        cv2.line(vis, tuple(keypoints[1]), tuple(keypoints[2]), (255,0,0), 2) # 파란 선 긋기
        text = f"Waist: {corrected_waist:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[2], text, True) # 텍스트가 이미지 밖으로 나가지 않게 오른쪽(True)에 배치하도록 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (255,0,0), thickness) # 계산된 위치에 파란색 텍스트 표시
        print(f"허리 단면: 원본 {raw_waist:.1f}cm → 보정 {corrected_waist:.1f}cm")
    
    if len(keypoints) >= 5: # 엉덩이 단면 (수평): horiz_dist 함수 사용
        raw_hip = horiz_dist(keypoints[3], keypoints[4]) # keypoints[3] = 왼쪽 엉덩이점, keypoints[4] = 오른쪽 엉덩이점 >> 수평 거리 계산
        hip_correction = get_dynamic_correction_factor_pants(raw_hip, 'hip') # hip 타입의 보정 계수 받기
        corrected_hip = raw_hip * hip_correction # 최종 치수 계산: 원본 치수 * 보정 계수
        cv2.line(vis, tuple(keypoints[3]), tuple(keypoints[4]), (255,128,0), 2) # 주황 선 긋기
        text = f"Hip: {corrected_hip:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[4], text, True) # 텍스트가 이미지 밖으로 나가지 않게 오른쪽(True)에 배치하도록 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (255,128,0), thickness) # 계산된 위치에 주황색 텍스트 표시
        print(f"엉덩이 단면: 원본 {raw_hip:.1f}cm → 보정 {corrected_hip:.1f}cm") 
    
    if len(keypoints) >= 6: # 밑위 (대각선 방향): euclid_cm 함수 사용
        raw_crotch = euclid_cm(keypoints[0], keypoints[5]) # keypoints[0] = 허리 상단 중앙점, keypoints[5] = (왼쪽) 허벅지 / 밑위 기준점 >> 대각선 거리 계산
        crotch_correction = get_dynamic_correction_factor_pants(raw_crotch, 'crotch') # crotch 타입의 보정 계수 받기
        corrected_crotch = raw_crotch * crotch_correction # 최종 치수 계산: 원본 치수 * 보정 계수
        cv2.line(vis, tuple(keypoints[0]), tuple(keypoints[5]), (255,255,0), 2) # 노란 선 긋기
        text = f"Crotch: {corrected_crotch:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[5], text) # 텍스트 위치 계산
        cv2.putText(vis, text, pos, font, font_scale, (255,255,0), thickness) # 노란색 텍스트 표시
        print(f"밑위: 원본 {raw_crotch:.1f}cm → 보정 {corrected_crotch:.1f}cm")
    
    if len(keypoints) >= 7: # 허벅지 단면 (수평): horiz_dist 함수 사용
        raw_thigh = horiz_dist(keypoints[5], keypoints[6]) # keypoints[5] = 왼쪽 허벅지 / 밑위 기준점, keypoints[6] = 오른쪽 허벅지 >> 수평 거리 계산
        thigh_correction = get_dynamic_correction_factor_pants(raw_thigh, 'thigh') # thigh 타입의 보정 계수 받기
        corrected_thigh = raw_thigh * thigh_correction # 최종 치수 계산
        cv2.line(vis, tuple(keypoints[5]), tuple(keypoints[6]), (0,255,0), 2) # 초록 선 긋기
        text = f"Thigh: {corrected_thigh:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[6], text, True) # 텍스트를 오른쪽(True)에 배치
        cv2.putText(vis, text, pos, font, font_scale, (0,255,0), thickness) # 초록색 텍스트 표시
        print(f"허벅지 단면: 원본 {raw_thigh:.1f}cm → 보정 {corrected_thigh:.1f}cm")
    
    if len(keypoints) >= 9: # 밑단 단면 (수평): horiz_dist 함수 사용
        raw_hem = horiz_dist(keypoints[7], keypoints[8]) # keypoints[7] = 밑단 좌측점, keypoints[8] = 밑단 우측점 >> 수평 거리 계산
        hem_correction = get_dynamic_correction_factor_pants(raw_hem, 'hem') # hem 타입의 보정 계수 받기
        
        # 플레어 보정: 밑단/허벅지 비율 기반
        raw_thigh_for_ratio = horiz_dist(keypoints[5], keypoints[6]) if len(keypoints) >= 7 else raw_hem # 허벅지 치수 (keypoints 5번, 6번 사이)를 가져옴
        ratio_ht = raw_hem / max(raw_thigh_for_ratio, 1e-6) # 밑단 / 허벅지 비율 계산 (1e-6은 허벅지 값이 0일때 0으로 나누기 오류를 방지하는 안전장치)
        flare_factor = 1.0 # 기본 보정 배율 1.0
        if ratio_ht > 1.20: #밑단이 허벅지 보다 1.2배 이상 넓다면 18% 줄이기 (와이드팬츠)
            flare_factor = 0.82
        elif ratio_ht > 1.10: # 밑단이 허벅지 보다 1.1배 이상 넓다면 10% 줄이기 (약한 부츠컷)
            flare_factor = 0.90
        
        corrected_hem = raw_hem * hem_correction * flare_factor # 원본 밑단에 일반 보정과 플레어 보정을 모두 곱하여 치수 계산
        # 봉제여유(시접) 보정 약 0.6cm 차감
        corrected_hem = max(0.0, corrected_hem - 0.6)
        
        cv2.line(vis, tuple(keypoints[7]), tuple(keypoints[8]), (128,0,128), 2) # 보라 선 긋기
        text = f"Hem: {corrected_hem:.1f}cm" # 측정값 표시
        pos = get_safe_text_position(keypoints[8], text, True) # 텍스트를 오른쪽(True)에 배치
        cv2.putText(vis, text, pos, font, font_scale, (128,0,128), thickness) # 보라색 텍스트 표시
        print(f"밑단 단면: 원본 {raw_hem:.1f}cm (H/T 비율 {ratio_ht:.2f}) → 보정 {corrected_hem:.1f}cm")
    
    cv2.imwrite("pants_measure_result.jpg", vis) #측정 결과 이미지 저장
    cv2.namedWindow("result", cv2.WINDOW_NORMAL) #창 생성
    cv2.imshow("result", vis) #창에 이미지 표시
    cv2.waitKey(0) #키보드 입력 대기
    cv2.destroyAllWindows() #창 닫기

def width_profile(binary_mask): #폭 프로파일 계산 함수
    """이미지의 각 y좌표에서 바지의 좌우 경계점을 찾습니다."""
    h, w = binary_mask.shape
    left = np.zeros(h, dtype=int)
    right = np.zeros(h, dtype=int)
    widths = np.zeros(h, dtype=int)
    
    for y in range(h):
        cols = np.where(binary_mask[y] > 0)[0]
        if len(cols):
            left[y], right[y] = cols[0], cols[-1]
            widths[y] = right[y] - left[y]
    
    return left, right, widths

def find_key_heights_pants(widths): #주요 높이 계산 함수 (바지용)
    """폭 프로파일을 분석하여 주요 높이(y좌표)를 찾습니다."""
    h = len(widths)
    valid_rows = np.where(widths > 0)[0]
    if len(valid_rows) == 0:
        return None, None, None, None, None, None, None
    
    top_y = valid_rows[0] # 가장 위쪽 y좌표 (허리)
    bottom_y = valid_rows[-1] # 가장 아래쪽 y좌표 (밑단)
    total_height = bottom_y - top_y
    
    # 바지 비율을 고려한 주요 지점 계산
    waist_y = top_y + int(total_height * 0.05)      # 상단에서 5% 지점 (허리)
    crotch_y = top_y + int(total_height * 0.25)     # 상단에서 25% 지점 (밑위)
    hip_y = top_y + int(total_height * 0.32)        # 상단에서 32% 지점 (엉덩이)
    thigh_y = top_y + int(total_height * 0.40)      # 상단에서 40% 지점 (허벅지)
    hem_y = bottom_y - int(total_height * 0.05)     # 하단에서 5% 지점 (밑단)
    
    return top_y, waist_y, crotch_y, hip_y, thigh_y, hem_y, bottom_y

#키포인트 자동 검출 함수 (바지용) - 최적화된 9개 키포인트
def auto_detect_keypoints_pants(image, contour):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    
    left, right, widths = width_profile(mask)
    result = find_key_heights_pants(widths)
    
    if result[0] is None:
        return np.zeros((9, 2), dtype=int)
    
    top_y, waist_y, crotch_y, hip_y, thigh_y, hem_y, bottom_y = result
    
    # 중심점 계산 (허리 부위 기준)
    waist_left = left[waist_y] if waist_y < len(left) else left[len(left)//4]
    waist_right = right[waist_y] if waist_y < len(right) else right[len(right)//4]
    x_center = (waist_left + waist_right) // 2
    
    keypoints = np.zeros((9, 2), dtype=int)
    
    # 이미지 경계 정보
    h, w = mask.shape
    
    # 키포인트 경계 검사 및 제한 함수
    def clamp_point(x, y, margin=5):
        """키포인트가 이미지 경계를 벗어나지 않도록 제한"""
        clamped_x = max(margin, min(x, w - margin))
        clamped_y = max(margin, min(y, h - margin))
        return [clamped_x, clamped_y]
    
    # 각 높이에서 좌우 경계점 찾기
    # 엉덩이 단면 초기 위치를 '밑위 높이(crotch_y)'로 배치하여 수동 조정 전에도 교차지점에 놓이도록 함
    hip_left_at_crotch = left[crotch_y] if crotch_y < len(left) else left[len(left)//3]
    hip_right_at_crotch = right[crotch_y] if crotch_y < len(right) else right[len(right)//3]
    
    thigh_left = left[thigh_y] if thigh_y < len(left) else left[len(left)//2]
    thigh_right = right[thigh_y] if thigh_y < len(right) else right[len(right)//2]
    
    hem_left = left[hem_y] if hem_y < len(left) else left[-10]
    hem_right = right[hem_y] if hem_y < len(right) else right[-10]
    
    # 키포인트 설정 (9개로 최적화)
    keypoints[0] = clamp_point(x_center, top_y)           # 허리 상단 중앙점 (총장 측정)
    keypoints[1] = clamp_point(waist_left, waist_y)       # 왼쪽 허리점 (허리 단면)
    keypoints[2] = clamp_point(waist_right, waist_y)      # 오른쪽 허리점 (허리 단면)
    keypoints[3] = clamp_point(hip_left_at_crotch, crotch_y)    # 왼쪽 엉덩이점 → 밑위 높이에 초기 배치
    keypoints[4] = clamp_point(hip_right_at_crotch, crotch_y)   # 오른쪽 엉덩이점 → 밑위 높이에 초기 배치
    keypoints[5] = clamp_point(thigh_left, thigh_y)       # 왼쪽 허벅지점 (허벅지 단면, 밑위)
    keypoints[6] = clamp_point(thigh_right, thigh_y)      # 오른쪽 허벅지점 (허벅지 단면)
    keypoints[7] = clamp_point(hem_left, hem_y)           # Bottom (밑단 단면, 총장)
    keypoints[8] = clamp_point(hem_right, hem_y)          # Ankel Opening (밑단 단면)
    
    return keypoints

#키포인트를 수동으로 조정
def get_keypoints_by_mouse(image, initial_points=None, window_name="Adjust Keypoints", point_labels=None):
    points = [] if initial_points is None else initial_points.tolist()
    clone = image.copy()
    h, w = image.shape[:2]
    screen_res = 1920, 1080
    scale = min(screen_res[0] / w, screen_res[1] / h, 1.0)
    win_w, win_h = int(w * scale), int(h * scale)
    
    display_img = cv2.resize(clone, (win_w, win_h)) if scale < 1.0 else clone.copy()
    selected_point = -1
    
    def redraw():
        img = display_img.copy()
        for idx, p in enumerate(points):
            px, py = int(p[0]*scale), int(p[1]*scale)
            color = (0, 0, 255) if idx == selected_point else (0, 255, 0)
            cv2.circle(img, (px, py), 8, color, -1)
            if point_labels and idx < len(point_labels):
                cv2.putText(img, f"{idx+1}: {point_labels[idx]}", 
                          (px+10, py-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2) 
        return img
    
    def click_event(event, x, y, *_): 
        nonlocal selected_point
        
        if event == cv2.EVENT_LBUTTONDOWN:
            min_dist = float('inf') 
            closest_point = -1
            for i, p in enumerate(points):
                px, py = int(p[0]*scale), int(p[1]*scale)
                dist = np.sqrt((x - px)**2 + (y - py)**2)
                if dist < min_dist and dist < 20:
                    min_dist = dist
                    closest_point = i
            selected_point = closest_point
            
        elif event == cv2.EVENT_MOUSEMOVE and selected_point != -1:
            orig_x = int(x/scale)
            orig_y = int(y/scale)
            orig_x = max(5, min(orig_x, w - 5))
            orig_y = max(5, min(orig_y, h - 5))
            points[selected_point] = [orig_x, orig_y]
            img = redraw()
            cv2.imshow(window_name, img)
            
        elif event == cv2.EVENT_LBUTTONUP:
            selected_point = -1
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, win_w, win_h)
    img = redraw()
    cv2.imshow(window_name, img)
    cv2.setMouseCallback(window_name, click_event)
    
    print("점을 드래그하여 위치를 조정하세요.")
    print("Enter 또는 Space를 눌러 완료")
    
    while True:
        key = cv2.waitKey(1)
        if key in [13, 32]:  # Enter 또는 Space
            break
            
    cv2.destroyWindow(window_name)
    return np.array(points, dtype="int")

def order_points(pts): #A4 용지 꼭짓점 좌표 정렬
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] #왼쪽 위
    rect[2] = pts[np.argmax(s)] #오른쪽 아래
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] #오른쪽 위
    rect[3] = pts[np.argmax(diff)] #왼쪽 아래
    return rect

# 프로그램 시작점
if __name__ == "__main__": 
    main()

