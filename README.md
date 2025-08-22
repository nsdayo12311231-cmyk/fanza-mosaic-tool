# 🔒 FANZA同人出版用モザイクツール

FANZA同人に出版する画像を、FANZA隠蔽処理規約第6条に準拠してモザイクを自動でかけるツールです。

## ✨ 特徴

- **完全自動化**: 性器検出からモザイク処理まで全自動実行
- **FANZA規約準拠**: 第6条の隠蔽処理規約に完全準拠
- **アニメ/イラスト特化**: アニメ系画像での高精度検出
- **CLI優先**: エンジニア向けのコマンドラインインターフェース
- **高速処理**: 1枚あたり5秒以内での完了
- **設定可能**: YAMLファイルでの詳細設定

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/nsdayo12311231-cmyk/fanza-mosaic-tool.git
cd fanza-mosaic-tool
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 設定ファイルの初期化（オプション）

```bash
python -m src.cli init-config config/user_config.yaml
```

## 📖 使用方法

### 基本的な使用方法

#### 単一画像の処理

```bash
# 基本的な使用方法
python -m src.cli process input.jpg output.jpg

# カスタムモザイクサイズを指定
python -m src.cli process input.jpg output.jpg --mosaic-size 8

# 既存ファイルの上書き
python -m src.cli process input.jpg output.jpg --force
```

#### 複数画像の一括処理

```bash
# ディレクトリ内の全画像を処理
python -m src.cli batch input_dir/ output_dir/

# サブディレクトリも含めて処理
python -m src.cli batch input_dir/ output_dir/ --recursive

# 特定のパターンのファイルのみ処理
python -m src.cli batch input_dir/ output_dir/ --pattern "*.jpg"
```

#### 設定と情報

```bash
# 設定ファイルの初期化
python -m src.cli init-config config/my_config.yaml

# カスタム設定ファイルを使用
python -m src.cli --config config/my_config.yaml process input.jpg output.jpg

# システム情報の表示
python -m src.cli info

# 詳細ログの出力
python -m src.cli --verbose process input.jpg output.jpg
```

## 🔧 FANZA規約対応

### 規約第6条の実装

- **（1）モザイクサイズ**: 画像長辺×1/100の自動計算
- **（2）視覚的不明瞭**: ピクセル化による細部の不明瞭化
- **（3）技術的不可逆**: 元の表現に戻せない処理
- **（4）範囲指定**: 輪郭線を含む完全隠蔽
- **（5）必要部位**: 検出された全性器領域への処理
- **（6）処理の完全性**: 必要な部分への全体的な隠蔽

### モザイク処理仕様

- **基本サイズ**: 最小4ピクセル平方
- **動的サイズ**: 画像長辺400px以上で長辺×1/100
- **処理方法**: ピクセル化 + 境界線ぼかし
- **適用範囲**: 検出された性器領域全体

## ⚙️ 設定ファイル

### デフォルト設定 (config/default.yaml)

```yaml
# モザイク設定
mosaic:
  min_size: 4          # 最小モザイクサイズ
  scale_factor: 0.01   # スケール係数（1%）
  blur_radius: 3       # ぼかし半径

# 検出設定
detection:
  confidence: 0.5      # 検出信頼度
  model_complexity: 1  # モデル複雑度
  max_image_size: 1024 # 最大画像サイズ

# 出力設定
output:
  format: "png"        # 出力形式
  quality: 95          # 画像品質
  prefix: "processed_" # ファイル名プレフィックス
```

### カスタム設定

`config/user_config.yaml`を作成して、デフォルト設定を上書きできます。

## 📁 プロジェクト構造

```
mozaic/
├── src/                    # ソースコード
│   ├── __init__.py
│   ├── mosaic_processor.py # モザイク処理エンジン
│   └── cli.py             # CLIインターフェース
├── config/                 # 設定ファイル
│   ├── default.yaml       # デフォルト設定
│   └── user_config.yaml   # ユーザー設定
├── tests/                  # テストコード
├── examples/               # 使用例
├── docs/                   # ドキュメント
├── requirements.txt        # 依存関係定義
├── setup.py               # インストール設定
├── README.md              # 使用方法説明書
└── requirements.md         # 要件定義書
```

## 🌐 GitHubでの共有

### 共有方法

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/nsdayo12311231-cmyk/fanza-mosaic-tool.git
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定ファイルのカスタマイズ**
   ```bash
   python -m src.cli init-config config/user_config.yaml
   ```

4. **CLIコマンドでの実行**
   ```bash
   python -m src.cli process input.jpg output.jpg
   ```

## ⚠️ 注意事項

- **対象ユーザー**: プログラミング経験のあるエンジニア
- **実行環境**: ローカル環境での実行のみ
- **サーバー公開**: なし（GitHubでのコード共有）
- 処理に失敗した画像はログに記録されます
- 高解像度画像は処理時間が長くなる場合があります
- アニメ/イラスト系の画像に最適化されています

## 🐛 トラブルシューティング

### よくある問題

1. **依存関係のエラー**
   ```bash
   pip install -r requirements.txt
   ```

2. **画像読み込みエラー**
   - ファイルパスの確認
   - ファイル形式の確認
   - ファイルの破損確認

3. **処理速度が遅い**
   - 画像サイズの確認
   - 設定ファイルでの最適化
   - 並列処理数の調整

## 📝 技術仕様

### 使用技術
- **Python 3.9+**
- **MediaPipe**: Google提供の人体検出ライブラリ
- **OpenCV**: 高速画像処理ライブラリ
- **Click**: Python CLIフレームワーク
- **PyYAML**: 設定ファイル管理

### 処理フロー
1. コマンドライン引数の解析
2. 設定ファイルの読み込み
3. 画像読み込み・前処理
4. MediaPipeによる人体・性器検出
5. 検出領域の自動特定
6. FANZA規約準拠のピクセル化モザイク
7. 境界線のぼかし処理
8. 結果保存・ログ出力

## 🤝 貢献

バグ報告や機能要望は、GitHubのIssueでお知らせください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**作成日**: 2024年12月  
**バージョン**: 2.0 (GitHub共有・エンジニア向け版)  
**作成者**: AI Assistant
