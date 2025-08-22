# FANZAモザイクツール 使用例

## 🚀 基本的な使用方法

### 1. 単一画像の処理

```bash
# 基本的な使用方法
python -m src.cli process input.jpg output.jpg

# カスタムモザイクサイズを指定
python -m src.cli process input.jpg output.jpg --mosaic-size 8

# 既存ファイルの上書き
python -m src.cli process input.jpg output.jpg --force
```

### 2. 複数画像の一括処理

```bash
# ディレクトリ内の全画像を処理
python -m src.cli batch input_dir/ output_dir/

# サブディレクトリも含めて処理
python -m src.cli batch input_dir/ output_dir/ --recursive

# 特定のパターンのファイルのみ処理
python -m src.cli batch input_dir/ output_dir/ --pattern "*.jpg"

# 並列処理（4並列）
python -m src.cli batch input_dir/ output_dir/ --parallel 4
```

### 3. 設定ファイルの管理

```bash
# 設定ファイルの初期化
python -m src.cli init-config config/my_config.yaml

# カスタム設定ファイルを使用
python -m src.cli --config config/my_config.yaml process input.jpg output.jpg

# システム情報の表示
python -m src.cli info
```

## ⚙️ 設定ファイルの例

### カスタム設定ファイル (user_config.yaml)

```yaml
# モザイク設定
mosaic:
  min_size: 6          # 最小モザイクサイズ
  scale_factor: 0.015  # スケール係数（1.5%）
  blur_radius: 4       # ぼかし半径

# 検出設定
detection:
  confidence: 0.6      # 検出信頼度
  model_complexity: 2  # モデル複雑度（高精度）
  max_image_size: 2048 # 最大画像サイズ

# 出力設定
output:
  format: "jpg"        # 出力形式
  quality: 90          # JPEG品質
  prefix: "mosaic_"    # ファイル名プレフィックス
```

## 🔧 高度な使用方法

### 1. ログレベルの調整

```bash
# 詳細ログの出力
python -m src.cli --verbose process input.jpg output.jpg

# 設定ファイルでログレベルを変更
logging:
  level: "DEBUG"
```

### 2. パイプライン処理

```bash
# 複数の画像を連続処理
for file in *.jpg; do
  python -m src.cli process "$file" "output/${file%.jpg}_processed.png"
done
```

### 3. エラーハンドリング

```bash
# エラー時の終了コードを確認
python -m src.cli process input.jpg output.jpg
echo $?  # 0: 成功, 1: 失敗
```

## 📁 ディレクトリ構造の例

```
project/
├── input/
│   ├── image1.jpg
│   ├── image2.png
│   └── subdir/
│       └── image3.jpg
├── output/
│   ├── image1_processed.png
│   ├── image2_processed.png
│   └── subdir/
│       └── image3_processed.png
└── config/
    └── user_config.yaml
```

## ⚠️ 注意事項

- 入力画像は一般的な形式（JPG, PNG, JPEG）に対応
- 出力形式はPNGが推奨（品質保持）
- 高解像度画像は処理時間が長くなる場合がある
- 処理に失敗した画像はログに記録される

## 🐛 トラブルシューティング

### よくある問題と解決法

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
