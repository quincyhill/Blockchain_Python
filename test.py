# this is for testing purposes
from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class Item:
    cat: int


@dataclass
class Item2:
    cat: int
    items: list[Item]


thing = Item(1)
thing2 = Item(2)
thing3 = Item2(cat=2, items=[Item(1), Item(2)])

cust_item = {"cat": 1}

thing3_bytes = bytes(str(thing3), encoding="utf8")

val = json.dumps(thing.__dict__).encode()


print("val: ", val)

print(hashlib.sha256(val).hexdigest())
print(hashlib.sha256(thing3_bytes).hexdigest())
