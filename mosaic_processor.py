import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import os
from typing import List
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FanzaMosaicProcessor:
    """
    FANZA隠蔽処理規約に準拠したモザイク処理エンジン（Streamlit Cloud対応版）
    """
    
    def __init__(self):
        """初期化"""
        try:
            # MediaPipeの初期化を軽量化
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=0,  # 最も軽量
                enable_segmentation=False,
                min_detection_confidence=0.2  # 閾値を下げて検出率向上
            )
            logger.info("MediaPipe Pose初期化完了")
        except Exception as e:
            logger.error(f"MediaPipe初期化エラー: {e}")
            self.pose = None
    
    def calculate_mosaic_size(self, image: np.ndarray) -> int:
        """
        FANZA規約に基づくモザイクサイズを計算
        規約（1）: 画像長辺×1/100、最小4ピクセル
        """
        try:
            height, width = image.shape[:2]
            long_side = max(height, width)
            
            if long_side < 400:
                return 4  # 最小サイズ
            
            mosaic_size = max(4, int(long_side / 100))
            logger.info(f"画像サイズ: {width}x{height}, モザイクサイズ: {mosaic_size}")
            return mosaic_size
        except Exception as e:
            logger.error(f"モザイクサイズ計算エラー: {e}")
            return 8  # デフォルト値
    
    def detect_sensitive_areas(self, image: np.ndarray) -> List[np.ndarray]:
        """
        MediaPipeを使用して性器領域を検出（軽量化版）
        """
        if self.pose is None:
            logger.warning("MediaPipe Poseが初期化されていません")
            return []
        
        try:
            # 画像サイズを大幅に調整（処理速度向上）
            h, w = image.shape[:2]
            if max(h, w) > 800:  # より小さく調整
                scale = 800 / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                resized_image = cv2.resize(image, (new_w, new_h))
            else:
                resized_image = image
                scale = 1.0
            
            # RGB変換（MediaPipeはRGBを要求）
            rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
            
            # ポーズ検出
            results = self.pose.process(rgb_image)
            
            if not results.pose_landmarks:
                logger.warning("人体の検出に失敗しました")
                return []
            
            # 性器領域の推定（腰周辺）
            sensitive_areas = []
            
            landmarks = results.pose_landmarks.landmark
            
            # 腰の位置を特定
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            
            if left_hip.visibility > 0.2 and right_hip.visibility > 0.2:  # 閾値を下げる
                # 腰周辺の矩形領域を作成
                left_x = int(left_hip.x * new_w / scale)
                right_x = int(right_hip.x * new_w / scale)
                hip_y = int(left_hip.y * new_h / scale)
                
                # 性器領域の推定（腰から下）
                sensitive_area = np.array([
                    [left_x - 25, hip_y],
                    [right_x + 25, hip_y],
                    [right_x + 25, h],
                    [left_x - 25, h]
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
        try:
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
                
                # 境界線のぼかし処理（軽量化）
                self._blur_boundaries_simple(result_image, x_min, x_max, y_min, y_max)
            
            return result_image
            
        except Exception as e:
            logger.error(f"モザイク適用中にエラーが発生: {e}")
            return image
    
    def _blur_boundaries_simple(self, image: np.ndarray, x_min: int, x_max: int, 
                               y_min: int, y_max: int):
        """
        モザイク境界の簡易ぼかし処理（軽量化版）
        """
        try:
            blur_radius = 3  # より小さく調整
            
            # 境界周辺の簡易ぼかし
            if y_min - blur_radius >= 0:
                cv2.GaussianBlur(image[y_min-blur_radius:y_min+blur_radius, x_min:x_max], 
                                (blur_radius*2+1, blur_radius*2+1), 0, 
                                dst=image[y_min-blur_radius:y_min+blur_radius, x_min:x_max])
            
            if y_max + blur_radius < image.shape[0]:
                cv2.GaussianBlur(image[y_max-blur_radius:y_max+blur_radius, x_min:x_max], 
                                (blur_radius*2+1, blur_radius*2+1), 0, 
                                dst=image[y_max-blur_radius:y_max+blur_radius, x_min:x_max])
            
        except Exception as e:
            logger.warning(f"境界ぼかし処理でエラー: {e}")
    
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
        try:
            if hasattr(self, 'pose') and self.pose:
                self.pose.close()
        except Exception as e:
            logger.warning(f"クリーンアップ中にエラー: {e}")
