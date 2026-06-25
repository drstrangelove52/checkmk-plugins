#!/usr/bin/env python3
"""VMware vSphere snapshot special agent for Checkmk 2.4+."""

import argparse
import atexit
import json
import ssl
import sys
from datetime import datetime, timezone

try:
    from pyVim.connect import Disconnect, SmartConnect
    from pyVmomi import vim
except ImportError:
    sys.stderr.write("Error: pyVmomi is not installed. Run: pip3 install pyVmomi\n")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="VMware vSphere snapshot check agent for Checkmk"
    )
    parser.add_argument("--hostname", required=True, help="vCenter hostname or IP")
    parser.add_argument("--user", required=True, help="vCenter username")
    parser.add_argument("--password", required=True, help="vCenter password")
    parser.add_argument("--port", type=int, default=443, help="vCenter port (default: 443)")
    parser.add_argument(
        "--no-ssl-verify",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--fallback-host",
        required=True,
        help="Checkmk hostname for VMs without a dedicated Checkmk host",
    )
    return parser.parse_args()


def connect_vcenter(hostname: str, user: str, password: str, port: int, no_ssl: bool):
    if no_ssl:
        context = ssl._create_unverified_context()
    else:
        context = ssl.create_default_context()
    return SmartConnect(host=hostname, user=user, pwd=password, port=port, sslContext=context)


def get_all_vms(content) -> list:
    view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    vms = list(view.view)
    view.Destroy()
    return vms


def build_snapshot_size_map(vm) -> dict:
    size_map: dict = {}
    if not hasattr(vm, "layoutEx") or vm.layoutEx is None:
        return size_map
    file_size_by_key = {f.key: f.size for f in (vm.layoutEx.file or [])}
    for snap_layout in vm.layoutEx.snapshot or []:
        mor_id = snap_layout.key._moId
        size_map[mor_id] = file_size_by_key.get(snap_layout.dataKey, 0)
    return size_map


def collect_snapshots(snapshot_list, size_map: dict) -> list:
    snapshots = []
    now = datetime.now(timezone.utc)
    for snap in snapshot_list:
        create_time = snap.createTime
        if create_time.tzinfo is None:
            create_time = create_time.replace(tzinfo=timezone.utc)
        age_days = (now - create_time).total_seconds() / 86400
        mor_id = snap.snapshot._moId
        snapshots.append(
            {
                "name": snap.name,
                "description": snap.description or "",
                "create_time": create_time.isoformat(),
                "age_days": round(age_days, 2),
                "size_bytes": size_map.get(mor_id, 0),
            }
        )
        if snap.childSnapshotList:
            snapshots.extend(collect_snapshots(snap.childSnapshotList, size_map))
    return snapshots


def guest_hostname(vm) -> str | None:
    if vm.guest and vm.guest.hostName:
        return vm.guest.hostName
    return None


def main() -> None:
    args = parse_args()

    try:
        si = connect_vcenter(
            args.hostname, args.user, args.password, args.port, args.no_ssl_verify
        )
    except Exception as exc:
        sys.stderr.write(f"Failed to connect to vCenter {args.hostname}: {exc}\n")
        sys.exit(1)

    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    vm_results = []
    fallback_results = []
    for vm in get_all_vms(content):
        if vm.snapshot is None:
            continue
        size_map = build_snapshot_size_map(vm)
        snapshots = collect_snapshots(vm.snapshot.rootSnapshotList, size_map)
        if not snapshots:
            continue
        pb_host = guest_hostname(vm)
        vm_data = {"vm_name": vm.name, "snapshots": snapshots}
        if pb_host:
            vm_results.append({"piggyback_host": pb_host, **vm_data})
        else:
            fallback_results.append(vm_data)

    # Piggyback-Sektion pro VM (VMware Tools liefert FQDN)
    for vm_data in vm_results:
        print(f"<<<<{vm_data['piggyback_host']}>>>>")
        print("<<<vsphere_snapshots:sep(0)>>>")
        print(json.dumps({"vm_name": vm_data["vm_name"], "snapshots": vm_data["snapshots"]}))
        print("<<<<>>>>")

    # Sammel-Host: nur VMs ohne VMware Tools / ohne Guest-Hostname
    if fallback_results:
        print(f"<<<<{args.fallback_host}>>>>")
        print("<<<vsphere_snapshots_all:sep(0)>>>")
        for vm_data in fallback_results:
            print(json.dumps(vm_data))
        print("<<<<>>>>")


if __name__ == "__main__":
    sys.exit(main())
