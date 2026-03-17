import streamlit as st
import re
from collections import defaultdict

from login import login_page
from email_service import fetch_all_accounts
from classifiers import predict_email
from text_summarizer import summarize_text
from voice_reader import speak_or_stop

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Smart Unified Email Aggregator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Session state
# -----------------------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("raw_emails", None)
st.session_state.setdefault("feedback", {})
st.session_state.setdefault("shown_reminders", set())

# =============================
# LOGIN
# =============================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# =============================
# HELPERS
# =============================
@st.cache_data(ttl=600)
def cached_fetch():
    return fetch_all_accounts()

@st.cache_data(ttl=600)
def cached_predict(mail):
    return predict_email(mail)

def clean_text(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()

def is_urgent_email(text):
    urgent_keywords = [
        "urgent", "deadline", "today", "immediately",
        "meeting", "submit", "invoice", "payment", "asap"
    ]
    text = text.lower()
    return any(word in text for word in urgent_keywords)

priority_rank = {"high": 0, "normal": 1, "low": 2}

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.title("📧 Smart Email Aggregator")

    refresh = st.button("🔄 Fetch / Refresh Emails", use_container_width=True)

    st.markdown("### Filters")
    show_high = st.checkbox("High Priority", True)
    show_personal = st.checkbox("Personal", True)
    show_promo = st.checkbox("Promotions", True)
    show_spam = st.checkbox("Spam", True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =============================
# FETCH EMAILS
# =============================
if refresh or st.session_state.raw_emails is None:
    st.session_state.raw_emails = cached_fetch()

raw_emails = st.session_state.raw_emails or []

# =============================
# PROCESS EMAILS
# =============================
processed = []
stats = defaultdict(int)

for i, mail in enumerate(raw_emails):
    cls = cached_predict(mail)
    item = {**mail, **cls}
    item["id"] = i

    body_text = clean_text(mail.get("body", ""))
    item["summary"] = summarize_text(body_text)

    if i in st.session_state.feedback:
        fb = st.session_state.feedback[i]
        item["category"] = fb
        item["priority"] = "high" if fb == "important" else "normal"

    processed.append(item)

    stats["total"] += 1
    stats[item["category"]] += 1
    if item["priority"] == "high":
        stats["high_priority"] += 1

processed.sort(
    key=lambda m: (
        priority_rank.get(m.get("priority", "normal"), 1),
        -m.get("confidence", 0),
    )
)

providers = sorted({m["account_label"] for m in processed})

# =============================
# METRICS
# =============================
st.markdown("## 📊 Inbox Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Emails", stats["total"])
c2.metric("High Priority", stats["high_priority"])
c3.metric("Promotions", stats["promotion"])
c4.metric("Spam", stats["spam"])
st.markdown("---")

# =============================
# SEARCH & FILTER
# =============================
col1, col2 = st.columns([2, 1])
with col1:
    search = st.text_input("🔍 Search emails")
with col2:
    provider_filter = st.selectbox("Filter by Provider", ["All"] + providers)

def visible(m):
    if provider_filter != "All" and m["account_label"] != provider_filter:
        return False
    if m["priority"] == "high" and not show_high:
        return False
    if m["category"] == "personal" and not show_personal:
        return False
    if m["category"] == "promotion" and not show_promo:
        return False
    if m["category"] == "spam" and not show_spam:
        return False
    if search and search.lower() not in (m["subject"] + m["sender"] + clean_text(m["body"])).lower():
        return False
    return True

filtered = [m for m in processed if visible(m)]

# =============================
# IMPORTANT EMAIL REMINDER POP-UP
# =============================
for m in filtered:
    if (
        m["priority"] == "high"
        and m["category"] == "important"
        and is_urgent_email(m.get("subject", "") + " " + m.get("summary", ""))
        and m["id"] not in st.session_state.shown_reminders
    ):
        st.warning(
            f"⚠️ IMPORTANT REMINDER\n\n"
            f"📧 Subject: {m['subject']}\n\n"
            f"📝 {m['summary']}",
            icon="⏰"
        )
        st.session_state.shown_reminders.add(m["id"])
        break

# =============================
# DISPLAY EMAILS
# =============================
for m in filtered:
    is_high = m["priority"] == "high"

    st.markdown(
        f"""
        <div style="padding:14px;
                    border-radius:8px;
                    border:{'2px solid #f4c542' if is_high else '1px solid #ddd'};
                    margin-bottom:6px;">
        <b>{m['subject']}</b><br>
        <span style="color:#555;font-size:13px;">
        From: {m['sender']} | {m['account_label']} | {m['date']}
        </span><br>
        Category: <b>{m['category']}</b> |
        Priority: <b>{m['priority']}</b> |
        Confidence: <b>{round(m['confidence'],2)}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([10, 1])

    with colA:
        st.markdown(
            f"""
            <div style="padding:10px;background:#eef6ff;
                        border-left:4px solid #3b82f6;
                        border-radius:6px;">
            🤖 <b>Summary</b><br>
            {m['summary'] or m['snippet']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📖 Read full email"):
            full_body = clean_text(m.get("body", ""))
            if full_body:
                st.text(full_body)
            else:
                st.info("No email body available.")

    with colB:
        voice_slot = st.empty()
        voice_slot.button(
            "🔊",
            key=f"voice-{m['id']}",
            on_click=speak_or_stop,
            args=(m['summary'] or m['snippet'],),
        )

    b1, b2, b3, b4 = st.columns(4)
    mid = m["id"]

    if b1.button("🚫 Spam", key=f"spam-{mid}"):
        st.session_state.feedback[mid] = "spam"
        st.rerun()

    if b2.button("📢 Promo", key=f"promo-{mid}"):
        st.session_state.feedback[mid] = "promotion"
        st.rerun()

    if b3.button("👤 Personal", key=f"personal-{mid}"):
        st.session_state.feedback[mid] = "personal"
        st.rerun()

    if b4.button("⭐ Important", key=f"important-{mid}"):
        st.session_state.feedback[mid] = "important"
        st.rerun()
