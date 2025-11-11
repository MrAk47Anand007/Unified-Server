# GitHub Repository Ingestion Tool

A Python tool to extract and analyze code from GitHub repositories using `gitingest`. This tool converts entire repositories or specific subdirectories into digestible text files suitable for analysis, documentation, or LLM processing.

## Features

- 🔐 Support for both public and private repositories (with GitHub token)
- 📂 Ingest entire repositories or specific subdirectories
- 📝 Generates formatted text output with summary, tree structure, and content
- ⚙️ Configurable options (submodules, gitignored files, file size limits)
- 🚀 Simple command-line interface

## Installation

1. Clone or download this project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- `gitingest` - Repository ingestion library
- `python-dotenv` - Environment variable management

3. Set up your GitHub token (for private repositories):

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
# GITHUB_TOKEN=ghp_your_token_here
```

Get your token at: https://github.com/settings/personal-access-tokens

## Usage

### Basic Examples

**Ingest a public repository:**
```bash
python repo_ingest.py https://github.com/user/repo
```

**Ingest a private repository (with .env configured):**
```bash
# Token automatically loaded from .env file
python repo_ingest.py https://github.com/user/repo
```

**Ingest a private repository (without .env):**
```bash
python repo_ingest.py https://github.com/user/repo --token ghp_your_github_token
```

**Ingest a specific subdirectory:**
```bash
python repo_ingest.py https://github.com/user/repo --subpath src/core
```

**Custom output file:**
```bash
python repo_ingest.py https://github.com/user/repo -o my_analysis.txt
```

**Include submodules and gitignored files:**
```bash
python repo_ingest.py https://github.com/user/repo --include-submodules --include-gitignored
```

### Command-Line Options

```
positional arguments:
  repo_url              GitHub repository URL (e.g., https://github.com/user/repo)

optional arguments:
  -h, --help            Show help message and exit
  -t TOKEN, --token TOKEN
                        GitHub Personal Access Token (or set GITHUB_TOKEN env var)
  -s SUBPATH, --subpath SUBPATH
                        Optional deeper path within the repository (e.g., src/core)
  -o OUTPUT, --output OUTPUT
                        Output file path (default: <repo_name>_digest.txt)
  --include-submodules  Include repository submodules
  --include-gitignored  Include files listed in .gitignore
  --max-file-size MAX_FILE_SIZE
                        Maximum file size to process in bytes
```

## Getting a GitHub Token

For private repositories, you need a GitHub Personal Access Token:

1. Go to https://github.com/settings/personal-access-tokens
2. Click "Generate new token" (classic)
3. Give it a name and select scopes (at minimum: `repo` for private repos)
4. Click "Generate token"
5. Copy the token (you won't see it again!)

### Recommended: Use .env file

Create a `.env` file in your project directory:

```bash
GITHUB_TOKEN=ghp_your_token_here
```

The tool will automatically load the token from this file. **No need to pass `--token` every time!**

### Alternative Methods

**Method 2: Environment variable**
```bash
export GITHUB_TOKEN=ghp_xxxxx  # Linux/Mac
set GITHUB_TOKEN=ghp_xxxxx     # Windows CMD
```

**Method 3: Command-line argument**
```bash
python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx
```

## Output Format

The generated text file contains:

1. **Repository Information**: URL and metadata
2. **Summary**: Statistics about the repository
3. **Directory Tree**: Visual representation of the file structure
4. **Content**: Full source code with clear file separators

Example output filename:
- Entire repo: `repo-name_digest.txt`
- Subdirectory: `repo-name_src_core_digest.txt`

## Use Cases

- 📚 Code documentation and analysis
- 🤖 Preparing codebases for LLM processing
- 🔍 Code review and auditing
- 📊 Repository analysis and statistics
- 🎓 Learning and studying code structure

## Advanced Examples

### Ingest specific path with custom settings
```bash
# Token loaded from .env automatically
python repo_ingest.py \
  https://github.com/user/repo \
  --subpath src/api/controllers \
  --output api_controllers_analysis.txt \
  --max-file-size 1048576
```

### Batch processing multiple repositories
```bash
#!/bin/bash
# ingest_multiple.sh

REPOS=(
  "https://github.com/user/repo1"
  "https://github.com/user/repo2"
  "https://github.com/user/repo3"
)

# Token loaded from .env automatically
for repo in "${REPOS[@]}"; do
  python repo_ingest.py "$repo"
done
```

## Troubleshooting

**Issue**: "Error: Repository URL must start with https://github.com/"
- Solution: Ensure you're using the full HTTPS URL, not SSH or other formats

**Issue**: Authentication errors for private repos
- Solution: Verify your GitHub token has the correct permissions (`repo` scope)

**Issue**: Large repository taking too long
- Solution: Use `--subpath` to focus on specific directories or `--max-file-size` to limit file sizes

## Dependencies

- Python 3.7+
- gitingest (automatically handles Git operations and parsing)

## License

This tool is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Related Resources

- [gitingest Documentation](https://pypi.org/project/gitingest/)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)
- [GitHub REST API](https://docs.github.com/en/rest)