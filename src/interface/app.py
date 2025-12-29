import streamlit as st
import requests
import os

# --- Configuration ---
API_URL = "http://localhost:3000/search"
PAGE_TITLE = "社会福祉士国家試験 法令検索AI (Rust Backend)"
PAGE_ICON = "⚖️"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# --- CSS Loading ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Note: Adjust path if necessary. Original logic used detailed paths.
# Assuming assets/custom.css exists relative to this file.
css_path = os.path.join(current_dir, "assets", "custom.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Header ---
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown("Backend migrated to **Rust** 🦀 for high-performance vector search.")
st.divider()

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Navigation ---
mode = st.sidebar.radio("モード選択", ["🔎 法令検索", "📖 法令閲覧 (全文)"])

if mode == "🔎 法令検索":
    # --- Search Interface ---
    with st.container():
        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([5, 1], gap="small")
        with col1:
            prompt = st.text_input(
                "質問を入力してください",
                placeholder="例: 生活保護の申請手続きについて / 高齢者虐待について",
                key="search_input",
                label_visibility="collapsed",
            )
        with col2:
            search_clicked = st.button("検索", type="primary", use_container_width=True)

    # --- Search Logic ---
    if (prompt and search_clicked) or (
        prompt and prompt != st.session_state.get("last_prompt", "")
    ):
        st.session_state.last_prompt = prompt
        st.session_state.messages.insert(0, {"role": "user", "content": prompt})

        with st.spinner("Running Search on Rust Backend..."):
            try:
                # Call Rust API
                response = requests.post(API_URL, json={"query": prompt}, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    intent_msg = data.get("intent")
                    targeted_laws = data.get("targeted_laws", [])

                    # AI Intent Info
                    if targeted_laws:
                        st.info(
                            f"💡 **AI Intent**: {intent_msg or 'Detected'} -> 限定検索: {', '.join(targeted_laws)}"
                        )

                    # HTML Formatting
                    if not results:
                        html_content = "<div class='law-card'>該当する条文が見つかりませんでした。</div>"
                    else:
                        html_content = f"<div class='result-stats'>関連条文 <b>{len(results)}件</b> Hit</div>"

                        for item in results:
                            doc_text = item.get("document", "")
                            metadata = item.get("metadata", {})
                            distance = item.get("distance", 1.0)
                            relevance = item.get("relevance", 0.0)

                            law_name = metadata.get("law_full_name", "Unknown Law")
                            article = metadata.get("article_number", "")

                            # Render Card
                            card = f"""<div class="law-card">
    <div class="law-card-header">
        <span class="law-name">{law_name}</span>
        <span class="law-article">{article}</span>
    </div>
    <div class="law-content">{doc_text}</div>
    <div class="relevance-container">
        <span class="relevance-tag">Relevance: {relevance:.1%}</span>
    </div>
</div>"""
                            html_content += card

                    st.session_state.messages.insert(
                        0, {"role": "assistant", "content": html_content}
                    )

                else:
                    st.error(f"Backend Error ({response.status_code}): {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to Backend. Is the Rust server running? (localhost:3000)"
                )
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

else:
    # --- Browse Mode ---
    st.header("📖 法令閲覧")

    # Fetch list of laws
    try:
        res = requests.get("http://localhost:3000/laws")
        if res.status_code == 200:
            law_list = res.json()
            selected_law = st.selectbox("閲覧する法令を選択", law_list)

            if selected_law:
                with st.spinner(f"{selected_law} を読み込み中..."):
                    res_content = requests.post(
                        "http://localhost:3000/laws/content",
                        json={"law_name": selected_law},
                    )
                    if res_content.status_code == 200:
                        articles = res_content.json().get("articles", [])

                        # --- Sorting ---
                        # Try to soft-sort by assuming logical order of retrieval or metadata
                        # Ideally, we would parse "第一条" etc, but for now let's trust the backend or sort by ID if possible
                        # Let's try to sort by 'id' if it exists in metadata or just keep as is if it looks OK.
                        # Simple alphanumeric sort of article_number might be better than random.
                        def sort_key(a):
                            # Try to extract number from article_number for sorting?
                            # e.g. "第一条" -> 1. Very hard to do perfectly with Kansuuji without library.
                            # Fallback: Sort by ID if available (often law_name + sequqence)
                            return a.get("metadata", {}).get("id", "")

                        # articles.sort(key=sort_key)
                        # (Keeping original order for now as Chroma often returns insertion order which is usually correct for single file ingestion)

                        # --- Sidebar TOC ---
                        st.sidebar.markdown("### 📑 条注目次")

                        toc_html = "<div style='max-height: 80vh; overflow-y: auto; font-size: 0.9em;'>"
                        for i, article in enumerate(articles):
                            meta = article.get("metadata", {})
                            art_num = meta.get("article_number", f"Article {i + 1}")
                            # Create a unique clean ID
                            anchor_id = f"art_{i}"

                            # Add link to sidebar (using HTML for better control if markdown fails, or just Markdown)
                            # Streamlit Sidebar Markdown links to main page anchors work in most versions.
                            st.sidebar.markdown(
                                f"[{art_num}](#{anchor_id})", unsafe_allow_html=True
                            )

                        st.success(f"{len(articles)} 条の条文を表示します。")

                        # Display Content
                        for i, article in enumerate(articles):
                            meta = article.get("metadata", {})
                            text = article.get("document", "")
                            art_num = meta.get("article_number", "条文")

                            # ID for anchor (not fully supported but good practice)
                            st.markdown(f"#### {art_num}")
                            st.text_area(
                                "内容",
                                text,
                                height=150,
                                key=f"text_{art_num}_{selected_law}",
                            )
                            st.divider()
                    else:
                        st.error("Failed to load content.")
        else:
            st.error("Failed to load law list from backend.")

    except Exception as e:
        st.error(f"Error: {e}")


# --- History ---
st.divider()
for msg in st.session_state.messages[:6]:
    if msg["role"] == "user":
        st.markdown(
            f"<div style='display:flex; justify-content:flex-end;'><div class='user-bubble'>{msg['content']}</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(msg["content"], unsafe_allow_html=True)
