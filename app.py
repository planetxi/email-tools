import streamlit as st
import csv
import io
import re
import smtplib
import dns.resolver
from typing import List
from itertools import product

# Suggested nicknames (you can expand this dictionary)
NICKNAME_MAP = {
    "johnathan": "john",
    "jonathan": "jon",
    "michael": "mike",
    "william": "will",
    "robert": "rob",
    "richard": "rick",
    "steven": "steve",
    "thomas": "tom",
    "james": "jim",
    "charles": "charlie",
    "jennifer": "jen",
    "elizabeth": "liz",
    "katherine": "kate",
    "christopher": "chris"
}

# ---------------------- Email Validation Logic ----------------------
def is_valid_email_format(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, email)

def has_mx_record(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except:
        return False

def smtp_check(email):
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mx_record)
        server.helo(server.local_hostname)
        server.mail('test@example.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def validate_email(email):
    if not is_valid_email_format(email):
        return "❌ Invalid Format"
    if not has_mx_record(email.split('@')[1]):
        return "❌ No MX Record"
    if smtp_check(email):
        return "✅ Deliverable"
    else:
        return "⚠️ Undeliverable"

# ---------------------- Permutation Logic ----------------------
def generate_permutations(first, middle, last, domain, nickname=None):
    first = first.lower()
    middle = middle.lower() if middle else ""
    last = last.lower()
    domain = domain.lower()
    
    all_firsts = [first]
    
    # Add suggested nickname
    if nickname:
        all_firsts.append(nickname.lower())
    elif first.lower() in NICKNAME_MAP:
        all_firsts.append(NICKNAME_MAP[first.lower()])
    
    middle_initial = middle[0] if middle else ""
    last_initial = last[0] if last else ""

    combos = set()

    for f, m, l in product(all_firsts, [middle, middle_initial, ""], [last, last_initial, ""]):
        combos.update({
            f"{f}@{domain}",
            f"{f}{l}@{domain}",
            f"{f}.{l}@{domain}",
            f"{f}{m}{l}@{domain}",
            f"{f}.{m}.{l}@{domain}",
            f"{f}_{l}@{domain}",
            f"{l}{f}@{domain}",
            f"{l}.{f}@{domain}",
            f"{l}_{f}@{domain}",
            f"{f}{m}@{domain}",
            f"{f}.{m}@{domain}",
            f"{f}{m}.{l}@{domain}",
        })

    return sorted(list(combos))

# ---------------------- App UI ----------------------

st.set_page_config(page_title="Email Permutator + Validator", layout="centered")
st.title("📧 Email Permutator + Validator")

tool_mode = st.radio("Select Tool:", ["Email Permutator", "Email Validator"])

if tool_mode == "Email Permutator":
    st.subheader("🔁 Generate Email Permutations")
    with st.form("permutation_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", max_chars=50)
            middle_name = st.text_input("Middle Name (Optional)", max_chars=50)
            nickname = st.text_input("Nickname (Optional)", max_chars=50)
        with col2:
            last_name = st.text_input("Last Name", max_chars=50)
            domain = st.text_input("Domain (example.com)", max_chars=100)
        submitted = st.form_submit_button("Generate Permutations")
    
    if submitted:
        if not (first_name and last_name and domain):
            st.warning("Please fill at least First Name, Last Name, and Domain.")
        else:
            emails = generate_permutations(first_name, middle_name, last_name, domain, nickname)
            results = [(email, validate_email(email)) for email in emails]
            
            st.success(f"Generated {len(results)} email combinations.")
            st.write("### Results:")
            st.dataframe(results, use_container_width=True)
            
            # Download as CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Email", "Status"])
            for row in results:
                writer.writerow(row)
            st.download_button("📥 Download CSV", output.getvalue(), "emails.csv", "text/csv")

elif tool_mode == "Email Validator":
    st.subheader("✅ Validate Email Addresses")

    uploaded_file = st.file_uploader("Upload CSV file (Column: email)", type="csv")
    email_list = []
    
    if uploaded_file:
        df = uploaded_file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(df))
        email_list = [row["email"] for row in reader if "email" in row]

    manual_input = st.text_area("Or Paste Emails (comma, space, or newline separated):")
    if manual_input:
        email_list.extend(re.split(r"[,\s]+", manual_input.strip()))

    email_list = list(set([e.strip() for e in email_list if e.strip()]))

    if email_list:
        if st.button("Validate Emails"):
            results = [(email, validate_email(email)) for email in email_list]
            st.success(f"Validated {len(results)} emails.")
            st.dataframe(results, use_container_width=True)

            # CSV download
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Email", "Status"])
            for row in results:
                writer.writerow(row)
            st.download_button("📥 Download CSV", output.getvalue(), "validated_emails.csv", "text/csv")
