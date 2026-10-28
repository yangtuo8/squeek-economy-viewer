# squeek-economy-viewer

A tiny, read-only command-line tool for inspecting the on-chain economy of
[Squeekchain](https://squeekchain.com) — a hamster-wheel PoW chain that settles
on Ethereum Sepolia.

It pulls the live economy state from the public community API
(`https://api.squeekchain.com/v1/economy/state`), lists the core Sepolia
contracts (SQK token, core, mining & staking proxies, gacha vault, token
factory), and can read the SQK balances held by those proxies straight from a
Sepolia RPC node.

## Why

The web app is great, but sometimes you just want a quick terminal snapshot of
where the SQK supply sits and which contracts are live. This tool does exactly
that with zero dependencies — pure Python standard library, no wallet, no keys,
no writes.

## Usage

```bash
python3 squeek_viewer.py            # economy state + resolved contracts
python3 squeek_viewer.py --staking  # also read SQK balances of the proxies
```

## Example output

```
== Squeekchain economy (Sepolia, chainId 11155111) ==
  core             0x980b4424c007caf7a1f3670b48c8eaef7ebc3d44
  token            0x5501e1fa81be1c3f49225fa7668da0245d07db60
  staking          0x4b67b739dfd832f4eac67a7aa3bc244fb74cea4f
  ...
```

## Notes

- Read-only: it never sends a transaction or asks for a private key.
- Sepolia only — Squeekchain's contracts live on testnet today.

## License

MIT
