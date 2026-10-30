"""Task 0.1 + 0.2. Run: python3 src/profile_env.py --student-id <YOUR_ID>"""
import argparse
import glob
import json
import os
import platform
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from salt import get_student_params

try:
    import psutil
except ImportError:
    psutil = None


def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def parse_size(txt):
    """'32K' / '1M' / '1024K' -> bytes."""
    m = re.match(r"(\d+)\s*([KMG]?)", txt.strip().upper())
    if not m:
        return None
    return int(m.group(1)) * {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}[m.group(2)]


def cpu_info_linux():
    info = {}
    try:
        with open("/proc/cpuinfo") as f:
            txt = f.read()
        for key, field in [("model_name", "model name"), ("family", "cpu family"),
                           ("model", "model"), ("stepping", "stepping"),
                           ("vendor", "vendor_id")]:
            m = re.search(rf"^{field}\s*:\s*(.+)$", txt, re.M)
            if m:
                info[key] = m.group(1).strip()
    except OSError:
        pass
    return info


def caches_linux():
    out = {"l1d_bytes": None, "l2_bytes": None, "l3_bytes": None, "line_bytes": None}
    for d in sorted(glob.glob("/sys/devices/system/cpu/cpu0/cache/index*")):
        try:
            rd = lambda n: open(os.path.join(d, n)).read().strip()
            level, ctype, size = rd("level"), rd("type"), parse_size(rd("size"))
            line = int(rd("coherency_line_size"))
        except (OSError, ValueError):
            continue
        out["line_bytes"] = line
        if level == "1" and ctype == "Data":
            out["l1d_bytes"] = size
        elif level == "2":
            out["l2_bytes"] = size
        elif level == "3":
            out["l3_bytes"] = size
    return out


def caches_macos():
    keys = {"l1d_bytes": "hw.l1dcachesize", "l2_bytes": "hw.l2cachesize",
            "l3_bytes": "hw.l3cachesize", "line_bytes": "hw.cachelinesize"}
    out = {}
    for k, name in keys.items():
        v = sh(f"sysctl -n {name}")
        out[k] = int(v) if v and v.isdigit() and int(v) > 0 else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-id", required=True)
    args = ap.parse_args()

    system = platform.system()
    cpu = {"model_name": platform.processor() or None, "machine": platform.machine()}
    if system == "Linux":
        cpu.update(cpu_info_linux())
        caches = caches_linux()
    elif system == "Darwin":
        cpu["model_name"] = sh("sysctl -n machdep.cpu.brand_string") or cpu["model_name"]
        caches = caches_macos()
    else:
        caches = {"l1d_bytes": None, "l2_bytes": None, "l3_bytes": None, "line_bytes": None}

    # Base frequency (MHz): psutil max is the closest portable value; verify with lscpu.
    freq = None
    if psutil:
        f = psutil.cpu_freq()
        if f:
            freq = {"current_mhz": f.current, "max_mhz": f.max, "min_mhz": f.min}
    cpu["frequency"] = freq

    logical = os.cpu_count()
    physical = psutil.cpu_count(logical=False) if psutil else None
    topology = {
        "physical_cores": physical,
        "logical_threads": logical,
        "smt_enabled": bool(physical and logical and logical > physical),
    }

    profile = {
        "cpu": cpu,
        "topology": topology,
        "caches": caches,
        "cache_line_bytes": caches.get("line_bytes") or 64,
        "os": {"system": system, "release": platform.release(),
               "kernel_version": platform.version()},
        "python": {"implementation": platform.python_implementation(),
                   "version": platform.python_version(),
                   "compiler": platform.python_compiler()},
        "notes": "Fields that are null could not be detected; fill from lscpu / "
                 "system docs and say so in the README.",
    }

    os.makedirs("results", exist_ok=True)
    with open("results/host_profile.json", "w") as f:
        json.dump(profile, f, indent=2)
    params = get_student_params(args.student_id)
    with open("results/salted_params.json", "w") as f:
        json.dump(params, f, indent=2)

    print(json.dumps(profile, indent=2))
    print(json.dumps(params, indent=2))


if __name__ == "__main__":
    main()