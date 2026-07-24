<div align="center">

# BatchRenamerTool v1.0

**[English](#english)** | **[中文](#中文)**

</div>

---

<a id="english"></a>
## English

A lightweight Windows desktop tool for batch renaming files. Portable — no installation required. It supports multiple renaming strategies, a full preview-before-apply workflow, one-click undo, light/dark themes, and 7 UI languages.

### Download & Run

1. Download the zip from the [Releases](../../releases) page (or, if you're already looking at this inside an unzipped release folder, skip to step 3).
2. Unzip it anywhere (e.g. Desktop, `D:\Tools`, a USB drive — no installer, no admin rights needed).
3. Double-click `BatchRenamerTool v1.0.exe` to launch.

That's it — the app is fully portable. To move it to another PC, just copy the whole unzipped folder.

**System requirements:** Windows 10/11 (64-bit). No other software needed.

> **Note on antivirus warnings:** Because this exe is built with PyInstaller and isn't code-signed, Windows Defender or some antivirus tools may flag it as unrecognized/suspicious on first run — a common false positive for small, unsigned Python-based executables. The full source is in this repository if you'd like to verify it yourself. If your antivirus blocks it, you may need to allow it or add an exclusion.

### Features

- **Four renaming modes**
  - **Number Rename** — add a numeric prefix/suffix, extract and renumber an existing digit group, restrict to a specific old-number range, zero-padding, and reverse ordering.
  - **Order Rename** — renumber files in natural (name-aware) sort order with a custom prefix/suffix, start number, and zero-padding.
  - **Time Rename** — renumber files sorted by last-modified time.
  - **Find & Replace** — plain-text or regular-expression search/replace across file names.
- **Preview before you commit** — every mode generates a full old-name → new-name preview table before any file on disk is touched.
- **Safe two-phase rename** — files are renamed to a temporary name first and then to the final name, avoiding collisions when renaming in place; if anything fails partway through, completed changes are still recorded for undo and the rest are rolled back automatically.
- **Undo** — revert the most recent batch rename operation, with partial-failure recovery so a failed undo doesn't lose history.
- **Crash recovery** — if the app was killed mid-rename, leftover temporary files are detected and automatically restored to their original names the next time you open the same folder.
- **Extension filtering** — restrict any operation to a comma-separated list of file extensions.
- **Light / Dark themes**.
- **7 languages** — Chinese, English, Japanese, Korean, French, German, and Spanish, switchable at runtime.
- **Persistent settings** — window language/theme and last-used directory are saved to `config.json`, with portable mode (config next to the executable) supported.

### How to Use

1. Launch `BatchRenamerTool v1.0.exe` and select a target folder.
2. Pick a tab: **Number**, **Order**, **Time**, or **Find & Replace**.
3. Configure the options for that mode (prefix, padding, extensions, etc.).
4. Click **Preview** to see the old name → new name mapping.
5. Click **Rename** to apply, or **Undo** to revert the last operation.

### What's in the Release Zip

| File | Purpose |
|---|---|
| `BatchRenamerTool v1.0.exe` | The application — just double-click to run. |
| `README.md` | This documentation. |
| `LICENSE.txt` | MIT License. |

The exe is fully self-contained; you don't need to install Python or anything else.

### Settings & Portability

The app saves your language, theme, and last-used folder to a `config.json`:
- If a `config.json` is present in the same folder as the exe, it's used directly (portable mode) — handy for running from a USB drive.
- Otherwise, settings are stored per-user under `%APPDATA%\BatchRenamer`.

### Building From Source

This tool is built with Python and Tkinter. If you'd like to run or modify it from source instead of using the packaged exe: the source (`main.py`, `engine.py`, `view.py`, `theme.py`, `language.py`) is in this repository. Install the one dependency and run it directly:

```bash
pip install appdirs
python main.py
```

### License

Released under the [MIT License](LICENSE.txt) — © 2026 Nidong.

---

<a id="中文"></a>
## 中文

一款轻量级的 Windows 批量重命名桌面工具，**免安装、解压即用**。支持多种重命名策略、"先预览后执行"的安全流程、一键撤销、明暗双主题以及 7 种界面语言。

### 下载与运行

1. 从 [Releases](../../releases) 页面下载压缩包（如果你已经在解压后的发布文件夹里看到这份文件，可直接跳到第 3 步）。
2. 解压到任意位置即可（桌面、`D:\Tools`、U 盘均可，无需安装程序，也不需要管理员权限）。
3. 双击 `BatchRenamerTool v1.0.exe` 即可启动。

就这么简单——本工具完全绿色便携。如需迁移到其他电脑，直接把整个解压后的文件夹复制过去即可。

**系统要求：** Windows 10/11（64 位），无需安装任何其他软件。

> **关于杀毒软件误报的说明：** 由于本 exe 使用 PyInstaller 打包且未进行代码签名，Windows Defender 或部分杀毒软件在首次运行时可能会将其标记为"未知/可疑"程序——这是小体积、未签名的 Python 打包程序常见的误报现象。本仓库包含完整源码，欢迎自行核实。如果被拦截，可以选择放行或添加信任/排除项。

### 功能特性

- **四种重命名模式**
  - **序号重命名** —— 添加数字前缀/后缀，提取并重新编号文件名中已有的某段数字，可限定原编号范围、支持补零和倒序编号。
  - **按顺序重命名** —— 按文件名自然排序（数字感知）批量重编号，可自定义前缀/后缀、起始编号和补零位数。
  - **按时间重命名** —— 按文件最后修改时间排序进行重编号。
  - **查找与替换** —— 支持普通文本或正则表达式对文件名进行查找替换。
- **执行前完整预览** —— 任何模式都会先生成"旧文件名 → 新文件名"的完整预览表，确认无误后才会真正修改磁盘上的文件。
- **安全的两阶段重命名** —— 先将文件改为临时名，再改为最终名，避免原地重命名时的命名冲突；若过程中途失败，已经生效的部分仍会被记录以便撤销，其余部分会自动回滚。
- **撤销功能** —— 可撤销最近一次批量重命名操作；即使撤销过程中部分失败，也不会丢失历史记录，可稍后重试。
- **崩溃恢复** —— 若程序在重命名过程中被意外终止，下次打开同一文件夹时会自动检测并恢复遗留的临时文件到原始文件名。
- **扩展名过滤** —— 可通过逗号分隔的扩展名列表，将任意操作限定在特定类型的文件上。
- **明暗主题切换**。
- **7 种界面语言** —— 中文、英文、日文、韩文、法文、德文、西班牙文，可在运行时随时切换。
- **配置持久化** —— 界面语言、主题以及上次使用的目录会保存到 `config.json`，同时支持便携模式（配置文件与可执行文件放在同一目录）。

### 使用方法

1. 双击 `BatchRenamerTool v1.0.exe` 启动，然后选择目标文件夹。
2. 切换到需要的标签页：**序号重命名**、**按顺序重命名**、**按时间重命名** 或 **查找与替换**。
3. 根据对应模式配置选项（前缀、补零位数、扩展名等）。
4. 点击 **预览**，查看"旧文件名 → 新文件名"的对照表。
5. 点击 **重命名** 执行操作，或点击 **撤销** 恢复上一次的更改。

### 发布压缩包内容

| 文件 | 说明 |
|---|---|
| `BatchRenamerTool v1.0.exe` | 主程序，双击即可运行。 |
| `README.md` | 本说明文档。 |
| `LICENSE.txt` | MIT 开源许可证。 |

该 exe 为独立可执行文件，无需另外安装 Python 或其他运行环境。

### 设置与便携性

程序会将语言、主题以及上次使用的文件夹保存到 `config.json`：
- 若 exe 同目录下已存在 `config.json`，则直接使用该文件（便携模式）——适合放在 U 盘里随身携带使用。
- 否则，配置将保存在用户级目录 `%APPDATA%\BatchRenamer` 下。

### 从源码构建

本工具基于 Python + Tkinter 开发。如果你想从源码运行或修改本工具（而非使用打包好的 exe）：源码（`main.py`、`engine.py`、`view.py`、`theme.py`、`language.py`）就在本仓库中。安装唯一的依赖库后即可直接运行：

```bash
pip install appdirs
python main.py
```

### 开源协议

本项目基于 [MIT License](LICENSE.txt) 开源 —— © 2026 Nidong。
