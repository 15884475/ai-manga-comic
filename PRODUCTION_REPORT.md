# 「雨巷青春」漫剧生产文档

> 生产时间：2026-05-30 19:00-19:45
> 生成代理：Hermes Agent (DeepSeek-V4-Flash)
> GitHub: `~/ai-manga-comic` (https://github.com/15884475/ai-manga-comic)

---

## 一、生产流程总览

```
剧本(story.json) → 面板图(panels/) → 排版(pages/) → 配音(audio/) → 合成(video)
           ↓
    我直接写的        PIL占位图     RTL 1x1      edge-tts      ffmpeg+h264_videotoolbox
```

**完整流程耗时：** ~45分钟（其中占位图生成10秒，TTS语音60秒，ffmpeg合成30秒）

---

## 二、剧本（JSON）

### 元信息

| 字段 | 值 |
|------|-----|
| 标题 | 雨巷青春 |
| 时代 | 1998年夏天 |
| 地点 | 某高中 |
| 主题 | 校园暗恋·躲雨·青春悸动 |

### 角色

- **林小北** — 男主角，文静内敛，喜欢文学
- **苏雨晴** — 女主角，温柔细腻，喜欢画画

### 场景结构（4场×3镜=12镜）

#### 场景1：放学前（教室）

| 镜号 | 镜头 | 旁白 | 对白 |
|------|------|------|------|
| 1-1 | 全景 | 1998年夏天，高三（2）班的最后一节课结束了。窗外，乌云正悄悄聚集。 | (无) |
| 1-2 | 中景 | 林小北收拾好书包，目光不由自主地飘向那个熟悉的背影。 | (无) |
| 1-3 | 特写 | 苏雨晴看了看窗外——下雨了。她没带伞。 | 「哎呀，忘带伞了…」 |

#### 场景2：屋檐下（教学楼门口）

| 镜号 | 镜头 | 旁白 | 对白 |
|------|------|------|------|
| 2-1 | 全景 | 雨越下越大。苏雨晴站在教学楼门口，看着雨帘发愁。 | (无) |
| 2-2 | 中景 | 林小北鼓起勇气，默默站到了她旁边。 | 「你…也没带伞啊？」「嗯，没想到下这么大。」 |
| 2-3 | 特写 | 雨飘进来，打湿了她的肩膀。他想说什么，话到嘴边又咽了回去。 | (无) |

#### 场景3：靠近（屋檐下，雨更大）

| 镜号 | 镜头 | 旁白 | 对白 |
|------|------|------|------|
| 3-1 | 中景 | 雨更大了。林小北鼓起勇气，把课本举在了两人头顶。 | 「那个…先遮一下吧。」 |
| 3-2 | 特写 | 近距离的瞬间，他闻到了她发梢淡淡的洗发水香味。 | 「谢谢…你叫林小北对吧？」「嗯。你是…苏雨晴，画画很好的那个。」 |
| 3-3 | 中景 | 雨渐渐小了。一道彩虹悄然挂在天边。 | 「雨停了。」「嗯…我送你回去吧。」 |

#### 场景4：同行（雨后校园小径）

| 镜号 | 镜头 | 旁白 | 对白 |
|------|------|------|------|
| 4-1 | 全景 | 两人并肩走在雨后湿漉漉的校园小路上。 | (无) |
| 4-2 | 特写 | 她打开速写本，里面画着一个在梧桐树下看书的少年。原来她早就注意到了他。 | 「我见过你——你在老梧桐下看书，我画过你。」 |
| 4-3 | 中景 | 那个夏天，那个下雨天，一段青春的故事，刚刚开始。 | 「明天…还会下雨吗？」「下雨的话，我在这等你。」 |

### 完整 story.json

文件路径：`story.json`（已在 repo 根目录）

---

## 三、面板图生成

### 目标
为12个漫画分镜各生成一张 512×768 竖版面板图

### 尝试1：SiliconFlow API（失败）

```python
# 调用 black-forest-labs/FLUX.1-schnell
POST https://api.siliconflow.cn/v1/images/generations

结果：HTTP 403 {"code":30003,"message":"Model disabled."}
原因：用户的 SiliconFlow API Key 仅开通了文本模型，图片生成模型未启用
```

### 尝试2：Pollinations.ai（失败）

```python
# 调用 https://image.pollinations.ai/prompt/{prompt}
结果：HTTP 402 Payment Required (11/12失败，仅1张成功)
原因：该服务已转为付费
```

### 方案3：PIL 风格化占位图（使用）

生成脚本：`outputs/panels/create_panels.py`

策略：
- 每张面板图使用 Pillow 绘制竖版渐变背景
- 12种不同的暖/冷色调配色方案，对应不同场景氛围
- 中文文字排版（场景标签、标题、描述、底部氛围提示）
- 每张图添加装饰性圆形等简约图形元素

**12张面板配色方案：**

| 文件名 | 配色 | 氛围 |
|--------|------|------|
| scene_1_1.png | #F5E6CA → #D4A574 暖黄 | 教室午后的闷热 |
| scene_1_2.png | #E8D5B7 → #C49A6C 米褐 | 暗恋的温暖忐忑 |
| scene_1_3.png | #C9D6E8 → #8FA8C9 冷蓝 | 担忧·雨将来 |
| scene_2_1.png | #6B8FA3 → #3A5A6F 灰蓝 | 大雨·发愁 |
| scene_2_2.png | #7A9BAE → #4A6B80 雾蓝 | 并肩·沉默 |
| scene_2_3.png | #5A7A8F → #3A5A6F 深灰蓝 | 犹豫·欲言又止 |
| scene_3_1.png | #D4A574 → #B88A4A 暖橙 | 靠近的勇气 |
| scene_3_2.png | #E8C49A → #C9A57A 粉橙 | 对视的心跳 |
| scene_3_3.png | #F5E6CA → #D4C47A 暖黄 | 雨过天晴 |
| scene_4_1.png | #F0D5A5 → #D4A040 金黄 | 夕阳·同行 |
| scene_4_2.png | #F5E0C0 → #D4B080 暖米 | 速写本里的秘密 |
| scene_4_3.png | #E8C47A → #C99A4A 琥珀 | 约定·开始 |

---

## 四、排版（Layout）

```bash
PYTHONPATH=src python -m ai_manga.cli.main layout \
  --panels-dir ./outputs/panels \
  --output ./outputs/pages \
  --direction rtl \
  --layout 1x1
```

- 格式：1页1格（1行×1列）
- 方向：从右到左（RTL 漫画传统方向）
- 输出：12页，每页 1080×1920 竖屏
- 页面文件名：`page_000.png` ~ `page_011.png`

> 注意：最初尝试 `--layout auto`（2列×6行=12格/页），结果只有1页。改用 `1x1` 得到12页，每页5秒=60秒。

---

## 五、配音（TTS）

```bash
PYTHONPATH=src python -m ai_manga.cli.main tts \
  --story-file ./story.json \
  --output ./outputs/audio \
  --voice zh-CN-XiaoxiaoNeural
```

- 引擎：edge-tts (Microsoft Edge TTS)
- 音色：`zh-CN-XiaoxiaoNeural`（中文女声，温柔甜美风格）
- 生成：12段单独音频 + 1段混音
- 总时长：01:07（比视频长一点，用 -shortest 对齐）

### 每段旁白文本

| 序号 | 时长 | 文本 |
|------|------|------|
| clip_01 | ~5s | 1998年夏天，高三（2）班的最后一节课结束了… |
| clip_02 | ~3s | 林小北收拾好书包，目光不由自主地飘向那个熟悉的背影。 |
| clip_03 | ~3s | 苏雨晴看了看窗外——下雨了。她没带伞。 |
| clip_04 | ~4s | 雨越下越大。苏雨晴站在教学楼门口，看着雨帘发愁。 |
| clip_05 | ~3s | 林小北鼓起勇气，默默站到了她旁边。 |
| clip_06 | ~4s | 雨飘进来，打湿了她的肩膀。他想说什么，话到嘴边又咽了回去。 |
| clip_07 | ~4s | 雨更大了。林小北鼓起勇气，把课本举在了两人头顶。 |
| clip_08 | ~4s | 近距离的瞬间，他闻到了她发梢淡淡的洗发水香味。 |
| clip_09 | ~3s | 雨渐渐小了。一道彩虹悄然挂在天边。 |
| clip_10 | ~4s | 两人并肩走在雨后湿漉漉的校园小路上。 |
| clip_11 | ~4s | 她打开速写本，里面画着一个在梧桐树下看书的少年。 |
| clip_12 | ~4s | 那个夏天，那个下雨天，一段青春的故事，刚刚开始。 |

---

## 六、视频合成

### 第一步：面板→视频（无音频）

```bash
~/.cache/ai-manga/ffmpeg -y -f concat -safe 0 -i /tmp/video_concat.txt \
  -c:v h264_videotoolbox -b:v 5M -pix_fmt yuv420p -r 30 \
  outputs/manga_video.mp4
```

- 编码器：`h264_videotoolbox`（Apple Silicon 硬件编码）
- 分辨率：1080×1920 (竖屏)
- 时长：00:00:59.97 (≈60秒)
- 文件大小：~2.4MB

### 第二步：配音混音

```bash
~/.cache/ai-manga/ffmpeg -y -f concat -safe 0 -i /tmp/audio_concat.txt \
  -c copy /tmp/all_narration.mp3
```

输出：01:07

### 第三步：音视频合成

```bash
~/.cache/ai-manga/ffmpeg -y -i outputs/manga_video.mp4 -i /tmp/all_narration.mp3 \
  -c:v copy -c:a aac -b:a 128k -shortest \
  -map 0:v:0 -map 1:a:0 outputs/manga_video_final.mp4
```

最终视频：
- 时长：00:00:59.97
- 分辨率：1080×1920
- 视频码率：326 kb/s (H.264 High)
- 音频码率：98 kb/s (AAC LC, mono)
- 文件大小：~3.1MB

---

## 七、已有技能（skills）状态

**检查结果：** `ai-manga-pipeline` skill 已存在，描述了完整的漫剧管道架构。

- `ai-manga-pipeline` — 已存在，覆盖了从故事生成到视频合成的全流程
- 该 skill 描述了 ComfyUI/Diffusers 图像生成、RTL 漫画排版、edge-tts 配音、ffmpeg 合成

**不足之处：**
- skill 中假定用户有 ComfyUI 或 Diffusers 环境，未覆盖无图像生成能力时的回退方案
- 未记录图像生成 API（SiliconFlow/Pollinations/FAL）不可用时的应对策略

---

## 八、问题分析与改进建议

### 根本问题：面板图是占位图，非真实画面

这是视频「废片」的核心原因。12张面板图全部是 PIL 生成的渐变色+文字占位图，没有任何真实画面内容。

#### 原因链
```
无 FAL_KEY → image_generate 工具不可用
无 SiliconFlow 生图权限 → API 403
无 ComfyUI/Diffusers 环境 → 本地生图不可用
Pollinations.ai 付费 → 免费方案失效
→ 最终只能 PIL 占位图
```

### 修复方案（优先级排序）

| 优先级 | 方案 | 所需配置 | 复杂度 |
|--------|------|---------|--------|
| 🔴 P0 | 配置 **FAL_KEY** 环境变量 | 注册 fal.ai 获取 API Key | 低 |
| 🔴 P0 | 开通 SiliconFlow 生图权限 | 控制台启用 FLUX.1-schnell | 低 |
| 🟡 P1 | 安装 Diffusers（本地） | `pip install torch diffusers` (~2GB) | 中 |
| 🟢 P2 | 配置 ComfyUI | 需 GPU 环境 | 高 |

### 其他可改进项

1. **剧本故事生成** — 当前我直接写 JSON，后续可以让 LLM 通过 story generator 自动生成
2. **画面风格** — 当前占位图为渐变色+文字，改为真实图片后需统一画风（角色一致性）
3. **排版密度** — 1x1 每页一格+5秒可能偏慢，建议 2x2 每页4格+6秒=更快节奏
4. **配音** — edge-tts Xiaoxiao 效果不错，可增加背景音乐（BGM）

---

## 九、输出文件清单

```
outputs/
├── manga_video.mp4           # 无配音版视频 (2.4MB)
├── manga_video_final.mp4     # 最终版视频 (3.1MB)
├── assemble_video.py         # 手动合成脚本
├── audio/
│   ├── audio_mapping.json    # 配音与面板映射
│   ├── mixed_narration.mp3   # 第一次混音（有bug，仅8秒）
│   ├── narration_*.mp3       # 12段单独旁白
├── pages/
│   ├── page_000.png ~ page_011.png  # 12页排版图
├── panels/
│   ├── create_panels.py      # PIL占位图生成脚本
│   ├── create_placeholders.py # 弃用（横版版本）
│   ├── generate_free.py      # Pollinations.ai 失败尝试
│   ├── generate_panels.py    # SiliconFlow 失败尝试
│   ├── panel_mapping.json    # 面板数据映射
│   ├── scene_1_1.png ~ scene_4_3.png  # 12张面板图
```

---

## 十、本次运行的命令汇总

```bash
# 1. 写入剧本
# → 直接写入 story.json

# 2. 生成面板图（PIL占位图，512×768）
python3 outputs/panels/create_panels.py

# 3. 排版（RTL，1页1格）
PYTHONPATH=src python -m ai_manga.cli.main layout \
  --panels-dir ./outputs/panels \
  --output ./outputs/pages \
  --direction rtl --layout 1x1

# 4. 配音（edge-tts，晓晓女声）
PYTHONPATH=src python -m ai_manga.cli.main tts \
  --story-file ./story.json \
  --output ./outputs/audio \
  --voice zh-CN-XiaoxiaoNeural

# 5. 合成视频（ffmpeg h264_videotoolbox）
# 使用 ~/.cache/ai-manga/ffmpeg（静态编译带 libx264）

# 6. 音视频合并
~/.cache/ai-manga/ffmpeg -i outputs/manga_video.mp4 \
  -i /tmp/all_narration.mp3 \
  -c:v copy -c:a aac -shortest \
  outputs/manga_video_final.mp4
```
