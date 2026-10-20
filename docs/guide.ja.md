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
python -m pip install -e '.[video]'
tennis-shot-demo --source video --input your_clip.mp4 --pose-model /path/to/pose_landmarker.task
```

動画モードでは MediaPipe Tasks を使用し、ローカルの Pose Landmarker
`.task` モデルファイルを指定します。モデルの重みは自動でダウンロード
されません。動画が開けることと FPS が有効であることを確認し、MediaPipe
には単調増加するミリ秒タイムスタンプを渡します。終了時や例外時には動画
キャプチャを解放します。抽出できない場合は `--min-visibility` を下げ、
単一人物・遮蔽の少ない動画を使用してください。従来の
`--use-mediapipe-video` と `--video-path` は `--pose-model` と併用できます。

## 機械可読な出力

CLI は、派生プロキシ指標を含むランドマーク CSV と、丸めていない JSON
サマリーを出力できます。

```bash
tennis-shot-demo --no-show --save-landmarks artifacts/landmarks.csv --save-summary artifacts/summary.json
```

JSON には `schema_version`、入力 `source`、データソースの表示名、サマリーが
含まれます。サマリーは `impact_row` と互換キー `impact_frame` の両方を提供
します。利用側は読み込み前に `schema_version` を確認してください。CSV には
解析済みランドマークと派生プロキシ指標が入ります。

## レビューで話せるポイント

1. Notebook 単体からパッケージ化した理由は？
   - 保守性、テスト性、再利用性が向上するため。
2. なぜプロキシ指標を使うのか？
   - 小規模公開プロジェクトで説明可能性を優先するため。
3. 今後の拡張は？
   - 時系列平滑化、イベント分類、評価データセットの導入。
