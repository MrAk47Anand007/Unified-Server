"""
GitHub Repository Ingestion Tool
Uses gitingest to extract code from GitHub repositories into text files
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from gitingest import ingest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def ingest_repository(
    repo_url: str,
    token: str = None,
    subpath: Optional[str] = None,
    branch: Optional[str] = None,               # <-- added
    output_file: str = None,
    include_submodules: bool = False,
    include_gitignored: bool = False,
    max_file_size: int = None
) -> tuple:
    """
    Ingest a GitHub repository and save to a text file.

    Args:
        repo_url: Root GitHub repository URL (e.g., https://github.com/user/repo)
        token: GitHub Personal Access Token for private repos
        subpath: Optional deeper path within the repository
        branch: Optional branch/ref to ingest (e.g., "main", "dev", "feature/x")
        output_file: Output file path (default: <repo_name>_digest.txt)
        include_submodules: Include repository submodules
        include_gitignored: Include files listed in .gitignore
        max_file_size: Maximum file size to process in bytes

    Returns:
        tuple: (summary, tree, content)
    """

    # Build the full URL with subpath and branch if provided
    if subpath:
        # Remove leading/trailing slashes from subpath
        subpath = subpath.strip('/')
        if branch:
            full_url = f"{repo_url}/tree/{branch}/{subpath}"
        else:
            full_url = f"{repo_url}/tree/main/{subpath}"
    else:
        # No subpath — if branch provided, point to the branch root; else repo root
        if branch:
            full_url = f"{repo_url}/tree/{branch}"
        else:
            full_url = repo_url

    print(f"🔍 Ingesting repository: {full_url}")

    # Set token as environment variable if provided
    if token:
        os.environ["GITHUB_TOKEN"] = token
        print("✓ GitHub token configured")

    # Prepare ingest parameters
    ingest_params = {
        "source": full_url,
        "include_submodules": include_submodules,
        "include_gitignored": include_gitignored,   # now honored
    }

    # pass branch/ref to gitingest if supported
    # if branch:
    #     ingest_params["ref"] = branch

    if max_file_size:
        ingest_params["max_file_size"] = max_file_size

    try:
        # Perform ingestion
        print("⏳ Processing repository...")
        summary, tree, content = ingest(**ingest_params)

        # Determine output filename
        if not output_file:
            repo_name = repo_url.rstrip('/').split('/')[-1]
            parts = [repo_name]
            if branch:
                parts.append(branch)
            if subpath:
                subpath_clean = subpath.replace('/', '_')
                parts.append(subpath_clean)
            output_file = "_".join(parts) + "_digest.txt"

        # Write to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPOSITORY DIGEST\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Repository: {full_url}\n\n")
            f.write("=" * 80 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write(summary + "\n\n")
            f.write("=" * 80 + "\n")
            f.write("DIRECTORY TREE\n")
            f.write("=" * 80 + "\n\n")
            f.write(tree + "\n\n")
            f.write("=" * 80 + "\n")
            f.write("CONTENT\n")
            f.write("=" * 80 + "\n\n")
            f.write(content)

        print(f"✅ Successfully ingested repository!")
        print(f"📄 Output saved to: {output_path.absolute()}")
        print(f"📊 File size: {output_path.stat().st_size / 1024:.2f} KB")

        return summary, tree, content

    except Exception as e:
        print(f"❌ Error during ingestion: {e}", file=sys.stderr)
        raise


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="Ingest GitHub repositories into text files using gitingest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - entire repository
  python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx
  
  # Ingest a specific subdirectory
  python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx --subpath src/core
  
  # Custom output file
  python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx -o my_digest.txt
  
  # Include submodules and gitignored files
  python repo_ingest.py https://github.com/user/repo --token ghp_xxxxx --include-submodules --include-gitignored

  # Ingest specific branch
  python repo_ingest.py https://github.com/user/repo --branch dev --subpath src
        """
    )

    parser.add_argument(
        "repo_url",
        help="GitHub repository URL (e.g., https://github.com/user/repo)"
    )

    parser.add_argument(
        "-t", "--token",
        help="GitHub Personal Access Token (or set GITHUB_TOKEN in .env file or environment)",
        default=os.getenv("GITHUB_TOKEN")
    )

    parser.add_argument(
        "-s", "--subpath",
        help="Optional deeper path within the repository (e.g., src/core)",
        default=None
    )

    parser.add_argument(
        "-b", "--branch",
        help="Branch or ref to ingest (e.g., main, dev, feature/x). If omitted, existing behavior uses 'main' when subpath provided else repo root.",
        default=None
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: <repo_name>_digest.txt)",
        default=None
    )

    parser.add_argument(
        "--include-submodules",
        action="store_true",
        help="Include repository submodules"
    )

    parser.add_argument(
        "--include-gitignored",
        action="store_true",
        help="Include files listed in .gitignore"
    )

    parser.add_argument(
        "--max-file-size",
        type=int,
        help="Maximum file size to process in bytes",
        default=None
    )

    args = parser.parse_args()

    # Validate repo URL
    if not args.repo_url.startswith("https://github.com/"):
        print("❌ Error: Repository URL must start with https://github.com/", file=sys.stderr)
        sys.exit(1)

    # Warn if no token provided
    if not args.token:
        print("⚠️  Warning: No GitHub token provided. This will only work for public repositories.")
        print("   Create a .env file with GITHUB_TOKEN=ghp_xxx or use --token flag for private repos.")
        print()

    try:
        ingest_repository(
            repo_url=args.repo_url,
            token=args.token,
            subpath=args.subpath,
            branch=args.branch,                         # <-- forward branch
            output_file=args.output,
            include_submodules=args.include_submodules,
            include_gitignored=args.include_gitignored,
            max_file_size=args.max_file_size
        )
    except Exception as e:
        print(f"❌ Failed to ingest repository: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
