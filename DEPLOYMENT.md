# Python零基础学习平台 - Cloudflare Pages 部署指南

## 一键部署到 Cloudflare Pages

### 前置条件
- 拥有 Cloudflare 账号（免费版即可）
- 本地已安装 Git

### 部署步骤

#### 方法一：使用 GitHub/GitLab 自动部署（推荐）

1. **创建 GitHub 仓库**
   - 在 GitHub 上创建一个新的公开或私有仓库
   - 将 `frontend/` 目录下的所有文件推送到仓库

2. **登录 Cloudflare 控制台**
   - 访问 [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - 登录你的账号

3. **创建 Pages 项目**
   - 点击左侧菜单的「Pages」
   - 点击「Create a project」
   - 选择「Connect to Git」
   - 选择你的 GitHub 仓库

4. **配置构建设置**
   - **Production branch**: `main` 或你的主分支
   - **Build command**: 留空（纯静态项目无需构建）
   - **Build output directory**: 留空（使用根目录）
   - 点击「Save and Deploy」

5. **等待部署完成**
   - Cloudflare 会自动构建并部署你的项目
   - 部署完成后会显示你的项目域名（类似 `xxx.pages.dev`）

#### 方法二：直接上传文件

1. **登录 Cloudflare 控制台**
   - 访问 [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - 点击左侧菜单的「Pages」
   - 点击「Create a project」

2. **选择「Direct Upload」**
   - 点击「Upload assets」
   - 选择 `frontend/` 目录下的所有文件（包含子目录）

3. **部署**
   - 点击「Deploy」按钮
   - 等待部署完成

### 验证部署

部署完成后，访问你的项目域名，应该能看到：
- 学习平台首页
- 第1周学习内容（6页）
- 语音讲解功能
- Python在线运行环境

---

## 新增学习内容规范

### JSON 文件格式

在 `data/` 目录下创建新的 JSON 文件，命名格式为 `weekN.json`（N 为周数）。

```json
{
  "week": "第N周",
  "title": "本周标题",
  "pages": [
    {
      "id": "page1",
      "title": "页面标题",
      "content": "HTML格式的学习内容",
      "speech": "语音讲解文本内容",
      "hasCode": false,
      "defaultCode": ""
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `week` | string | 是 | 周数标识，如「第2周」 |
| `title` | string | 是 | 本周主题标题 |
| `pages` | array | 是 | 页面数组 |
| `pages[].id` | string | 是 | 页面唯一标识 |
| `pages[].title` | string | 是 | 页面标题 |
| `pages[].content` | string | 是 | HTML格式的学习内容 |
| `pages[].speech` | string | 否 | 语音讲解文本 |
| `pages[].hasCode` | boolean | 否 | 是否显示代码编辑器 |
| `pages[].defaultCode` | string | 否 | 默认代码内容 |

### 更新周选择器

在 `index.html` 中添加新的选项：

```html
<select id="weekSelect" class="week-select">
  <option value="week1">第1周：编程初识与环境搭建</option>
  <option value="week2">第2周：变量与数据类型</option>
</select>
```

### 内容编写规范

1. **HTML 内容**
   - 支持 `<p>`, `<h3>`, `<ul>`, `<ol>`, `<li>`, `<code>`, `<pre>`, `<blockquote>` 标签
   - 使用 `<span class="highlight">` 标记重点内容

2. **语音文本**
   - 使用纯文本，避免 HTML 标签
   - 分段清晰，便于阅读
   - 避免特殊字符

3. **代码示例**
   - 确保代码可以在 Pyodide 中运行
   - 避免使用系统级操作（如文件读写）
   - 保持代码简洁

---

## Cloudflare Pages 免费版限制说明

| 限制项 | 免费版限制 | 说明 |
|--------|-----------|------|
| 带宽 | 100GB/月 | 足够个人学习使用 |
| 存储 | 无限制 | 静态文件存储 |
| 请求数 | 无限制 | |
| 单文件大小 | 25MiB | 本项目所有文件都远小于此限制 |
| 构建时间 | 15分钟 | 纯静态项目无需构建 |

---

## 技术栈说明

### 前端框架
- **纯静态 HTML/CSS/JS** - 无需后端服务器
- **Monaco Editor** - 代码编辑器（CDN引入）
- **Pyodide** - 浏览器端Python运行环境（CDN引入）
- **Edge-TTS Browser** - 高质量语音合成（本地文件）
- **Web Speech API** - 语音合成（降级方案）

### 第三方 CDN 依赖

| 依赖 | CDN 地址 | 用途 |
|------|----------|------|
| Font Awesome | `cdnjs.cloudflare.com` | 图标库 |
| Noto Sans SC | `fonts.googleapis.com` | 中文字体 |
| Monaco Editor | `cdnjs.cloudflare.com` | 代码编辑器 |
| Pyodide | `cdn.jsdelivr.net` | Python运行环境 |

### Edge-TTS 本地文件

为了获得更好的语音质量，项目支持 Edge-TTS Browser。请手动下载并放置到 `libs/` 目录：

```bash
# 下载 Edge-TTS Browser（需要手动执行）
curl -o libs/edge-tts-browser.min.js \
  https://cdn.jsdelivr.net/npm/@kingdanx/edge-tts-browser@latest/dist/edge-tts-browser.min.js
```

如果本地文件不存在，系统会自动降级使用浏览器原生语音合成。

---

## 本地开发

### 启动本地服务器

```bash
# 使用 Python 3
python -m http.server 8000

# 或使用 Node.js
npx serve .

# 或使用 PHP
php -S localhost:8000
```

### 访问地址

打开浏览器访问 `http://localhost:8000`

---

## 故障排除

### 问题1：Pyodide 加载缓慢

**原因**：Pyodide 是一个较大的 WASM 文件（约 15MB）

**解决方案**：
- 首次加载可能需要较长时间，后续会缓存
- 确保使用稳定的网络连接

### 问题2：语音合成不工作

**原因**：浏览器不支持 Web Speech API 或未授权麦克风权限

**解决方案**：
- 使用 Chrome、Edge 或 Safari 浏览器
- 确保已授权网站使用麦克风

### 问题3：代码运行报错

**原因**：Pyodide 环境与本地 Python 环境有差异

**解决方案**：
- 避免使用系统级模块（如 `os`, `subprocess`）
- 避免使用文件读写操作
- 查看浏览器控制台获取详细错误信息

### 问题4：部署后页面空白

**原因**：文件路径不正确或构建配置错误

**解决方案**：
- 确保所有文件都已上传
- 检查 `index.html` 中的路径引用
- 查看浏览器控制台的错误信息