"""
Unified Server - GitRepoExtractor + LinguaFix
A combined Streamlit application for repository ingestion and grammar correction
Uses modular grammar corrector with retry logic and proper error handling
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, Tuple
import streamlit as st
from dotenv import load_dotenv
import json

# Windows fix for asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Load environment variables
load_dotenv()

# Import gitingest
try:
    from gitingest import ingest
except ImportError:
    st.error("Please install gitingest: pip install gitingest")
    st.stop()

# Import grammar corrector module
try:
    from grammar_corrector import GrammarCorrector, GrammarCorrectionError
except ImportError:
    st.error("grammar_corrector.py module not found")
    st.stop()

# Cache file for storing settings
CACHE_FILE = ".unified_server_cache.json"

# Page configuration
st.set_page_config(
    page_title="Unified Server - Repo & Grammar",
    page_icon="🚀",
    layout="wide"
)


# Utility functions for caching
def load_cache():
    """Load cached values from file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache_data):
    """Save cache to file"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)


def save_github_token(token: str):
    """Save GitHub token to .env file"""
    env_path = Path('.env')

    # Read existing .env content
    existing_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_content[key.strip()] = value.strip()

    # Update token
    existing_content['GITHUB_TOKEN'] = token

    # Write back
    with open(env_path, 'w') as f:
        for key, value in existing_content.items():
            f.write(f"{key}={value}\n")

    # Reload environment
    load_dotenv(override=True)
    os.environ['GITHUB_TOKEN'] = token


def save_gemini_key(api_key: str):
    """Save Gemini API key to .env file"""
    env_path = Path('.env')

    # Read existing .env content
    existing_content = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_content[key.strip()] = value.strip()

    # Update API key
    existing_content['GEMINI_API_KEY'] = api_key

    # Write back
    with open(env_path, 'w') as f:
        for key, value in existing_content.items():
            f.write(f"{key}={value}\n")

    # Reload environment
    load_dotenv(override=True)
    os.environ['GEMINI_API_KEY'] = api_key


def ingest_repository(
    repo_url: str,
    subpath: Optional[str] = None,
    branch: Optional[str] = None,
    output_file: Optional[str] = None,
    include_submodules: bool = False,
    max_file_size: Optional[int] = None
) -> Tuple[str, str, str]:
    """Ingest a GitHub repository"""

    # Build full URL
    if subpath:
        subpath = subpath.strip('/')
        if branch:
            full_url = f"{repo_url}/tree/{branch}/{subpath}"
        else:
            full_url = f"{repo_url}/tree/main/{subpath}"
    else:
        full_url = f"{repo_url}/tree/{branch}" if branch else repo_url

    # Prepare ingest parameters
    ingest_params = {
        "source": full_url,
        "include_submodules": include_submodules,
    }

    if max_file_size:
        ingest_params["max_file_size"] = max_file_size

    # Perform ingestion
    summary, tree, content = ingest(**ingest_params)

    # Save to file if requested
    if output_file:
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

    return summary, tree, content


# Main app
def main():
    st.title("🚀 Unified Server")
    st.caption("Repository Extraction & Grammar Correction in One Place")

    # Load cache
    cache = load_cache()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose Feature",
        ["🗂️ GitRepo Extractor", "✍️ Grammar Correction", "⚙️ Settings", "ℹ️ About"]
    )

    # GitRepo Extractor Page
    if page == "🗂️ GitRepo Extractor":
        st.header("GitHub Repository Extractor")
        st.write("Extract and analyze GitHub repositories into text format")

        # Input fields
        repo_url = st.text_input(
            "Repository URL",
            value=cache.get('repo_url', ''),
            placeholder="https://github.com/user/repo",
            help="Full GitHub repository URL"
        )

        col1, col2 = st.columns(2)

        with col1:
            branch = st.text_input(
                "Branch (optional)",
                value=cache.get('branch', ''),
                placeholder="main",
                help="Leave empty for default branch"
            )

        with col2:
            subpath = st.text_input(
                "Subpath (optional)",
                value=cache.get('subpath', ''),
                placeholder="src/api",
                help="Specific directory within the repository"
            )

        output_folder = st.text_input(
            "Output Folder",
            value=cache.get('output_folder', './outputs'),
            help="Where to save the generated files"
        )

        # Advanced options
        with st.expander("Advanced Options"):
            include_submodules = st.checkbox(
                "Include Submodules",
                value=cache.get('include_submodules', False)
            )

            max_file_size = st.number_input(
                "Max File Size (bytes)",
                value=cache.get('max_file_size', 1000000),
                min_value=0,
                help="Maximum size per file in bytes (0 for no limit)"
            )

        if st.button("🚀 Generate Repository Digest", type="primary"):
            if not repo_url:
                st.error("Please enter a repository URL")
            else:
                # Ensure output folder exists
                os.makedirs(output_folder, exist_ok=True)

                # Generate output filename
                repo_name = repo_url.rstrip('/').split('/')[-1]
                parts = [repo_name]
                if branch:
                    parts.append(branch)
                if subpath:
                    subpath_clean = subpath.replace('/', '_')
                    parts.append(subpath_clean)
                output_file = os.path.join(output_folder, "_".join(parts) + "_digest.txt")

                # Save cache
                cache.update({
                    'repo_url': repo_url,
                    'branch': branch,
                    'subpath': subpath,
                    'output_folder': output_folder,
                    'include_submodules': include_submodules,
                    'max_file_size': max_file_size
                })
                save_cache(cache)

                # Perform ingestion
                with st.spinner("Processing repository..."):
                    try:
                        summary, tree, content = ingest_repository(
                            repo_url=repo_url,
                            subpath=subpath if subpath else None,
                            branch=branch if branch else None,
                            output_file=output_file,
                            include_submodules=include_submodules,
                            max_file_size=max_file_size if max_file_size > 0 else None
                        )

                        st.success(f"✅ Successfully generated repository digest!")
                        st.info(f"📄 Output saved to: {output_file}")

                        # Display results
                        st.subheader("Summary")
                        st.text(summary)

                        st.subheader("Directory Tree")
                        st.code(tree, language="text")

                        # Download button
                        with open(output_file, 'r', encoding='utf-8') as f:
                            file_content = f.read()

                        st.download_button(
                            label="📥 Download Digest",
                            data=file_content,
                            file_name=os.path.basename(output_file),
                            mime="text/plain"
                        )

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    # Grammar Correction Page
    elif page == "✍️ Grammar Correction":
        st.header("LinguaFix - Grammar Correction")
        st.write("Perfect your writing with AI-powered grammar correction")

        # Check if API key is set
        if not os.getenv('GEMINI_API_KEY'):
            st.warning("⚠️ Gemini API key not set. Please configure it in Settings.")

        sentence = st.text_area(
            "Enter text to correct",
            value=cache.get('last_sentence', ''),
            placeholder="Enter a sentence to correct, for example: 'he walk to the store yesteday.'",
            height=150,
            help="Type or paste the text you want to correct"
        )

        if st.button("✨ Fix Grammar", type="primary"):
            if not sentence or len(sentence.strip()) < 3:
                st.error("Please enter a sentence with at least 3 characters.")
            elif not os.getenv('GEMINI_API_KEY'):
                st.error("Please set your Gemini API key in Settings.")
            else:
                # Save to cache
                cache['last_sentence'] = sentence
                save_cache(cache)

                with st.spinner("Correcting grammar with retry logic..."):
                    try:
                        # Initialize grammar corrector
                        corrector = GrammarCorrector()

                        # Correct the sentence
                        result = corrector.correct(sentence)

                        if result["success"]:
                            st.success("✅ Grammar corrected!")

                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("Original")
                                st.info(result["original"])

                            with col2:
                                st.subheader("Corrected")
                                st.success(result["corrected"])
                        else:
                            st.error(f"❌ {result['error']}")

                    except GrammarCorrectionError as e:
                        st.error(f"❌ Grammar correction failed: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

    # Settings Page
    elif page == "⚙️ Settings":
        st.header("Settings")
        st.write("Configure API keys and preferences")

        # GitHub Token
        st.subheader("GitHub Token")
        st.write("Required for private repositories and higher rate limits")

        current_token = os.getenv('GITHUB_TOKEN', '')
        github_token = st.text_input(
            "GitHub Personal Access Token",
            value=current_token[:10] + "..." if current_token else "",
            type="password",
            help="Get from https://github.com/settings/personal-access-tokens"
        )

        if st.button("Save GitHub Token"):
            if github_token:
                save_github_token(github_token)
                st.success("✅ GitHub token saved successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid token")

        st.divider()

        # Gemini API Key
        st.subheader("Gemini API Key")
        st.write("Required for grammar correction feature")

        current_key = os.getenv('GEMINI_API_KEY', '')
        gemini_key = st.text_input(
            "Gemini API Key",
            value=current_key[:10] + "..." if current_key else "",
            type="password",
            help="Get from https://aistudio.google.com/apikey"
        )

        if st.button("Save Gemini API Key"):
            if gemini_key:
                save_gemini_key(gemini_key)
                st.success("✅ Gemini API key saved successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid API key")

        st.divider()

        # Cache management
        st.subheader("Cache Management")
        if st.button("🗑️ Clear Cache"):
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
                st.success("Cache cleared!")
                st.rerun()

    # About Page
    elif page == "ℹ️ About":
        st.header("About Unified Server")

        st.markdown("""
        ### 🚀 Features
        
        **GitRepo Extractor**
        - Extract entire GitHub repositories or specific directories
        - Support for public and private repositories
        - Branch-specific ingestion
        - Configurable file size limits
        - Generates comprehensive text digests
        
        **LinguaFix Grammar Correction**
        - AI-powered grammar correction using Google Gemini
        - **Retry logic with exponential backoff** for rate limit handling
        - Real-time text analysis
        - Simple and intuitive interface
        - Robust error handling
        
        ### 🔧 Technologies
        - **Streamlit** - Web interface
        - **gitingest** - Repository extraction
        - **Google Generative AI** - AI operations
        - **Python** - Backend processing
        - **Modular Architecture** - Separate grammar_corrector.py module
        
        ### ⚡ Rate Limit Handling
        
        The grammar corrector includes:
        - **Exponential backoff** - Progressively increases wait time
        - **Jitter** - Random variation to prevent synchronized retries
        - **3 retry attempts** - Automatic retry on rate limit errors
        - **Clear error messages** - Helpful feedback on quota issues
        
        ### 📝 Usage Tips
        
        1. **For Repository Extraction:**
           - Get a GitHub token from Settings for private repos
           - Use subpath to extract specific directories
           - Specify branch for version-specific extraction
        
        2. **For Grammar Correction:**
           - Configure Gemini API key in Settings
           - Enter text and click "Fix Grammar"
           - If rate limited, wait a moment and retry
           - Check quota at https://aistudio.google.com/
        
        ### 🔐 Privacy & Security
        - All API keys are stored locally in `.env` file
        - No data is sent to external servers except AI APIs
        - Cache is stored locally for convenience
        
        ### 🌟 Resource Optimization
        This unified server runs both features on a single local instance,
        optimizing system resources and simplifying management.
        """)


if __name__ == "__main__":
    main()