# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
```

This will install:
- `gitingest` - Main library for repository ingestion
- `python-dotenv` - For loading environment variables from .env file

## Setup GitHub Token

### Option 1: Using .env file (Recommended)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your token:
```bash
GITHUB_TOKEN=ghp_your_github_token_here
```

3. Get your token from: https://github.com/settings/personal-access-tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (for private repos)
   - Generate and copy the token

### Option 2: Command Line

Pass the token directly with `--token` flag (see usage examples below)

### Option 3: Environment Variable

```bash
export GITHUB_TOKEN=ghp_your_token  # Linux/Mac
set GITHUB_TOKEN=ghp_your_token     # Windows CMD
$env:GITHUB_TOKEN="ghp_your_token"  # Windows PowerShell
```

## Usage

### With .env file (No need to pass token each time!)

Once you've set up your `.env` file with `GITHUB_TOKEN`:

```bash
# Public repository
python repo_ingest.py https://github.com/user/repo

# Private repository (token loaded from .env automatically)
python repo_ingest.py https://github.com/user/repo

# Specific subdirectory
python repo_ingest.py https://github.com/user/repo --subpath src/core

# Custom output
python repo_ingest.py https://github.com/user/repo -o my_output.txt
```

### Without .env file (Pass token manually)

```bash
# Private repository with token flag
python repo_ingest.py https://github.com/user/repo --token ghp_your_token

# With subpath
python repo_ingest.py https://github.com/user/repo --token ghp_your_token --subpath src/core
```

### Python Script Usage

```python
from repo_ingester import RepoIngester

# Token is loaded automatically from .env file
ingester = RepoIngester()

# Or pass token explicitly
ingester = RepoIngester(token="ghp_your_token")

# Ingest entire repo
summary, tree, content = ingester.ingest_repo(
    "https://github.com/user/repo",
    output_file="output.txt"
)

# Ingest specific subdirectory
summary, tree, content = ingester.ingest_repo(
    repo_url="https://github.com/user/repo",
    subpath="src/api",
    output_file="api_only.txt"
)
```

### Quick Functions

```python
from repo_ingester import quick_ingest, ingest_and_save

# Token loaded from .env automatically
content = quick_ingest("https://github.com/user/repo")

# Ingest and save in one line
ingest_and_save(
    "https://github.com/user/repo",
    "output.txt",
    subpath="src"
)
```

## Real-World Examples

### Example 1: Analyze Your Healthcare Automation Project

With `.env` file configured:
```bash
python repo_ingest.py \
  https://github.com/your-username/eob-automation \
  --subpath src/edi \
  --output eob_edi_analysis.txt
```

### Example 2: Extract UiPath Bot Code

```bash
python repo_ingest.py \
  https://github.com/your-org/uipath-bots \
  --subpath workflow \
  --output uipath_workflow.txt
```

### Example 3: Multiple Paths from Same Repo

```python
from repo_ingester import RepoIngester

# Token loaded from .env
ingester = RepoIngester()

results = ingester.ingest_multiple_paths(
    repo_url="https://github.com/your-org/automation-project",
    subpaths=[
        "src/api",
        "src/workers",
        "src/utils",
        "tests"
    ],
    output_dir="project_analysis"
)
```

### Example 4: Batch Process Multiple Repos

```python
from repo_ingester import RepoIngester

# Token loaded from .env
ingester = RepoIngester()

repos = [
    ("https://github.com/org/repo1", "frontend"),
    ("https://github.com/org/repo2", "backend"),
    ("https://github.com/org/repo3", "automation")
]

for url, name in repos:
    print(f"Processing {name}...")
    ingester.ingest_repo(url, output_file=f"{name}_digest.txt")
```

## Tips

1. **For Large Repos**: Use `--subpath` to focus on specific directories
2. **File Size Limits**: Use `--max-file-size` to skip large files
3. **Private Repos**: Always use `--token` or set `GITHUB_TOKEN` env var
4. **Batch Processing**: Use the Python API for multiple repos/paths

## Troubleshooting

- **"Rate limit exceeded"**: Wait a few minutes or use a different token
- **"Repository not found"**: Check URL and token permissions
- **"No such file or directory"**: Verify subpath exists in the repository
- **Large output files**: Consider using `--max-file-size` or specific subpaths

## Output Structure

The generated `.txt` files contain:

```
================================================================================
REPOSITORY DIGEST
================================================================================

Repository: https://github.com/user/repo/tree/main/src

================================================================================
SUMMARY
================================================================================

[Statistics about files, lines, size, etc.]

================================================================================
DIRECTORY TREE
================================================================================

[Visual tree structure of the repository]

================================================================================
CONTENT
================================================================================

[Full source code with file markers]
```

## Next Steps

1. Run `python examples.py` to see 8 different usage patterns
2. Read `README.md` for comprehensive documentation
3. Check out `repo_ingester.py` for the Python API reference