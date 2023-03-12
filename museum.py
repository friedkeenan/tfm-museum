#!/usr/bin/env python3

import importlib
import caseus

from pathlib import Path

def run_exhibit(name, *, log=False, **kwargs):
    try:
        module = importlib.import_module(f"exhibits.{name}")

    except ModuleNotFoundError:
        raise ValueError(f"No exhibit named '{name}'")

    exhibit_name = name.split(".")[-1]
    exhibit      = getattr(module, exhibit_name)

    if log:
        # Redefine 'exhibit' to inherit from 'LoggingProxy'.
        class exhibit(caseus.proxies.LoggingProxy, exhibit):
            pass

    exhibit(**kwargs).run()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("exhibit", help="The exhibit to visit")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="The directory for the exhibit data (defaulted to 'data')")
    parser.add_argument("--log", action="store_true", help="Log packets from the client and server")

    # TODO: Add way to list available exhibits?

    args = parser.parse_args()

    run_exhibit(args.exhibit, log=args.log, data_dir=args.data_dir)
