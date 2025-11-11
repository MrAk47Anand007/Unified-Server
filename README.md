# 🧠 GitHub Repository Ingestion Suite

A powerful Python-based toolkit to **extract and analyze GitHub repositories** using [`gitingest`](https://pypi.org/project/gitingest/).
It supports both **CLI** and a **Streamlit-based graphical interface** for convenient repository ingestion, documentation generation, and LLM-ready text conversion.

---

## 🚀 Features

### 🧰 Core (CLI)

* 🔐 Works with **public and private repositories** (via GitHub token)
* 🌳 Supports **branch-wise ingestion**
* 📂 Ingest **entire repositories** or **specific subdirectories**
* 🧩 Configurable:

  * Include submodules (`--include-submodules`)
  * Include `.gitignored` files (`--include-gitignored`)
  * Limit by file size (`--max-file-size`)
* 💾 Supports **custom output paths and filenames**
* 📝 Produces rich text output:

  * Repository info
  * Directory tree
  * Summary
  * Full content

### 💡 Streamlit UI

* 🎨 Clean web interface (runs locally)
* ⚙️ Settings page for **GitHub token management**
* 🧠 Persistent **cache** remembers last used values
* 🧾 View generated text directly in the browser
* 💾 Download output directly
* 📁 Select or auto-create output folder
* ✅ Windows-compatible (Proactor event loop fix applied)

---

## 🧩 Installation

1. Clone or download this repository:

```bash
git clone https://github.com/your-user/repo-ingest-tool.git
cd repo-ingest-tool
```

2. Create and activate a virtual environment *(recommended)*:

```bash
python -m venv .venv
.venv\Scripts\activate    # on Windows
source .venv/bin/activate # on Mac/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

**Dependencies include:**

* `gitingest` — Core ingestion library
* `streamlit` — Web UI framework
* `python-dotenv` — Environment variable management

---

## 🔑 Setup GitHub Token

For **private repositories**, you must use a GitHub Personal Access Token.

1. Visit [GitHub Personal Access Tokens](https://github.com/settings/personal-access-tokens)
2. Click **“Generate new token (classic)”**
3. Give it a name and select **`repo`** scope
4. Copy the token — you won’t see it again!

### Option 1: Store in `.env`

```bash
GITHUB_TOKEN=ghp_your_token_here
```

### Option 2: Environment variable

```bash
set GITHUB_TOKEN=ghp_xxxxx    # Windows
export GITHUB_TOKEN=ghp_xxxxx # Mac/Linux
```

### Option 3: CLI flag

```bash
python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx
```

---

## ⚙️ Command-Line Usage

### 🧩 Basic Ingestion Examples

**Ingest a public repository:**

```bash
python repo_ingest.py https://github.com/user/repo
```

**Ingest a private repository (token auto-loaded from .env):**

```bash
python repo_ingest.py https://github.com/user/repo
```

**Ingest from a specific branch:**

```bash
python repo_ingest.py https://github.com/user/repo --branch dev
```

**Ingest a specific subdirectory:**

```bash
python repo_ingest.py https://github.com/user/repo --subpath src/backend
```

**Custom output file:**

```bash
python repo_ingest.py https://github.com/user/repo -o "C:\Output\repo_backend.txt"
```

**Include submodules and gitignored files:**

```bash
python repo_ingest.py https://github.com/user/repo --include-submodules --include-gitignored
```

**Limit file size (e.g., 500KB):**

```bash
python repo_ingest.py https://github.com/user/repo --max-file-size 512000
```

---

### 🧩 Full Command Reference

| Flag                   | Description                                                   |
| ---------------------- | ------------------------------------------------------------- |
| `repo_url`             | GitHub repository URL (must start with `https://github.com/`) |
| `-t, --token`          | GitHub Personal Access Token                                  |
| `-b, --branch`         | Branch or ref to ingest (`main`, `dev`, etc.)                 |
| `-s, --subpath`        | Optional subdirectory path                                    |
| `-o, --output`         | Custom output file path                                       |
| `--include-submodules` | Include repository submodules                                 |
| `--include-gitignored` | Include files listed in `.gitignore`                          |
| `--max-file-size`      | Maximum size per file (bytes)                                 |

---

### 🧠 Example — Complete Command

```bash
python repo_ingest.py "https://github.com/MrAk47Anand007/QuickComm---Hyperlocal-Quick-Commerce-Platform" --branch dev --subpath backend -o "C:\Users\Anand\Desktop\backend_dev_extract.txt" --token ghp_yourGitHubTokenHere
```

---

## 💻 Streamlit Web UI

You can also run a **beautiful GUI** with caching and live preview.

### 🧩 Launch the App

```bash
streamlit run app.py
```

### 🔧 Features in UI

| Section         | Functionality                                                       |
| --------------- | ------------------------------------------------------------------- |
| **Ingest Page** | Enter repo URL, branch, subpath, output folder, and generate output |
| **Settings**    | Manage GitHub token (`.env` stored)                                 |
| **Cache**       | View or clear saved field values                                    |
| **About**       | Learn about the tool and backend logic                              |

### 🗂 Persistent Cache

* Saves previous inputs (except tokens) to `.repo_ingest_cache.json`
* Auto-loads cached values on restart
* Clear anytime from the **Cache** page

### 🪶 Windows Fix

If you’re on Windows, the app automatically applies the **Proactor event loop policy** to fix `NotImplementedError` from asyncio.

---

## 📜 Output Format

Each generated text file includes:

1. **Repository metadata**
2. **Summary**
3. **Directory tree structure**
4. **Full code content**

Example auto-generated filename:

```
repo_name_dev_backend_digest.txt
```

---

## 🧪 Example Use Cases

| Use Case         | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| 🤖 LLM Training  | Convert repo code into structured text for context ingestion |
| 📚 Documentation | Automatically generate repository summaries and structure    |
| 🧮 Analysis      | Extract and analyze code structure for audits or metrics     |
| 🧑‍💻 Research   | Study project patterns or architecture easily                |

---

## 🩺 Troubleshooting

| Issue                                                                           | Solution                                                                  |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **`NotImplementedError` from asyncio**                                          | Windows fix applied — ensure Proactor policy is set (already in `app.py`) |
| **"Repository URL must start with [https://github.com/](https://github.com/)"** | Use HTTPS link (not SSH)                                                  |
| **Private repo access denied**                                                  | Check token permissions (`repo` scope)                                    |
| **Output path not found**                                                       | Ensure folder exists or use `--output` to specify valid directory         |
| **Large repo takes long**                                                       | Use `--subpath` or limit file size with `--max-file-size`                 |

---

## 🧱 Folder Structure

```
GitRepoExtracter/
│
├── repo_ingest.py           # CLI ingestion tool (main entry point)
├── repo_ingester.py         # Library version (programmatic API)
├── app.py                   # Streamlit UI (with caching + settings)
├── .env                     # GitHub token (optional)
├── .repo_ingest_cache.json  # Cached UI values (auto-created)
├── requirements.txt
└── README.md
```

---

## 📦 Requirements

* **Python** ≥ 3.8
* **Libraries**:

  * `gitingest`
  * `streamlit`
  * `python-dotenv`

Install all at once:

```bash
pip install gitingest streamlit python-dotenv
```

---

## 🪄 Example Workflow

### 1️⃣ CLI (quick extraction)

```bash
python repo_ingest.py "https://github.com/user/repo" --branch main --subpath src
```

### 2️⃣ UI (interactive)

```bash
streamlit run app.py
```

Use the interface to set repo, branch, output path → click **Generate** → view and download results.

---

## ⚖️ License

This project is provided **as-is** for learning and development purposes.
Feel free to modify or integrate it into your own workflows.

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome!
If you build new capabilities (like multi-branch ingestion or repo comparison), feel free to share them.

---

## 🔗 Related Resources

* [📦 gitingest PyPI](https://pypi.org/project/gitingest/)
* [🔐 GitHub Personal Access Tokens](https://github.com/settings/tokens)
* [🧭 GitHub REST API Docs](https://docs.github.com/en/rest)
* [💡 Streamlit Documentation](https://docs.streamlit.io)

---