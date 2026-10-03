import io, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

def build():
    tpl = io.open(os.path.join(BASE, "_template.html"), encoding="utf-8").read()
    data = io.open(os.path.join(BASE, "data.js"), encoding="utf-8").read()
    out = tpl.replace("/*__DATA__*/", data)
    io.open(os.path.join(BASE, "index.html"), "w", encoding="utf-8").write(out)
    print("index.html written:", len(out), "bytes")

if __name__ == "__main__":
    build()
