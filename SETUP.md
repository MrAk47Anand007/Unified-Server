# Setup Guide - GitHub Repository Ingestion Tool

Complete setup instructions from scratch.

---

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning repositories)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **gitingest** (≥0.3.0) - Core library for repository ingestion
- **python-dotenv** (≥1.0.0) - For managing environment variables

### Step 2: Configure GitHub Token

#### Why do you need a token?
- **Public repositories**: No token needed
- **Private repositories**: Token required
- **Rate limits**: Token provides higher API limits

#### Get your GitHub token:

1. Visit: https://github.com/settings/personal-access-tokens
2. Click **"Generate new token (classic)"**
3. Fill in:
   - **Note**: Give it a descriptive name (e.g., "Repo Ingestion Tool")
   - **Expiration**: Choose your preference (recommend 90 days)
   - **Scopes**: Select **`repo`** (for full repository access)
4. Click **"Generate token"**
5. **IMPORTANT**: Copy the token immediately (starts with `ghp_`)

#### Configure the token:

**Option A: Using .env file (RECOMMENDED)**

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit .env file and add your token
nano .env  # or use any text editor
```

Your `.env` file should look like:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Benefits of .env file:**
- ✅ No need to pass token every time
- ✅ Secure (not visible in command history)
- ✅ Easy to manage
- ✅ Works across all scripts

**Option B: Environment Variable**

```bash
# Linux/Mac
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Windows Command Prompt
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Option C: Command-line argument** (not recommended for frequent use)

```bash
python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx
```

### Step 3: Verify Installation

Test that everything is working:

```bash
# Test with a public repository (no token needed)
python repo_ingest.py https://github.com/cyclotruc/gitingest --output test_output.txt
```

If successful, you'll see:
```
🔍 Ingesting repository: https://github.com/cyclotruc/gitingest
⏳ Processing repository...
✅ Successfully ingested repository!
📄 Output saved to: test_output.txt
📊 File size: XX.XX KB
```

---

## 🎯 Quick Start Commands

### Command Line Interface

```bash
# Public repo
python repo_ingest.py https://github.com/user/repo

# Private repo (with .env configured)
python repo_ingest.py https://github.com/user/private-repo

# Specific subdirectory
python repo_ingest.py https://github.com/user/repo --subpath src/api

# Custom output filename
python repo_ingest.py https://github.com/user/repo -o my_analysis.txt
```

### Python Script

```python
from repo_ingester import RepoIngester

# Token automatically loaded from .env
ingester = RepoIngester()

# Ingest repository
summary, tree, content = ingester.ingest_repo(
    repo_url="https://github.com/user/repo",
    output_file="output.txt"
)

print(f"✅ Ingested {len(content)} characters")
```

---

## 📁 Project Structure After Setup

```
your-project-folder/
├── .env                        # Your token (DO NOT COMMIT!)
├── .env.example                # Example template
├── .gitignore                  # Excludes .env and outputs
├── requirements.txt            # Dependencies
├── repo_ingest.py              # CLI tool
├── repo_ingester.py            # Python library
├── examples.py                 # Usage examples
├── README.md                   # Full documentation
├── QUICKSTART.md               # Quick reference
└── SETUP.md                    # This file
```

---

## 🔒 Security Best Practices

### DO:
✅ Use `.env` file for tokens
✅ Add `.env` to `.gitignore`
✅ Use token expiration (90 days recommended)
✅ Limit token scope to only what's needed
✅ Store tokens securely

### DON'T:
❌ Commit `.env` file to Git
❌ Share your token publicly
❌ Use `--token` flag in shared scripts
❌ Store tokens in command history
❌ Give tokens more permissions than needed

---

## 🧪 Testing Your Setup

Run the examples to test all features:

```bash
python examples.py
```

This will show you 8 different usage patterns interactively.

---

## 🔧 Troubleshooting

### Issue: "No module named 'gitingest'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'dotenv'"
**Solution:**
```bash
pip install python-dotenv
```

### Issue: Token not working
**Solutions:**
1. Verify token starts with `ghp_`
2. Check token hasn't expired
3. Ensure token has `repo` scope
4. Verify `.env` file format: `GITHUB_TOKEN=ghp_xxx` (no quotes, no spaces)

### Issue: "Repository not found" for private repo
**Solutions:**
1. Verify token is loaded: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GITHUB_TOKEN')[:10])"`
2. Check token permissions include private repos
3. Verify you have access to the repository

### Issue: Rate limit exceeded
**Solutions:**
1. Use a GitHub token (higher limits)
2. Wait for rate limit reset (check headers)
3. Use different token

---

## 🎓 Next Steps

1. ✅ **Setup Complete** - You're ready to go!
2. 📖 Read **QUICKSTART.md** for common commands
3. 📚 Check **README.md** for full documentation
4. 🧪 Run **python examples.py** for interactive demos
5. 🚀 Start ingesting your repositories!

---

## 📞 Getting Help

- Full docs: `README.md`
- Quick reference: `QUICKSTART.md`
- Examples: `python examples.py`
- File structure: `FOLDER_STRUCTURE.txt`
- gitingest docs: https://pypi.org/project/gitingest/

---

## 🎉 You're All Set!

Try your first ingestion:

```bash
python repo_ingest.py https://github.com/your-username/your-repo --subpath src
```

Happy ingesting! 🚀