import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import os
from typing import Tuple, List, Optional
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FanzaMosaicProcessor:
    """
    FANZA隠蔽処理規約に準拠したモザイク処理エンジン
    """
    
    def __init__(self):
        """初期化"""
        self.mp_pose = mp.solutions.pose
        self.mp_face_detection = mp.solutions.face_detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
    def calculate_mosaic_size(self, image: np.ndarray) -> int:
        """
        FANZA規約に基づくモザイクサイズを計算
        規約（1）: 画像長辺×1/100、最小4ピクセル
        """
        height, width = image.shape[:2]
        long_side = max(height, width)
        
        if long_side < 400:
            return 4  # 最小サイズ
        
        mosaic_size = max(4, int(long_side / 100))
        logger.info(f"画像サイズ: {width}x{height}, モザイクサイズ: {mosaic_size}")
        return mosaic_size
    
    def detect_sensitive_areas(self, image: np.ndarray) -> List[np.ndarray]:
        """
        MediaPipeを使用して性器領域を検出
        """
        try:
            # RGB変換（MediaPipeはRGBを要求）
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # ポーズ検出
            results = self.pose.process(rgb_image)
            
            if not results.pose_landmarks:
                logger.warning("人体の検出に失敗しました")
                return []
            
            # 性器領域の推定（腰周辺）
            sensitive_areas = []
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                h, w = image.shape[:2]
                
                # 腰の位置を特定（MediaPipe Poseのインデックス）
                left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
                
                if left_hip.visibility > 0.5 and right_hip.visibility > 0.5:
                    # 腰周辺の矩形領域を作成
                    left_x = int(left_hip.x * w)
                    right_x = int(right_hip.x * w)
                    hip_y = int(left_hip.y * h)
                    
                    # 性器領域の推定（腰から下）
                    sensitive_area = np.array([
                        [left_x - 20, hip_y],
                        [right_x + 20, hip_y],
                        [right_x + 20, h],
                        [left_x - 20, h]
                    ], dtype=np.int32)
                    
                    sensitive_areas.append(sensitive_area)
                    logger.info(f"性器領域を検出: {sensitive_area}")
            
            return sensitive_areas
            
        except Exception as e:
            logger.error(f"性器検出中にエラーが発生: {e}")
            return []
    
    def apply_mosaic(self, image: np.ndarray, areas: List[np.ndarray], 
                     mosaic_size: int) -> np.ndarray:
        """
        指定された領域にモザイクを適用
        """
        result_image = image.copy()
        
        for area in areas:
            # 領域の境界を取得
            x_coords = area[:, 0]
            y_coords = area[:, 1]
            
            x_min, x_max = max(0, min(x_coords)), min(image.shape[1], max(x_coords))
            y_min, y_max = max(0, min(y_coords)), min(image.shape[0], max(y_coords))
            
            if x_max <= x_min or y_max <= y_min:
                continue
            
            # モザイク処理
            region = result_image[y_min:y_max, x_min:x_max]
            
            # ピクセル化処理
            small = cv2.resize(region, (mosaic_size, mosaic_size))
            mosaic_region = cv2.resize(small, (x_max - x_min, y_max - y_min), 
                                     interpolation=cv2.INTER_NEAREST)
            
            result_image[y_min:y_max, x_min:x_max] = mosaic_region
            
            # 境界線のぼかし処理
            self._blur_boundaries(result_image, x_min, x_max, y_min, y_max, mosaic_size)
        
        return result_image
    
    def _blur_boundaries(self, image: np.ndarray, x_min: int, x_max: int, 
                         y_min: int, y_max: int, blur_size: int):
        """
        モザイク境界のぼかし処理
        """
        blur_radius = max(3, blur_size // 2)
        
        # 境界周辺のぼかし
        for i in range(blur_radius):
            # 上境界
            if y_min - i >= 0:
                cv2.GaussianBlur(image[y_min-i:y_min+i+1, x_min:x_max], 
                                (blur_radius, blur_radius), 0, 
                                dst=image[y_min-i:y_min+i+1, x_min:x_max])
            
            # 下境界
            if y_max + i < image.shape[0]:
                cv2.GaussianBlur(image[y_max-i:y_max+i+1, x_min:x_max], 
                                (blur_radius, blur_radius), 0, 
                                dst=image[y_max-i:y_max+i+1, x_min:x_max])
            
            # 左境界
            if x_min - i >= 0:
                cv2.GaussianBlur(image[y_min:y_max, x_min-i:x_min+i+1], 
                                (blur_radius, blur_radius), 0, 
                                dst=image[y_min:y_max, x_min-i:x_min+i+1])
            
            # 右境界
            if x_max + i < image.shape[1]:
                cv2.GaussianBlur(image[y_min:y_max, x_max-i:x_max+i+1], 
                                (blur_radius, blur_radius), 0, 
                                dst=image[y_min:y_max, x_max-i:x_max+i+1])
    
    def process_image(self, image_path: str, output_path: str) -> bool:
        """
        画像の完全処理（検出→モザイク→保存）
        """
        try:
            logger.info(f"画像処理開始: {image_path}")
            
            # 画像読み込み
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"画像の読み込みに失敗: {image_path}")
                return False
            
            # モザイクサイズ計算
            mosaic_size = self.calculate_mosaic_size(image)
            
            # 性器領域検出
            sensitive_areas = self.detect_sensitive_areas(image)
            
            if not sensitive_areas:
                logger.warning("性器領域が検出できませんでした")
                return False
            
            # モザイク適用
            processed_image = self.apply_mosaic(image, sensitive_areas, mosaic_size)
            
            # 結果保存
            cv2.imwrite(output_path, processed_image)
            logger.info(f"処理完了: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"画像処理中にエラーが発生: {e}")
            return False
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if hasattr(self, 'pose'):
            self.pose.close()
        if hasattr(self, 'mp_pose'):
            self.mp_pose = None
