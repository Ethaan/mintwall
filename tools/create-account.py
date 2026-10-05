"""Create a player account (7.4 has no account creation in the client; until the website exists, this script).

    tests\\.venv\\Scripts\\python.exe tools\\create-account.py --db server\\db.db3
        [--account 1234567] [--password PASS] [--premium-days N] [--email ADDRESS]
        [--character "Name" [--female]]

Without --account a random free 7-digit number is picked; without --password one is generated and printed once -
it is stored only as a salted PBKDF2 hash (config PasswordType = "pbkdf2"), nobody can read it back. --character adds
a level 1 Rookgaard character (like seed.sql's), which gets the beginner set at its first login.

Safe while the server runs (see tools/accountlib.py): the engine reads accounts from the database at every login.
An existing account number or character name (any case) is refused, nothing is changed then.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accountlib import PASSWORD_WARNING, AccountError, connect, create_account  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", required=True, type=Path, help="the server database (server\\db.db3)")
    ap.add_argument("--account", type=int, help="account number (default: a random free 7-digit one)")
    ap.add_argument("--password", help="password (default: generated and printed once)")
    ap.add_argument("--premium-days", type=int, default=0, metavar="N")
    ap.add_argument("--email", default="")
    ap.add_argument("--character", metavar="NAME", help="also create a level 1 Rookgaard character")
    ap.add_argument("--female", action="store_true", help="the character is female (default male)")
    args = ap.parse_args(argv)

    if not args.db.exists():
        raise SystemExit(f"{args.db} not found")
    con = connect(args.db)
    try:
        created = create_account(con, number=args.account, password=args.password,
                                 premium_days=args.premium_days, email=args.email,
                                 character=args.character, sex=0 if args.female else 1)
    except AccountError as e:
        raise SystemExit(f"not created: {e}")
    finally:
        con.close()

    print(f"account:   {created['account']}")
    if args.password is None:
        print(f"password:  {created['password']}    (shown only this once - write it down)")
    if args.premium_days:
        print(f"premium:   {args.premium_days} days")
    if created["character"]:
        print(f"character: {created['character']} (Rookgaard)")
    print()
    print(f"Note: {PASSWORD_WARNING}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
