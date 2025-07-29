import streamlit as st
import re
from urllib.parse import urlparse

st.set_page_config(page_title="Email Permutator & Validator", layout="wide")

# Nickname dictionary
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

# Simple email validator using regex
def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

# Extract domain from URL or domain input
def extract_domain(raw_input):
    if not raw_input.startswith("http"):
        raw_input = "http://" + raw_input
    try:
        domain = urlparse(raw_input).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return ""

# Generate permutations
def generate_permutations(first, middle, last, domain):
    names = [first]
    if middle:
        names.append(middle)
    names.append(last)

    variants = [first, middle, last]
    all_variants = list(filter(None, set(variants + nickname_map.get(first.capitalize(), []))))

    combinations = set()

    for v1 in all_variants:
        v1 = v1.lower()
        combinations.update([
            f"{v1}@{domain}",
            f"{v1}{last}@{domain}",
            f"{v1}.{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first[0]}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first}.{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}.{first}@{domain}",
            f"{last}{first}@{domain}"
        ])
    return sorted(combinations)

# Streamlit UI
st.title("📧 Email Permutator & Validator")

col1, col2 = st.columns(2)

with col1:
    raw_name = st.text_input("Full Name").strip()
    domain_input = st.text_input("Website or Domain").strip()

with col2:
    st.markdown("**How it works:**")
    st.markdown("- Enter full name and website/domain")
    st.markdown("- Automatically generates email permutations")
    st.markdown("- Uses built-in nickname logic")
    st.markdown("- Validates format only")

if raw_name and domain_input:
    name_parts = raw_name.lower().split()
    first = name_parts[0]
    middle = name_parts[1] if len(name_parts) == 3 else ""
    last = name_parts[-1] if len(name_parts) > 1 else ""

    domain = extract_domain(domain_input)
    permutations = generate_permutations(first, middle, last, domain)

    st.subheader("Generated Emails")
    for email in permutations:
        status = "✅ Valid" if is_valid_email(email) else "❌ Invalid"
        st.write(f"{email} — {status}")
