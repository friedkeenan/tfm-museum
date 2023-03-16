import asyncio

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Armageddon(AdventureExhibit):
    adventure_id = 10

    map_code = 2009
    map_xml_path = "Armageddon/Arena.xml"

    FEATHER_ID   = 9
    FEATHER_PATH = "x_transformice/x_aventure/x_recoltables/x_9.png"

    # NOTE: Educated guess.
    FEATHER_OFFSET = (-28, -22)

    # NOTE: Educated guesses.
    FEATHER_X = 50
    FEATHER_Y = [208 - 11 - 18 + 1, 114 - 25 - 18 - 1]

    # NOTE: Educated guesses.
    FEATHER_DEPOSIT_X      = 370
    FEATHER_DEPOSIT_Y      = 330
    FEATHER_DEPOSIT_WIDTH  = 100
    FEATHER_DEPOSIT_HEIGHT = 30

    # TODO: Apparently the original value was '32'.
    # This does not seem very feasible to beat with
    # only one player. Should we add an option to
    # change this?
    FEATHER_TOTAL = 32

    async def add_feather(self, client, id):
        await self.add_collectable(
            client,

            individual_id  = id,
            collectable_id = self.FEATHER_ID,
            x              = self.FEATHER_X,
            y              = self.FEATHER_Y[id],
        )

    async def start_new_round(self):
        self.feather_progress = 0

        await super().start_new_round()

    async def report_feather_progress_to(self, client):
        await self.adventure_action(client, 10, self.FEATHER_TOTAL, self.feather_progress)

        if self.feather_progress >= self.FEATHER_TOTAL:
            await self.adventure_action(client, 2)

    async def increment_feather_progress(self):
        # NOTE: I do not know whether the server still changed
        # the feather progress after reaching the required feathers,
        # but it would not have resulted in any visual changes.
        if self.feather_progress >= self.FEATHER_TOTAL:
            return

        self.feather_progress += 1

        # TODO: TaskGroup in Python 3.11.
        await asyncio.gather(*[
            self.report_feather_progress_to(client)

            for client in self.clients
        ])

    async def on_exit_exhibit(self, client):
        try:
            del client.carrying_id

        except AttributeError:
            pass

    async def setup_round(self, client):
        client.carrying_id = None

        # NOTE: The specific IDs used aren't based on anything.
        for id in range(len(self.FEATHER_Y)):
            await self.add_feather(client, id)

        # NOTE: Area ID not based on anything.
        await self.add_area(
            client,

            area_id = 1,
            x       = self.FEATHER_DEPOSIT_X,
            y       = self.FEATHER_DEPOSIT_Y,
            width   = self.FEATHER_DEPOSIT_WIDTH,
            height  = self.FEATHER_DEPOSIT_HEIGHT,
        )

        await self.report_feather_progress_to(client)

    async def on_get_collectable(self, client, packet):
        await self.set_can_collect(client, False)

        await self.add_carrying(
            client,

            image_path = self.FEATHER_PATH,
            offset_x   = self.FEATHER_OFFSET[0],
            offset_y   = self.FEATHER_OFFSET[1],
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
