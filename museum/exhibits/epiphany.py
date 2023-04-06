import asyncio

import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Epiphany(AdventureExhibit):
    adventure_id = 2

    map_code     = 2001
    map_xml_path = "Epiphany/Castle.xml"

    has_synchronizer = True

    KING_NAME   = "Fromagnus"
    KING_SPRITE = "$Roi"

    # NOTE: In 2016 there appears to have been
    # no title ID for the king, only appearing
    # in 2017 onwards. In fact, the game no longer
    # has the capacity for NPCs without titles,
    # and so we use the title for 2017 onwards,
    # which is 'Big Turkey'.
    KING_TITLE_ID = 353

    # NOTE: Educated guesses.
    KING_X = 1792
    KING_Y = 286

    CAKE_ID = 4

    CAKES = [
        # TODO: Actually figure this out.
        (100, 350),
    ]

    CAKE_PATH = "x_transformice/x_aventure/x_recoltables/x_4.png"

    # NOTE: Educated guesses.
    CAKE_OFFSET_X = -22
    CAKE_OFFSET_Y = -22

    incomplete = True

    async def start_new_round(self):
        self.collected_cakes = []

        await super().start_new_round()

    async def on_exit_exhibit(self, client):
        try:
            del client.carrying_cake

        except AttributeError:
            pass

    async def setup_round(self, client):
        client.carrying_cake = False

        await self.give_meep(client)

        await self.add_npc_for_individual(
            client,

            # NOTE: Session ID not based on anything.
            session_id   = -1,
            name         = self.KING_NAME,
            title_id     = self.KING_TITLE_ID,
            feminine     = False,
            outfit_code  = self.KING_SPRITE,
            x            = self.KING_X,
            y            = self.KING_Y,
            facing_right = False,
        )

        # NOTE: Individual IDs not based on anything.
        for id, (x, y) in enumerate(self.CAKES):
            if id in self.collected_cakes:
                continue

            await self.add_collectible(
                client,

                individual_id  = id,
                collectible_id = self.CAKE_ID,
                x              = x,
                y              = y,
            )

        for other_client in self.alive_clients:
            if other_client is client:
                continue

            if not other_client.carrying_cake:
                continue

            await self.add_carrying_for_individual(
                client,

                carrying_client = other_client,

                image_path = self.CAKE_PATH,
                offset_x   = self.CAKE_OFFSET_X,
                offset_y   = self.CAKE_OFFSET_Y,
                foreground = False,
            )

    async def on_get_collectible(self, client, packet):
        if packet.individual_id in self.collected_cakes:
            return

        self.collected_cakes.append(packet.individual_id)

        # TODO: TaskGroup in Python 3.11.
        await asyncio.gather(*[
            self.remove_collectible(other_client, packet.individual_id)

            for other_client in self.clients

            if other_client is not client
        ])

        client.carrying_cake = True
        await self.set_can_collect(client, False)

        await self.add_carrying(
            client,

            image_path = self.CAKE_PATH,
            offset_x   = self.CAKE_OFFSET_X,
            offset_y   = self.CAKE_OFFSET_Y,
            foreground = False,
        )

    async def on_adventure_action(self, client, packet):
        # When the client is within 100 units of King Fromagnus
        # and clicks him, then they send an adventure action with
        # action ID '1'. This should be acknowledged instead of
        # the normal click NPC interaction packet because that
        # does not care about how far the client is from the NPC.

        if not client.carrying_cake:
            return

        client.carrying_cake = False

        await self.clear_carrying(client)
        await self.raise_inventory_item(client, 2224)
