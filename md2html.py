#!/usr/bin/env python3
"""md2html.py — Markdown → 幕布风折叠大纲 HTML 笔记生成器

把 Markdown 笔记转换成统一视觉风格(白底幕布风)的折叠大纲 HTML,
自带主页索引、键盘导航、代码高亮、一键复制、折叠状态记忆等能力。

══════════════════════════════════════════════════════════════════════
依赖
══════════════════════════════════════════════════════════════════════

    pip install markdown beautifulsoup4

(Arch Linux 需要 --break-system-packages)

══════════════════════════════════════════════════════════════════════
命令总览
══════════════════════════════════════════════════════════════════════

  python3 md2html.py list                 # 列出所有笔记
  python3 md2html.py list --sections      # 详细列出含每篇的章节
  python3 md2html.py search "redis"       # 按关键词搜索笔记/章节
  python3 md2html.py show  "Rust 资源"    # 查看单篇详情(含锚点链接)
  python3 md2html.py add   new.md         # 添加 .md(自动转换+入主页)
  python3 md2html.py add   note.html      # 关联现成 HTML(不转换)
  python3 md2html.py delete 旧笔记         # 删除 HTML(保留源 .md)
  python3 md2html.py delete 旧笔记 --purge # 连源 .md 一起删
  python3 md2html.py batch                # 全量重建所有 .md + index.html
  python3 md2html.py convert file.md      # 只转换单文件(不更新主页)
  python3 md2html.py file.md              # 兼容旧用法,等同 convert
  python3 md2html.py --batch              # 兼容旧用法,等同 batch

所有命令均可用 --dir <path> 指定其他目录(默认当前目录)。

══════════════════════════════════════════════════════════════════════
典型工作流
══════════════════════════════════════════════════════════════════════

1. 初始化一个笔记目录,丢几个 .md 进去
2. python3 md2html.py batch              # 一次性转换 + 生成主页
3. 浏览器打开 index.html 看效果
4. 之后每次新增/修改 .md 后,挑一种方式更新:
     python3 md2html.py add 新笔记.md    # 增量(快)
     python3 md2html.py batch            # 全量重建(稳)
5. 不要的笔记:
     python3 md2html.py delete 笔记名     # 移除 HTML
     python3 md2html.py delete 笔记名 --purge  # 连源 MD 一起删

══════════════════════════════════════════════════════════════════════
部署到 GitHub Pages
══════════════════════════════════════════════════════════════════════

1. 新建仓库 <username>.github.io(或任意名,启用 Pages)
2. 把整个目录推上去:
     git init && git add . && git commit -m "notes"
     git remote add origin git@github.com:<username>/<username>.github.io.git
     git push -u origin main
3. 访问 https://<username>.github.io/ 即可
4. 之后每次更新笔记 → 跑一次 batch → git push

══════════════════════════════════════════════════════════════════════
名称匹配规则(add/delete/show 共用)
══════════════════════════════════════════════════════════════════════

按以下顺序尝试匹配,任意一级命中即返回:
  1. 文件 stem 完全相等(如 "Rust-造轮子资源")
  2. 文件名相等(如 "Rust-造轮子资源.md" / ".html")
  3. 标题完全相等(如 "Rust 造轮子 / 动手实践资源")
  4. 标题或 stem 子串包含(大小写不敏感)

匹配不到会列出所有候选,方便复制粘贴。

══════════════════════════════════════════════════════════════════════
自定义
══════════════════════════════════════════════════════════════════════

直接编辑本脚本顶部的常量:
  SITE_TITLE     主页和顶栏的站点标题
  SITE_SUBTITLE  主页副标题
  SITE_AUTHOR    footer 署名

颜色、字号、间距在 THEME_CSS 字符串里,改 CSS 变量即可:
  --bg / --text / --accent / --code-bg / --indent ...

══════════════════════════════════════════════════════════════════════
键盘快捷键(页面上)
══════════════════════════════════════════════════════════════════════

  Tab            折叠/展开当前聚焦的节点
  Shift + Tab    全局折叠/展开
  /              聚焦搜索框
  点击 ●         折叠当前
  点击标题       进入文章页 / 跳转章节
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag

# ============================================================================
# 配置
# ============================================================================
SITE_TITLE = "Salted的笔记"
SITE_SUBTITLE = ""
SITE_AUTHOR = "Salted"

# ============================================================================
# 主题 CSS — 幕布视觉 + org 操作
# ============================================================================
THEME_CSS = r"""
:root {
  --bg: #ffffff;
  --bg-soft: #fafafa;
  --bg-hover: #f5f5f7;
  --bg-inset: #f4f4f5;
  --bg-toc: #fafbfc;

  --text: #1a1a1f;
  --text-secondary: #4a4a55;
  --text-muted: #8a8a95;
  --text-faint: #c8c8d0;
  --text-ghost: #e6e6ea;

  --accent: #2563eb;
  --accent-soft: rgba(37, 99, 235, 0.07);
  --accent-hover: #1d4ed8;
  --accent-glow: rgba(37, 99, 235, 0.18);

  --link: #2563eb;
  --link-hover: #1d4ed8;

  --border: #ececef;
  --border-soft: #f2f2f5;
  --border-strong: #d8d8de;

  --code-bg: #f6f6f8;
  --code-text: #1a1a1f;
  --code-border: #e8e8ec;

  --quote-bg: #fafbfc;
  --quote-border: #d8d8de;

  --shadow-sm: 0 1px 2px rgba(15, 15, 30, 0.04);
  --shadow-md: 0 4px 12px rgba(15, 15, 30, 0.06), 0 1px 3px rgba(15, 15, 30, 0.04);
  --shadow-lg: 0 12px 28px rgba(15, 15, 30, 0.08);

  --radius-sm: 4px;
  --radius: 6px;
  --radius-lg: 8px;

  --max-width: 860px;

  --font-sans: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI",
               "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  min-height: 100vh;
}

main, header, footer, .topbar { position: relative; }

/* ---------- 顶部进度条 ---------- */
.progress-bar {
  position: fixed;
  top: 0; left: 0;
  height: 2px;
  width: 0%;
  background: var(--accent);
  z-index: 100;
  transition: width 0.05s linear;
}

/* ---------- 顶栏 ---------- */
.topbar {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: saturate(180%) blur(12px);
  -webkit-backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--border-soft);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  z-index: 50;
}

.topbar .brand {
  font-weight: 600;
  color: var(--text);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: -0.01em;
  font-size: 14px;
  border-bottom: none;
  transition: color 0.12s;
}
.topbar .brand:hover { color: var(--accent); border-bottom: none; }
.topbar .brand .seal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--text);
  color: white;
  border-radius: 5px;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: -0.02em;
}

.topbar .spacer { flex: 1; }

.topbar button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 28px;
  padding: 0 11px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font: 500 12px/1 var(--font-sans);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, transform 0.06s;
  white-space: nowrap;
  letter-spacing: -0.005em;
  font-family: var(--font-sans);
}
.topbar button:hover {
  background: var(--bg-hover);
  color: var(--text);
}
.topbar button:active {
  background: var(--bg-inset);
  transform: scale(0.97);
}
.topbar button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}
.topbar button.icon {
  width: 28px;
  padding: 0;
  font-size: 13px;
  font-weight: 700;
}
.topbar button .chev {
  display: inline-block;
  transition: transform 0.15s;
  font-size: 9px;
  color: var(--text-muted);
}
.topbar button:hover .chev { color: inherit; }
.topbar button[data-state="folded"] .chev { transform: rotate(-90deg); }
.topbar button[data-state="expanded"] .chev { transform: rotate(0deg); }

.topbar .search {
  flex: 0 1 280px;
  padding: 5px 11px 5px 30px;
  background: var(--bg-inset) url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%238a8a95' stroke-width='2' stroke-linecap='round'><circle cx='11' cy='11' r='7'/><line x1='21' y1='21' x2='16.5' y2='16.5'/></svg>") 9px center/13px no-repeat;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: all 0.12s;
}
.topbar .search:focus {
  background-color: white;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.topbar .search::placeholder { color: var(--text-muted); }

/* ---------- hero ---------- */
.hero {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 20px 32px 4px;
}
.hero .eyebrow {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin: 0 0 16px;
}
.hero .title {
  font-size: 2em;
  font-weight: 700;
  margin: 0 0 4px;
  letter-spacing: -0.025em;
  line-height: 1.2;
  color: var(--text);
}
.hero .subtitle {
  color: var(--text-secondary);
  font-size: 0.92em;
  margin: 0;
  line-height: 1.55;
}
.hero .stats {
  display: flex;
  gap: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-soft);
  font-size: 12px;
  color: var(--text-muted);
}
.hero .stats > div { display: flex; align-items: baseline; gap: 6px; }
.hero .stats .num {
  font-size: 1.5em;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
}
.hero .stats .label {
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 500;
}

/* ---------- 笔记页文档头 ---------- */
article {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 48px 32px 120px;
}
.back-link {
  font-size: 13px;
  color: var(--text-muted);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 24px;
  border-bottom: none;
  transition: color 0.12s;
}
.back-link:hover { color: var(--accent); border-bottom: none; }
.doc-title {
  font-size: 2.2em;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: var(--text);
}
.doc-meta {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 36px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-soft);
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}
.doc-meta code { font-size: 12px; }
.doc-meta .sep { color: var(--text-ghost); }

/* ---------- 折叠节点 — 树形大纲 ---------- */
.outline { padding: 0; margin: 0; list-style: none; }

.section {
  margin: 0;
  padding: 0;
  position: relative;
}

/* 行(标题区) */
.section > summary,
.node-row {
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 8px 7px 0;
  color: var(--text);
  position: relative;
  user-select: none;
  outline: none;
  border-radius: var(--radius-sm);
  transition: background 0.1s, color 0.1s;
}
.section > summary::-webkit-details-marker { display: none; }
.section > summary:hover,
.note-node > summary:hover { background: var(--bg-hover); }
.section > summary:focus-visible,
.note-node > summary:focus-visible {
  box-shadow: 0 0 0 2px var(--accent-glow);
}

/* 折叠图标 */
.caret {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  color: var(--text-faint);
  transition: transform 0.15s ease, color 0.1s;
  font-size: 9px;
  line-height: 1;
}
details[open] > summary > .caret,
.section[open] > summary > .caret {
  transform: rotate(90deg);
  color: var(--text-muted);
}
.section > summary:hover > .caret,
.note-node > summary:hover > .caret { color: var(--text-secondary); }

/* 圆点 — org-mode bullet */
.bullet {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-ghost);
  flex-shrink: 0;
  transition: background 0.12s, transform 0.12s;
  position: relative;
}
.section > summary:hover > .bullet,
.note-node > summary:hover > .bullet { background: var(--accent); }
.section[open] > summary > .bullet { background: var(--text-secondary); }
.note-node[open] > summary > .bullet { background: var(--text-secondary); }

/* 标题文字 */
.heading-text,
.note-node > summary > .title {
  flex: 1;
  min-width: 0;
  color: var(--text);
  text-decoration: none;
  border-bottom: none;
  transition: color 0.12s;
}
.section > summary:hover > .heading-text,
.note-node > summary:hover > .title { color: var(--accent); }

.note-node > summary > .title {
  font-weight: 600;
  font-size: 1.05em;
  letter-spacing: -0.005em;
}

/* 锚点链接 */
.anchor-link {
  opacity: 0;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 11px;
  padding: 2px 6px;
  margin-left: 4px;
  border-radius: var(--radius-sm);
  transition: opacity 0.12s, background 0.12s;
  border-bottom: none;
}
.section > summary:hover > .anchor-link { opacity: 1; }
.anchor-link:hover { background: var(--accent-soft); color: var(--accent); }

/* 元数据(章节计数等) */
.row-meta {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  padding: 2px 8px;
  background: var(--bg-inset);
  border-radius: 10px;
  flex-shrink: 0;
  letter-spacing: 0.01em;
}

/* ---------- 层级字号 ---------- */
.section.level-1 > summary { padding: 12px 8px 12px 0; }
.section.level-1 > summary > .heading-text {
  font-size: 1.35em;
  font-weight: 700;
  letter-spacing: -0.015em;
}
.section.level-1 > summary > .bullet { width: 7px; height: 7px; }

.section.level-2 > summary > .heading-text {
  font-size: 1.1em;
  font-weight: 600;
}
.section.level-2 > summary > .bullet { width: 6px; height: 6px; }

.section.level-3 > summary > .heading-text {
  font-size: 0.98em;
  font-weight: 500;
  color: var(--text-secondary);
}
.section.level-3 > summary > .bullet { width: 5px; height: 5px; }

.section.level-4 > summary,
.section.level-5 > summary,
.section.level-6 > summary { padding: 5px 8px 5px 0; }
.section.level-4 > summary > .heading-text,
.section.level-5 > summary > .heading-text,
.section.level-6 > summary > .heading-text {
  font-size: 0.92em;
  font-weight: 400;
  color: var(--text-secondary);
}
.section.level-4 > summary > .bullet,
.section.level-5 > summary > .bullet,
.section.level-6 > summary > .bullet { width: 4px; height: 4px; }

/* 缩进 — 层级通过 padding-left */
/* 层级缩进由 section-body padding-left 统一负责,这里不再额外加 */

/* 标题前缩进对齐 caret+bullet,使内容左边缘整齐 */
.section > summary {
  position: relative;
}

/* 层级缩进:统一通过 section-body 的 padding-left 实现,每嵌套一层 +16px */
.section-body {
  padding: 6px 0 14px 16px;
  margin-left: 0;
}

/* 折叠动画(用 interpolate-size,现代浏览器支持) */
@supports (interpolate-size: allow-keywords) {
  html { interpolate-size: allow-keywords; }
  .section > .section-body {
    display: grid;
    grid-template-rows: 1fr;
    transition: grid-template-rows 0.2s ease;
  }
  .section:not([open]) > .section-body {
    grid-template-rows: 0fr;
    overflow: hidden;
    padding-top: 0;
    padding-bottom: 0;
  }
  .section-body > * { overflow: hidden; min-height: 0; }
}

/* ---------- 内容样式 ---------- */
.section-body > p { margin: 10px 0; }
.section-body > p:first-child { margin-top: 6px; }
.section-body > p:last-child { margin-bottom: 4px; }

a {
  color: var(--link);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.12s;
}
a:hover {
  color: var(--link-hover);
  border-bottom-color: var(--link-hover);
}

strong, b { font-weight: 650; color: var(--text); }
em, i { font-style: italic; }

ul, ol { margin: 10px 0; padding-left: 24px; }
li { margin: 3px 0; }
li > p { margin: 4px 0; }

hr {
  border: none;
  height: 1px;
  background: var(--border);
  margin: 28px 0;
}

blockquote {
  margin: 12px 0;
  padding: 10px 16px;
  background: var(--quote-bg);
  border-left: 2px solid var(--quote-border);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
  font-size: 0.96em;
}
blockquote p { margin: 4px 0; }

/* 表格 */
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 16px 0;
  font-size: 0.93em;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
thead { background: var(--bg-soft); }
th, td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid var(--border-soft);
  vertical-align: top;
  line-height: 1.6;
}
th {
  font-weight: 600;
  color: var(--text);
  font-size: 0.92em;
  letter-spacing: -0.005em;
  border-bottom: 1px solid var(--border);
}
tbody tr:last-child td { border-bottom: none; }
tbody tr { transition: background 0.08s; }
tbody tr:hover { background: var(--bg-hover); }

/* 行内代码 — 关键修复:无 border,纯净 */
code {
  font-family: var(--font-mono);
  font-size: 0.86em;
  background: var(--code-bg);
  color: var(--code-text);
  padding: 1.5px 5px;
  border-radius: 3px;
  font-feature-settings: "calt" 1, "zero" 1;
  border: none;
}

/* 代码块容器 — 用 highlight.js 做高亮 */
.code-block {
  margin: 18px 0;
  background: #f6f8fa;
  border: 1px solid #e6e8eb;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(15, 15, 30, 0.04);
  position: relative;
}
.code-block + .code-block { margin-top: 18px; }

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px 6px 14px;
  background: rgba(255, 255, 255, 0.55);
  border-bottom: 1px solid #eaecef;
  font-family: var(--font-sans);
  font-size: 11px;
  user-select: none;
}
.code-header .dots {
  display: inline-flex;
  gap: 5px;
  margin-right: 10px;
}
.code-header .dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e1e4e8;
}
.code-lang {
  font-family: var(--font-sans);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  font-size: 10px;
  flex: 1;
  text-align: center;
}
.code-block pre {
  display: block;
  margin: 0;
  padding: 13px 16px;
  background: transparent;
  color: #1f2328;
  border: none;
  border-radius: 0;
  box-shadow: none;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 0.85em;
  line-height: 1.7;
  white-space: pre;
  word-break: normal;
  tab-size: 4;
}
.code-block pre code {
  background: transparent;
  padding: 0;
  border: none;
  color: inherit;
  font-size: 1em;
}
.code-block pre code.hljs {
  background: transparent !important;
  padding: 0 !important;
  color: #1f2328;
}

/* 没被包成 .code-block 的裸 pre(理论上不会出现,留个 fallback) */
pre:not(.code-block pre) {
  display: block;
  margin: 14px 0;
  padding: 13px 16px;
  background: #f6f8fa;
  color: #1f2328;
  border: 1px solid #e6e8eb;
  border-radius: 8px;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 0.85em;
  line-height: 1.7;
  white-space: pre;
  tab-size: 4;
  position: relative;
}

/* 复制按钮(放在 code-header 里,常驻显示) */
.code-copy-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  font-size: 11px;
  font-family: var(--font-sans);
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.12s;
  user-select: none;
  line-height: 1.4;
}
.code-copy-btn:hover {
  background: var(--accent-soft);
  color: var(--accent);
  border-color: var(--accent);
}
.code-copy-btn.copied {
  background: #16a34a;
  color: white;
  border-color: #16a34a;
}
.code-copy-btn:focus-visible {
  box-shadow: 0 0 0 2px var(--accent-glow);
}

/* ---------- 主页:大纲树 ---------- */
.outline-tree {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 8px 32px 120px;
}

.note-node {
  margin: 0;
  padding: 0;
  border-bottom: 1px solid var(--border-soft);
}
.note-node:last-child { border-bottom: none; }

.note-node > summary {
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 8px;
  position: relative;
  user-select: none;
  border-radius: var(--radius-sm);
  transition: background 0.1s;
}
.note-node > summary::-webkit-details-marker { display: none; }
.note-node > summary > .caret {
  width: 16px; height: 16px;
  font-size: 10px;
}
.note-node > summary > .bullet {
  width: 7px; height: 7px;
}
.note-node[open] > summary { padding-bottom: 8px; }
.note-node > summary > .title {
  font-size: 1.1em;
  font-weight: 600;
  letter-spacing: -0.005em;
}
.note-node > summary > .desc {
  flex: 0 1 40%;
  font-size: 0.84em;
  color: var(--text-muted);
  font-weight: 400;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

/* 章节列表(在主页 note-node 展开时显示) */
.note-children {
  padding: 0 0 16px 30px;
  margin: 0;
  list-style: none;
  position: relative;
}
.note-children::before {
  content: "";
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 14px;
  width: 1px;
  background: var(--border);
}
.note-children li { margin: 0; }
.note-children a {
  color: var(--text-secondary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px 5px 14px;
  border-radius: var(--radius-sm);
  transition: all 0.1s;
  border-bottom: none;
  position: relative;
  font-size: 13px;
  line-height: 1.5;
}
.note-children a::before {
  content: "";
  position: absolute;
  left: -3px;
  top: 50%;
  width: 11px;
  height: 1px;
  background: var(--border);
}
.note-children a:hover {
  background: var(--bg-hover);
  color: var(--accent);
  border-bottom: none;
}
.note-children .lvl-2 { font-weight: 600; color: var(--text); font-size: 14px; }
.note-children .lvl-3 { padding-left: 26px; }
.note-children .lvl-4,
.note-children .lvl-5 { padding-left: 38px; color: var(--text-muted); font-size: 12px; }
.note-children .dot {
  display: inline-block;
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--text-faint);
  flex-shrink: 0;
}
.note-children a:hover .dot { background: var(--accent); }

/* 搜索过滤 */
.hidden-by-search { display: none !important; }

/* ---------- 回到顶部 ---------- */
.to-top {
  position: fixed;
  right: 28px;
  bottom: 28px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s;
  box-shadow: var(--shadow-md);
  z-index: 40;
  font-size: 16px;
}
.to-top.visible { opacity: 1; pointer-events: auto; }
.to-top:hover {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
  transform: translateY(-1px);
}

/* ---------- footer ---------- */
footer {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 32px;
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--border-soft);
}
footer a {
  color: var(--link);
  border-bottom: 1px dotted var(--text-muted);
}
footer a:hover { border-bottom-color: var(--accent); }
footer code { font-size: 11px; }

/* ---------- 快捷键提示 ---------- */
.kbd-hints { display: none; }  /* 已废弃,保留以防漏改 */

.help-wrap {
  position: relative;
  display: inline-flex;
}
.help-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 10px 14px;
  box-shadow: var(--shadow-lg);
  font-size: 12px;
  color: var(--text-secondary);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  transition: opacity 0.15s, transform 0.15s, visibility 0.15s;
  z-index: 100;
  font-family: var(--font-sans);
  pointer-events: none;
}
.help-wrap:hover .help-popover,
.help-wrap:focus-within .help-popover,
.help-popover:hover {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}
.help-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
  line-height: 1.5;
}
.help-row + .help-row { border-top: 1px solid var(--border-soft); }
.help-row .keys {
  flex: 0 0 64px;
  display: flex;
  align-items: center;
  gap: 3px;
  color: var(--text-muted);
}
.help-row .desc {
  flex: 1;
  color: var(--text);
}
.help-row kbd {
  display: inline-block;
  padding: 1px 6px;
  background: var(--bg-inset);
  border: 1px solid var(--border);
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text);
}
.help-row .dot-demo {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-faint);
}
.help-row .link-demo {
  color: var(--accent);
  font-weight: 600;
}
.help-btn {
  font-weight: 700;
}
.help-btn:hover {
  color: var(--accent);
}

/* ---------- 响应式 ---------- */
@media (max-width: 720px) {
  body { font-size: 14px; }
  .hero { padding: 16px 20px 4px; }
  .hero .title { font-size: 1.7em; }
  .hero .stats { gap: 20px; flex-wrap: wrap; }
  article, .outline-tree { padding: 24px 18px 80px; }
  .section.level-1 > summary > .heading-text { font-size: 1.2em; }
  .section.level-2 > summary > .heading-text { font-size: 1em; }
  .note-node > summary > .desc { display: none; }
  .note-children { padding-left: 22px; }
  .note-children .lvl-3 { padding-left: 18px; }
  table { font-size: 0.85em; }
  th, td { padding: 8px 10px; }
  .topbar { padding: 10px 16px; flex-wrap: wrap; gap: 8px; }
  .topbar .search { flex: 1 1 100%; order: 10; }
  .kbd-hints { padding: 0 18px 24px; font-size: 11px; }
}

@media print {
  body { background: white; }
  .topbar, .to-top, .progress-bar, .kbd-hints { display: none; }
  .section-body { padding-left: 0 !important; }
  details > .section-body { display: block !important; }
  .section { padding-left: 0 !important; }
}

::selection { background: var(--accent-glow); color: var(--text); }

/* ---------- 滚动条 ---------- */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) transparent;
}
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 8px;
  border: 2px solid transparent;
  background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
  background-clip: content-box;
}
::-webkit-scrollbar-corner {
  background: transparent;
}
/* 代码块水平滚动条更细 */
.code-block pre::-webkit-scrollbar,
pre::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}
.code-block pre::-webkit-scrollbar-thumb,
pre::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  background-clip: content-box;
}
"""

# ============================================================================
# 交互 JS — org 操作 + 幕布视觉
# ============================================================================
NOTE_JS = r"""
(function() {
  'use strict';

  /* ---------- 阅读进度条 ---------- */
  const bar = document.querySelector('.progress-bar');
  function updateProgress() {
    if (!bar) return;
    const h = document.documentElement;
    const total = h.scrollHeight - h.clientHeight;
    bar.style.width = (total > 0 ? h.scrollTop / total * 100 : 0) + '%';
  }
  document.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  /* ---------- 回到顶部 ---------- */
  const toTop = document.querySelector('.to-top');
  if (toTop) {
    window.addEventListener('scroll', () => {
      toTop.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  /* ---------- 全局折叠/展开(单 toggle 按钮) ---------- */
  const foldBtn = document.querySelector('[data-action="toggle-fold"]');
  function syncFoldBtnState() {
    if (!foldBtn) return;
    const all = document.querySelectorAll('details');
    if (!all.length) return;
    const open = Array.from(all).filter(d => d.open).length;
    const expanded = open >= all.length / 2;
    foldBtn.dataset.state = expanded ? 'expanded' : 'folded';
    foldBtn.innerHTML = expanded
      ? '<span class="chev">▾</span>折叠'
      : '<span class="chev">▾</span>展开';
    foldBtn.setAttribute('aria-label', expanded ? '折叠全部' : '展开全部');
  }
  if (foldBtn) {
    foldBtn.addEventListener('click', () => {
      const all = document.querySelectorAll('details');
      const open = Array.from(all).filter(d => d.open).length;
      const expanded = open >= all.length / 2;
      all.forEach(d => { d.open = !expanded; });
      syncFoldBtnState();
    });
    // 用户手动折叠/展开后,标签也跟着更新
    document.querySelectorAll('details').forEach(d => {
      d.addEventListener('toggle', syncFoldBtnState);
    });
    syncFoldBtnState();
  }

  /* ---------- 代码块:包成 .code-block + header(语言徽章 + 复制按钮) ---------- */
  async function copyCode(text, btn) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.cssText = 'position:fixed;opacity:0;';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      const old = btn.textContent;
      btn.textContent = '已复制';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = old;
        btn.classList.remove('copied');
      }, 1500);
    } catch (err) {
      btn.textContent = '失败';
      setTimeout(() => { btn.textContent = '复制'; }, 1500);
    }
  }

  document.querySelectorAll('pre').forEach(pre => {
    if (pre.closest('.code-block')) return;  // 已包装
    const code = pre.querySelector('code');
    let lang = '';
    if (code) {
      const m = (code.className || '').match(/language-([\w+-]+)/);
      if (m) lang = m[1];
    }

    const wrap = document.createElement('div');
    wrap.className = 'code-block';

    const header = document.createElement('div');
    header.className = 'code-header';
    header.innerHTML = '<span class="dots"><span></span><span></span><span></span></span>'
                     + '<span class="code-lang">' + (lang || 'text') + '</span>';

    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.type = 'button';
    btn.textContent = '复制';
    btn.setAttribute('aria-label', '复制代码');
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const text = (code ? code.textContent : pre.textContent) || '';
      copyCode(text, btn);
    });
    header.appendChild(btn);

    pre.parentElement.insertBefore(wrap, pre);
    wrap.appendChild(header);
    wrap.appendChild(pre);
  });

  /* ---------- localStorage 记忆折叠 ---------- */
  const noteId = document.body.getAttribute('data-note-id');
  if (noteId) {
    const KEY = 'md2html:state:' + noteId;
    const saved = (() => { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch { return {}; } })();
    document.querySelectorAll('details.section').forEach((d) => {
      const id = d.getAttribute('data-anchor');
      if (!id) return;
      if (saved[id] === false) d.open = false;
      else if (saved[id] === true) d.open = true;
    });
    document.querySelectorAll('details.section').forEach((d) => {
      const id = d.getAttribute('data-anchor');
      if (!id) return;
      d.addEventListener('toggle', () => {
        saved[id] = d.open;
        try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch {}
      });
    });
  }

  /* ---------- org-mode 键盘:Tab / Shift+Tab / J K ---------- */
  const isHeading = (el) => el && el.matches && el.matches('summary');
  const allHeadings = () => Array.from(document.querySelectorAll('details.section > summary, details.note-node > summary'));

  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, textarea')) return;
    const meta = e.metaKey || e.ctrlKey;

    // / 聚焦搜索
    if (e.key === '/' && !meta) {
      const s = document.querySelector('input.search');
      if (s) { e.preventDefault(); s.focus(); return; }
    }

    // Tab / Shift+Tab 折叠当前聚焦的 summary
    if (e.key === 'Tab') {
      const f = document.activeElement;
      if (isHeading(f)) {
        e.preventDefault();
        const d = f.parentElement;
        if (e.shiftKey) {
          // Shift+Tab: 全局折叠/展开所有
          const all = document.querySelectorAll('details');
          const allOpen = Array.from(all).every(x => x.open);
          all.forEach(x => { x.open = !allOpen; });
        } else {
          // Tab: 折叠/展开当前节点
          d.open = !d.open;
        }
        return;
      }
    }

    // J/K 或 ↓/↑ 跳转标题 — 已移除(行为不一致,容易让用户迷惑)

    // Enter: 在 note-node 上是跟随标题链接;在 section 上是 toggle
    if (e.key === 'Enter') {
      const f = document.activeElement;
      if (isHeading(f)) {
        const titleLink = f.querySelector('.title, .heading-text');
        if (titleLink && titleLink.tagName === 'A') {
          e.preventDefault();
          titleLink.click();
        }
      }
    }
  });

  /* ---------- 点击 caret 只 toggle,不让 summary 的默认 toggle 干扰; 点击 title 跟随链接 ---------- */
  // 默认浏览器:点 summary 任意位置都会 toggle,点 <a> 会先 toggle 再 navigate。
  // 我们让 title 链接的 click 阻止冒泡,避免 toggle 副作用(navigate 后虽然看不到,但保证一致性)。
  document.querySelectorAll('details.note-node > summary > .title').forEach(link => {
    if (link.tagName !== 'A') return;
    link.addEventListener('click', (e) => {
      e.stopPropagation();
      // 让浏览器默认行为(navigate)发生
    });
  });
  // caret 点击:默认也会 toggle,不用特殊处理

  /* ---------- 搜索 ---------- */
  const search = document.querySelector('input.search');
  if (search && document.body.classList.contains('page-index')) {
    search.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      const nodes = document.querySelectorAll('.note-node');
      nodes.forEach(node => {
        if (!q) {
          node.classList.remove('hidden-by-search');
          node.querySelectorAll('li').forEach(li => li.classList.remove('hidden-by-search'));
          return;
        }
        const nodeText = node.textContent.toLowerCase();
        if (!nodeText.includes(q)) {
          node.classList.add('hidden-by-search');
          return;
        }
        node.classList.remove('hidden-by-search');
        let anyMatch = false;
        node.querySelectorAll('li').forEach(li => {
          const t = li.textContent.toLowerCase();
          if (t.includes(q)) {
            li.classList.remove('hidden-by-search');
            anyMatch = true;
          } else {
            li.classList.add('hidden-by-search');
          }
        });
        if (anyMatch) node.open = true;
      });
    });
  }
  if (search && document.body.classList.contains('page-note')) {
    search.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      document.querySelectorAll('details.section').forEach(s => {
        if (!q) { s.style.opacity = ''; s.open = s.getAttribute('data-was-open') === '1'; return; }
        const t = s.querySelector('summary').textContent.toLowerCase();
        s.style.opacity = t.includes(q) ? '1' : '0.3';
      });
    });
  }
})();
"""

# ============================================================================
# Markdown → HTML body
# ============================================================================

def md_to_html_body(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=['extra', 'toc', 'sane_lists', 'admonition'],
        extension_configs={
            'toc': {
                'title': '',
                'baselevel': 1,
                'permalink': '¶',
            },
        },
    )
    return md.convert(md_text)


def slugify(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^\w\s一-鿿-]', '', text, flags=re.UNICODE)
    text = re.sub(r'\s+', '-', text.strip().lower())
    return text or 'section'


class Section:
    __slots__ = ('level', 'heading', 'content', 'children')
    def __init__(self, level: int, heading: Tag | None = None):
        self.level = level
        self.heading = heading
        self.content: list = []
        self.children: list[Section] = []


def build_section_tree(parent) -> Section:
    root = Section(0)
    stack: list[Section] = [root]
    for el in parent.children:
        if isinstance(el, NavigableString):
            if str(el).strip():
                stack[-1].content.append(el)
            continue
        if not isinstance(el, Tag):
            continue
        m = re.fullmatch(r'h([1-6])', el.name or '')
        if m:
            level = int(m.group(1))
            while stack and stack[-1].level >= level:
                stack.pop()
            parent_sec = stack[-1] if stack else root
            sec = Section(level, el)
            parent_sec.children.append(sec)
            stack.append(sec)
        else:
            stack[-1].content.append(el)
    return root


def render_section(sec: Section) -> str:
    if sec.level == 0:
        parts = [str(el) for el in sec.content]
        for c in sec.children:
            parts.append(render_section(c))
        return '\n'.join(parts)

    heading = sec.heading
    anchor = heading.get('id') if heading else ''
    text_html = ''.join(str(c) for c in heading.children) if heading else ''
    text_html = re.sub(r'<a class="headerlink"[^>]*>.*?</a>', '', text_html)

    body_parts = [str(el) for el in sec.content]
    for c in sec.children:
        body_parts.append(render_section(c))
    body_html = '\n'.join(body_parts)

    return (
        f'<details class="section level-{sec.level}" open data-anchor="{escape(anchor)}">\n'
        f'  <summary id="{escape(anchor)}" tabindex="0">\n'
        f'    <span class="caret" aria-hidden="true">▶</span>'
        f'<span class="bullet" aria-hidden="true"></span>'
        f'<span class="heading-text">{text_html}</span>'
        f'<a class="anchor-link" href="#{escape(anchor)}" title="复制链接">§</a>\n'
        f'  </summary>\n'
        f'  <div class="section-body">\n{body_html}\n  </div>\n'
        f'</details>'
    )


def build_note_html(stem: str, md_path: Path) -> tuple[str, dict]:
    md_text = md_path.read_text(encoding='utf-8')
    body_html = md_to_html_body(md_text)
    soup = BeautifulSoup(body_html, 'html.parser')

    h1 = soup.find('h1')
    title = stem  # 默认 fallback 到文件名
    if h1:
        for a in h1.find_all('a', class_='headerlink'):
            a.decompose()
        h1_text = h1.get_text(strip=True)
        if h1_text:
            title = h1_text
        h1.decompose()  # 总是移除首个 H1(标题已在 doc-title 显示)
    title = re.sub(r'\s*¶\s*$', '', title)

    first_p = soup.find('p')
    description = ''
    if first_p:
        d = ' '.join(first_p.get_text(strip=True).split())
        if d:
            description = (d[:160] + '…') if len(d) > 160 else d

    tree = build_section_tree(soup)
    body_rendered = render_section(tree)

    sections_meta = []
    def collect(sec):
        for c in sec.children:
            anchor = c.heading.get('id') if c.heading else ''
            t = c.heading.get_text(strip=True) if c.heading else ''
            t = re.sub(r'\s*¶\s*$', '', t)
            sections_meta.append({'level': c.level, 'title': t, 'anchor': anchor})
            collect(c)
    collect(tree)

    today = date.today().isoformat()
    html = NOTE_TEMPLATE.format(
        title=escape(title),
        body=body_rendered,
        css=THEME_CSS,
        js=NOTE_JS,
        note_id=escape(stem),
        source=escape(md_path.name),
        author=escape(SITE_AUTHOR),
        today=today,
        site_title=escape(SITE_TITLE),
        site_subtitle=escape(SITE_SUBTITLE),
        section_count=len(sections_meta),
    )

    meta = {
        'filename': stem + '.html',
        'source': md_path.name,
        'title': title,
        'description': description,
        'sections': sections_meta,
        'section_count': len(sections_meta),
    }
    return html, meta


NOTE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {site_title}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" referrerpolicy="no-referrer">
<style>
{css}
</style>
</head>
<body class="page-note" data-note-id="{note_id}">
<div class="progress-bar"></div>
<div class="topbar">
  <a class="brand" href="index.html"><span class="seal">造</span> {site_title}</a>
  <span class="spacer"></span>
  <input type="search" class="search" placeholder="搜索章节 (按 / 聚焦)" autocomplete="off">
  <div class="help-wrap">
    <button class="help-btn icon" aria-label="快捷键">?</button>
    <div class="help-popover">
      <div class="help-row"><span class="keys"><kbd>Tab</kbd></span><span class="desc">折叠当前</span></div>
      <div class="help-row"><span class="keys"><kbd>Shift</kbd>+<kbd>Tab</kbd></span><span class="desc">全局折叠</span></div>
      <div class="help-row"><span class="keys"><kbd>/</kbd></span><span class="desc">搜索</span></div>
      <div class="help-row"><span class="keys"><span class="dot-demo"></span></span><span class="desc">点击圆点折叠</span></div>
    </div>
  </div>
  <button data-action="toggle-fold" data-state="expanded"><span class="chev">▾</span>折叠</button>
</div>
<article>
  <h1 class="doc-title">{title}</h1>
  <div class="doc-meta">
    <span>{section_count} 章</span>
    <span class="sep">·</span>
    <span>更新 {today}</span>
  </div>
{body}
</article>
<button class="to-top" aria-label="回到顶部">↑</button>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" referrerpolicy="no-referrer"></script>
<script>
hljs.highlightAll();
{js}
</script>
</body>
</html>
"""


# ============================================================================
# Index
# ============================================================================

def render_section_list_for_index(meta: dict) -> str:
    sections = meta['sections']
    if not sections:
        return '<p style="color: var(--text-muted); padding: 8px 0; font-size: 13px;">(无章节)</p>'
    items = []
    for s in sections:
        lvl = max(2, min(5, s['level']))
        items.append(
            f'<li><a class="lvl-{lvl}" href="{escape(meta["filename"])}#{escape(s["anchor"])}">'
            f'<span class="dot"></span>{escape(s["title"])}</a></li>'
        )
    return '<ul class="note-children">' + '\n'.join(items) + '</ul>'


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{site_title}</title>
<style>
{css}
</style>
</head>
<body class="page-index">
<div class="progress-bar"></div>
<div class="topbar">
  <a class="brand" href="#"><span class="seal">S</span> {site_title}</a>
  <span class="spacer"></span>
  <input type="search" class="search" placeholder="搜索笔记或章节 (按 / 聚焦)" autocomplete="off">
  <div class="help-wrap">
    <button class="help-btn icon" aria-label="快捷键">?</button>
    <div class="help-popover">
      <div class="help-row"><span class="keys"><kbd>Tab</kbd></span><span class="desc">折叠当前</span></div>
      <div class="help-row"><span class="keys"><kbd>Shift</kbd>+<kbd>Tab</kbd></span><span class="desc">全局折叠</span></div>
      <div class="help-row"><span class="keys"><kbd>/</kbd></span><span class="desc">搜索</span></div>
      <div class="help-row"><span class="keys"><span class="dot-demo"></span></span><span class="desc">点击圆点折叠</span></div>
      <div class="help-row"><span class="keys"><span class="link-demo">T</span></span><span class="desc">点击标题进入</span></div>
    </div>
  </div>
  <button data-action="toggle-fold" data-state="expanded"><span class="chev">▾</span>折叠</button>
</div>
<header class="hero">
  <h1 class="title">{site_title}</h1>
  <p class="subtitle">{site_subtitle}</p>
</header>
<main class="outline-tree">
{nodes}
</main>
<button class="to-top" aria-label="回到顶部">↑</button>
<script>
{js}
</script>
</body>
</html>
"""


def build_note_node_html(meta: dict) -> str:
    """生成单个 note-node 的 HTML 片段(供增量更新用)"""
    children_html = render_section_list_for_index(meta)
    desc = escape(meta.get('description') or '(无描述)')
    kind_badge = ''
    if meta.get('kind') == 'html':
        kind_badge = '<span class="row-meta" style="background:transparent;color:var(--text-muted);" title="关联的现成 HTML">html</span>'
    return f'''<details class="note-node">
  <summary tabindex="0">
    <span class="caret" aria-hidden="true">▶</span>
    <span class="bullet" aria-hidden="true"></span>
    <a class="title" href="{escape(meta["filename"])}">{escape(meta["title"])}</a>
    <span class="desc">{desc}</span>
    {kind_badge if kind_badge else ''}
    <span class="row-meta">{meta["section_count"]} 章</span>
  </summary>
  {children_html}
</details>'''


def build_index_html(notes_meta: list[dict]) -> str:
    nodes = [build_note_node_html(m) for m in notes_meta]
    return INDEX_TEMPLATE.format(
        site_title=escape(SITE_TITLE),
        site_subtitle=escape(SITE_SUBTITLE),
        nodes='\n'.join(nodes),
        css=THEME_CSS,
        js=NOTE_JS,
    )


def _find_note_node(soup, filename: str):
    """在 index.html 的 BeautifulSoup 树里按 filename 找 note-node"""
    for node in soup.find_all('details', class_='note-node'):
        link = node.find('a', class_='title')
        if link and link.get('href') == filename:
            return node
    return None


def update_index_add(meta: dict, index_path: Path) -> str:
    """向 index.html 增量添加/更新一篇笔记。
    如果 index.html 不存在或解析失败,返回 'rebuilt' 表示走了全量重建路径。
    """
    if not index_path.exists():
        return 'rebuilt'
    try:
        soup = BeautifulSoup(index_path.read_text(encoding='utf-8'), 'html.parser')
    except Exception:
        return 'rebuilt'

    outline = soup.find('main', class_='outline-tree')
    if outline is None:
        return 'rebuilt'

    new_node_html = build_note_node_html(meta)
    new_node = BeautifulSoup(new_node_html, 'html.parser').find('details')

    existing = _find_note_node(soup, meta['filename'])
    if existing:
        existing.replace_with(new_node)
        action = 'updated'
    else:
        outline.append(new_node)
        action = 'added'

    index_path.write_text(str(soup), encoding='utf-8')
    return action


def update_index_delete(filename: str, index_path: Path) -> str:
    """从 index.html 增量删除一篇笔记。
    返回 'deleted' / 'not_found' / 'rebuilt'."""
    if not index_path.exists():
        return 'rebuilt'
    try:
        soup = BeautifulSoup(index_path.read_text(encoding='utf-8'), 'html.parser')
    except Exception:
        return 'rebuilt'

    node = _find_note_node(soup, filename)
    if node is None:
        return 'not_found'
    node.decompose()
    index_path.write_text(str(soup), encoding='utf-8')
    return 'deleted'


# ============================================================================
# 元数据抽取(轻量,用于 list / search / delete)
# ============================================================================

def get_metadata(md_path: Path) -> dict:
    """读取 .md,只返回元数据(不写 HTML)"""
    md_text = md_path.read_text(encoding='utf-8')
    body = md_to_html_body(md_text)
    soup = BeautifulSoup(body, 'html.parser')

    h1 = soup.find('h1')
    title = md_path.stem  # 默认 fallback 到文件名
    if h1:
        for a in h1.find_all('a', class_='headerlink'):
            a.decompose()
        h1_text = h1.get_text(strip=True)
        if h1_text:
            title = h1_text
    title = re.sub(r'\s*¶\s*$', '', title)

    first_p = soup.find('p')
    desc = ''
    if first_p:
        d = ' '.join(first_p.get_text(strip=True).split())
        if d:
            desc = (d[:160] + '…') if len(d) > 160 else d

    sections = []
    for h in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        for a in h.find_all('a', class_='headerlink'):
            a.decompose()
        sections.append({
            'level': int(h.name[1]),
            'title': re.sub(r'\s*¶\s*$', '', h.get_text(strip=True)),
            'anchor': h.get('id', ''),
        })

    return {
        'filename': md_path.stem + '.html',
        'source': md_path.name,
        'stem': md_path.stem,
        'kind': 'md',
        'title': title,
        'description': desc,
        'sections': sections,
        'section_count': len(sections),
    }


def get_metadata_from_html(html_path: Path) -> dict:
    """从已有 HTML 文件提取元数据(关联现成 HTML 时使用)"""
    html = html_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # 标题优先级:<h1 class="doc-title"> → <h1> → <title> → 文件名
    h1 = soup.find('h1', class_='doc-title') or soup.find('h1')
    if h1:
        for a in h1.find_all('a', class_='headerlink'):
            a.decompose()
        title = h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
        title = re.sub(r'\s*[—-]\s*.*$', '', title)  # 去掉 " — Site" 后缀
    else:
        title = html_path.stem
    title = re.sub(r'\s*¶\s*$', '', title)

    # 描述:第一段
    first_p = soup.find('p')
    desc = ''
    if first_p:
        d = ' '.join(first_p.get_text(strip=True).split())
        desc = (d[:160] + '…') if len(d) > 160 else d

    # 章节:h2-h6
    sections = []
    for h in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        sections.append({
            'level': int(h.name[1]),
            'title': h.get_text(strip=True),
            'anchor': h.get('id', ''),
        })

    return {
        'filename': html_path.name,
        'source': html_path.name,
        'stem': html_path.stem,
        'kind': 'html',
        'title': title,
        'description': desc,
        'sections': sections,
        'section_count': len(sections),
    }


def scan_notes(dir_path: Path) -> list[dict]:
    """扫描目录下所有 .md 和孤立 .html,返回 metadata 列表"""
    md_files = sorted(dir_path.glob('*.md'))
    html_files = sorted(dir_path.glob('*.html'))

    metas = []
    md_stems = {f.stem for f in md_files}

    for f in md_files:
        metas.append(get_metadata(f))

    # 关联孤立 HTML(没有对应 .md 的)
    for f in html_files:
        if f.name == 'index.html':
            continue
        if f.stem in md_stems:
            continue  # 已经由 .md 覆盖
        try:
            metas.append(get_metadata_from_html(f))
        except Exception as e:
            print(f'  ⚠ 跳过 {f.name}: {e}', file=sys.stderr)

    # 按标题排序(中文按拼音走系统 locale)
    metas.sort(key=lambda m: m['title'])
    return metas


def regenerate_index(dir_path: Path) -> int:
    """重新生成 index.html,返回笔记数"""
    metas = scan_notes(dir_path)
    (dir_path / 'index.html').write_text(build_index_html(metas), encoding='utf-8')
    return len(metas)


def match_note(query: str, metas: list[dict]) -> tuple[dict | None, list[dict]]:
    """按 stem / 文件名 / 标题 / 子串 匹配笔记。

    返回 (definitive_match, candidates):
      - definitive_match: 唯一命中则返回该 dict;多个或无命中返回 None
      - candidates: 该层级所有命中,供调用方在歧义时列出
    """
    q = query.strip()

    # 1) stem 完全匹配(每个 stem 在目录里唯一)
    for m in metas:
        if m['stem'] == q:
            return m, [m]

    # 2) 文件名 / HTML 名匹配(文件名也唯一)
    for m in metas:
        if m['source'] == q or m['filename'] == q:
            return m, [m]

    # 3) 标题完全匹配(可能多篇同标题)
    title_matches = [m for m in metas if m['title'] == q]
    if title_matches:
        if len(title_matches) == 1:
            return title_matches[0], title_matches
        return None, title_matches

    # 4) 标题或 stem 子串包含(可能多个)
    ql = q.lower()
    substr_matches = [m for m in metas
                      if ql in m['title'].lower() or ql in m['stem'].lower()]
    if substr_matches:
        if len(substr_matches) == 1:
            return substr_matches[0], substr_matches
        return None, substr_matches

    return None, []


def _print_candidates(query: str, candidates: list[dict], file=sys.stderr):
    """列出候选供用户挑选"""
    print(f'  ✗ "{query}" 匹配到 {len(candidates)} 篇,请用更精确的名字:',
          file=file)
    for c in candidates:
        kind = c.get('kind', 'md')
        print(f'      • {c["title"]}  [{kind}]  ({c["source"]})', file=file)


# ============================================================================
# 子命令实现
# ============================================================================

def cmd_list(args) -> int:
    d = Path(args.dir).resolve()
    metas = scan_notes(d)
    if not metas:
        print(f'(空) {d} 下没有 .md 文件')
        return 0
    print(f'共 {len(metas)} 篇笔记\n')
    if args.sections:
        for m in metas:
            print(f'■ {m["title"]}  ({m["section_count"]} 章 · {m["source"]})')
            for s in m['sections']:
                indent = '  ' * (s['level'] - 1)
                mark = '◆' if s['level'] == 2 else '·'
                print(f'    {indent}{mark} {s["title"]}')
            print()
    else:
        # 表格对齐
        title_w = max(len(m['title']) for m in metas)
        for m in metas:
            kind_tag = 'md' if m.get('kind') == 'md' else 'html'
            print(f'  {m["title"].ljust(title_w)}  {m["section_count"]:>3} 章  [{kind_tag}]  {m["source"]}')
    return 0


def cmd_search(args) -> int:
    d = Path(args.dir).resolve()
    metas = scan_notes(d)
    q = args.query.lower()
    matches = []
    for m in metas:
        if q in m['title'].lower():
            matches.append((m, None))
        for s in m['sections']:
            if q in s['title'].lower():
                matches.append((m, s))
    if not matches:
        print(f'未找到匹配 "{args.query}" 的笔记或章节')
        return 1
    print(f'找到 {len(matches)} 处匹配 "{args.query}":\n')
    last_note = None
    for m, s in matches:
        if m['title'] != last_note:
            print(f'[{m["title"]}]  ({m["filename"]})')
            last_note = m['title']
        if s:
            indent = '  ' * (s['level'] - 1)
            print(f'    {indent}→ {s["title"]}  ({m["filename"]}#{s["anchor"]})')
        else:
            print(f'    → (标题匹配)')
    return 0


def cmd_add(args) -> int:
    d = Path(args.dir).resolve() if args.dir else Path('.').resolve()
    index_path = d / 'index.html'
    added = []
    for f in args.files:
        fp = Path(f)
        if not fp.exists():
            print(f'  ✗ {f} 不存在', file=sys.stderr)
            continue
        # 如果不在当前目录,复制过来
        target = d / fp.name
        if fp.resolve() != target.resolve():
            target.write_text(fp.read_text(encoding='utf-8'), encoding='utf-8')
            fp = target
        suffix = fp.suffix.lower()
        if suffix == '.md':
            meta = convert_one(fp, force=False)
        elif suffix in ('.html', '.htm'):
            print(f'  ✓ 关联 HTML: {fp.name}')
            meta = get_metadata_from_html(fp)
        else:
            print(f'  ✗ 不支持的文件类型: {fp.name}(只支持 .md / .html)', file=sys.stderr)
            continue
        # 增量更新 index.html
        action = update_index_add(meta, index_path)
        if action == 'rebuilt':
            n = regenerate_index(d)
            print(f'  ✓ index.html 全量重建({n} 篇笔记)')
        else:
            print(f'  ✓ index.html 增量{action}: {meta["filename"]}')
        added.append(fp.name)
    return 0 if added else 1


def cmd_delete(args) -> int:
    d = Path(args.dir).resolve()
    index_path = d / 'index.html'
    metas = scan_notes(d)
    deleted = []
    had_failure = False
    for name in args.names:
        m, candidates = match_note(name, metas)
        if not candidates:
            print(f'  ✗ 未找到 "{name}"', file=sys.stderr)
            had_failure = True
            continue
        if m is None:
            _print_candidates(name, candidates)
            had_failure = True
            continue
        html_path = d / m['filename']
        md_path = d / m['source']
        if html_path.exists():
            html_path.unlink()
            print(f'  ✓ 删除 HTML: {m["filename"]}')
        if args.purge:
            if md_path.exists() and md_path != html_path:
                md_path.unlink()
                print(f'  ✓ 删除源 MD: {m["source"]}')
        else:
            if m.get('kind') == 'md':
                print(f'    (源 .md 未删除,如需同时删除加 --purge)')
        # 增量更新 index.html
        action = update_index_delete(m['filename'], index_path)
        if action == 'rebuilt':
            n = regenerate_index(d)
            print(f'  ✓ index.html 全量重建({n} 篇笔记)')
        elif action == 'deleted':
            print(f'  ✓ index.html 增量删除: {m["filename"]}')
        deleted.append(m['filename'])
        metas = [x for x in metas if x['filename'] != m['filename']]
    return 0 if not had_failure else 1


def cmd_show(args) -> int:
    d = Path(args.dir).resolve()
    metas = scan_notes(d)
    m = match_note(args.name, metas)
    if not m:
        print(f'未找到 "{args.name}"', file=sys.stderr)
        return 1
    print(f'标题:   {m["title"]}')
    print(f'文件:   {m["source"]} → {m["filename"]}')
    print(f'章节:   {m["section_count"]}')
    print(f'描述:   {m["description"] or "(无)"}')
    print(f'\n章节列表:')
    for s in m['sections']:
        indent = '  ' * (s['level'] - 1)
        mark = '◆' if s['level'] == 2 else '·'
        print(f'  {indent}{mark} {s["title"]}')
        print(f'  {indent}  → {m["filename"]}#{s["anchor"]}')
    return 0


# ============================================================================
# CLI
# ============================================================================

def convert_one(md_path: Path, force: bool = False) -> dict:
    """转换单个文件,生成同名 .html,返回 metadata。
    force=False 时按 mtime 跳过未变化的(保护用户对 HTML 的手改)。
    """
    stem = md_path.stem
    html_path = md_path.parent / (stem + '.html')
    if not force and html_path.exists():
        try:
            if md_path.stat().st_mtime <= html_path.stat().st_mtime:
                print(f'  · {md_path.name} 未变化,跳过(HTML 已是最新)')
                return get_metadata(md_path)
        except OSError:
            pass
    html, meta = build_note_html(stem, md_path)
    html_path.write_text(html, encoding='utf-8')
    print(f'  ✓ {md_path.name} → {html_path.name}')
    return meta


def _build_subparsers():
    p = argparse.ArgumentParser(
        description='Markdown → 幕布风折叠大纲 HTML(支持 CRUD)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest='cmd', metavar='COMMAND')

    def add_dir(sp):
        sp.add_argument('--dir', default='.', help='目录(默认当前目录)')

    p_list = sub.add_parser('list', aliases=['ls'], help='列出所有笔记')
    p_list.add_argument('--sections', action='store_true', help='显示每篇的章节')
    add_dir(p_list)

    p_search = sub.add_parser('search', aliases=['find'], help='搜索笔记或章节')
    p_search.add_argument('query', help='搜索关键词')
    add_dir(p_search)

    p_add = sub.add_parser('add', help='添加 .md / .html 笔记(.md 转换,.html 直接关联)')
    p_add.add_argument('files', nargs='+', help='.md 或 .html 文件路径(可多个)')
    add_dir(p_add)

    p_del = sub.add_parser('delete', aliases=['rm'], help='删除笔记 HTML(可选删除源 MD)')
    p_del.add_argument('names', nargs='+', help='笔记名(stem / 文件名 / 标题,可多个)')
    p_del.add_argument('--purge', action='store_true', help='同时删除源 .md 文件')
    add_dir(p_del)

    p_show = sub.add_parser('show', help='查看单篇笔记详情')
    p_show.add_argument('name', help='笔记名(stem / 文件名 / 标题)')
    add_dir(p_show)

    p_batch = sub.add_parser('batch', help='批量重建所有 .md + index.html')
    add_dir(p_batch)

    p_conv = sub.add_parser('convert', help='转换单个或多个 .md(不更新主页)')
    p_conv.add_argument('files', nargs='+')

    return p, sub


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    KNOWN = {'list', 'ls', 'search', 'find', 'add', 'delete', 'rm', 'show',
             'batch', 'convert'}

    if argv and argv[0] in KNOWN:
        p, _ = _build_subparsers()
        args = p.parse_args(argv)
        if args.cmd in ('list', 'ls'):
            return cmd_list(args)
        if args.cmd in ('search', 'find'):
            return cmd_search(args)
        if args.cmd == 'add':
            return cmd_add(args)
        if args.cmd in ('delete', 'rm'):
            return cmd_delete(args)
        if args.cmd == 'show':
            return cmd_show(args)
        if args.cmd == 'batch':
            d = Path(args.dir).resolve()
            md_files = sorted(d.glob('*.md'))
            if not md_files:
                print(f'未在 {d} 找到 .md 文件', file=sys.stderr)
                return 1
            print(f'转换 {len(md_files)} 个 markdown 文件...')
            for f in md_files:
                convert_one(f, force=True)
            n = regenerate_index(d)
            print(f'  ✓ index.html 已生成({n} 篇笔记)')
            return 0
        if args.cmd == 'convert':
            for f in args.files:
                fp = Path(f)
                if not fp.exists():
                    print(f'文件不存在: {f}', file=sys.stderr)
                    return 1
                convert_one(fp, force=False)
            return 0
        p.print_help()
        return 1

    # Legacy 兼容:--batch 或裸文件
    p = argparse.ArgumentParser(
        description='Markdown → 幕布风折叠大纲 HTML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('files', nargs='*', help='.md 文件路径')
    p.add_argument('--batch', action='store_true', help='批量转换目录下所有 .md 并生成 index.html')
    p.add_argument('--dir', default='.', help='批量模式的目录(默认当前目录)')
    args = p.parse_args(argv)

    if args.batch:
        d = Path(args.dir).resolve()
        md_files = sorted(d.glob('*.md'))
        if not md_files:
            print(f'未在 {d} 找到 .md 文件', file=sys.stderr)
            return 1
        print(f'转换 {len(md_files)} 个 markdown 文件...')
        for f in md_files:
            convert_one(f, force=True)
        n = regenerate_index(d)
        print(f'  ✓ index.html 已生成({n} 篇笔记)')
        return 0

    if args.files:
        for f in args.files:
            fp = Path(f)
            if not fp.exists():
                print(f'文件不存在: {f}', file=sys.stderr)
                return 1
            convert_one(fp, force=False)
        return 0

    # 没有参数:显示帮助
    p, _ = _build_subparsers()
    p.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
