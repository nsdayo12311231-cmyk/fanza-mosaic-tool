import streamlit as st
import os
import time
from pathlib import Path
from mosaic_processor import FanzaMosaicProcessor
import logging

# ページ設定
st.set_page_config(
    page_title="FANZAモザイクツール",
    page_icon="🔒",
    layout="wide"
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """メインアプリケーション"""
    
    # ヘッダー
    st.title("🔒 FANZA同人出版用モザイクツール")
    st.markdown("---")
    
    # 説明
    st.markdown("""
    ### 📋 使用方法
    1. **input**フォルダにモザイクをかけたい画像を配置
    2. 「処理開始」ボタンをクリック
    3. 処理完了後、**output**フォルダに結果が保存されます
    
    ### ⚠️ 注意事項
    - FANZA隠蔽処理規約第6条に準拠した処理を行います
    - 処理に失敗した画像は**error**フォルダに移動されます
    - 対応形式: PNG, JPG, JPEG
    """)
    
    # フォルダ状況の表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_count = len([f for f in os.listdir("input") if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        st.metric("📁 入力画像数", input_count)
    
    with col2:
        output_count = len([f for f in os.listdir("output") if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        st.metric("✅ 処理済み画像数", output_count)
    
    with col3:
        error_count = len([f for f in os.listdir("error") if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        st.metric("❌ エラー画像数", error_count)
    
    st.markdown("---")
    
    # 処理開始ボタン
    if st.button("🚀 処理開始", type="primary", use_container_width=True):
        if input_count == 0:
            st.error("❌ inputフォルダに画像がありません")
            return
        
        # 処理実行
        process_images()
    
    # 処理状況の表示
    if 'processing_status' in st.session_state:
        st.markdown("---")
        st.subheader("📊 処理状況")
        
        for status in st.session_state.processing_status:
            if status['status'] == 'success':
                st.success(f"✅ {status['filename']}: 処理完了")
            elif status['status'] == 'error':
                st.error(f"❌ {status['filename']}: 処理失敗 - {status['message']}")
            else:
                st.info(f"⏳ {status['filename']}: 処理中...")

def process_images():
    """画像の一括処理"""
    
    # 処理状況の初期化
    st.session_state.processing_status = []
    
    # プログレスバー
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 入力画像の取得
    input_files = [f for f in os.listdir("input") 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not input_files:
        st.error("処理対象の画像が見つかりません")
        return
    
    # モザイク処理エンジンの初期化
    processor = FanzaMosaicProcessor()
    
    try:
        for i, filename in enumerate(input_files):
            input_path = os.path.join("input", filename)
            output_path = os.path.join("output", filename)
            error_path = os.path.join("error", filename)
            
            # 進捗更新
            progress = (i + 1) / len(input_files)
            progress_bar.progress(progress)
            status_text.text(f"処理中: {filename} ({i+1}/{len(input_files)})")
            
            # 処理状況を更新
            st.session_state.processing_status.append({
                'filename': filename,
                'status': 'processing'
            })
            
            # 画像処理実行
            start_time = time.time()
            success = processor.process_image(input_path, output_path)
            processing_time = time.time() - start_time
            
            if success:
                # 処理成功
                st.session_state.processing_status[-1] = {
                    'filename': filename,
                    'status': 'success'
                }
                
                # 元ファイルを削除
                os.remove(input_path)
                
                logger.info(f"処理成功: {filename} (処理時間: {processing_time:.2f}秒)")
                
            else:
                # 処理失敗
                st.session_state.processing_status[-1] = {
                    'filename': filename,
                    'status': 'error',
                    'message': '性器領域の検出に失敗'
                }
                
                # エラーフォルダに移動
                os.rename(input_path, error_path)
                
                logger.error(f"処理失敗: {filename}")
        
        # 完了
        progress_bar.progress(1.0)
        status_text.text("✅ 全処理完了！")
        
        # 結果表示
        st.success(f"🎉 処理完了！ {len(input_files)}枚の画像を処理しました")
        
        # ページを再読み込み
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 処理中にエラーが発生しました: {str(e)}")
        logger.error(f"処理中にエラーが発生: {e}")
        
    finally:
        # リソースのクリーンアップ
        processor.cleanup()

def check_folders():
    """必要なフォルダの存在確認と作成"""
    folders = ["input", "output", "error"]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logger.info(f"フォルダを作成: {folder}")

if __name__ == "__main__":
    # フォルダの確認・作成
    check_folders()
    
    # メインアプリケーション実行
    main()
