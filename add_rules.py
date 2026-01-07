import streamlit as st
import json
import os

# -------------------------
# CONFIG (CLOUD-SAFE)
# -------------------------
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(
    REPO_ROOT,
    "Rules",
    "Textile_Exchange_Style_Guide_STRICT.json"
)

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def load_rules():
    """Load rules from JSON file"""
    if not os.path.exists(RULES_FILE):
        return {"terminology": [], "flag_only": []}
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rules(rules_data):
    """Save rules to JSON file"""
    os.makedirs(os.path.dirname(RULES_FILE), exist_ok=True)
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules_data, f, indent=2, ensure_ascii=False)

def display_rules(section_name, rules_data):
    """Display rules in Streamlit with edit/delete buttons"""
    st.subheader(section_name.capitalize())
    for idx, rule in enumerate(rules_data):
        cols = st.columns([5, 1, 1])
        with cols[0]:
            st.markdown(
                f"**Match:** {rule.get('match', '')}  \n"
                f"**Replacement:** {rule.get('replace_with', '')}  \n"
                f"**Message:** {rule.get('message', '')}  \n"
                f"**Severity:** {rule.get('severity', '')}"
            )
        with cols[1]:
            if st.button("Edit", key=f"edit_{section_name}_{idx}"):
                st.session_state.edit_rule = (section_name, idx)
                st.experimental_rerun()
        with cols[2]:
            if st.button("Delete", key=f"del_{section_name}_{idx}"):
                return "delete", section_name, idx
    return None, None, None

# -------------------------
# MAIN STREAMLIT APP
# -------------------------
st.title("📝 Textile Exchange Style Rules Editor")

# -------------------------
# DEBUG / STATUS (TEMPORARY BUT IMPORTANT)
# -------------------------
st.caption(f"📄 Rules file path: `{RULES_FILE}`")

if not os.path.exists(RULES_FILE):
    st.error("❌ Rules JSON file NOT found by Streamlit")
else:
    st.success("✅ Rules JSON file loaded successfully")

# -------------------------
# Load rules
# -------------------------
rules_data = load_rules()
terminology_rules = rules_data.get("terminology", [])
flag_only_rules = rules_data.get("flag_only", [])

# -------------------------
# Add new rule (at top)
# -------------------------
st.subheader("➕ Add New Rule")

with st.form("add_rule_form"):
    section = st.selectbox("Section", ["terminology", "flag_only"])
    match_text = st.text_input("Match text")
    replacement = st.text_input("Replacement (optional)")
    message = st.text_input("Message / Reasoning")
    severity = st.selectbox("Severity", ["advice", "warning", "error"])
    submitted = st.form_submit_button("Add Rule")

    if submitted:
        if not match_text or not message:
            st.error("Match and Message are required")
        else:
            new_rule = {
                "match": match_text.strip(),
                "replace_with": replacement.strip() if replacement else None,
                "message": message.strip(),
                "severity": severity
            }
            rules_data[section].insert(0, new_rule)
            save_rules(rules_data)
            st.success(f"✅ New rule added to `{section}`")
            st.experimental_rerun()

# -------------------------
# Display existing rules
# -------------------------
action, section, idx = display_rules("terminology", terminology_rules)
if not action:
    action, section, idx = display_rules("flag_only", flag_only_rules)

# -------------------------
# Handle delete
# -------------------------
if action == "delete":
    if section and idx is not None:
        rules_data[section].pop(idx)
        save_rules(rules_data)
        st.success("✅ Rule deleted")
        st.experimental_rerun()

# -------------------------
# Handle edit
# -------------------------
if "edit_rule" in st.session_state:
    section, idx = st.session_state.edit_rule
    rule = rules_data[section][idx]

    st.subheader(f"✏️ Edit Rule ({section}, #{idx + 1})")

    with st.form("edit_rule_form"):
        match_text = st.text_input("Match text", value=rule.get("match", ""))
        replacement = st.text_input(
            "Replacement (optional)",
            value=rule.get("replace_with", "") or ""
        )
        message = st.text_input("Message / Reasoning", value=rule.get("message", ""))
        severity = st.selectbox(
            "Severity",
            ["advice", "warning", "error"],
            index=["advice", "warning", "error"].index(
                rule.get("severity", "warning")
            )
        )
        submitted = st.form_submit_button("Update Rule")

        if submitted:
            rules_data[section][idx] = {
                "match": match_text.strip(),
                "replace_with": replacement.strip() if replacement else None,
                "message": message.strip(),
                "severity": severity
            }
            save_rules(rules_data)
            st.success("✅ Rule updated")
            del st.session_state.edit_rule
            st.experimental_rerun()
