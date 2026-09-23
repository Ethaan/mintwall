"""Parcels: a labelled parcel dropped into a mailbox arrives in the receiver's depot of that town."""
import pytest

from tibia74 import BACKPACK, Item
from tibia74.server import TESTER_GROUP

MAILBOX = (32365, 32213, 7)          # next to the Thais temple
NEXT_TO_MAILBOX = (32366, 32213, 7)
PARCEL, STAMPED_PARCEL, LABEL = 2595, 2596, 2599
THAIS_DEPOT = 2                      # depot id = town id; its root item is the depot locker
DEPOT_LOCKER = 2589


def _send_parcel(new_player, label_text):
    p = new_player(pos=NEXT_TO_MAILBOX, group_id=TESTER_GROUP, inventory={BACKPACK: Item(1988, contents=[
        Item(PARCEL, contents=[Item(LABEL, attributes=Item.text(label_text)), Item(2148, 7)])])})
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    parcel = bag.items[0]
    p.move_item(p.container_pos(cid, 0), parcel.client_id, 0, MAILBOX, 1)
    p.wait_for(lambda: not bag.items or p.text_messages[-1:] and "not possible" in p.text_messages[-1][1], timeout=3)
    return p, bag


def _depot(db, guid):
    con = db._connect()
    try:
        return con.execute("SELECT pid, itemtype FROM player_depotitems WHERE player_id = ?", (guid,)).fetchall()
    finally:
        con.close()


@pytest.mark.parametrize("write", [lambda n: n, lambda n: f"  {n.lower()} "],
                         ids=["exact-name", "lowercase-with-spaces"])
def test_parcel_arrives_in_the_receivers_thais_depot(new_player, db, write):
    receiver = db.create_character()
    p, bag = _send_parcel(new_player, f"{write(receiver.name)}\nThais")
    assert not bag.items, f"the parcel was not taken: {p.text_messages[-2:]}"
    rows = _depot(db, receiver.guid)
    assert (THAIS_DEPOT, DEPOT_LOCKER) in rows and any(t == STAMPED_PARCEL for _, t in rows), rows


def test_undeliverable_parcel_stays_with_the_sender(new_player):
    """It used to be taken by the mailbox and lost."""
    p, bag = _send_parcel(new_player, "Nobody Of That Name\nThais")
    assert [i.name for i in bag.items] == ["parcel"], "the parcel is gone"
    assert p.messages("not possible"), p.text_messages[-2:]
