"""Build script for vsphere_snapshots MKP — run on the Checkmk server with Python 3."""
import io, os, tarfile

VERSION = "1.0.17"
CMK_VERSION = "2.4.0p26"
BASE = "cmk_addons/plugins/vsphere_snapshots"

files = []
for root, dirs, filenames in os.walk(BASE):
    for fname in filenames:
        full = os.path.join(root, fname)
        arc = "vsphere_snapshots" + full[len(BASE):]
        files.append((full, arc))

inner_buf = io.BytesIO()
with tarfile.open(fileobj=inner_buf, mode="w") as t:
    for full, arc in files:
        t.add(full, arcname=arc)
inner_bytes = inner_buf.getvalue()

info = {
    "name": "vsphere_snapshots",
    "version": VERSION,
    "version.min_required": "2.4.0",
    "version.packaged": CMK_VERSION,
    "version.usable_until": None,
    "download_url": "",
    "title": "VMware vSphere Snapshots",
    "author": "Martin Nigg",
    "description": (
        "Special Agent for monitoring VMware vSphere snapshots. "
        "No external dependencies -- uses vSphere SOAP API via Python stdlib only."
    ),
    "category": "monitoring",
    "files": {"cmk_addons_plugins": [arc for _, arc in files]},
}

outer_buf = io.BytesIO()
with tarfile.open(fileobj=outer_buf, mode="w:gz") as t:
    info_bytes = repr(info).encode()
    ti = tarfile.TarInfo(name="info"); ti.size = len(info_bytes)
    t.addfile(ti, io.BytesIO(info_bytes))
    ti2 = tarfile.TarInfo(name="cmk_addons_plugins.tar"); ti2.size = len(inner_bytes)
    t.addfile(ti2, io.BytesIO(inner_bytes))

mkp_name = f"vsphere_snapshots-{VERSION}.mkp"
with open(mkp_name, "wb") as f:
    f.write(outer_buf.getvalue())
print(f"Built {mkp_name}: {len(outer_buf.getvalue())} bytes")
