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
python -m pip install -e '.[video]'
tennis-shot-demo --source video --input your_clip.mp4 --pose-model /path/to/pose_landmarker.task
```

视频模式使用 MediaPipe Tasks，需要用户提供本地 Pose Landmarker `.task`
模型文件；项目不会自动下载模型权重。提取器会检查视频是否可打开及帧率
是否有效，向 MediaPipe 传入严格递增的毫秒时间戳，并在结束或异常时释放视频
句柄。如果没有有效关键点，可以降低 `--min-visibility`，并优先使用单人、
无遮挡、机位稳定的视频。旧的 `--use-mediapipe-video` 和 `--video-path`
参数仍可使用，但也需要配合 `--pose-model`。

## 机器可读输出

CLI 可以导出包含派生代理指标的关键点 CSV，以及未舍入的 JSON 摘要，方便
后续脚本稳定读取：

```bash
tennis-shot-demo --no-show --save-landmarks artifacts/landmarks.csv --save-summary artifacts/summary.json
```

JSON 包含 `schema_version`、输入 `source`、可读数据来源标签和摘要；摘要同时
提供 `impact_row` 与兼容字段 `impact_frame`。读取方应先检查
`schema_version`。CSV 保存分析后的关键点行及派生代理指标。

## 常见问题解答

1. 为什么从 notebook 改成包结构？
   - 模块化、可测试、可发布。
2. 为什么先做代理指标？
   - 在开源场景先保证解释性和工程完整性。
3. 下一步怎么升级？
   - 增加动作阶段识别、时序平滑、多样本评估。

## v0.4 开源工程升级

`--no-plot` 可跳过绘图及 Matplotlib 导入，适合批处理；`--no-show` 使用
Agg 后端渲染但不开窗口。所有输出必须指向不同文件，且不能覆盖输入或模型，
也不能通过软链接或硬链接绕过。CSV 表头和 DataFrame 列名必须唯一。
`--version` 显示已安装的版本。普通 requirements 安装不再引入视频依赖。

核心 CI 增加 Windows、Python 3.11 和最低数值依赖组合；视频 CI 单独验证
OpenCV 编解码与 Tasks 导入，推理仍使用替身。发布前在干净环境安装 wheel
并验证真实命令行入口，发布 wheel、源码包与 SHA-256 校验清单。

详见 [接口与输出契约](CLI.md)、[指标定义及限制](METRICS.md)、
[验证记录](VALIDATION.md)、[详细升级路线](ROADMAP.md) 和
[macOS 外置盘开发说明](MACOS.md)。本项目仍处于 alpha 阶段；上述工程验证
不代表已验证真实模型、击球事件或人体运动学准确性。
