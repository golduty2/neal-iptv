#!/usr/bin/env python3
"""Probe every channel in an M3U: manifest -> first variant -> first segment. Direct connection, no proxy."""
import sys, re, json, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

os.environ.pop('http_proxy', None); os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None); os.environ.pop('HTTPS_PROXY', None); os.environ.pop('ALL_PROXY', None); os.environ.pop('all_proxy', None)
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"

def fetch(url, maxbytes=None, timeout=12):
    cmd = ["curl", "-sS", "-L", "--noproxy", "*", "-m", str(timeout), "-A", UA, "-o", "-",
           "-w", "\n@@%{http_code} %{time_starttransfer} %{url_effective}"]
    if maxbytes: cmd += ["-r", f"0-{maxbytes-1}"]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout+5)
    except subprocess.TimeoutExpired:
        return None, 0, 0.0, url, "timeout"
    out = p.stdout
    i = out.rfind(b"\n@@")
    if i < 0:
        return None, 0, 0.0, url, (p.stderr.decode(errors='replace').strip()[:80] or "no response")
    body, meta = out[:i], out[i+3:].decode(errors='replace').split(" ", 2)
    code = int(meta[0] or 0); t = float(meta[1] or 0); eff = meta[2].strip() if len(meta) > 2 else url
    err = p.stderr.decode(errors='replace').strip()[:80]
    return body, code, t, eff, err

def parse_master(body):
    lines = body.decode('utf-8', errors='replace').splitlines()
    variants = []
    for i, l in enumerate(lines):
        if l.startswith('#EXT-X-STREAM-INF'):
            m = re.search(r'RESOLUTION=(\d+)x(\d+)', l); bw = re.search(r'BANDWIDTH=(\d+)', l)
            uri = next((x for x in lines[i+1:] if x and not x.startswith('#')), None)
            variants.append(((int(m.group(1)), int(m.group(2))) if m else None, int(bw.group(1)) if bw else 0, uri))
    return variants

def first_segment(body):
    for l in body.decode('utf-8', errors='replace').splitlines():
        if l and not l.startswith('#'):
            return l
    return None

def probe(ch):
    name, group, url = ch
    r = {"name": name, "group": group, "url": url}
    t0 = time.time()
    body, code, t, eff, err = fetch(url)
    r["code"] = code; r["ttfb"] = round(t, 2)
    if body is None or code != 200 or not body.lstrip().startswith(b"#EXTM3U"):
        r["status"] = "DEAD"; r["why"] = err or f"http {code}" + ("" if body is None or body.lstrip().startswith(b"#EXTM3U") else " non-m3u8 body")
        return r
    variants = parse_master(body)
    res = None
    media_url, media_body = eff, body
    if variants:
        variants.sort(key=lambda v: (v[0][0]*v[0][1] if v[0] else 0, v[1]), reverse=True)
        res = variants[0][0]; r["variants"] = len(variants)
        vb, vc, vt, veff, verr = fetch(urljoin(eff, variants[0][2]))
        if vb is None or vc != 200 or not vb.lstrip().startswith(b"#EXTM3U"):
            # try lowest variant too
            r["status"] = "DEAD"; r["why"] = f"variant http {vc} {verr}"; r["res"] = f"{res[0]}x{res[1]}" if res else "?"; return r
        media_url, media_body = veff, vb
    r["res"] = f"{res[0]}x{res[1]}" if res else "?"
    seg = first_segment(media_body)
    if not seg:
        r["status"] = "DEAD"; r["why"] = "no segments in media playlist"; return r
    sb, sc, st, seff, serr = fetch(urljoin(media_url, seg), maxbytes=65536, timeout=15)
    if sb is None or sc not in (200, 206) or len(sb) == 0:
        r["status"] = "DEAD"; r["why"] = f"segment http {sc} {serr}"; return r
    total = time.time() - t0
    r["status"] = "OK" if total < 6 else "SLOW"
    r["total"] = round(total, 1)
    return r

def load(path):
    L = open(path, encoding='utf-8').read().splitlines(); chans = []
    for i, l in enumerate(L):
        if l.startswith('#EXTINF'):
            g = re.search(r'group-title="([^"]*)"', l); name = l.rsplit(',', 1)[-1].strip()
            chans.append((name, g.group(1) if g else "", L[i+1].strip()))
    return chans

if __name__ == "__main__":
    chans = load(sys.argv[1])
    with ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(probe, chans))
    json.dump(results, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    ok = sum(r["status"]=="OK" for r in results); slow = sum(r["status"]=="SLOW" for r in results); dead = sum(r["status"]=="DEAD" for r in results)
    print(f"OK={ok} SLOW={slow} DEAD={dead} / {len(results)}")
    for r in results:
        flag = {"OK":"✅","SLOW":"🐢","DEAD":"❌"}[r["status"]]
        print(f'{flag} [{r["group"]}] {r["name"]:<28} res={r.get("res","-"):<10} ttfb={r["ttfb"]:<5} {r.get("total","")} {r.get("why","")}')
