# wordpress_bruteforce/modules/utils.py
from termcolor import colored
from urllib.parse import urlparse
import re

def load_wordlist(path):
    """Load and validate password wordlist"""
    try:
        with open(path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        raise SystemExit(f"Error: Wordlist file not found at {path}")
    except Exception as e:
        raise SystemExit(f"Error loading wordlist: {str(e)}")

class Mutagen:
    """Password mutation engine with advanced rules"""

    def mutate_passwords(self, passwords):
        """Generate intelligent password variations"""
        mutated = set()
        for pwd in passwords:
            # Basic mutations
            mutations = [
                pwd,
                pwd.capitalize(),
                pwd.upper(),
                pwd + "123",
                pwd + "!",
                pwd.replace("a", "@"),
                pwd.replace("s", "$"),
                pwd[::-1],
            ]

            # Year suffix mutations
            for year in ["2023", "2024", "2022", "2021"]:
                mutations.append(pwd + year)

            # Special character mutations
            for special in ["!", "@", "#", "$"]:
                mutations.append(pwd + special)

            mutated.update(mutations)

        return list(mutated)


def validate_url(url):
    """Validate and normalize URL"""
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
    if not parsed.path.endswith("/"):
        url += "/"
    return url


def print_colored_bold(text, color="green"):
    """Print colored bold text"""
    print(colored(text, color, attrs=["bold"]))
