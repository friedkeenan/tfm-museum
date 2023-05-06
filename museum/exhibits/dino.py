import asyncio

import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Dino(AdventureExhibit):
    adventure_id = 16

    map_code     = 2015
    map_xml_path = "Dino/TimeMachine.xml"

    GEAR_PATH = "x_transformice/x_aventure/x_recoltables/x_25.png"

    # NOTE: Educated guesses.
    GEAR_OFFSET_X = -38
    GEAR_OFFSET_Y = -35

    GEAR_ID = 25

    # NOTE: Educated guesses.
    # Also note that the gear positions changed in 2018.
    # We use the 2016 positions. Maybe we should randomly
    # pick between the two? There are however other
    # differences too, which we would want to also replicate.
    GEARS = [
        (120, 225),
        (458, 190),
        (470, 33),
    ]

    # NOTE: Educated guesses.
    GEAR_DEPOSIT_X      = 740
    GEAR_DEPOSIT_Y      = 285
    GEAR_DEPOSIT_WIDTH  = 50
    GEAR_DEPOSIT_HEIGHT = 90

    async def start_new_round(self):
        self.gear_progress = 0

        # NOTE: Definitely in 2022 the number of needed gears
        # was dynamic with respect to the number of players,
        # I expect the same was true in 2018, and I am unsure
        # of 2016. I don't know the exact calculations that
        # were used to determine the number of needed gears,
        # but we want something still attainable anyways,
        # especially in the case of one player. So we do
        # the following calculation:
        self.needed_gears = int(2.5 * len(self.clients))

        await super().start_new_round()

    async def _show_time_travel(self, client, time_traveler):
        await self.adventure_action(client, 2, time_traveler.session_id)

        time_traveler.activity = caseus.enums.PlayerActivity.Dead

    async def show_time_travel(self, client):
        async with asyncio.TaskGroup() as tg:
            for time_traveler in self.alive_clients:
                tg.create_task(
                    self._show_time_travel(client, time_traveler)
                )

        # Make the tardis time travel too.
        await self.adventure_action(client, 3)

    async def report_gear_progress_to(self, client):
        await self.adventure_action(client, 1, self.gear_progress, self.needed_gears)

        if self.gear_progress >= self.needed_gears:
            await self.show_time_travel(client)

    async def increment_gear_progress(self):
        if self.gear_progress >= self.needed_gears:
            return

        self.gear_progress += 1

        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    self.report_gear_progress_to(client)
                )

        if self.gear_progress >= self.needed_gears:
            await self.shorten_round(15)

    async def on_exit_exhibit(self, client):
        try:
            del client.carrying_gear

        except AttributeError:
            pass

    async def add_gears(self, client):
        # NOTE: Individual IDs not based on anything.
        for id, (x, y) in enumerate(self.GEARS):
            await self.add_collectible(
                client,

                individual_id  = id,
                collectible_id = self.GEAR_ID,
                x              = x,
                y              = y,
            )

    async def setup_round(self, client):
        client.carrying_gear = False

        await self.add_gears(client)

        # NOTE: Area ID not based on anything.
        await self.add_area(
            client,

            area_id = 1,
            x       = self.GEAR_DEPOSIT_X,
            y       = self.GEAR_DEPOSIT_Y,
            width   = self.GEAR_DEPOSIT_WIDTH,
            height  = self.GEAR_DEPOSIT_HEIGHT,
        )

        await self.report_gear_progress_to(client)

        for other_client in self.alive_clients:
            if other_client is client:
                continue

            if not other_client.carrying_gear:
                continue

            await self.add_carrying_for_individual(
                client,

                carrying_client = other_client,

                image_path = self.GEAR_PATH,
                offset_x   = self.GEAR_OFFSET_X,
                offset_y   = self.GEAR_OFFSET_Y,
                foreground = True,
            )

    async def on_get_collectible(self, client, packet):
        await self.set_can_collect(client, False)
        client.carrying_gear = True

        await self.add_carrying(
            client,

            image_path = self.GEAR_PATH,
            offset_x   = self.GEAR_OFFSET_X,
            offset_y   = self.GEAR_OFFSET_Y,
            foreground = False,
        )

    async def on_enter_area(self, client, packet):
        if not client.carrying_gear:
            return

        client.carrying_gear = False
        await self.set_can_collect(client, True)

        await self.clear_carrying(client)

        await self.increment_gear_progress()
