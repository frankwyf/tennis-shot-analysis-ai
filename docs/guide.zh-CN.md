# 技术说明（简体中文）

本说明用于帮助你在个人作品集中清晰介绍该项目的设计、实现与可扩展方向。

## 项目结构

- `src/tennis_shot_analysis/config.py`：运行配置对象（`AnalysisConfig`）
- `src/tennis_shot_analysis/data.py`：合成数据生成 + 可选 BlazePose 视频提取
- `src/tennis_shot_analysis/metrics.py`：特征计算与摘要指标
- `src/tennis_shot_analysis/pipeline.py`：分析流程编排
- `src/tennis_shot_analysis/visualize.py`：可视化绘图
- `src/tennis_shot_analysis/cli.py`：命令行入口
- `tests/`：基础回归测试

## 核心指标

- 手腕速度代理：
  - 根据归一化坐标位移计算：
  - $speed_t = \frac{\sqrt{(\Delta x_t)^2 + (\Delta y_t)^2}}{\Delta t_t}$
- 躯干旋转代理：
  - $shoulder\_x - hip\_x$
- 击球时刻代理：
  - 手腕速度达到峰值的帧。

## 为什么要保留合成模式

- 无需私有视频即可完整运行。
- 结果可复现，便于测试与演示。
- 能把重点放在工程设计，而非数据权限。

## 可选真实视频模式

```bash
pip install -e .[video]
tennis-shot-demo --use-mediapipe-video --video-path your_clip.mp4
```

如果提取失败，可以降低 `--min-visibility`，并优先使用单人、无遮挡、机位稳定的视频。

## 常见问题解答

1. 为什么从 notebook 改成包结构？
   - 模块化、可测试、可发布。
2. 为什么先做代理指标？
   - 在开源场景先保证解释性和工程完整性。
3. 下一步怎么升级？
   - 增加动作阶段识别、时序平滑、多样本评估。
