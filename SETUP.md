# 主页维护说明

这是 lzy3090Ti 的 GitHub Profile README，不是一个独立网站。上传到公开同名仓库 `lzy3090Ti/lzy3090Ti` 的默认分支后，GitHub 会在个人主页显示根目录 README.md。

## 首次发布

1. 新建 **Public** 仓库，名称必须是 `lzy3090Ti`。
2. 将本目录里的 `README.md`、`assets/`、`scripts/`、`.github/` 和 `.gitignore` 上传到仓库根目录。不要再包一层 `profile-homepage/`。
3. 在 Actions 中打开 **Refresh profile artwork**，手动执行一次，确认成功。
4. 打开 https://github.com/lzy3090Ti 检查显示。

默认工作流每天北京时间约 08:23 更新 GitHub 图表，调度可能延迟。只使用内置 GITHUB_TOKEN，不需要购买服务或额外设置 Personal Access Token。公开仓库的定时工作流可能因长期无活动被 GitHub 暂停，重新启用即可。

## 修改内容

- 自我介绍、项目链接、精选视频链接：编辑 `README.md`。
- 横幅与项目卡：修改 `scripts/build_assets.py`，运行 `python3 scripts/build_assets.py`。
- 图表：运行 `python3 scripts/update_profile.py`（Python 3.10+，无需 pip 依赖，使用系统正常 HTTPS 证书验证）。
- 视频封面：`assets/video-*.png` 来自本人的 B 站公开视频原封面，统一为圆角裁切。更换视频时同步修改链接与封面。
- B 站视频是手选作品，不声称“最新视频”，不会抓取私人收藏、历史记录或登录数据。

## 兼容与设计

- GitHub README 会清理任意 CSS、脚本和 iframe，因此使用 Markdown、受支持 HTML 与仓库内 SVG/PNG。
- 没有嵌入播放器，点击视频封面会跳到 B 站播放。
- 不依赖第三方统计卡片服务；API 故障时保留上次成功生成的图表。
- 首屏与图表有独立窄屏素材，支持浅色和深色；视觉素材采用静态形状与清晰排版。
- 静态 SVG 可选用已安装的 FontTools 将本机 Avenir Next / Hiragino Sans GB 的文字转为轮廓；无需额外安装即可浏览，自动更新图表也不依赖这些字体或 FontTools。
- F1 项目插画是赛道造型示意，不是应用界面，不包含虚构数据。
- F1 Calendar 等仓库有自己的许可证，公开展示不等于允许商业使用。

设计参考：用户指定的 https://zhuanlan.zhihu.com/p/454597068 ，采用同名仓库与 Profile README 的机制；视觉素材与文案为本次创作，没有复制文章示例主页。
