"""
GitHub Repository Ingestion Library
Use this module to programmatically ingest GitHub repositories
"""

import os
from typing import Optional, Tuple, List
from pathlib import Path
from gitingest import ingest
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RepoIngester:
    """
    A class to handle GitHub repository ingestion with gitingest.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the RepoIngester.

        Args:
            token: GitHub Personal Access Token (optional)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if self.token:
            os.environ["GITHUB_TOKEN"] = self.token

    def ingest_repo(
        self,
        repo_url: str,
        subpath: Optional[str] = None,
        branch: Optional[str] = None,   # <-- added branch support
        output_file: Optional[str] = None,
        include_submodules: bool = False,
        max_file_size: Optional[int] = None
    ) -> Tuple[str, str, str]:
        """
        Ingest a GitHub repository.

        Args:
            repo_url: GitHub repository URL
            subpath: Optional path within the repository
            branch: Optional branch/ref to ingest (e.g., "main", "dev", "feature/x")
            output_file: Optional output file path
            include_submodules: Include submodules
            max_file_size: Maximum file size in bytes

        Returns:
            Tuple of (summary, tree, content)
        """
        # Build full URL (use branch if provided; otherwise preserve existing behavior)
        if subpath:
            subpath = subpath.strip('/')
            if branch:
                full_url = f"{repo_url}/tree/{branch}/{subpath}"
            else:
                full_url = f"{repo_url}/tree/main/{subpath}"
        else:
            full_url = f"{repo_url}/tree/{branch}" if branch else repo_url

        # Prepare parameters
        params = {
            "source": full_url,
            "include_submodules": include_submodules
        }

        # pass branch/ref to gitingest if available
        if branch:
            params["ref"] = branch

        if max_file_size:
            params["max_file_size"] = max_file_size

        # Perform ingestion
        summary, tree, content = ingest(**params)

        # Save to file if requested
        if output_file:
            self._save_to_file(full_url, summary, tree, content, output_file)

        return summary, tree, content

    def ingest_multiple_paths(
        self,
        repo_url: str,
        subpaths: List[str],
        branch: Optional[str] = None,    # <-- added branch support
        output_dir: str = "outputs"
    ) -> dict:
        """
        Ingest multiple subdirectories from the same repository.

        Args:
            repo_url: GitHub repository URL
            subpaths: List of subdirectories to ingest
            branch: Optional branch/ref to ingest for all subpaths
            output_dir: Directory to save outputs

        Returns:
            Dictionary mapping subpaths to their ingestion results
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results = {}
        repo_name = repo_url.rstrip('/').split('/')[-1]

        for subpath in subpaths:
            print(f"Processing {subpath} on branch {branch or 'main'}...")
            subpath_clean = subpath.replace('/', '_')
            if branch:
                output_file = output_path / f"{repo_name}_{branch}_{subpath_clean}_digest.txt"
            else:
                output_file = output_path / f"{repo_name}_{subpath_clean}_digest.txt"

            try:
                summary, tree, content = self.ingest_repo(
                    repo_url=repo_url,
                    subpath=subpath,
                    branch=branch,
                    output_file=str(output_file)
                )
                results[subpath] = {
                    "success": True,
                    "summary": summary,
                    "tree": tree,
                    "content": content,
                    "output_file": str(output_file)
                }
            except Exception as e:
                results[subpath] = {
                    "success": False,
                    "error": str(e)
                }

        return results

    def _save_to_file(
        self,
        url: str,
        summary: str,
        tree: str,
        content: str,
        output_file: str
    ):
        """Save ingestion results to a formatted text file."""
        output_path = Path(output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPOSITORY DIGEST\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Repository: {url}\n\n")
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


# Example usage functions
def quick_ingest(repo_url: str, token: Optional[str] = None, branch: Optional[str] = None) -> str:
    """
    Quick ingest function that returns the content as a string.

    Args:
        repo_url: GitHub repository URL
        token: Optional GitHub token
        branch: Optional branch/ref to ingest

    Returns:
        Ingested content as string
    """
    ingester = RepoIngester(token=token)
    summary, tree, content = ingester.ingest_repo(repo_url, branch=branch)
    return content


def ingest_and_save(
    repo_url: str,
    output_file: str,
    token: Optional[str] = None,
    subpath: Optional[str] = None,
    branch: Optional[str] = None
) -> str:
    """
    Ingest repository and save to file.

    Args:
        repo_url: GitHub repository URL
        output_file: Path to save output
        token: Optional GitHub token
        subpath: Optional subdirectory path
        branch: Optional branch/ref to ingest

    Returns:
        Path to output file
    """
    ingester = RepoIngester(token=token)
    ingester.ingest_repo(
        repo_url=repo_url,
        subpath=subpath,
        branch=branch,
        output_file=output_file
    )
    return output_file


# Example usage
if __name__ == "__main__":
    # Example 1: Simple usage
    print("Example 1: Quick ingest")
    ingester = RepoIngester(token="your_token_here")
    summary, tree, content = ingester.ingest_repo(
        "https://github.com/user/repo",
        subpath="src"
    )
    print(f"Summary length: {len(summary)}")
    print(f"Content length: {len(content)}")

    # Example 1b: Branch usage
    print("\nExample 1b: Quick ingest from branch 'dev'")
    summary_b, tree_b, content_b = ingester.ingest_repo(
        "https://github.com/user/repo",
        subpath="src",
        branch="dev"
    )
    print(f"Summary length: {len(summary_b)}")
    print(f"Content length: {len(content_b)}")

    # Example 2: Ingest with file output
    print("\nExample 2: Ingest and save")
    ingester.ingest_repo(
        "https://github.com/user/repo",
        subpath="src/core",
        output_file="output.txt"
    )

    # Example 3: Multiple paths
    print("\nExample 3: Multiple paths")
    results = ingester.ingest_multiple_paths(
        repo_url="https://github.com/user/repo",
        subpaths=["src/api", "src/utils", "tests"],
        output_dir="repo_analysis"
    )

    for path, result in results.items():
        if result["success"]:
            print(f"✓ {path} -> {result['output_file']}")
        else:
            print(f"✗ {path} -> {result['error']}")
