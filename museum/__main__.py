import caseus

from pathlib import Path

from .museum import Museum

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("museum")

    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="The directory for the exhibit data (defaulted to 'data')")
    parser.add_argument("--log", action="store_true", help="Log packets from the client and server")

    args = parser.parse_args()

    if args.log:
        # Redefine 'Museum' to inherit from 'LoggingServer'.
        class Museum(caseus.servers.LoggingServer, Museum):
            pass

    Museum(data_dir=args.data_dir).run()
