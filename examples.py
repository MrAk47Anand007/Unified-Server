"""
Example usage demonstrations for the GitHub Repository Ingestion Tool
"""

import os
from repo_ingester import RepoIngester, quick_ingest, ingest_and_save
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def example_1_basic_usage():
    """Example 1: Basic repository ingestion"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Repository Ingestion")
    print("=" * 60)

    # For public repositories (no token needed)
    ingester = RepoIngester()
    summary, tree, content = ingester.ingest_repo(
        "https://github.com/cyclotruc/gitingest"
    )

    print(f"✓ Repository ingested successfully")
    print(f"  Summary length: {len(summary)} chars")
    print(f"  Tree length: {len(tree)} chars")
    print(f"  Content length: {len(content)} chars")
    print()


def example_2_private_repo():
    """Example 2: Ingest a private repository with token"""
    print("=" * 60)
    print("EXAMPLE 2: Private Repository with Token")
    print("=" * 60)

    # Replace with your actual token
    token = os.getenv("GITHUB_TOKEN", "ghp_your_token_here")

    ingester = RepoIngester(token=token)
    summary, tree, content = ingester.ingest_repo(
        repo_url="https://github.com/your-username/private-repo",
        output_file="private_repo_digest.txt"
    )

    print(f"✓ Private repository ingested and saved")
    print(f"  Output file: private_repo_digest.txt")
    print()


def example_3_specific_subdirectory():
    """Example 3: Ingest a specific subdirectory"""
    print("=" * 60)
    print("EXAMPLE 3: Specific Subdirectory")
    print("=" * 60)

    ingester = RepoIngester()

    # Only ingest the 'src' directory
    summary, tree, content = ingester.ingest_repo(
        repo_url="https://github.com/cyclotruc/gitingest",
        subpath="src/gitingest",
        output_file="gitingest_src_only.txt"
    )

    print(f"✓ Subdirectory ingested")
    print(f"  Path: src/gitingest")
    print(f"  Output file: gitingest_src_only.txt")
    print()


def example_4_multiple_paths():
    """Example 4: Ingest multiple subdirectories from same repo"""
    print("=" * 60)
    print("EXAMPLE 4: Multiple Subdirectories")
    print("=" * 60)

    ingester = RepoIngester()

    # Ingest multiple paths from the same repository
    paths_to_ingest = [
        "src/gitingest",
        "tests",
        "docs"
    ]

    results = ingester.ingest_multiple_paths(
        repo_url="https://github.com/cyclotruc/gitingest",
        subpaths=paths_to_ingest,
        output_dir="gitingest_analysis"
    )

    print(f"✓ Multiple paths processed:")
    for path, result in results.items():
        if result["success"]:
            print(f"  ✓ {path} -> {result['output_file']}")
        else:
            print(f"  ✗ {path} -> Error: {result['error']}")
    print()


def example_5_batch_repos():
    """Example 5: Batch process multiple repositories"""
    print("=" * 60)
    print("EXAMPLE 5: Batch Process Multiple Repositories")
    print("=" * 60)

    ingester = RepoIngester()

    repositories = [
        {
            "url": "https://github.com/cyclotruc/gitingest",
            "name": "gitingest"
        },
        {
            "url": "https://github.com/pallets/flask",
            "name": "flask",
            "subpath": "src/flask"
        }
    ]

    for repo in repositories:
        try:
            print(f"Processing {repo['name']}...")
            ingester.ingest_repo(
                repo_url=repo["url"],
                subpath=repo.get("subpath"),
                output_file=f"{repo['name']}_digest.txt"
            )
            print(f"  ✓ {repo['name']} completed\n")
        except Exception as e:
            print(f"  ✗ {repo['name']} failed: {e}\n")


def example_6_quick_functions():
    """Example 6: Using convenience functions"""
    print("=" * 60)
    print("EXAMPLE 6: Quick Convenience Functions")
    print("=" * 60)

    # Quick ingest - returns content directly
    content = quick_ingest("https://github.com/cyclotruc/gitingest")
    print(f"✓ Quick ingest: {len(content)} chars retrieved")

    # Ingest and save in one call
    output_file = ingest_and_save(
        repo_url="https://github.com/cyclotruc/gitingest",
        output_file="quick_save.txt",
        subpath="src"
    )
    print(f"✓ Quick save: {output_file}")
    print()


def example_7_custom_settings():
    """Example 7: Custom settings and filtering"""
    print("=" * 60)
    print("EXAMPLE 7: Custom Settings")
    print("=" * 60)

    ingester = RepoIngester()

    # Limit file size to 1MB
    summary, tree, content = ingester.ingest_repo(
        repo_url="https://github.com/cyclotruc/gitingest",
        max_file_size=1048576,  # 1MB in bytes
        include_submodules=True,
        output_file="custom_settings_digest.txt"
    )

    print(f"✓ Custom settings applied")
    print(f"  Max file size: 1MB")
    print(f"  Submodules included: Yes")
    print()


def example_8_error_handling():
    """Example 8: Proper error handling"""
    print("=" * 60)
    print("EXAMPLE 8: Error Handling")
    print("=" * 60)

    ingester = RepoIngester()

    try:
        # Try to ingest a non-existent repo
        summary, tree, content = ingester.ingest_repo(
            "https://github.com/nonexistent/repository-xyz-123"
        )
    except Exception as e:
        print(f"✓ Error caught properly: {type(e).__name__}")
        print(f"  Message: {str(e)[:100]}...")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("GITHUB REPOSITORY INGESTION - EXAMPLES")
    print("=" * 60 + "\n")

    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Private Repository", example_2_private_repo),
        ("Specific Subdirectory", example_3_specific_subdirectory),
        ("Multiple Paths", example_4_multiple_paths),
        ("Batch Repositories", example_5_batch_repos),
        ("Quick Functions", example_6_quick_functions),
        ("Custom Settings", example_7_custom_settings),
        ("Error Handling", example_8_error_handling),
    ]

    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()

    choice = input("Enter example number (1-8, or 'all' to run all): ").strip().lower()
    print()

    if choice == 'all':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}\n")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice. Please run again and select 1-8 or 'all'.")


if __name__ == "__main__":
    main()