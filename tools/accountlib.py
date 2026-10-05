"""Accounts and characters in the server database - shared by tools/create-account.py, tools/provision-accounts.py
and, later, the website (call create_account()).

Safe while the server runs: the engine reads an account from the database on every login (IOAccount::loadAccount
in the login server, IOAccount::getPassword in the game server - nothing is cached), the only account write it makes
is UPDATE warnings/premend of one existing account (IOAccount::saveAccount, bans and premium scripts) and the
passwords.cpp rehash of one account; player saves write players rows by id. The database runs in WAL mode with a
5 s busy timeout (databasesqlite.cpp), so a short insert transaction from here just waits for, or is waited for by,
a save. Character names: the engine looks them up case-insensitively (IOPlayer::getGuidByName: LOWER(name)) and
caches only names it found - a new name is read from the database at its first login.
"""
import base64
import hashlib
import os
import re
import secrets
import sqlite3
import time

ITERATIONS = 600_000                 # = config.lua PasswordIterations (tests/test_provision.py checks it)

# Shown by create-account.py; the same warning is in config.lua (MOTD and LoginMsg): the 7.4 protocol has no
# encryption (it came with 7.7), the password crosses the network as typed.
PASSWORD_WARNING = ("Tibia 7.4 sends your password unencrypted - use a password you use nowhere else.")

PASSWORD_MIN, PASSWORD_MAX = 6, 29   # 29: what the 7.4 client's password field takes, conservatively
NAME_MIN, NAME_MAX = 2, 25           # the engine has no rule; 25 keeps clear of its 32-character VIP limit
RESERVED_PREFIXES = ("gm ", "cm ", "god ", "tutor ")

# A new Rookgaard character, as server/sql/seed.sql writes "Mintwall": level 1, no vocation, at the temple of
# town 1 (position 0,0,0 = the town's temple). login.lua gives the beginner set and the outfit at the first login.
LOOKTYPE = {0: 136, 1: 128}          # female / male citizen (login.lua LOOKTYPE_FEMALE / LOOKTYPE_MALE)
LOOK = (78, 69, 58, 114)             # head, body, legs, feet - login.lua's LOOK
NEW_CHARACTER = {"group_id": 1, "vocation": 0, "level": 1, "experience": 0, "health": 150, "healthmax": 150,
                 "mana": 0, "manamax": 0, "cap": 400, "posx": 0, "posy": 0, "posz": 0, "rank_id": 0, "town_id": 1}

_PASSWORD_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no 0/O, 1/l/I


class AccountError(ValueError):
    """The request cannot be done (taken number or name, bad password...): the message is meant for the user."""


def pbkdf2(password: str, iterations: int = ITERATIONS) -> str:
    """The server's stored format (server/src/passwords.cpp): pbkdf2_sha256$iterations$salt$digest, base64."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("latin-1"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def random_account_number(taken) -> int:
    """7 digits, never sequential (nobody guesses the next one)."""
    while True:
        number = secrets.randbelow(9_000_000) + 1_000_000
        if number not in taken:
            return number


def generate_password(length: int = 12) -> str:
    """Easy to type into the 7.4 client: letters and digits, no look-alikes."""
    return "".join(secrets.choice(_PASSWORD_ALPHABET) for _ in range(length))


def check_password(password: str):
    if not PASSWORD_MIN <= len(password) <= PASSWORD_MAX:
        raise AccountError(f"the password must be {PASSWORD_MIN} to {PASSWORD_MAX} characters long")
    if not all(33 <= ord(ch) <= 126 for ch in password):
        raise AccountError("the password may use letters, digits and punctuation only (no spaces, no accents)")


def check_name(name: str):
    """Tibia-style character names: letters and single spaces, starting with a capital ("Sir Galahad",
    "Lord of Ashes")."""
    if not NAME_MIN <= len(name) <= NAME_MAX:
        raise AccountError(f"a character name is {NAME_MIN} to {NAME_MAX} characters long")
    if not re.fullmatch(r"[A-Z][a-z]+( [A-Za-z][a-z]*)*", name):
        raise AccountError("a character name is letters and single spaces and starts with a capital letter"
                           " (e.g. \"Sir Galahad\")")
    if name.lower().startswith(RESERVED_PREFIXES):
        raise AccountError("a character name may not start with GM, CM, God or Tutor")


def check_email(email: str):
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise AccountError(f"{email!r} is not an e-mail address")


def connect(path) -> sqlite3.Connection:
    """A connection that waits (like the engine's busy timeout) instead of failing while the server writes."""
    con = sqlite3.connect(path, timeout=10, isolation_level=None)   # transactions are explicit below
    return con


def create_account(con: sqlite3.Connection, *, number: int = None, password: str = None, premium_days: int = 0,
                   email: str = "", character: str = None, sex: int = 1) -> dict:
    """A new account (and optionally a level 1 Rookgaard character on it), in one transaction.
    number: None picks a random free 7-digit one; password: None generates one. Raises AccountError for anything
    the user should change (taken number or name, bad password / name / e-mail).
    Returns {"account": number, "password": password, "premend": t, "character": name or None}."""
    if number is not None and not (isinstance(number, int) and 1 <= number <= 0xFFFFFFFF):
        raise AccountError("the account number must be a positive whole number")
    if password is None:
        password = generate_password()
    check_password(password)
    if premium_days < 0:
        raise AccountError("premium days cannot be negative")
    check_email(email)
    if character is not None:
        check_name(character)
        if sex not in LOOKTYPE:
            raise AccountError("sex is 0 (female) or 1 (male)")
    stored = pbkdf2(password)                         # the slow part (~0.5 s), outside the write transaction
    premend = int(time.time()) + premium_days * 86400 if premium_days else 0

    con.execute("BEGIN IMMEDIATE")                    # the write lock first: checks and inserts see the same data
    try:
        if number is None:
            number = random_account_number({row[0] for row in con.execute("SELECT id FROM accounts")})
        elif con.execute("SELECT 1 FROM accounts WHERE id = ?", (number,)).fetchone():
            raise AccountError(f"account {number} already exists")
        if character is not None and con.execute("SELECT 1 FROM players WHERE LOWER(name) = LOWER(?)",
                                                 (character,)).fetchone():
            raise AccountError(f"the name {character!r} is taken")
        con.execute("INSERT INTO accounts (id, password, email, premend) VALUES (?, ?, ?, ?)",
                    (number, stored, email, premend))
        if character is not None:
            c = NEW_CHARACTER
            con.execute(
                "INSERT INTO players (name, account_id, group_id, sex, vocation, experience, level, health,"
                " healthmax, mana, manamax, cap, looktype, lookhead, lookbody, looklegs, lookfeet, posx, posy, posz,"
                " conditions, rank_id, town_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
                " X'', ?, ?)",
                (character, number, c["group_id"], sex, c["vocation"], c["experience"], c["level"], c["health"],
                 c["healthmax"], c["mana"], c["manamax"], c["cap"], LOOKTYPE[sex], *LOOK,
                 c["posx"], c["posy"], c["posz"], c["rank_id"], c["town_id"]))
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise
    return {"account": number, "password": password, "premend": premend, "character": character}
