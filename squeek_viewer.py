#!/usr/bin/env python3
"""squeek-economy-viewer — a tiny read-only CLI for Squeekchain's on-chain economy.

Squeekchain is a hamster-wheel PoW chain settling on Ethereum Sepolia. This tool
pulls the live economy state from the public community API and resolves the core
Sepolia contracts so you can inspect SQK supply, the mining/staking proxies and the
gacha vault without opening the web app.

Usage:
    python3 squeek_viewer.py              # print economy state + contracts
    python3 squeek_viewer.py --staking    # also read SQK balances of the proxies
"""
import argparse
import json
import urllib.request

ECONOMY_API = "https://api.squeekchain.com/v1/economy/state"
SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
SQK_DECIMALS = 18


def _get_json(url):
    req = urllib.request.Request(url, headers={"accept": "application/json",
                                               "user-agent": "squeek-economy-viewer/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def _rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(SEPOLIA_RPC, data=body,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode()).get("result")


def erc20_balance(token, holder):
    data = "0x70a08231" + holder[2:].lower().rjust(64, "0")
    try:
        res = _rpc("eth_call", [{"to": token, "data": data}, "latest"])
    except Exception:
        return None
    return int(res, 16) / 10 ** SQK_DECIMALS if res and res != "0x" else 0.0


def _flatten(o, prefix=""):
    """Collect every 0x-address in a nested dict, keyed by dotted path."""
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and v.startswith("0x") and len(v) == 42:
                out[prefix + k] = v
            elif isinstance(v, dict):
                out.update(_flatten(v, prefix + k + "."))
    return out


def main():
    ap = argparse.ArgumentParser(description="Inspect Squeekchain's economy state.")
    ap.add_argument("--staking", action="store_true", help="read SQK balances of proxies")
    args = ap.parse_args()

    state = _get_json(ECONOMY_API)
    ids = _flatten(state.get("identities", {}))
    ids.update(_flatten(state.get("mining", {}), "mining."))
    print("== Squeekchain economy (Sepolia, chainId 11155111) ==")
    sup = state.get("supply", {})
    if sup:
        print(f"  status={state.get('status')}  release={state.get('release')}  supply={sup}")
    for name, addr in sorted(ids.items()):
        print(f"  {name:22} {addr}")

    token = ids.get("token")
    if args.staking and token:
        print("\n== SQK balances of key contracts ==")
        for name in ("staking.proxy", "mining.proxy", "core", "mining.gachaVault"):
            addr = ids.get(name)
            if addr:
                bal = erc20_balance(token, addr)
                print(f"  {name:18} " + (f"{bal:,.4f} SQK" if bal is not None else "n/a (rpc busy)"))


if __name__ == "__main__":
    main()
