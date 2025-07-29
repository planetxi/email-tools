import streamlit as st
import re
import socket
import dns.resolver

st.set_page_config(page_title="Email Permutator + Validator", layout="centered")

# Nickname directory
nickname_map = {
    "Alexander": ["Alex", "Xander", "Lex"],
    "Andrew": ["Andy", "Drew"],
    "Anthony": ["Tony"],
    "Barbara": ["Barb", "Babs"],
    "Benjamin": ["Ben", "Benny"],
    "Brandon": ["Brad", "Bran"],
    "Catherine": ["Cathy", "Cat", "Kate", "Katie"],
    "Katherine": ["Cathy", "Cat", "Kate", "Katie"],
    "Charles": ["Charlie", "Chuck", "Chaz"],
    "Christopher": ["Chris", "Topher", "Kit"],
    "Daniel": ["Dan", "Danny"],
    "David": ["Dave", "Davey"],
    "Dorothy": ["Dot", "Dottie"],
    "Edward": ["Ed", "Eddie", "Ned", "Ted"],
    "Elizabeth": ["Liz", "Lizzy", "Beth", "Eliza", "Ellie", "Betty", "Liza", "Libby"],
    "Eleanor": ["Ellie", "Nora"],
    "Francis": ["Frank", "Frankie"],
    "Frances": ["Fran", "Frankie"],
    "Frederick": ["Fred", "Freddy", "Rick"],
    "George": ["Geo", "Georgie"],
    "Gregory": ["Greg"],
    "Harold": ["Harry", "Hal"],
    "Henry": ["Hank", "Harry"],
    "Isabella": ["Bella", "Izzy"],
    "Jacob": ["Jake"],
    "James": ["Jim", "Jimmy", "Jamie"],
    "Jennifer": ["Jen", "Jenny"],
    "John": ["Jack", "Johnny"],
    "Jonathan": ["Jon", "Jonny", "Nate"],
    "Joseph": ["Joe", "Joey"],
    "Joshua": ["Josh"],
    "Judith": ["Judy"],
    "Kenneth": ["Ken", "Kenny"],
    "Kimberly": ["Kim"],
    "Lawrence": ["Larry"],
    "Leonard": ["Lenny", "Leo"],
    "Margaret": ["Maggie", "Meg", "Peggy", "Margo", "Greta", "Daisy"],
    "Matthew": ["Matt"],
    "Michael": ["Mike", "Mikey"],
    "Michelle": ["Shelly", "Mich"],
    "Nicholas": ["Nick", "Nicky"],
    "Olivia": ["Liv", "Livvy", "Ollie"],
    "Oscar": ["Ozzy"],
    "Patricia": ["Pat", "Patty", "Trish"],
    "Patrick": ["Pat", "Rick"],
    "Raymond": ["Ray"],
    "Rebecca": ["Becky", "Becca"],
    "Richard": ["Rich", "Rick", "Dick", "Richie"],
    "Robert": ["Rob", "Robbie", "Bob", "Bobby"],
    "Samuel": ["Sam", "Sammy"],
    "Sandra": ["Sandy"],
    "Stephen": ["Steve", "Stevie"],
    "Steven": ["Steve", "Stevie"],
    "Susan": ["Sue", "Susie"],
    "Theodore": ["Theo", "Ted", "Teddy"],
    "Thomas": ["Tom", "Tommy"],
    "Timothy": ["Tim", "Timmy"],
    "Teresa": ["Terry", "Tessa", "Tess"],
    "Theresa": ["Terry", "Tessa", "Tess"],
    "Victoria": ["Vicky", "Tori"],
    "Vincent": ["Vince", "Vinny"],
    "Walter": ["Walt", "Wally"],
    "William": ["Will", "Bill", "Billy", "Liam"],
    "Zachary": ["Zack", "Zach"]
}

def clean_domain(raw_input):
    domain = re.sub(r"https?://", "", raw_input.strip().lower())
    domain = domain.split("/")[0]
    return domain

def validate_email_syntax(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

def check_dns_records(domain):
    results = {"MX": False, "SPF": False, "DMARC": False}
    try:
        results["MX"] = bool(dns.resolver.resolve(domain, "MX"))
    except:
        pass
    try:
        spf = dns.resolver.resolve(domain, "TXT")
        results["SPF"] = any("v=spf1" in str(r) for r in spf)
    except:
        pass
    try:
        dmarc = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        results["DMARC"] = any("v=DMARC1" in str(r) for r in dmarc)
    except:
        pass
    return results

def generate_combinations(first, middle, last, domain):
    names = [first, last, first + last, last + first]
    initials = [first[0], last[0]]
    combos = [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last[0]}@{domain}",
        f"{last}.{first}@{domain}",
        f"{first}_{last}@{domain}",
        f"{last}@{domain}",
    ]
    if middle:
        combos += [
            f"{first}.{middle}.{last}@{domain}",
            f"{first[0]}{middle[0]}{last}@{domain}",
            f"{first}{middle[0]}{last}@{domain}"
        ]
    nicknames = nickname_map.get(first.capitalize(), [])
    for nick in nicknames:
        combos += [
            f"{nick}@{domain}",
            f"{nick}.{last}@{domain}",
            f"{nick}{last}@{domain}",
            f"{nick[0]}{last}@{domain}"
        ]
    return list(set(combos))

# UI
st.title("🔧 Email Permutator + Validator")
st.caption("Enter name and domain. Tool generates possible email IDs + DNS-based validation.")

col1, col2 = st.columns(2)
with col1:
    raw_name = st.text_input("Full Name (First Middle Last):", "Jonathan Smith")
with col2:
    raw_domain = st.text_input("Website or Domain:", "https://example.com")

if raw_name and raw_domain:
    name_parts = raw_name.replace("  ", " ").strip().split()
    first = name_parts[0].lower()
    middle = name_parts[1].lower() if len(name_parts) == 3 else ""
    last = name_parts[-1].lower()

    domain = clean_domain(raw_domain)
    combinations = generate_combinations(first, middle, last, domain)

    dns_info = check_dns_records(domain)

    st.markdown(f"### ✅ Generated Emails ({len(combinations)})")
    for email in combinations:
        syntax_ok = validate_email_syntax(email)
        emoji = "✅" if syntax_ok else "❌"
        st.write(f"{emoji} `{email}`")

    st.markdown("---")
    st.markdown(f"### 🧪 DNS Email Validation for `{domain}`")
    st.write(f"- MX Records: {'✅' if dns_info['MX'] else '❌'}")
    st.write(f"- SPF Record: {'✅' if dns_info['SPF'] else '❌'}")
    st.write(f"- DMARC Record: {'✅' if dns_info['DMARC'] else '❌'}")
