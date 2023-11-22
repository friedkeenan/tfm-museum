import caseus

import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Rain(AdventureExhibit):
    adventure_id = 9

    map_code     = 2008
    map_xml_path = "Rain/Pinball.xml"

    round_duration = 80

    has_synchronizer = True

    BERRY_INFO = {
        # X: (collectible_id, number)

        # NOTE: X values are educated guesses
        # which I am 99% sure are correct.

        105: (7, 1),
        205: (7, 2),
        305: (8, 1),
        405: (8, 3),
        505: (8, 1),
        605: (7, 2),
        705: (7, 1),
    }

    # NOTE: Educated guess which I'm 99% sure is correct.
    BERRY_Y = 1970

    # NOTE: Educated guesses which I'm 99% sure are correct.
    BERRY_OFFSETS = {
        # Number of berries: [(offset_x, offset_y), ...]

        1: [(0, 0)],
        2: [(-10, 0), (0, 0)],
        3: [(-10, 0), (-5, 15), (0, 0)],
    }

    REWARDS = {
        # collectible_id: [item_id, ...]

        7: [2238, 800],
        8: [2245, 800],
    }

    # NOTE: Exact time of immobilization is an educated guess.
    # The plank is removed after 15 seconds, but the latest
    # I've seen players move in videos is right before 12
    # seconds have passed, and with players who were moving
    # at that point, it seems like the client extrapolates
    # their movement a little forward and then they rubberband
    # back, suggesting that the player was immobilized while moving.
    FREEZE_PLAYERS_TIME = 12

    async def immobilize_players(self):
        await self.broadcast_packet(
            caseus.clientbound.ImmobilizePlayerPacket,

            immobilize = True,
        )

    def perform_initial_scheduling(self):
        self.schedule(self.FREEZE_PLAYERS_TIME, self.immobilize_players)

    async def setup_round(self, client):
        # NOTE: Individual IDs not based on anything.
        individual_id = 0

        for berry_x, (berry_id, num_berries) in self.BERRY_INFO.items():
            for offset in self.BERRY_OFFSETS[num_berries]:
                await self.add_collectible(
                    client,

                    individual_id  = individual_id,
                    collectible_id = berry_id,
                    x              = berry_x      + offset[0],
                    y              = self.BERRY_Y + offset[1],
                )

                individual_id += 1

    def individual_id_to_collectible_id(self, individual_id):
        other_individual_id = 0
        for berry_id, num_berries in self.BERRY_INFO.values():
            if individual_id < other_individual_id + num_berries:
                return berry_id

            other_individual_id += num_berries

        return None

    async def on_get_collectible(self, client, packet):
        # NOTE: Originally you could only collect three
        # berries every ten minutes. Theoretically a player
        # could bounce out of one bucket and into another,
        # collecting more than three berries. The ten minute
        # restriction would normally stop that, but we choose
        # not to care.

        berry_id = self.individual_id_to_collectible_id(packet.individual_id)

        await self.raise_inventory_item(client, random.choice(self.REWARDS[berry_id]))
