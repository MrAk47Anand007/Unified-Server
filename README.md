# 🚀 Unified Server

A powerful all-in-one Streamlit application that combines **GitHub Repository Extraction**, **AI-Powered Grammar Correction**, and **Python Script Runner** with a modern, professional interface.

Perfect for developers who want repository analysis, writing assistance, and a sandboxed Python playground - all in one unified platform.

---

## 🚀 Features

### 🗂️ GitRepo Extractor

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

### ✍️ LinguaFix Grammar Correction (Enhanced!)

* ✨ **AI-powered grammar correction** using Google Gemini 2.5 Flash
* 📄 **Supports long text and paragraphs** (up to 5000 characters)
* 🔄 Smart retry logic with exponential backoff for rate limiting
* 📊 Real-time character count
* 💾 Download corrected text
* 🎨 Side-by-side comparison view (Original vs Corrected)
* 🚀 Robust error handling with helpful feedback

### 🐍 Python Script Runner (Modernized!)

* 🎨 **Professional code editor** with syntax highlighting powered by Ace Editor
* ⌨️ **VSCode-like keyboard shortcuts** and features
* 🎯 **Smart autocompletion** and code snippets
* 📦 **Collection management** - organize scripts like Postman collections
* 🔍 **Search functionality** - find scripts by name or tags
* 📝 **Script tagging** for better organization
* 🔒 **Secure sandboxed execution** environment
* 📊 Captures stdout, stderr, and return values
* 💾 Export execution results
* 🕒 Recent scripts quick access

### 💡 Modern UI Features

* 🎨 Custom dark theme with professional styling
* 🧠 Persistent **cache** remembers last used values
* 🧾 View results directly in the browser
* 💾 Download outputs
* ⚙️ Settings page for **API key management**
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
* `google-generativeai` — AI grammar correction
* `streamlit-code-editor` — Modern code editor component

---

## 🔑 Setup API Keys

### GitHub Token (for GitRepo Extractor)

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

### Option 3: Use Settings page in UI

Navigate to **Settings** in the app and enter your GitHub token.

### Gemini API Key (for Grammar Correction)

For **grammar correction**, you need a Google Gemini API key:

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **"Get API Key"** or **"Create API Key"**
3. Copy the API key

**Add to `.env`:**

```bash
GEMINI_API_KEY=your_api_key_here
```

**Or use Settings page in UI** to configure it.

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

Launch the **modern unified interface** with all features in one place.

### 🧩 Launch the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 🔧 Features in UI

| Section                | Functionality                                                              |
| ---------------------- | -------------------------------------------------------------------------- |
| **🗂️ GitRepo Extractor** | Extract GitHub repositories with advanced options                          |
| **✍️ Grammar Correction** | AI-powered text correction with side-by-side comparison                    |
| **🐍 Script Runner**      | Write, organize, and execute Python scripts with a professional code editor |
| **⚙️ Settings**           | Manage GitHub token and Gemini API key (saved to `.env`)                   |
| **ℹ️ About**              | Learn about features and technologies                                      |

### 🐍 Using the Python Script Runner

1. **Create Collections**: Organize your scripts into collections (like folders)
2. **Write Code**: Use the modern code editor with syntax highlighting and autocomplete
3. **Add Metadata**: Give your scripts names, descriptions, and tags
4. **Execute**: Run scripts in a secure sandbox environment
5. **View Results**: See stdout, stderr, execution time, and return values
6. **Export**: Download execution results as text files

**Features:**
- Line numbers and syntax highlighting
- Code folding and auto-indentation
- VSCode-like keyboard shortcuts (Ctrl+/, Ctrl+D, etc.)
- Search and replace within code
- Multiple script collections for organization
- Tag-based script filtering

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

| Use Case                     | Description                                                       |
| ---------------------------- | ----------------------------------------------------------------- |
| 🤖 LLM Training              | Convert repo code into structured text for context ingestion      |
| 📚 Documentation             | Automatically generate repository summaries and structure         |
| 🧮 Code Analysis             | Extract and analyze code structure for audits or metrics          |
| 🧑‍💻 Research                | Study project patterns or architecture easily                     |
| ✍️ Content Writing           | Polish blog posts, emails, and documentation with AI              |
| 📝 Academic Writing          | Improve grammar in research papers and essays                     |
| 🧪 Quick Prototyping         | Test Python code snippets without setting up an environment       |
| 📚 Learning Python           | Practice coding with instant feedback and safe execution          |
| 🔬 Algorithm Testing         | Develop and test algorithms with organized script collections     |
| 🛠️ Utility Scripts           | Store and manage frequently used Python utilities                 |

---

## 🩺 Troubleshooting

| Issue                                    | Solution                                                                  |
| ---------------------------------------- | ------------------------------------------------------------------------- |
| **`NotImplementedError` from asyncio**   | Windows fix applied — ensure Proactor policy is set (already in `app.py`) |
| **Private repo access denied**           | Check token permissions (`repo` scope)                                    |
| **Grammar correction rate limited**      | Wait a moment and retry; check quota at Google AI Studio                  |
| **Script execution timeout**             | Default timeout is 30s; avoid infinite loops                              |
| **Code editor not loading**              | Clear browser cache or try incognito mode                                 |
| **Import errors in script runner**       | Some modules are blocked for security (os, sys, subprocess, etc.)         |

---

## 🧱 Folder Structure

```
Unified-Server/
│
├── app.py                        # Main Streamlit application
├── script_runner.py              # Python Script Runner module
├── grammar_corrector.py          # Grammar correction module
├── repo_ingest.py                # CLI ingestion tool
├── repo_ingester.py              # Library version (programmatic API)
├── .env                          # API keys and tokens
├── .streamlit/
│   └── config.toml               # Streamlit theme configuration
├── scripts/                      # User scripts storage
│   ├── Uncategorized/            # Default collection
│   └── collections.json          # Collections metadata
├── .unified_server_cache.json    # Cached UI values (auto-created)
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