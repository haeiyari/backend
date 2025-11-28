import { CameraView, useCameraPermissions } from "expo-camera";
import React, { useRef, useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Dimensions, Alert, Linking, PanResponder } from 'react-native';

export default function App() {
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState('back'); // 카메라 방향
  const [zoom, setZoom] = useState(0); // 줌 레벨
  const [flash, setFlash] = useState('off'); // 플래시 상태
  const [showCamera, setShowCamera] = useState(false); // 카메라 표시 여부
  const cameraRef = useRef(null); // 카메라 참조
  const lastDistance = useRef(null); // 마지막 거리

  // 핀치줌 제스처 처리
  const panResponder = useRef(// 핀치줌 제스처 처리
    PanResponder.create({
      onStartShouldSetPanResponder: () => true, // 제스처 시작 시 활성화
      onMoveShouldSetPanResponder: () => true, // 제스처 이동 시 활성화
      onPanResponderMove: (evt) => {
        const touches = evt.nativeEvent.touches; // 터치 이벤트 처리
        if (touches.length === 2) {
          const [t1, t2] = touches; 
          const dx = t1.pageX - t2.pageX;
          const dy = t1.pageY - t2.pageY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (lastDistance.current !== null) { // 마지막 거리가 있는 경우
            const diff = dist - lastDistance.current; // 현재 거리와 마지막 거리의 차이
            if (Math.abs(diff) > 2) setZoom(z => Math.max(0, Math.min(1, z + diff / 300))); // 줌 레벨 업데이트
          }
          lastDistance.current = dist; // 현재 거리를 마지막 거리로 저장
        }
      },
      onPanResponderRelease: () => { lastDistance.current = null; }, // 제스처 해제 시 마지막 거리 초기화
      onPanResponderTerminate: () => { lastDistance.current = null; }, // 제스처 종료 시 마지막 거리 초기화
    })
  ).current;

  // 권한 확인 및 요청
  const checkPermissions = async () => {
    if (!permission) return; // 권한이 없는 경우 종료
    if (permission.status !== "granted") { // 권한이 부여되지 않은 경우
      if (!permission.canAskAgain) { // 다시 요청할 수 없는 경우
        Alert.alert( // 경고 메시지 표시
          "권한 필요",
          "앱 설정에서 카메라 권한을 변경해주세요.",
          [
            { text: "취소", style: "cancel" },
            { text: "설정 열기", onPress: () => Linking.openSettings() },
          ],
          { cancelable: false }
        );
      } else {
        requestPermission(); // 권한 요청
      }
    }
  };

  // 측정 버튼 클릭 시 카메라 표시
  const handlePress = async () => {
    if (!permission || permission.status !== 'granted') { // 권한이 없거나 부여되지 않은 경우
      await requestPermission(); // 권한 요청
      return; // 권한 요청 후 종료
    }
    setShowCamera(true); // 카메라 표시
  };

  // 촬영 버튼 클릭 시 촬영 완료 메시지 표시
  const handleCapture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync(); // 촬영 완료 후 이미지 저장
        Alert.alert('촬영 완료', photo.uri); // 촬영 완료 메시지 표시
      } catch {
        Alert.alert('오류', '촬영 실패'); // 오류 메시지 표시
      }
    }
  };

  // 카메라 표시 여부 확인
  return (
    <View style={styles.container}>
      {!showCamera && (
        <TouchableOpacity style={styles.button} onPress={handlePress}> 
          <Text style={styles.buttonText}>측정하기</Text> 
        </TouchableOpacity>
      )}
      {showCamera && permission?.status === "granted" && ( // 카메라 표시 여부 확인
        <View style={StyleSheet.absoluteFill} {...panResponder.panHandlers}> 
          <CameraView // 카메라 뷰
            style={StyleSheet.absoluteFill} // 카메라 뷰 스타일
            facing={facing} // 카메라 방향
            zoom={zoom} // 줌 레벨
            flash={flash} // 플래시 상태
            ref={cameraRef} // 카메라 참조
          />
          <View style={styles.bottomBar}> 
            <TouchableOpacity onPress={() => setFlash(f => f === 'off' ? 'on' : 'off')}> // 플래시 토글
              <Text style={styles.iconText}>{flash === 'on' ? '⚡' : '⚡︎'}</Text> // 플래시 아이콘
            </TouchableOpacity>
            <TouchableOpacity style={styles.captureButton} onPress={handleCapture} /> // 촬영 버튼
            <TouchableOpacity onPress={() => setFacing(f => f === 'back' ? 'front' : 'back')}> // 카메라 전환
              <Text style={styles.iconText}>⟳</Text> // 카메라 아이콘
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}

// 스타일 정의
const { width } = Dimensions.get('window');

// 스타일 정의
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // 화면 모든 요소 중앙 정렬
  button: { width: width * 0.8, height: 60, backgroundColor: '#007bff', borderRadius: 10, justifyContent: 'center', alignItems: 'center' }, // 버튼 스타일
  buttonText: { color: '#fff', fontSize: 18 }, // 버튼 텍스트 스타일
  captureButton: { width: 70, height: 70, borderRadius: 35, backgroundColor: '#fff', borderWidth: 4, borderColor: '#ddd' }, // 촬영 버튼 스타일
  bottomBar: { position: 'absolute', bottom: 45, width: '100%', height: 120, backgroundColor: 'black', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-around' }, // 하단 바 스타일
  iconText: { color: '#fff', fontSize: 32 }, // 아이콘 스타일
});

