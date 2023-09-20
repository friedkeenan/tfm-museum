import asyncio
import caseus

from aioconsole import aprint

class TimedLoggingProxy(caseus.proxies.LoggingProxy):
    # I use this to log the packets of event maps
    # I partake in, taking special note of timings.

    async def _log_packet(self, source, packet):
        if isinstance(packet, caseus.ServerboundPacket):
            bound = "Serverbound"
        else:
            bound = "Clientbound"

        if source.is_satellite:
            connection = "SATELLITE"
        else:
            connection = "MAIN"

        await aprint(f"{asyncio.get_running_loop().time():.6f} | {connection}: {bound}: {packet}")

if __name__ == "__main__":
    print("Proxying...")

    TimedLoggingProxy().run()
