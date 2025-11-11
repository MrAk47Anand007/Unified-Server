# app.py
"""
Streamlit UI for GitHub Repository Ingestion (with persistent cache)
- Uses your existing repo_ingest.ingest_repository or RepoIngester if available.
- Settings page to change GitHub token (stored in .env)
- Inputs: repo URL, branch, subpath, output folder, include options
- Generate button runs ingestion synchronously and shows logs + output text
- Persistent JSON cache (.repo_ingest_cache.json) to remember non-sensitive fields across restarts
"""

import os
import sys
import json
import traceback
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values

# -------------------------
# Configuration / Constants
# -------------------------
CACHE_FILE = ".repo_ingest_cache.json"
load_dotenv()
ENV_PATH = find_dotenv() or ".env"

if sys.platform == "win32":
    import asyncio
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        # ignore if policy cannot be set for some reason
        pass

# -------------------------
# Try to import ingestion backends
# -------------------------
_ingest_func = None
_ingester_class = None
try:
    from repo_ingest import ingest_repository as _imported_ingest_repository  # CLI file
    _ingest_func = _imported_ingest_repository
except Exception:
    try:
        from repo_ingester import RepoIngester as _imported_repo_ingester
        _ingester_class = _imported_repo_ingester
    except Exception:
        try:
            from repo_ingester import ingest_repo_branch as _imported_ingest_repo_branch
            _ingest_func = _imported_ingest_repo_branch
        except Exception:
            _ingest_func = None
            _ingester_class = None

# -------------------------
# Cache helpers
# -------------------------
DEFAULT_CACHE = {
    "repo_url": "https://github.com/MrAk47Anand007/QuickComm---Hyperlocal-Quick-Commerce-Platform",
    "branch": "dev",
    "subpath": "backend",
    "output_folder": str(Path.cwd()),
    "output_filename": "",
    "include_submodules": False,
    "include_gitignored": False,
    "max_file_size": 0
}

def load_cache() -> dict:
    """Load cache from CACHE_FILE, falling back to defaults."""
    try:
        p = Path(CACHE_FILE)
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge defaults -> data to ensure keys exist
            merged = DEFAULT_CACHE.copy()
            merged.update({k: v for k, v in data.items() if k in merged})
            return merged
        else:
            return DEFAULT_CACHE.copy()
    except Exception as e:
        # If cache corrupted, ignore and return defaults
        st.warning(f"Warning: failed to load cache ({e}). Using defaults.")
        return DEFAULT_CACHE.copy()

def save_cache(values: dict):
    """Save provided values (only allowed keys) into CACHE_FILE."""
    try:
        allowed = {k: DEFAULT_CACHE[k] for k in DEFAULT_CACHE.keys()}
        # sanitize incoming values - keep only allowed keys
        to_save = {k: values.get(k, allowed[k]) for k in allowed.keys()}
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
    except Exception as e:
        st.error(f"Failed to write cache: {e}")

def clear_cache():
    p = Path(CACHE_FILE)
    if p.exists():
        p.unlink()

# -------------------------
# .env token helper
# -------------------------
def save_token_to_env(token: str):
    """Save GITHUB_TOKEN to .env (create if needed)."""
    token = token.strip()
    if not ENV_PATH or ENV_PATH == "":
        # create .env file
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"GITHUB_TOKEN={token}\n")
        set_result = True
    else:
        try:
            set_key(ENV_PATH, "GITHUB_TOKEN", token)
            set_result = True
        except Exception:
            # fallback: append or overwrite manually
            vals = dotenv_values(ENV_PATH)
            d = dict(vals)
            d["GITHUB_TOKEN"] = token
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                for k, v in d.items():
                    f.write(f"{k}={v}\n")
            set_result = True
    # reload env
    load_dotenv(override=True)
    os.environ["GITHUB_TOKEN"] = token
    return set_result

# -------------------------
# Utility functions for ingestion calls (try multiple signatures)
# -------------------------
def validate_repo_url(url: str) -> bool:
    return url.startswith("https://github.com/")

def ensure_output_dir(path: str) -> Path:
    p = Path(path)
    if p.exists():
        if p.is_file():
            raise ValueError("Output folder path points to a file, not a directory.")
        return p
    else:
        p.mkdir(parents=True, exist_ok=True)
        return p

def run_ingest_using_function(func, repo_url, token, subpath, branch, output_file, include_submodules, include_gitignored, max_file_size, logger):
    # Try calling function with a flexible approach
    try:
        kwargs = {
            "repo_url": repo_url,
            "token": token,
            "subpath": subpath,
            "branch": branch,
            "output_file": output_file,
            "include_submodules": include_submodules,
            "include_gitignored": include_gitignored,
            "max_file_size": max_file_size
        }
        # filter None values
        call_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        logger.write("Calling ingestion function with flexible kwargs...\n")
        return func(**call_kwargs)
    except TypeError as e:
        logger.write(f"Full-kwargs call failed: {e}\nTrying simpler signatures...\n")
    except Exception as e:
        logger.write(f"Error while calling ingestion function: {e}\n")
        raise

    # try signature: func(repo_url, token, subpath, output_file)
    try:
        logger.write("Trying signature: func(repo_url, token, subpath, output_file)\n")
        return func(repo_url, token, subpath, output_file)
    except Exception as e:
        logger.write(f"Signature attempt failed: {e}\n")
        raise

def run_ingest_using_class(cls, repo_url, token, subpath, branch, output_file, include_submodules, include_gitignored, max_file_size, logger):
    # instantiate class
    try:
        ing = cls(token=token)
    except Exception as e:
        logger.write(f"Failed to instantiate ingester class: {e}\n")
        raise
    # call ingest_repo, try with branch first
    try:
        logger.write("Calling ingester.ingest_repo(...)\n")
        return ing.ingest_repo(repo_url=repo_url, subpath=subpath, branch=branch, output_file=output_file, include_submodules=include_submodules, max_file_size=max_file_size)
    except TypeError:
        logger.write("ingest_repo signature doesn't accept 'branch' — trying without branch...\n")
        return ing.ingest_repo(repo_url=repo_url, subpath=subpath, output_file=output_file, include_submodules=include_submodules, max_file_size=max_file_size)
    except Exception as e:
        logger.write(f"Error in ingester.ingest_repo: {e}\n")
        raise

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Repo Ingestor — GUI", layout="wide")
st.title("🔎 GitHub Repository Ingestion (GUI)")

# Load cache and initialize session_state defaults
cache_values = load_cache()
for k, v in cache_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Top-level navigation
nav = st.sidebar.radio("Navigation", ["Ingest", "Settings", "About", "Cache"])

if nav == "Settings":
    st.header("Settings")
    st.markdown("Change GitHub token (stored in `.env`). The token will be available to ingestion calls.")
    current_token = os.getenv("GITHUB_TOKEN", "")
    token_input = st.text_input("GitHub Personal Access Token", value=current_token, type="password")
    if st.button("Save token to .env"):
        if token_input.strip() == "":
            st.warning("Token is empty — nothing saved.")
        else:
            try:
                save_token_to_env(token_input)
                st.success("Token saved to .env and environment (GITHUB_TOKEN).")
            except Exception as e:
                st.error(f"Failed to save token: {e}")
    st.markdown("---")
    st.markdown("Detected ingestion backend:")
    st.write(f"- ingest function available: {'Yes' if _ingest_func else 'No'}")
    st.write(f"- RepoIngester class available: {'Yes' if _ingester_class else 'No'}")
    st.info("This UI will prefer `ingest_repository` (from repo_ingest.py) then fallback to `RepoIngester` class.")

elif nav == "About":
    st.header("About")
    st.markdown(
        """
        This Streamlit UI lets you ingest GitHub repositories using your project's ingestion functions.
        Features:
        - Enter repo URL, branch, subpath
        - Choose output folder / name
        - Save GitHub token to .env (token is not stored in the JSON cache)
        - Generate and view resulting text digest
        - Download the generated file
        - Persistent cache for non-sensitive fields (stored in .repo_ingest_cache.json)
        """
    )
    st.markdown("---")
    st.markdown("If your ingestion functions live in a different module name, please adjust the import in this app (`app.py`).")

elif nav == "Cache":
    st.header("Cache (persistent values)")
    st.markdown("This cache stores non-sensitive fields so the form remembers them across restarts.")
    st.write(json.dumps(load_cache(), indent=2))
    if st.button("Clear cached values"):
        clear_cache()
        st.success("Cache cleared. Reload the app to see defaults.")
    st.markdown("---")
    st.markdown("Note: GitHub token is not cached here. Use Settings to save token to `.env`.")

else:
    # Ingest page
    st.header("Ingest repository")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        repo_url = st.text_input("Repository URL", value=st.session_state.get("repo_url", DEFAULT_CACHE["repo_url"]), key="repo_url")
        branch = st.text_input("Branch (leave empty for default/main)", value=st.session_state.get("branch", DEFAULT_CACHE["branch"]), key="branch")
        subpath = st.text_input("Subpath (optional)", value=st.session_state.get("subpath", DEFAULT_CACHE["subpath"]), key="subpath")
        token = st.text_input("GitHub Token (optional - overrides .env)", value=os.getenv("GITHUB_TOKEN", ""), type="password")
        include_submodules = st.checkbox("Include submodules", value=st.session_state.get("include_submodules", False), key="include_submodules")
        include_gitignored = st.checkbox("Include gitignored files", value=st.session_state.get("include_gitignored", False), key="include_gitignored")
        max_file_size = st.number_input("Max file size per file (bytes, 0 for no limit)", value=st.session_state.get("max_file_size", 0), step=1, min_value=0, key="max_file_size")
        st.markdown("**Output destination**")
        output_folder = st.text_input("Output folder (will be created if missing)", value=st.session_state.get("output_folder", str(Path.cwd())), key="output_folder")
        output_filename = st.text_input("Output filename (optional)", value=st.session_state.get("output_filename", ""), key="output_filename")
        if output_filename.strip() == "":
            preview_name = Path(repo_url.rstrip('/').split('/')[-1]) if repo_url else Path("repo")
            parts = [preview_name.name]
            if branch:
                parts.append(branch)
            if subpath:
                parts.append(subpath.replace("/", "_"))
            preview = "_".join([p for p in parts if p]) + "_digest.txt"
            st.caption(f"Auto-generated if filename left blank: `{preview}`")

    with col_right:
        st.markdown("### Actions")
        generate = st.button("▶️ Generate", key="generate")
        create_folder = st.button("📁 Create output folder", key="create_folder")
        st.markdown("---")
        st.markdown("Help & tips")
        st.markdown("- Make sure `repo_ingest.py` or `repo_ingester.py` is in the same folder as this app.")
        st.markdown("- If your repo is private, set the token either in Settings or in the token field above.")
        st.markdown("- This runs synchronously — large repos can take some time.")

    # Create output folder if asked
    if create_folder:
        try:
            ensure_output_dir(output_folder)
            # Save cache after creating folder
            save_cache({
                "repo_url": repo_url,
                "branch": branch,
                "subpath": subpath,
                "output_folder": output_folder,
                "output_filename": output_filename,
                "include_submodules": include_submodules,
                "include_gitignored": include_gitignored,
                "max_file_size": max_file_size
            })
            st.success(f"Folder ready: {output_folder} (cache updated)")
        except Exception as e:
            st.error(f"Failed to create folder: {e}")

    # Perform generate
    if generate:
        st.info("Starting ingestion... logs will appear below.")
        log_area = st.empty()
        progress = st.progress(0)

        class Logger:
            def __init__(self):
                self._lines = []
            def write(self, s):
                if s is None:
                    return
                self._lines.append(str(s))
                log_area.text("\n".join(self._lines))
            def get_text(self):
                return "\n".join(self._lines)

        logger = Logger()

        # validation
        if not validate_repo_url(repo_url):
            st.error("Repository URL must start with https://github.com/")
        else:
            try:
                # ensure folder exists
                out_dir = ensure_output_dir(output_folder)
                if output_filename.strip():
                    out_path = out_dir / output_filename
                else:
                    repo_name = repo_url.rstrip('/').split('/')[-1]
                    parts = [repo_name]
                    if branch:
                        parts.append(branch)
                    if subpath:
                        parts.append(subpath.replace("/", "_"))
                    out_path = out_dir / ("_".join([p for p in parts if p]) + "_digest.txt")

                # Save cache (persist non-sensitive inputs)
                save_cache({
                    "repo_url": repo_url,
                    "branch": branch,
                    "subpath": subpath,
                    "output_folder": output_folder,
                    "output_filename": output_filename,
                    "include_submodules": include_submodules,
                    "include_gitignored": include_gitignored,
                    "max_file_size": max_file_size
                })

                progress.progress(5)
                logger.write(f"Using output file: {out_path}\n")
                # override environment token if provided
                if token:
                    os.environ["GITHUB_TOKEN"] = token
                    logger.write("Using token from UI (overrides .env)\n")
                else:
                    tkn = os.getenv("GITHUB_TOKEN")
                    if tkn:
                        logger.write("Using token from environment (.env)\n")
                progress.progress(10)

                # call available backend
                result = None
                if _ingest_func:
                    logger.write("Detected ingestion function. Calling it...\n")
                    result = run_ingest_using_function(_ingest_func, repo_url, token or os.getenv("GITHUB_TOKEN", None), subpath or None, branch or None, str(out_path), include_submodules, include_gitignored, None if max_file_size == 0 else max_file_size, logger)
                elif _ingester_class:
                    logger.write("Detected RepoIngester class. Instantiating and calling...\n")
                    result = run_ingest_using_class(_ingester_class, repo_url, token or os.getenv("GITHUB_TOKEN", None), subpath or None, branch or None, str(out_path), include_submodules, include_gitignored, None if max_file_size == 0 else max_file_size, logger)
                else:
                    st.error("No ingestion backend detected. Place `repo_ingest.py` or `repo_ingester.py` in the same folder and restart the app.")
                    raise RuntimeError("No ingestion backend available")

                progress.progress(80)
                logger.write("Ingestion call finished. Preparing output preview...\n")

                # If the backend returned tuple (summary, tree, content) we can also display & write file if missing
                if isinstance(result, tuple) and len(result) >= 3:
                    summary, tree, content = result[:3]
                    if not out_path.exists():
                        logger.write("Backend didn't write output file — writing file from returned content...\n")
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write("="*80 + "\nREPOSITORY DIGEST\n" + "="*80 + "\n\n")
                            f.write(f"Repository: {repo_url}\n\n")
                            f.write("="*80 + "\nSUMMARY\n" + "="*80 + "\n\n")
                            f.write(summary + "\n\n")
                            f.write("="*80 + "\nDIRECTORY TREE\n" + "="*80 + "\n\n")
                            f.write(tree + "\n\n")
                            f.write("="*80 + "\nCONTENT\n" + "="*80 + "\n\n")
                            f.write(content)
                    preview_text = ""
                    try:
                        preview_text = out_path.read_text(encoding="utf-8")
                    except Exception as e:
                        preview_text = f"(Failed to read output file: {e})"
                else:
                    # backend may have already written file; try to read
                    try:
                        preview_text = out_path.read_text(encoding="utf-8")
                    except Exception as e:
                        preview_text = f"(No readable output file at {out_path}: {e})"

                progress.progress(95)
                logger.write("Done.\n")
                progress.progress(100)

                # Show results
                st.success("Ingestion complete.")
                st.markdown(f"**Output file:** `{out_path}`")
                try:
                    st.download_button("⬇️ Download output", data=preview_text.encode("utf-8"), file_name=out_path.name, mime="text/plain")
                except Exception:
                    st.warning("Download not available (large content?). You can open the file directly from disk.")

                # Text viewer with folding / large content handling
                with st.expander("View output text", expanded=True):
                    max_preview_chars = 200_000
                    if len(preview_text) > max_preview_chars:
                        st.warning("Output is large — showing beginning and end. Use download to get full file.")
                        st.text(preview_text[:100000])
                        st.markdown("---")
                        st.text(preview_text[-100000:])
                    else:
                        st.text(preview_text)

            except Exception as e:
                tb = traceback.format_exc()
                st.error(f"Ingestion failed: {e}")
                st.code(tb)
                logger.write(f"Exception:\n{tb}\n")
