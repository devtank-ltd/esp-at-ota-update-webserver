#!/usr/bin/env python3

import sys
import os
import json
import random


KEY_LEN = 40


def gen_random_key(seed=None):
    if seed is not None:
        random.seed(seed)
    return "".join(map(lambda x: hex(random.randint(0, 15))[2:], [""] * KEY_LEN))


def main(args):
    keys = []
    if not os.isatty(sys.stdin.fileno()):
        keys += json.load(sys.stdin)
    if len(args) >= 1:
        name = args[0]
        existing_key = filter(lambda key: key["Name"] == name, keys)
        list(map(lambda key: keys.remove(key), existing_key))
        keys.append({"Name": name, "Token": gen_random_key()})
    os.write(sys.stdout.fileno(), json.dumps(keys, indent=2).encode())
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
