import streamlit as st

# ページ設定
st.set_page_config(
    page_title="FANZAモザイクツール",
    page_icon="🔒",
    layout="wide"
)

def main():
    """メインアプリケーション（テスト版）"""
    
    # ヘッダー
    st.title("🔒 FANZA同人出版用モザイクツール")
    st.markdown("---")
    
    # 説明
    st.markdown("""
    ### 📋 テスト版アプリケーション
    
    このアプリケーションは、Streamlit Cloudでの起動テスト用です。
    
    ### ✅ 起動確認
    - Streamlit Cloudでの起動が成功しました
    - 基本的な機能が動作しています
    
    ### 🔄 次のステップ
    起動が確認できたら、モザイク処理機能を段階的に追加していきます。
    """)
    
    # テスト用のボタン
    if st.button("🧪 テストボタン", type="primary"):
        st.success("✅ アプリケーションが正常に動作しています！")
    
    # 現在の時刻表示
    import datetime
    st.write(f"**現在時刻**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
