# 抖音 / 小红书 AI 热门内容互动助手

[English](README.md) | 简体中文

Visible Social Conversation Scout 是一个面向 Codex 的抖音与小红书互动辅助 Skill。它在用户主动启动、已经登录且持续可见的浏览器中，寻找与账号定位相符的热门公开内容，保留 3–5 个原页面，并为每页生成 3 条符合当前账号人设的待审评论。

项目不会代替用户点赞、收藏、关注、评论、发布或发送私信，也不提供验证码处理、身份伪装、网络轮换、随机操作或反检测能力。

## 当前状态

`0.5.0-rc.4` 是按独立产品需求重新编写的公开候选版本。项目与抖音、小红书、OpenCLI 或 DokoBot 没有隶属、合作或认可关系。

## 一次运行会交付什么

- 单个平台 3–5 个已经核验的原内容页面；
- 另保留 1 个能看到完整搜索词的搜索工作页，作为发现过程凭据，不计入 3–5 个原页面；
- 页面保留在用户自己的可见浏览器中；
- 每页恰好 3 条基于页面证据和账号公开声纹的回复选项；
- 可按当前平台账号的公开资料匹配并冻结一个主题，不沿用另一平台账号的主题；
- 选择依据、证据限制、账号声纹置信度和披露提醒；
- 平台写操作始终为零，最终编辑和发布由人完成。

## 安装

将本目录复制到：

```text
~/.codex/skills/visible-social-conversation-scout
```

下一轮 Codex 对话即可使用：

```text
使用 $visible-social-conversation-scout，在我当前已登录且可见的 Chrome 中审阅一个小红书主题。交付 3 个原页面，每页给 3 条待审回复，不执行任何平台写操作。
```

也可以让 Skill 先按当前平台账号匹配一个主题：

```text
使用 $visible-social-conversation-scout，在抖音当前账号的公开主页和最多 5 条公开作品中匹配一个主题，搜索前冻结主题，再交付 3 个原页面和每页 3 条待审回复，不执行任何平台写操作。
```

## 依赖

- Python 3.10 或更高版本；
- 能控制并持久保留可见浏览器页面的宿主环境；
- OpenCLI、DokoBot 等外部适配器为可选依赖，本仓库不包含这些软件。

工具可用不等于平台允许自动化。每次运行前仍须检查最新平台规则、账号权限和适用法律。

## 本地验证

```text
python -m unittest discover -s tests -v
python scripts/check_run_plan.py --input examples/run-plan.example.json --output run-plan-receipt.json
python scripts/authorize_browser_read.py --plan examples/run-plan.example.json --receipt run-plan-receipt.json --target-url https://www.xiaohongshu.com/ --output browser-read-authorization.json
python scripts/rank_review_queue.py --input examples/review-items.example.json --output review-queue.json
```

许可证和来源说明见 `LICENSE`、`NOTICE` 与 `THIRD_PARTY.md`。
