import streamlit as st
import os
import time
from pathlib import Path
from mosaic_processor import FanzaMosaicProcessor
import logging
import tempfile
import shutil

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
    1. **画像をアップロード**または**input**フォルダに配置
    2. 「処理開始」ボタンをクリック
    3. 処理完了後、結果をダウンロード
    
    ### ⚠️ 注意事項
    - FANZA隠蔽処理規約第6条に準拠した処理を行います
    - 処理に失敗した画像はエラーとして表示されます
    - 対応形式: PNG, JPG, JPEG
    """)
    
    # ファイルアップロード機能
    st.markdown("### 📤 画像アップロード")
    uploaded_files = st.file_uploader(
        "モザイクをかけたい画像を選択してください",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="複数の画像を同時に選択できます"
    )
    
    # 処理開始ボタン
    if st.button("🚀 処理開始", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("❌ 画像がアップロードされていません")
            return
        
        # 処理実行
        process_uploaded_images(uploaded_files)
    
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

def process_uploaded_images(uploaded_files):
    """アップロードされた画像の処理"""
    
    # 処理状況の初期化
    st.session_state.processing_status = []
    
    # プログレスバー
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # モザイク処理エンジンの初期化
    processor = FanzaMosaicProcessor()
    
    try:
        processed_images = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # 進捗更新
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"処理中: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
            
            # 処理状況を更新
            st.session_state.processing_status.append({
                'filename': uploaded_file.name,
                'status': 'processing'
            })
            
            # 一時ファイルとして保存
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # 画像処理実行
                start_time = time.time()
                success = processor.process_image(tmp_path, tmp_path)
                processing_time = time.time() - start_time
                
                if success:
                    # 処理成功
                    st.session_state.processing_status[-1] = {
                        'filename': uploaded_file.name,
                        'status': 'success'
                    }
                    
                    # 処理済み画像をリストに追加
                    with open(tmp_path, 'rb') as f:
                        processed_images.append({
                            'name': f"processed_{uploaded_file.name}",
                            'data': f.read(),
                            'type': uploaded_file.type
                        })
                    
                    logger.info(f"処理成功: {uploaded_file.name} (処理時間: {processing_time:.2f}秒)")
                    
                else:
                    # 処理失敗
                    st.session_state.processing_status[-1] = {
                        'filename': uploaded_file.name,
                        'status': 'error',
                        'message': '性器領域の検出に失敗'
                    }
                    
                    logger.error(f"処理失敗: {uploaded_file.name}")
                
            finally:
                # 一時ファイルの削除
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        # 完了
        progress_bar.progress(1.0)
        status_text.text("✅ 全処理完了！")
        
        # 結果表示
        if processed_images:
            st.success(f"🎉 処理完了！ {len(processed_images)}枚の画像が処理されました")
            
            # ダウンロードボタンの表示
            st.markdown("### 📥 処理済み画像のダウンロード")
            for img in processed_images:
                st.download_button(
                    label=f"📥 {img['name']} をダウンロード",
                    data=img['data'],
                    file_name=img['name'],
                    mime=img['type']
                )
        else:
            st.warning("⚠️ 処理に成功した画像がありません")
        
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
