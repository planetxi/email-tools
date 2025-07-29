import streamlit as st
import pandas as pd
import re
from itertools import product
import base64
import io

# Nickname map
NICKNAME_MAP = {
    "johnathan": "john",
    "michael": "mike",
    "william": "bill",
    "elizabeth": "liz",
    "robert": "bob",
    "jennifer": "jen",
    "stephanie": "steph",
    "christopher": "chris",
    "james": "jim",
    "richard": "rich",
    "charles": "chuck",
    "daniel": "dan",
    "anthony": "tony",
    "patricia": "pat",
}

# Email syntax validator (not server check)
def is_valid_email(email):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(regex, email))

# Email permutation generator
def generate_permutations(first, middle, last, domain, nickname=None):
    first = first.lower().strip()
    middle = middle.lower().strip() if middle else ""
    last = last.lower().strip()
    domain = domain.lower().strip()

    all_firsts = [first]

    # Add nickname if available
    if nickname:
        all_firsts.append(nickname.lower())
    elif first in NICKNAME_MAP:
        all_firsts.append(NICKNAME_MAP[first])

    middle_initial = middle[0] if middle else ""
    last_initial = last[0] if last else ""

    # Full name variations
    full_name_variants = set()
    for f in all_firsts:
        if last:
            full_name_variants.update({
                f"{f}{last}",
                f"{f}.{last}",
                f"{f}_{last}",
                f"{last}{f}",
                f"{last}.{f}",
                f"{last}_{f}",
            })
        if middle:
            full_name_variants.update({
                f"{f}{middle}{last}",
                f"{f}.{middle}.{last}",
                f"{f}_{middle}_{last}",
                f"{f}{middle_initial}{last}",
            })

    # Part-based combinations
    part_combos = set()
    for f, m, l in product(all_firsts, [middle, middle_initial, ""], [last, last_initial, ""]):
        part_combos.update({
            f"{f}@{domain}",
            f"{f}{l}@{domain}",
            f"{f}.{l}@{domain}",
            f"{f}_{l}@{domain}",
            f"{f}{m}{l}@{domain}",
            f"{f}.{m}.{l}@{domain}",
            f"{f}{m}@{domain}",
            f"{f}.{m}@{domain}",
            f"{f}{m}.{l}@{domain}",
        })

    all_emails = {f"{email}@{domain}" if '@' not in email else email for email in full_name_variants}
    all_emails.update(part_combos)

    # Validate syntax
    return sorted([email for email in all_emails if is_valid_email(email)])

# App UI
st.set_page_config(page_title="Email Permutator + Validator", layout="centered")
st.title("📧 Email Permutator & Validator")

st.markdown("Generate possible professional email combinations with validation.")

with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name*", "")
        middle_name = st.text_input("Middle Name (Optional)", "")
        nickname = st.text_input("Nickname (Optional)", "")
    with col2:
        last_name = st.text_input("Last Name*", "")
        domain = st.text_input("Domain (example.com)*", "")
    submitted = st.form_submit_button("Generate Emails")

if submitted:
    if not first_name or not last_name or not domain:
        st.warning("First name, Last name, and Domain are required.")
    else:
        with st.spinner("Generating..."):
            emails = generate_permutations(first_name, middle_name, last_name, domain, nickname)
            if emails:
                st.success(f"✅ Generated {len(emails)} email combinations.")
                df = pd.DataFrame(emails, columns=["Email Address"])
                st.dataframe(df, use_container_width=True)

                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="email_combinations.csv">📥 Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("No valid combinations generated.")
