import streamlit as st
import json
import os

# -------------------------
# CONFIG
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(BASE_DIR, "Rules", "Textile_Exchange_Style_Guide_STRICT.json")

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
                return "edit", section_name, idx
        with cols[2]:
            if st.button("Delete", key=f"del_{section_name}_{idx}"):
                return "delete", section_name, idx
    return None, None, None

# -------------------------
# MAIN STREAMLIT APP
# -------------------------
st.title("Textile Exchange Style Rules Editor")

rules_data = load_rules()

# -------------------------
# Add new rule (moved to top)
# -------------------------
st.subheader("Add new rule")
new_section = st.selectbox("Section", ["terminology","flag_only"])
new_match = st.text_input("Match word or phrase")
new_replace = st.text_input("Replacement (optional)")
new_message = st.text_input("Message / Reasoning")
new_severity = st.selectbox("Severity", ["advice","warning","error"], index=1)
if st.button("Add Rule"):
    if not new_match or not new_message:
        st.error("Match and Message are required")
    else:
        new_rule = {
            "match": new_match,
            "replace_with": new_replace if new_replace else None,
            "message": new_message,
            "severity": new_severity
        }
        rules_data[new_section].append(new_rule)
        save_rules(rules_data)
        st.success("New rule added!")
        st.experimental_rerun()

# -------------------------
# Display existing rules
# -------------------------
action, section, idx = display_rules("terminology", rules_data.get("terminology", []))
if not action:
    action, section, idx = display_rules("flag_only", rules_data.get("flag_only", []))

# -------------------------
# Handle delete
# -------------------------
if action == "delete":
    if section and idx is not None:
        rules_data[section].pop(idx)
        save_rules(rules_data)
        st.experimental_rerun()

# -------------------------
# Handle edit
# -------------------------
if action == "edit":
    rule = rules_data[section][idx]
    st.subheader(f"Edit rule: {rule.get('match','')}")
    match = st.text_input("Match", value=rule.get("match",""))
    replace_with = st.text_input("Replacement", value=rule.get("replace_with",""))
    message = st.text_input("Message", value=rule.get("message",""))
    severity = st.selectbox(
        "Severity",
        ["advice","warning","error"],
        index=["advice","warning","error"].index(rule.get("severity","warning"))
    )
    if st.button("Save"):
        rules_data[section][idx] = {
            "match": match,
            "replace_with": replace_with if replace_with else None,
            "message": message,
            "severity": severity
        }
        save_rules(rules_data)
        st.success("Rule updated!")
        st.experimental_rerun()
