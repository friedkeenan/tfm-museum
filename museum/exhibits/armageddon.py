import asyncio
import math

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Armageddon(AdventureExhibit):
    adventure_id = 10

    map_code = 2009
    map_xml_path = "Armageddon/Arena.xml"

    FEATHER_ID   = 9
    FEATHER_PATH = "x_transformice/x_aventure/x_recoltables/x_9.png"

    FEATHER_OFFSET_X = -21
    FEATHER_OFFSET_Y = -22

    FEATHER_X = 50
    FEATHER_Y = [70, 180]

    FEATHER_DEPOSIT_X      = 350
    FEATHER_DEPOSIT_Y      = 300
    FEATHER_DEPOSIT_WIDTH  = 128
    FEATHER_DEPOSIT_HEIGHT = 60

    # NOTE: I believe that previously in 2016 the needed
    # amount of feathers was a static value of '32'.
    NEEDED_FEATHERS_MULTIPLIER = 1.5
    MIN_NEEDED_FEATHERS        = 15

    async def add_feather(self, client, id):
        await self.add_collectible(
            client,

            individual_id  = id,
            collectible_id = self.FEATHER_ID,
            x              = self.FEATHER_X,
            y              = self.FEATHER_Y[id],
        )

    async def start_new_round(self):
        self.feather_progress = 0

        self.total_feathers = max(
            self.MIN_NEEDED_FEATHERS,

            math.floor(len(self.clients) * self.NEEDED_FEATHERS_MULTIPLIER),
        )

        await super().start_new_round()

    async def report_feather_progress_to(self, client):
        await self.adventure_action(client, 10, self.total_feathers, self.feather_progress)

        if self.feather_progress >= self.total_feathers:
            await self.adventure_action(client, 2)

    async def increment_feather_progress(self):
        # NOTE: The server still updates the client on the feather
        # progress even after the needed amount has been reached,
        # despite it not resulting in any visual changes.

        self.feather_progress += 1

        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    self.report_feather_progress_to(client)
                )

        if self.feather_progress == self.total_feathers:
            await self.shorten_round()

    async def on_exit_exhibit(self, client):
        try:
            del client.carrying_id

        except AttributeError:
            pass

    async def setup_round(self, client):
        client.carrying_id = None

        # NOTE: The collectible IDs increment like other events,
        # where they globally increment per satellite server.
        #
        # The feathers have adjacent ID values, for instance
        # the higher feather would have 49 and the lower would
        # have 50 as its ID value.
        #
        # For the exhibit we just use the index from 'FEATHER_Y'.
        for id in range(len(self.FEATHER_Y)):
            await self.add_feather(client, id)

        # NOTE: The area ID would increment per-room(!) starting at '1'.
        #
        # Here however we just always send the same area ID of '1'.
        await self.add_area(
            client,

            area_id = 1,
            x       = self.FEATHER_DEPOSIT_X,
            y       = self.FEATHER_DEPOSIT_Y,
            width   = self.FEATHER_DEPOSIT_WIDTH,
            height  = self.FEATHER_DEPOSIT_HEIGHT,
        )

        await self.report_feather_progress_to(client)

        for other_client in self.alive_clients:
            if other_client is client:
                continue

            if other_client.carrying_id is None:
                continue

            await self.add_carrying_for_individual(
                client,

                carrying_client = other_client,

                image_path = self.FEATHER_PATH,
                offset_x   = self.FEATHER_OFFSET_X,
                offset_y   = self.FEATHER_OFFSET_Y,
                foreground = False,
            )

    async def on_get_collectible(self, client, packet):
        await self.set_can_collect(client, False)

        await self.add_carrying(
            client,

            image_path = self.FEATHER_PATH,
            offset_x   = self.FEATHER_OFFSET_X,
            offset_y   = self.FEATHER_OFFSET_Y,
            foreground = False,
        )

        client.carrying_id = packet.individual_id

    async def on_enter_area(self, client, packet):
        if client.carrying_id is None:
            return

        await self.add_feather(client, client.carrying_id)

        client.carrying_id = None
        await self.set_can_collect(client, True)

        await self.clear_carrying(client)

        await self.increment_feather_progress()
