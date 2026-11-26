"""Initialize optional private, passphrase-encrypted bootstrap on first launch."""
import json
from contextlib import closing
from .server import ROOT, TOKEN, connect, initialize, seal


def main():
    initialize()
    seed = ROOT / "private-vault.json"
    if seed.is_file():
        box = json.loads(seed.read_bytes())
        with closing(connect()) as c, c:
            c.execute("INSERT OR IGNORE INTO vault VALUES(1,1,?)", (seal(box),))
    print("رمز ربط الخادم المحلي:", TOKEN.decode())


if __name__ == "__main__":
    main()
