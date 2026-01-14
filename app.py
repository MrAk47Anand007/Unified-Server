"""
Unified Server - GitRepoExtractor + LinguaFix
A combined Streamlit application for repository ingestion and grammar correction
Uses modular grammar corrector with retry logic and proper error handling
"""

import os
import sys
import asyncio
import time
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import json
from code_editor import code_editor

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

# Import Script Runner
try:
    from script_runner import ScriptRunner
except ImportError:
    st.error("script_runner.py module not found")
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
        ["🗂️ GitRepo Extractor", "✍️ Grammar Correction", "🐍 Script Runner", "⚙️ Settings", "ℹ️ About"]
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
        st.header("✍️ LinguaFix - Grammar Correction")
        st.write("Perfect your writing with AI-powered grammar correction. Now supports paragraphs and long text!")

        # Check if API key is set
        if not os.getenv('GEMINI_API_KEY'):
            st.warning("⚠️ Gemini API key not set. Please configure it in Settings.")
            st.info("💡 Get your free API key from [Google AI Studio](https://aistudio.google.com/apikey)")

        sentence = st.text_area(
            "Enter text to correct",
            value=cache.get('last_sentence', ''),
            placeholder="Enter text to correct. Can be a single sentence, multiple sentences, or even full paragraphs.\n\nExample: 'he walk to the store yesteday. She dont like pizza. They was going too the park.'",
            height=250,
            help="Type or paste the text you want to correct. Supports multi-line text and paragraphs.",
            max_chars=5000
        )

        # Character count
        char_count = len(sentence)
        col_info1, col_info2 = st.columns([3, 1])
        with col_info2:
            st.caption(f"Characters: {char_count}/5000")

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

                            # Display results in expandable sections for better readability
                            col1, col2 = st.columns(2)

                            with col1:
                                st.subheader("📝 Original Text")
                                with st.container():
                                    st.text_area(
                                        "Original",
                                        value=result["original"],
                                        height=200,
                                        disabled=True,
                                        label_visibility="collapsed"
                                    )

                            with col2:
                                st.subheader("✨ Corrected Text")
                                with st.container():
                                    st.text_area(
                                        "Corrected",
                                        value=result["corrected"],
                                        height=200,
                                        disabled=True,
                                        label_visibility="collapsed"
                                    )

                            # Copy button for corrected text
                            st.download_button(
                                label="📋 Copy Corrected Text",
                                data=result["corrected"],
                                file_name="corrected_text.txt",
                                mime="text/plain",
                                help="Download the corrected text"
                            )
                        else:
                            st.error(f"❌ {result['error']}")

                    except GrammarCorrectionError as e:
                        st.error(f"❌ Grammar correction failed: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

    # Script Runner Page
    elif page == "🐍 Script Runner":
        # Compact header
        st.markdown("### 🐍 Python Script Runner")

        # Initialize Script Runner
        runner = ScriptRunner()

        # Sidebar: Collections & Navigation
        st.sidebar.markdown("---")

        # Search
        search_query = st.sidebar.text_input("🔍 Search Scripts", placeholder="Name or tag...")

        # Recent Scripts
        st.sidebar.subheader("🕒 Recent Scripts")
        all_scripts = runner.list_all_scripts()

        def get_mod_time(s):
            return s.get("modified", s.get("created", ""))

        recent_scripts = sorted(all_scripts, key=get_mod_time, reverse=True)[:5]

        for s in recent_scripts:
            if st.sidebar.button(f"{s['name']} ({s['collection']})", key=f"recent_{s['collection']}_{s['name']}"):
                loaded = runner.load_script(s["name"], s["collection"])
                if loaded:
                    st.session_state.current_script = {
                        "name": loaded["metadata"]["name"],
                        "code": loaded["code"],
                        "collection": s["collection"],
                        "description": loaded["metadata"].get("description", ""),
                        "tags": loaded["metadata"].get("tags", []),
                        "original_name": loaded["metadata"]["name"],
                        "original_collection": s["collection"]
                    }
                    # Clear output
                    if "last_result" in st.session_state:
                        del st.session_state.last_result
                    # Increment refresh counter to force editor reload
                    st.session_state.editor_refresh_counter = st.session_state.get('editor_refresh_counter', 0) + 1
                    st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.subheader("📁 Collections")

        collections = runner.collection_manager.list_collections()

        # 1. State Initialization
        if "current_script" not in st.session_state:
            # Try to load from cache
            sr_cache = cache.get('script_runner', {})
            last_collection = sr_cache.get('last_collection', 'Uncategorized')
            last_script = sr_cache.get('last_script', '')

            # Verify collection exists
            if last_collection not in collections:
                last_collection = "Uncategorized"

            initial_state = {
                "name": "",
                "code": "",
                "collection": last_collection,
                "description": "",
                "tags": [],
                "original_name": None,
                "original_collection": None
            }

            # If we have a last script, try to load it
            if last_script:
                loaded = runner.load_script(last_script, last_collection)
                if loaded:
                     initial_state = {
                        "name": loaded["metadata"]["name"],
                        "code": loaded["code"],
                        "collection": last_collection,
                        "description": loaded["metadata"].get("description", ""),
                        "tags": loaded["metadata"].get("tags", []),
                        "original_name": loaded["metadata"]["name"],
                        "original_collection": last_collection
                    }

            st.session_state.current_script = initial_state

        # 2. Sidebar Navigation Tree
        for col_name in collections:
            col_scripts = runner.collection_manager.get_scripts_in_collection(col_name)

            # Filter if search query exists
            if search_query:
                col_scripts = [s for s in col_scripts if search_query.lower() in s["name"].lower() or any(search_query.lower() in t.lower() for t in s.get("tags", []))]
                if not col_scripts:
                    continue # Skip empty collections during search

            with st.sidebar.expander(f"{col_name} ({len(col_scripts)})", expanded=(col_name == st.session_state.current_script["collection"] or bool(search_query))):

                # Button to select/create new in this collection (only show if not searching or matches logic?)
                # Keeping it always available in expander
                if st.button("➕ New Script", key=f"new_{col_name}"):
                    st.session_state.current_script = {
                        "name": "",
                        "code": "",
                        "collection": col_name,
                        "description": "",
                        "tags": [],
                        "original_name": None,
                        "original_collection": None
                    }
                    # Clear output
                    if "last_result" in st.session_state:
                        del st.session_state.last_result
                    # Increment refresh counter to force editor reload
                    st.session_state.editor_refresh_counter = st.session_state.get('editor_refresh_counter', 0) + 1
                    st.rerun()

                for s in col_scripts:
                    # Highlight active script
                    is_active = (s["name"] == st.session_state.current_script["name"] and col_name == st.session_state.current_script["collection"])
                    label = f"{'🟢 ' if is_active else ''}{s['name']}"

                    if st.button(label, key=f"nav_{col_name}_{s['name']}"):
                        loaded = runner.load_script(s["name"], col_name)
                        if loaded:
                            st.session_state.current_script = {
                                "name": loaded["metadata"]["name"],
                                "code": loaded["code"],
                                "collection": col_name,
                                "description": loaded["metadata"].get("description", ""),
                                "tags": loaded["metadata"].get("tags", []),
                                "original_name": loaded["metadata"]["name"],
                                "original_collection": col_name
                            }
                            # Clear output when switching scripts
                            if "last_result" in st.session_state:
                                del st.session_state.last_result
                            # Increment refresh counter to force editor reload
                            st.session_state.editor_refresh_counter = st.session_state.get('editor_refresh_counter', 0) + 1
                            # Update Cache
                            sr_cache = cache.get('script_runner', {})
                            sr_cache['last_collection'] = col_name
                            sr_cache['last_script'] = s["name"]
                            cache['script_runner'] = sr_cache
                            save_cache(cache)
                            st.rerun()

        st.sidebar.markdown("---")

        # Collection management in sidebar
        with st.sidebar.popover("➕ Create Collection"):
            new_col_name = st.text_input("Collection Name", placeholder="My Scripts")
            if st.button("Create"):
                if new_col_name:
                    if runner.collection_manager.create_collection(new_col_name):
                        st.sidebar.success(f"Created {new_col_name}")
                        st.rerun()
                    else:
                        st.error("Collection already exists")

        # 3. Main Area - Script Editor

        # Helper to determine if we are editing a new or existing script
        is_new_script = not st.session_state.current_script["name"]

        # Compact title and action buttons at top
        col_title, col_actions = st.columns([2, 3])
        with col_title:
            if is_new_script:
                st.markdown(f"**📝 New Script** in *{st.session_state.current_script['collection']}*")
            else:
                st.markdown(f"**📝 {st.session_state.current_script['name']}**")

        with col_actions:
            # Action buttons in one row at the top
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            with btn_col1:
                save_clicked = st.button("💾 Save", use_container_width=True)
            with btn_col2:
                run_clicked = st.button("▶️ Run", type="primary", use_container_width=True)
            with btn_col3:
                delete_clicked = st.button("🗑️ Delete", use_container_width=True)
            with btn_col4:
                clear_output_clicked = st.button("🧹 Clear Output", use_container_width=True)

        st.markdown("---")

        # Metadata section - more compact
        col_meta1, col_meta2, col_meta3, col_meta4 = st.columns([2, 2, 1.5, 2.5])
        with col_meta1:
            script_name = st.text_input("Name", value=st.session_state.current_script["name"], label_visibility="collapsed", placeholder="Script Name")
        with col_meta2:
            script_tags = st.text_input("Tags", value=",".join(st.session_state.current_script["tags"]), label_visibility="collapsed", placeholder="Tags (comma separated)")
        with col_meta3:
            # Collection Dropdown (Assignment)
            current_col_idx = 0
            if st.session_state.current_script["collection"] in collections:
                current_col_idx = collections.index(st.session_state.current_script["collection"])

            selected_collection = st.selectbox(
                "Collection",
                collections,
                index=current_col_idx,
                label_visibility="collapsed"
            )
        with col_meta4:
            script_desc = st.text_input("Description", value=st.session_state.current_script["description"], label_visibility="collapsed", placeholder="Description")

        # VS Code-like layout: Editor on left, Output on right
        editor_col, output_col = st.columns([1.2, 1])

        with editor_col:
            st.markdown("**💻 Code Editor**")

            # Configure code editor with modern features
            editor_btns = [{
                "name": "Copy",
                "feather": "Copy",
                "hasText": True,
                "alwaysOn": True,
                "commands": ["copyAll"],
                "style": {"top": "0.46rem", "right": "0.4rem"}
            }]

            # Generate unique key based on script identity to force reload
            script_key = f"{st.session_state.current_script['collection']}_{st.session_state.current_script.get('original_name', 'new')}_{st.session_state.get('editor_refresh_counter', 0)}"

            # Get current code from session state
            current_code = st.session_state.current_script.get("code", "")

            response_dict = code_editor(
                current_code,
                lang="python",
                height=[25, 35],  # min, max rows - taller for better coding
                theme="contrast",  # Modern dark theme
                shortcuts="vscode",  # VSCode-like shortcuts
                focus=False,
                buttons=editor_btns,
                allow_reset=True,
                key=f"code_editor_{script_key}",
                options={
                    "wrap": True,
                    "showLineNumbers": True,
                    "highlightActiveLine": True,
                    "showPrintMargin": False,
                    "fontSize": 14,
                    "enableBasicAutocompletion": True,
                    "enableLiveAutocompletion": True,
                    "enableSnippets": True,
                    "showGutter": True,
                    "displayIndentGuides": True,
                    "highlightSelectedWord": True,
                }
            )

            # Extract code from editor response
            if response_dict and "text" in response_dict:
                script_code = response_dict["text"]
            else:
                script_code = current_code

            # Compact input section
            st.markdown("**📥 Input (stdin)**")
            script_input = st.text_area(
                "stdin",
                height=100,
                placeholder="Enter input for script (if needed)",
                key="input_area",
                label_visibility="collapsed"
            )

        with output_col:
            st.markdown("**📊 Output Terminal**")

            # Output section with container for better visibility
            output_container = st.container()

            with output_container:
                if "last_result" in st.session_state:
                    result = st.session_state.last_result

                    # Status indicators
                    status_col1, status_col2 = st.columns(2)
                    with status_col1:
                        if result.get("success"):
                            st.success("✅ Success", icon="✅")
                        else:
                            st.error("❌ Failed", icon="❌")
                    with status_col2:
                        exec_time = result.get("execution_time", 0)
                        st.info(f"⏱️ {exec_time:.4f}s", icon="⏱️")

                    st.markdown("---")

                    # Output display with better visibility
                    stdout_content = result.get("stdout", "")
                    stderr_content = result.get("stderr", "")
                    error_content = result.get("error", None)
                    return_value = result.get("result", None)

                    if stdout_content:
                        st.markdown("**📤 Standard Output:**")
                        st.code(stdout_content, language="text")

                    if stderr_content:
                        st.markdown("**⚠️ Error Output:**")
                        st.code(stderr_content, language="text")

                    if error_content:
                        st.error(f"**💥 Error:** {error_content}")

                    if return_value is not None:
                        st.markdown("**↩️ Return Value:**")
                        st.code(str(return_value), language="python")

                # Download output
                output_content = f"""Execution Report
Date: {datetime.now().isoformat()}
Status: {'Success' if result['success'] else 'Failed'}
Execution Time: {result['execution_time']:.4f}s

--- STDOUT ---
{result['stdout']}

--- STDERR ---
{result['stderr']}

--- RESULT ---
{result['result']}

--- ERROR ---
{result.get('error', 'None')}
"""
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download Output",
                        data=output_content,
                        file_name=f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    # No output yet - show helpful message
                    st.info("👉 Click **Run** to execute your script", icon="▶️")
                    st.markdown("---")
                    st.markdown("""
                    **Terminal Ready:**
                    - Write your Python code in the editor
                    - Click the ▶️ Run button
                    - Watch output appear here in real-time
                    - Use `print()` for output
                    - Provide input via stdin box
                    """)

        # Update session state with edits
        st.session_state.current_script["name"] = script_name
        st.session_state.current_script["code"] = script_code
        st.session_state.current_script["description"] = script_desc
        st.session_state.current_script["tags"] = [t.strip() for t in script_tags.split(",") if t.strip()]
        st.session_state.current_script["collection"] = selected_collection

        # Handle button actions
        if save_clicked:
            if not script_name:
                st.error("⚠️ Please provide a script name")
            else:
                # Check for Move/Rename
                orig_name = st.session_state.current_script.get("original_name")
                orig_col = st.session_state.current_script.get("original_collection")

                # Update session state code before saving
                st.session_state.current_script["code"] = script_code

                save_result = runner.save_script(
                    script_name,
                    script_code,
                    selected_collection,
                    script_desc,
                    st.session_state.current_script["tags"]
                )

                if save_result:
                    # Get the saved path
                    clean_name = "".join(c for c in script_name if c.isalnum() or c in ('-', '_')).strip()
                    saved_path = f"./scripts/{selected_collection}/{clean_name}.py"

                    # Verify file was actually created
                    import os
                    if os.path.exists(saved_path):
                        file_size = os.path.getsize(saved_path)

                        # If successful save, check if we need to delete the old one
                        if orig_name and orig_col:
                            if orig_name != script_name or orig_col != selected_collection:
                                runner.delete_script(orig_name, orig_col)
                                st.success(f"✅ Moved script from `{orig_col}/{orig_name}` to `{selected_collection}/{script_name}`\n\n📁 Saved at: `{saved_path}` ({file_size} bytes)")
                        else:
                            st.success(f"✅ Script saved successfully!\n\n📁 Location: `{saved_path}`\n💾 Size: {file_size} bytes")

                        # Update state to reflect new identity
                        st.session_state.current_script["original_name"] = script_name
                        st.session_state.current_script["original_collection"] = selected_collection
                        st.session_state.current_script["name"] = script_name
                        st.session_state.current_script["collection"] = selected_collection

                        # Increment refresh counter to force editor reload
                        st.session_state.editor_refresh_counter = st.session_state.get('editor_refresh_counter', 0) + 1

                        time.sleep(1.5)  # Show message briefly
                        st.rerun()
                    else:
                        st.error(f"❌ Save reported success but file not found at: `{saved_path}`")
                else:
                    st.error(f"❌ Failed to save script to collection '{selected_collection}'. Check if collection exists.")

        if run_clicked:
            # Show live execution feedback
            with st.spinner("⚙️ Executing script... Please wait"):
                try:
                    # Execute the script
                    result = runner.execute_script(script_code, script_input)
                    st.session_state.last_result = result

                    # Show immediate feedback
                    if result.get("success"):
                        st.toast("✅ Script executed successfully!", icon="✅")
                    else:
                        st.toast("❌ Script execution failed", icon="❌")

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Execution error: {str(e)}")
                    st.session_state.last_result = {
                        "success": False,
                        "stdout": "",
                        "stderr": str(e),
                        "error": f"Execution failed: {str(e)}",
                        "result": None,
                        "execution_time": 0
                    }
                    st.rerun()

        if delete_clicked:
            current_script_name = st.session_state.current_script["name"]
            if not current_script_name:
                st.warning("⚠️ Cannot delete unsaved script")
            else:
                # Use original collection if available, else current
                target_collection = st.session_state.current_script.get("original_collection") or selected_collection
                target_name = st.session_state.current_script.get("original_name") or current_script_name

                if runner.delete_script(target_name, target_collection):
                    st.success(f"✅ Deleted `{target_name}` from `{target_collection}`")
                    # Reset state
                    st.session_state.current_script = {
                        "name": "",
                        "code": "",
                        "collection": "Uncategorized",
                        "description": "",
                        "tags": [],
                        "original_name": None,
                        "original_collection": None
                    }
                    if "last_result" in st.session_state:
                        del st.session_state.last_result
                    st.rerun()
                else:
                    st.error("❌ Failed to delete script")

        if clear_output_clicked:
            if "last_result" in st.session_state:
                del st.session_state.last_result
                st.rerun()
            else:
                st.info("ℹ️ No output to clear")

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
        
        **LinguaFix Grammar Correction** (Enhanced!)
        - ✨ AI-powered grammar correction using Google Gemini 2.5 Flash
        - 📄 **Now supports long text and multi-paragraph content** (up to 5000 characters)
        - 🔄 Retry logic with exponential backoff for rate limit handling
        - 📊 Real-time character count
        - 💾 Download corrected text
        - 🎨 Side-by-side comparison view
        - 🚀 Robust error handling with helpful feedback
        
        **Python Script Runner** (Modernized!)
        - 🎨 **Modern Code Editor** with syntax highlighting, line numbers, and autocomplete
        - 📦 Organize scripts into collections (Postman-like)
        - 🔒 Secure sandboxed execution environment
        - 📊 Capture stdout, stderr, and return values
        - ⌨️ VSCode-like keyboard shortcuts
        - 🎯 Smart autocompletion and code snippets
        - 📝 Script tagging and search functionality

        ### 🔧 Technologies
        - **Streamlit** - Web interface
        - **gitingest** - Repository extraction
        - **Google Generative AI** - AI operations
        - **Python** - Backend processing
        - **Modular Architecture** - Separate grammar_corrector.py and script_runner.py modules
        
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