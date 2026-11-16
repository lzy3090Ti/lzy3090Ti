# 主页维护说明

这是 lzy3090Ti 的 GitHub Profile README，不是一个独立网站。上传到公开同名仓库 `lzy3090Ti/lzy3090Ti` 的默认分支后，GitHub 会在个人主页显示根目录 README.md。

## 首次发布

1. 新建 **Public** 仓库，名称必须是 `lzy3090Ti`。
2. 将本目录里的 `README.md`、`assets/`、`scripts/`、`.github/` 和 `.gitignore` 上传到仓库根目录。不要再包一层 `profile-homepage/`。
3. 在 Actions 中打开 **Refresh profile artwork**，手动执行一次，确认成功。
4. 打开 https://github.com/lzy3090Ti 检查显示。

默认工作流每小时第 23 分钟尝试更新 GitHub 图表和 B 站 / 抖音粉丝数，调度可能延迟。只使用内置 GITHUB_TOKEN，不需要购买服务或额外设置 Personal Access Token。公开仓库的定时工作流可能因长期无活动被 GitHub 暂停，重新启用即可。

## 粉丝数与抖音入口

- 抖音号：`94425926195`，与页面昵称「硬盒子和软盒子」同时校验，入口直接指向已核实的个人主页。
- B 站使用公开 `x/relation/stat` 接口，校验返回的 UID 为 `1785338201`。
- 抖音使用 Playwright 打开未登录的公开页面，只读取 `user-info` 里的抖音号及 `user-info-fans`。不使用浏览器登录状态、Cookie、逆向签名或第三方粉丝服务。
- 新增运行依赖：Node.js 22+、固定版本 Playwright 1.65.1 及 Chromium；依赖锁定在 `package-lock.json`。
- 本地运行：`npm ci --ignore-scripts`、`npx playwright install chromium`、`npm run update:social`。已有 Chromium 时可设置 `PROFILE_CHROMIUM_PATH` 为其可执行文件绝对路径。
- 自动更新只需要公开页面，无需额外凭据。抖音可能限制云端或海外机器访问；请求失败、要求验证或字段变化时，保留上次成功的数字及原始获取时间，不显示为零。Actions 日志会发出 warning；两个平台均失败时工作流失败。
- 数字图片同时显示北京时间的最近获取时间，仓库内 `assets/social-data.json` 保存来源与时间。简写为“万 / 亿”的平台数据会标注“约”。
- GitHub README 不能执行实时脚本，图片还有 GitHub / 浏览器缓存，因此这里是每小时尝试刷新的快照，不能保证秒级实时；点击图片进入平台查看当前数据。
- `npm test` 校验数值解析、账号身份及时间显示。

## Gitee 官方镜像

- 源仓库：<https://github.com/lzy3090Ti/lzy3090Ti>；目标仓库：<https://gitee.com/ZackLi09/ZackLi09>。
- 使用 Gitee「仓库镜像管理」的 **Pull** 镜像，并开启「自动从 GitHub 同步仓库」。由 Gitee 官方创建 GitHub Webhook，在源仓库推送后触发同步；同一镜像最短更新间隔为 5 分钟。
- GitHub 是内容源，日常修改和粉丝数自动更新都在 GitHub 完成，再同步至 Gitee。直接修改 Gitee 镜像中的文件会被后续同步覆盖。
- 镜像凭据是专用的 GitHub classic PAT，按用户要求设置为 **No expiration**，权限为 Gitee 官方要求的 `repo` 和 `admin:repo_hook`。令牌仅填入 Gitee 官方配置，不保存在本仓库。若主动撤销令牌，需要在镜像编辑页更换并检查 Webhook。
- Gitee 个人主页已添加镜像仓库精选入口；完整主页展示在镜像仓库的 README。Gitee 会使用图片的浅色回退版本。
- 镜像设置：<https://gitee.com/ZackLi09/ZackLi09/mirrors>；官方说明：<https://help.gitee.com/repository/settings/sync-between-gitee-github>。

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
