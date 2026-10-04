"""tools/grant-learned-spells.py: existing characters get the spells their vocation could buy from the teachers."""
import importlib.util
import sqlite3

import pytest

from tibia74 import SERVER_DIR
from tibia74 import TestDatabase as Database
from tibia74.db import learnable_spells

spec = importlib.util.spec_from_file_location("grant", SERVER_DIR.parent / "tools" / "grant-learned-spells.py")
grant = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grant)

FREE_PORT = 7999                     # nothing listens here: the "server running" guard lets it through


@pytest.fixture
def scratch(tmp_path):
    path = tmp_path / "db.db3"
    con = sqlite3.connect(path)
    con.executescript((SERVER_DIR / "sql" / "schema.sqlite").read_text(encoding="latin-1"))
    con.executescript((SERVER_DIR / "sql" / "seed.sql").read_text(encoding="latin-1"))   # groups, towns
    con.commit()
    con.close()
    return Database(path)


def _run(db, *extra):
    return grant.main(["--db", str(db.path), "--port", str(FREE_PORT), *extra])


def test_a_sorcerer_gets_its_spells_a_rookie_none_and_a_second_run_nothing(scratch, capsys):
    sorcerer = scratch.create_character(level=20, vocation=1, maglevel=100, spells=[])
    apprentice = scratch.create_character(level=20, vocation=1, maglevel=0, spells=["light"])   # bought, lower case
    rookie = scratch.create_character(level=5, vocation=0, spells=[])

    assert _run(scratch, "--backup") == 0
    # spells.xml (needlearn, vocation Sorcerer) says the same as the teachers: everything but Enchant Staff,
    # which is for master sorcerers only
    assert sorted(scratch.spells(sorcerer.guid)) == sorted(learnable_spells(1))
    assert sorted(scratch.spells(apprentice.guid)) == ["Find Person", "light"]     # magic level 0 spells only
    assert scratch.spells(rookie.guid) == []
    assert list(scratch.path.parent.glob("db.db3.bak-*")), "no backup made"

    before = {c.guid: scratch.spells(c.guid) for c in (sorcerer, apprentice, rookie)}
    capsys.readouterr()
    assert _run(scratch, "--backup") == 0
    assert {guid: scratch.spells(guid) for guid in before} == before
    assert "added 0 spells" in capsys.readouterr().out


def test_promoted_spells_and_dry_run(scratch, capsys):
    master = scratch.create_character(level=60, vocation=5, maglevel=100, spells=[])
    assert _run(scratch, "--dry-run") == 0
    assert scratch.spells(master.guid) == []                                        # nothing written
    out = capsys.readouterr().out
    assert "would add" in out and "Enchant Staff" in out
    assert not list(scratch.path.parent.glob("db.db3.bak-*"))


def test_a_real_run_needs_a_backup_and_a_stopped_server(scratch, monkeypatch):
    with pytest.raises(SystemExit, match="--backup"):
        _run(scratch)
    monkeypatch.setattr(grant, "server_running", lambda port: True)
    with pytest.raises(SystemExit, match="stop it first"):
        _run(scratch, "--backup")
    assert _run(scratch, "--backup", "--force") == 0
