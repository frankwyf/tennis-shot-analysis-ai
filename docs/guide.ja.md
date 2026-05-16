# 技術ガイド（日本語）

このドキュメントは、ポートフォリオ公開時に本プロジェクトの技術的価値を説明しやすくするための補足資料です。

## 構成

- `src/tennis_shot_analysis/config.py`: 実行設定 (`AnalysisConfig`)
- `src/tennis_shot_analysis/data.py`: 合成データ生成 + 任意の BlazePose 動画抽出
- `src/tennis_shot_analysis/metrics.py`: 指標計算とサマリー
- `src/tennis_shot_analysis/pipeline.py`: パイプライン制御
- `src/tennis_shot_analysis/visualize.py`: 可視化
- `src/tennis_shot_analysis/cli.py`: CLI エントリ
- `tests/`: 基本的な回帰テスト

## 主要な指標

- 手首速度プロキシ:
  - 正規化座標のフレーム間変位から計算:
  - $speed_t = \frac{\sqrt{(\Delta x_t)^2 + (\Delta y_t)^2}}{\Delta t_t}$
- 体幹回旋プロキシ:
  - $shoulder\_x - hip\_x$
- インパクト推定フレーム:
  - 手首速度が最大になるフレーム。

## 合成モードを残す理由

- 非公開動画なしで再現可能。
- テストとデモで同じ結果を得やすい。
- 推論モデル依存を分離し、設計を説明しやすい。

## 実動画モード（任意）

```bash
pip install -e .[video]
tennis-shot-demo --use-mediapipe-video --video-path your_clip.mp4
```

抽出できない場合は `--min-visibility` を下げ、単一人物・遮蔽の少ない動画を使用してください。

## レビューで話せるポイント

1. Notebook 単体からパッケージ化した理由は？
   - 保守性、テスト性、再利用性が向上するため。
2. なぜプロキシ指標を使うのか？
   - 小規模公開プロジェクトで説明可能性を優先するため。
3. 今後の拡張は？
   - 時系列平滑化、イベント分類、評価データセットの導入。
