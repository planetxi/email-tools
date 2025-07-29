import streamlit as st
import pandas as pd
import re
import dns.resolver
import smtplib
import socket
from io import StringIO

# ----------------------------------------
# Helper Functions
# ----------------------------------------

def is_valid_syntax(email):
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(regex, email) is not None

def has_mx_record(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except Exception:
        return False

def is_disposable(email):
    disposable_domains = ['mailinator.com', '10minutemail.com', 'guerrillamail.com']
    return any(domain in email for domain in disposable_domains)

def is_role_based(email):
    return any(role in email.split('@')[0] for role in ['admin', 'info', 'support', 'contact'])

def smtp_check(email):
    domain = email.split('@')[1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo()
        server.mail('test@example.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except Exception:
        return False

def validate_email(email):
    result = {
        "Email": email,
        "Valid Syntax": is_valid_syntax(email),
        "MX Record": False,
        "Disposable": is_disposable(email),
        "Role-based": is_role_based(email),
        "SMTP Check": False
    }

    if result["Valid Syntax"]:
        domain = email.split('@')[1]
        result["MX Record"] = has_mx_record(domain)
        if result["MX Record"]:
            result["SMTP Check"] = smtp_check(email)

    return result

def generate_permutations(first, middle, last, domain, nickname=None):
    first, middle, last = first.lower(), middle.lower(), last.lower()
    nickname = nickname.lower() if nickname else ""
    
    nick_map = {
        "johnathan": "john", "jonathan": "john", "michael": "mike", "robert": "rob", "william": "bill",
        "steven": "steve", "jennifer": "jen", "katherine": "kat", "jessica": "jess", "elizabeth": "liz"
    }
    
    if not nickname and first in nick_map:
        nickname = nick_map[first]

    parts = list(set(filter(None, [first, middle, last, nickname, first[0], last[0]])))
    
    combos = set()
    for p1 in parts:
        for p2 in parts:
            if p1 != p2:
                combos.add(f"{p1}{p2}@{domain}")
                combos.add(f"{p1}.{p2}@{domain}")
                combos.add(f"{p1}_{p2}@{domain}")
    for p in parts:
        combos.add(f"{p}@{domain}")
    return sorted(combos)

# ----------------------------------------
# Streamlit App
# ----------------------------------------

st.title("📧 Email Permutator + Validator")

tool = st.sidebar.radio("Select Tool", ["Email Permutator", "Email Validator", "Permutator + Validator"])

# -------------------------------
# Email Permutator
# -------------------------------
if tool in ["Email Permutator", "Permutator + Validator"]:
    st.header("Step 1: Enter Details for Email Permutation")
    with st.form("permutation_form"):
        first_name = st.text_input("First Name")
        middle_name = st.text_input("Middle Name (Optional)", "")
        last_name = st.text_input("Last Name")
        domain = st.text_input("Domain (example.com)")
        nickname = st.text_input("Nickname (Optional)", "")
        submit_perm = st.form_submit_button("Generate Emails")

    emails = []
    if submit_perm and first_name and last_name and domain:
        emails = generate_permutations(first_name, middle_name, last_name, domain, nickname)
        st.success(f"✅ Generated {len(emails)} email combinations.")
        st.write(emails)
        csv_perm = pd.DataFrame(emails, columns=["Email"]).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Emails", data=csv_perm, file_name="email_permutations.csv")

# -------------------------------
# Email Validator
# -------------------------------
if tool in ["Email Validator", "Permutator + Validator"]:
    st.header("Step 2: Validate Emails")
    source_type = st.radio("Input Method", ["Paste Emails", "Upload CSV"])

    emails_to_check = []

    if source_type == "Paste Emails":
        input_text = st.text_area("Enter emails (one per line)")
        if input_text:
            emails_to_check = [e.strip() for e in input_text.splitlines() if e.strip()]
    else:
        uploaded_file = st.file_uploader("Upload CSV with 'Email' column", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if 'Email' in df.columns:
                emails_to_check = df['Email'].dropna().tolist()
            else:
                st.error("CSV must contain an 'Email' column.")

    if emails_to_check:
        if st.button("Start Validation"):
            with st.spinner("Validating..."):
                results = [validate_email(email) for email in emails_to_check]
                result_df = pd.DataFrame(results)
                st.dataframe(result_df)
                csv_result = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Validation Results", data=csv_result, file_name="email_validation_results.csv")
