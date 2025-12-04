import re
import sys

# Mocking streamlit to avoid import error if not running in streamlit environment
# or just import the function if possible. 
# Since app.py has streamlit calls at top level, importing it might trigger them.
# I'll just copy the function for testing logic, or try to import it.
# Let's try to import the function by mocking streamlit first.

from unittest.mock import MagicMock
sys.modules["streamlit"] = MagicMock()

# Now we can import app
# But app.py has 'import streamlit as st' and 'st.set_page_config' at top level.
# The mock should handle it.

try:
    from app import convert_google_drive_url
except ImportError:
    # Fallback if import fails (e.g. pandas dependency etc)
    # Copying the function logic here for verification of the regex logic
    def convert_google_drive_url(url):
        if not isinstance(url, str):
            return ""
        
        match_id = re.search(r'[?&]id=([^&]+)', url)
        if match_id:
            return f"https://drive.google.com/uc?export=view&id={match_id.group(1)}"
        
        match_path = re.search(r'/file/d/([^/]+)', url)
        if match_path:
            return f"https://drive.google.com/uc?export=view&id={match_path.group(1)}"

        return url

def test_urls():
    test_cases = [
        ("https://drive.google.com/open?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh", "https://drive.google.com/thumbnail?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh&sz=w1000"),
        ("https://drive.google.com/file/d/1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh/view", "https://drive.google.com/thumbnail?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh&sz=w1000"),
        ("https://drive.google.com/file/d/1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh/view?usp=sharing", "https://drive.google.com/thumbnail?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh&sz=w1000"),
        ("https://drive.google.com/uc?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh", "https://drive.google.com/thumbnail?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh&sz=w1000"),
        ("Not a url", "Not a url"),
        (None, "")
    ]

    print("Running tests...")
    all_passed = True
    for input_url, expected in test_cases:
        result = convert_google_drive_url(input_url)
        if result == expected:
            print(f"[PASS] {input_url} -> {result}")
        else:
            print(f"[FAIL] {input_url}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")

if __name__ == "__main__":
    test_urls()
