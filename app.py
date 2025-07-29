import streamlit as st
import re
from itertools import product
import validators
import dns.resolver

# Nickname map
NICKNAME_MAP = {
    "Johnathan": ["John"],
    "Michael": ["Mike"],
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


def clean_name(name):
    return re.sub(r"\s+", "", name.strip())


def extract_domain(url_or_domain):
    url_or_domain = url_or_domain.strip().lower()
    if "http" in url_or_domain:
        url_or_domain = re.sub(r"https?://", "", url_or_domain)
    return url_or_domain.split("/")[0]


def get_permutations(first, middle, last, nicknames):
    firsts = [first] + nicknames.get(first, [])
    middles = [middle] if middle else [""]
    lasts = [last] if last else [""]

    patterns = [
        ["{f}{l}", "{f}.{l}", "{f}_{l}", "{f}{m}{l}", "{f}.{m}.{l}", "{f}_{m}_{l}", "{l}{f}"],
        ["{l}{f}", "{l}.{f}", "{l}_{f}", "{l}{m}{f}"],
    ]

    combos = set()
    for fn, mn, ln in product(firsts, middles, lasts):
        for pattern_group in patterns:
            for pattern in pattern_group:
                email = pattern.format(f=fn.lower(), m=mn.lower(), l=ln.lower()).strip("._")
                combos.add(email)
    return sorted(combos)


def validate_email_syntax(email):
    return validators.email(email)


def validate_domain(domain):
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

# Streamlit UI
st.title("Email Permutator & Validator")

col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name (e.g., John Michael Doe)")
with col2:
    domain_input = st.text_input("Website or Domain (e.g., example.com or https://example.com)")

if full_name and domain_input:
    name_parts = clean_name(full_name).split()
    first = name_parts[0] if len(name_parts) > 0 else ""
    middle = name_parts[1] if len(name_parts) > 2 else ""
    last = name_parts[-1] if len(name_parts) > 1 else ""

    domain = extract_domain(domain_input)
    emails = get_permutations(first, middle, last, NICKNAME_MAP)

    valid_domain = validate_domain(domain)

    st.subheader("Generated Emails")
    for e in emails:
        email = f"{e}@{domain}"
        syntax_valid = validate_email_syntax(email)
        st.markdown(f"✅ `{email}`" if syntax_valid and valid_domain else f"❌ `{email}`")
