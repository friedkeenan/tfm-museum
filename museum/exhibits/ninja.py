import asyncio

import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Ninja(AdventureExhibit):
    adventure_id = 18

    map_code     = 2017
    map_xml_path = "Ninja/Training.xml"

    has_shaman       = True
    has_synchronizer = True

    SCROLL_ID = 26

    # NOTE: Educated guesses which I'm pretty sure are correct.
    SCROLL_X = 64
    SCROLL_Y = 105

    TURTLE_SHELL_PATH = "x_transformice/x_evt/x_evt_18/sdnjqj/carapace.png"

    # NOTE: Educated guesses.
    TURTLE_OFFSET_X = -20
    TURTLE_OFFSET_Y = -22

    REWARD_ID = 2257

    async def setup_round(self, client):
        await self.add_collectible(
            client,

            # NOTE: Individual ID not based on anything.
            individual_id  = 0,
            collectible_id = self.SCROLL_ID,
            x              = self.SCROLL_X,
            y              = self.SCROLL_Y,
        )

        await asyncio.gather(*[
            self.add_carrying_for_individual(
                client,

                carrying_client = other_client,

                image_path = self.TURTLE_SHELL_PATH,
                offset_x   = self.TURTLE_OFFSET_X,
                offset_y   = self.TURTLE_OFFSET_Y,
                foreground = False,
            )

            for other_client in self.clients

            if other_client.activity is not caseus.enums.PlayerActivity.Inert
        ])

    async def on_get_collectible(self, client, packet):
        await self.broadcast_packet(
            caseus.clientbound.RaiseItemPacket,

            session_id = client.session_id,
            item       = caseus.clientbound.RaiseItemPacket.InventoryItem(
                item_id = self.REWARD_ID,
            ),
        )
