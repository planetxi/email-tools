import streamlit as st
import csv
import io
import re
import smtplib
import dns.resolver
import socket
import ssl

# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------

def clean_name(name):
    return re.sub(r'[^a-zA-Z]', '', name.lower()) if name else ''

def generate_permutations(first, middle, last, domain, nickname=None):
    first, middle, last = clean_name(first), clean_name(middle), clean_name(last)
    nickname = clean_name(nickname) if nickname else ''
    
    firsts = [first, first[0]] if first else []
    middles = [middle, middle[0]] if middle else []
    lasts = [last, last[0]] if last else []
    nicknames = [nickname] if nickname else []

    combos = set()

    for f in firsts + nicknames:
        for m in [''] + middles:
            for l in [''] + lasts:
                if f and l:
                    combos.add(f"{f}{l}@{domain}")
                    combos.add(f"{f}.{l}@{domain}")
                if f and m and l:
                    combos.add(f"{f}{m}{l}@{domain}")
                    combos.add(f"{f}.{m}.{l}@{domain}")
                if f and m:
                    combos.add(f"{f}{m}@{domain}")
                if f:
                    combos.add(f"{f}@{domain}")
                if l:
                    combos.add(f"{l}@{domain}")

    return sorted(list(combos))

def check_mx(domain):
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

def is_disposable(email):
    disposable_domains = ['mailinator.com', '10minutemail.com', 'tempmail.com']
    return any(d in email for d in disposable_domains)

def is_role_based(email):
    roles = ['admin', 'support', 'info', 'sales', 'contact', 'team']
    local = email.split('@')[0]
    return any(local.startswith(role) for role in roles)

def smtp_check(email):
    domain = email.split('@')[-1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo(socket.gethostname())
        server.mail('test@example.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def validate_email(email):
    domain = email.split('@')[-1]
    return {
        "Email": email,
        "Valid Format": re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None,
        "MX Record": check_mx(domain),
        "Disposable": is_disposable(email),
        "Role-Based": is_role_based(email),
        "SMTP Valid": smtp_check(email),
    }

# ----------------------------
# STREAMLIT APP
# ----------------------------

st.title("📧 Email Toolkit: Permutator + Validator")
option = st.radio("Choose a tool:", ["Email Permutator", "Email Validator"])

if option == "Email Permutator":
    st.header("🔁 Generate Email Permutations")
    
    col1, col2 = st.columns(2)
    with col1:
        first = st.text_input("First Name", "")
        middle = st.text_input("Middle Name (Optional)", "")
        nickname = st.text_input("Nickname (Optional)", "")
    with col2:
        last = st.text_input("Last Name", "")
        domain = st.text_input("Domain (e.g. example.com)", "")

    validate_checkbox = st.checkbox("Validate each email (may take time)")

    if st.button("Generate Emails"):
        if not first or not last or not domain:
            st.error("Please fill at least First Name, Last Name, and Domain.")
        else:
            results = generate_permutations(first, middle, last, domain, nickname)
            if validate_checkbox:
                validated = [validate_email(email) for email in results]
                st.write("### ✅ Validated Email Permutations")
                st.dataframe(validated)
                csv_data = io.StringIO()
                writer = csv.DictWriter(csv_data, fieldnames=validated[0].keys())
                writer.writeheader()
                writer.writerows(validated)
                st.download_button("📥 Download CSV", csv_data.getvalue(), file_name="validated_emails.csv", mime="text/csv")
            else:
                st.write("### 📬 Generated Emails")
                st.dataframe(results)
                csv_data = io.StringIO()
                writer = csv.writer(csv_data)
                writer.writerow(["Email"])
                writer.writerows([[r] for r in results])
                st.download_button("📥 Download CSV", csv_data.getvalue(), file_name="emails.csv", mime="text/csv")

elif option == "Email Validator":
    st.header("✅ Bulk Email Validator")
    uploaded_file = st.file_uploader("Upload CSV with Email column", type=['csv'])

    if uploaded_file:
        file = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        reader = csv.DictReader(file)
        if 'Email' not in reader.fieldnames:
            st.error("CSV must contain 'Email' column.")
        else:
            emails = [row['Email'] for row in reader]
            with st.spinner("Validating emails..."):
                results = [validate_email(email) for email in emails]
            st.success("Validation Complete ✅")
            st.dataframe(results)

            csv_out = io.StringIO()
            writer = csv.DictWriter(csv_out, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            st.download_button("📥 Download Validated Emails", csv_out.getvalue(), file_name="validated_emails.csv", mime="text/csv")
