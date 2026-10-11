import os

# A pretend filesystem for Quarrybank's CA files. The "certificates" are
# placeholders with real PEM markers; nothing here is a usable certificate.
_PEM = "-----BEGIN CERTIFICATE-----\nMIIB{n}PLACEHOLDER\n-----END CERTIFICATE-----\n"
os.makedirs("/tmp/quarrybank", exist_ok=True)
with open("/tmp/quarrybank/ca-bundle.pem", "w") as f:
    f.write("# public roots\n" + _PEM.format(n=1) + _PEM.format(n=2) + "# Quarrybank Root CA\n" + _PEM.format(n=3))
with open("/tmp/quarrybank/corp-root-only.pem", "w") as f:
    f.write("# Quarrybank Root CA\n" + _PEM.format(n=3))
with open("/tmp/quarrybank/empty.pem", "w") as f:
    f.write("")
with open("/tmp/quarrybank/root.der.txt", "w") as f:
    f.write("binary-looking DER bytes, not PEM")
