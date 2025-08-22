#!/usr/bin/env python3
"""
FANZAモザイクツール CLIインターフェース
エンジニア向けのコマンドライン操作
"""

import click
import os
import sys
import yaml
import logging
from pathlib import Path
from typing import List, Optional
from .mosaic_processor import FanzaMosaicProcessor

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: Optional[str] = None) -> dict:
    """設定ファイルの読み込み"""
    default_config = {
        'mosaic': {
            'min_size': 4,
            'scale_factor': 0.01,
            'blur_radius': 3
        },
        'detection': {
            'confidence': 0.5,
            'model_complexity': 1,
            'max_image_size': 1024
        },
        'output': {
            'format': 'png',
            'quality': 95
        }
    }
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                # デフォルト設定とユーザー設定をマージ
                for key, value in user_config.items():
                    if key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
                logger.info(f"設定ファイルを読み込み: {config_path}")
        except Exception as e:
            logger.warning(f"設定ファイルの読み込みに失敗: {e}")
    
    return default_config

@click.group()
@click.version_option(version="2.0.0")
@click.option('--config', '-c', help='設定ファイルのパス')
@click.option('--verbose', '-v', is_flag=True, help='詳細ログの出力')
@click.pass_context
def cli(ctx, config, verbose):
    """FANZA同人出版用モザイクツール CLI"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    
    logger.info("FANZAモザイクツール CLI 開始")

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('--mosaic-size', '-s', type=int, help='モザイクサイズ（ピクセル）')
@click.option('--force', '-f', is_flag=True, help='既存ファイルの上書き')
@click.pass_context
def process(ctx, input_path: str, output_path: str, mosaic_size: Optional[int], force: bool):
    """単一画像のモザイク処理"""
    config = ctx.obj['config']
    
    # 出力ディレクトリの確認
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"出力ディレクトリを作成: {output_dir}")
    
    # 既存ファイルの確認
    if os.path.exists(output_path) and not force:
        if not click.confirm(f"ファイル {output_path} は既に存在します。上書きしますか？"):
            return
    
    # モザイク処理の実行
    processor = FanzaMosaicProcessor()
    try:
        logger.info(f"画像処理開始: {input_path}")
        
        # カスタムモザイクサイズの適用
        if mosaic_size:
            config['mosaic']['min_size'] = mosaic_size
            logger.info(f"カスタムモザイクサイズ: {mosaic_size}")
        
        success = processor.process_image(input_path, output_path)
        
        if success:
            click.echo(f"✅ 処理完了: {output_path}")
            logger.info(f"処理成功: {input_path} -> {output_path}")
        else:
            click.echo(f"❌ 処理失敗: {input_path}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"処理中にエラーが発生: {e}")
        click.echo(f"❌ エラーが発生しました: {e}")
        sys.exit(1)
    finally:
        processor.cleanup()

@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.argument('output_dir', type=click.Path())
@click.option('--pattern', '-p', default='*.{jpg,jpeg,png}', help='ファイルパターン')
@click.option('--recursive', '-r', is_flag=True, help='サブディレクトリも処理')
@click.option('--parallel', '-j', default=1, help='並列処理数')
@click.option('--force', '-f', is_flag=True, help='既存ファイルの上書き')
@click.pass_context
def batch(ctx, input_dir: str, output_dir: str, pattern: str, recursive: bool, parallel: int, force: bool):
    """複数画像の一括モザイク処理"""
    config = ctx.obj['config']
    
    # 出力ディレクトリの作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"出力ディレクトリを作成: {output_dir}")
    
    # 入力ファイルの検索
    input_path = Path(input_dir)
    if recursive:
        files = list(input_path.rglob(pattern))
    else:
        files = list(input_path.glob(pattern))
    
    if not files:
        click.echo(f"❌ 入力ディレクトリ {input_dir} に画像が見つかりません")
        return
    
    click.echo(f"📁 処理対象: {len(files)}ファイル")
    
    # バッチ処理の実行
    processor = FanzaMosaicProcessor()
    success_count = 0
    error_count = 0
    
    try:
        with click.progressbar(files, label='処理中') as file_list:
            for file_path in file_list:
                # 出力パスの生成
                rel_path = file_path.relative_to(input_path)
                output_path = Path(output_dir) / rel_path
                output_path = output_path.with_suffix('.png')  # 出力形式を統一
                
                # 出力ディレクトリの作成
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 既存ファイルの確認
                if output_path.exists() and not force:
                    continue
                
                # モザイク処理
                try:
                    success = processor.process_image(str(file_path), str(output_path))
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        logger.warning(f"処理失敗: {file_path}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"処理エラー: {file_path} - {e}")
        
        # 結果表示
        click.echo(f"\n🎉 バッチ処理完了!")
        click.echo(f"✅ 成功: {success_count}ファイル")
        click.echo(f"❌ 失敗: {error_count}ファイル")
        
        if error_count > 0:
            sys.exit(1)
            
    finally:
        processor.cleanup()

@cli.command()
@click.argument('config_path', type=click.Path())
@click.pass_context
def init_config(ctx, config_path: str):
    """設定ファイルの初期化"""
    config = ctx.obj['config']
    
    # 設定ディレクトリの作成
    config_dir = os.path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # 設定ファイルの作成
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        click.echo(f"✅ 設定ファイルを作成: {config_path}")
        click.echo("設定をカスタマイズしてから使用してください")
        
    except Exception as e:
        logger.error(f"設定ファイルの作成に失敗: {e}")
        click.echo(f"❌ 設定ファイルの作成に失敗: {e}")
        sys.exit(1)

@cli.command()
@click.pass_context
def info(ctx):
    """システム情報の表示"""
    config = ctx.obj['config']
    
    click.echo("🔒 FANZAモザイクツール システム情報")
    click.echo("=" * 50)
    click.echo(f"バージョン: 2.0.0")
    click.echo(f"Python: {sys.version}")
    click.echo(f"設定ファイル: 読み込み済み")
    click.echo(f"モザイク設定: {config['mosaic']}")
    click.echo(f"検出設定: {config['detection']}")
    click.echo(f"出力設定: {config['output']}")

if __name__ == '__main__':
    cli()
