import sys
import os

sys.path.append(os.path.abspath('.'))

try:
    print("[+] Loading queries...")
    from bot.database.queries import get_referral_stats
    print("[+] Successfully parsed get_referral_stats!")
    print("[***] ALL REFERRAL COMPILE CHECKS PASSED! [***]")
except Exception as e:
    print(f"[-] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
