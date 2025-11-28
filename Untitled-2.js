// 버튼 및 비디오 요소를 저장할 변수
let measurementButton;
let videoElement;

// 버튼을 생성하고 스타일을 적용하는 함수
function createMeasurementButton() {
  // 버튼 요소 생성
  const button = document.createElement('button');
  button.textContent = '측정 시작하기'; // 버튼 텍스트 설정

  // 버튼 스타일 설정
  button.style.position = 'fixed'; // 화면에 고정
  button.style.left = '50%';       // 왼쪽에서 50% 위치
  button.style.bottom = '20px';    // 하단에서 20px 위치
  button.style.transform = 'translateX(-50%)'; // X축 기준으로 -50% 이동하여 중앙 정렬
  button.style.height = '40px';    // 세로 크기 (20px은 너무 작을 수 있어 40px로 제안, 필요시 조절)
  button.style.padding = '10px 30px'; // 내부 여백 (세로, 가로) - 버튼이 길어 보이도록 가로 여백을 넉넉하게 줍니다.
  button.style.backgroundColor = '#007bff'; // 배경색 (예시)
  button.style.color = 'white';             // 글자색 (예시)
  button.style.border = 'none';               // 테두리 없음
  button.style.borderRadius = '5px';          // 모서리 둥글게
  button.style.cursor = 'pointer';            // 마우스 커서 모양
  button.style.fontSize = '16px';             // 글자 크기 (예시)
  button.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)'; // 그림자 효과 (선택 사항)
  button.style.zIndex = '1000'; // 다른 요소들 위에 보이도록 z-index 설정

    // 버튼 클릭 이벤트 리스너 추가
    measurementButton.addEventListener('click', requestCameraPermissionAndActivate);

    document.body.appendChild(measurementButton);
}
  // body 요소에 버튼 추가
  document.body.appendChild(button);


// 카메라 권한 요청 및 활성화 함수
async function requestCameraPermissionAndActivate() {
    if (videoElement && videoElement.srcObject) {
        // 이미 카메라가 활성화된 경우, 다시 누르면 중지 (선택적 기능)
        stopCamera();
        measurementButton.textContent = '측정 시작하기';
        measurementButton.style.backgroundColor = '#007bff'; // 원래 색으로
        return;
    }

    // navigator.mediaDevices.getUserMedia 지원 확인
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
            // 사용자에게 카메라 접근 권한 요청 (비디오만, 오디오는 false)
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });

            // 비디오 요소가 없으면 생성
            if (!videoElement) {
                videoElement = document.createElement('video');
                videoElement.style.position = 'fixed'; // 화면 전체를 덮도록 설정
                videoElement.style.top = '0';
                videoElement.style.left = '0';
                videoElement.style.width = '100vw'; // 뷰포트 너비의 100%
                videoElement.style.height = '100vh';// 뷰포트 높이의 100%
                videoElement.style.objectFit = 'cover'; // 비디오 비율 유지하며 꽉 채우기
                videoElement.style.zIndex = '1000'; // 버튼보다 뒤에 있도록 z-index 설정
                videoElement.setAttribute('playsinline', ''); // iOS에서 전체 화면으로 자동 전환 방지
                videoElement.setAttribute('autoplay', '');   // 자동 재생
                videoElement.setAttribute('muted', '');      // 음소거 (autoplay 정책 위반 방지)
                document.body.appendChild(videoElement);
            }

            videoElement.srcObject = stream; // 비디오 요소에 스트림 연결
            videoElement.play(); // 비디오 재생 (autoplay 속성으로 인해 대부분 자동 재생됨)

            console.log('카메라가 활성화되었습니다.');
            measurementButton.textContent = '측정 중지하기'; // 버튼 텍스트 변경
            measurementButton.style.backgroundColor = '#dc3545'; // 중지 버튼 색상 변경

        } catch (error) {
            console.error('카메라 접근 중 오류 발생:', error);
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                alert('카메라 접근 권한이 거부되었습니다. 브라우저 설정을 확인해주세요.');
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                alert('사용 가능한 카메라를 찾을 수 없습니다.');
            } else {
                alert('카메라를 시작하는 중 오류가 발생했습니다: ' + error.message);
            }
        }
    } else {
        alert('죄송합니다. 사용하시는 브라우저에서는 카메라 기능을 지원하지 않습니다.');
    }
}

// 카메라 중지 함수
function stopCamera() {
    if (videoElement && videoElement.srcObject) {
        const stream = videoElement.srcObject;
        const tracks = stream.getTracks();

        tracks.forEach(track => {
            track.stop(); // 각 트랙 (비디오) 중지
        });

        videoElement.srcObject = null; // 비디오 요소에서 스트림 연결 해제
        // videoElement.remove(); // 비디오 요소를 DOM에서 제거하려면 주석 해제
        // videoElement = null;
        console.log('카메라가 중지되었습니다.');
    }
}

// DOM이 완전히 로드된 후 버튼 생성 함수 호출
document.addEventListener('DOMContentLoaded', createMeasurementButton);