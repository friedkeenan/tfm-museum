import caseus

import asyncio
import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Dance(AdventureExhibit):
    adventure_id = 22

    map_code     = 941
    map_author   = "_Classroom"
    map_xml_path = "School/Classroom.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    round_duration = 60

    ARROW_INTERVALS = [5, 12, 18]
    ARROW_COUNTS    = [5,  7, 10]

    ARROW_VALUES = range(4)

    COMPLETED_TEMPLATE = "<V>$RentreeSerieReussie</V>"
    COMPLETED_REWARD   = 2334

    INCOMPLETE_TEMPLATE = "<R>$RentreeSerieEchouee</R>"
    INCOMPLETE_REWARD   = 2335

    def setup_round_timings(self, round_start):
        self.next_arrows_time = round_start + self.ARROW_INTERVALS[0]

        self.arrow_intervals = self.ARROW_INTERVALS[1:]

    async def _report_complete(self, client):
        await self.translated_general_message(client, self.COMPLETED_TEMPLATE)
        await self.raise_inventory_item(client, self.COMPLETED_REWARD)

    async def _report_incomplete(self, client):
        await self.translated_general_message(client, self.INCOMPLETE_TEMPLATE)
        await self.raise_inventory_item(client, self.INCOMPLETE_REWARD)

    async def _send_next_arrows(self, client, next_arrows, *, check_incomplete):
        if check_incomplete and client.attempted_dance and not client.completed_dance:
            await self._report_incomplete(client)

        client.attempted_dance = False
        client.completed_dance = False

        await self.adventure_action(client, 2, *next_arrows)

    async def check_round_timings(self, time):
        if len(self.arrow_groups) <= 0:
            return

        if time >= self.next_arrows_time:
            # If this is not the first set of arrows,
            # check whether the clients failed the dance.
            check_incomplete = len(self.arrow_groups) < len(self.ARROW_COUNTS)

            next_arrows = self.arrow_groups.pop(0)

            async with asyncio.TaskGroup() as tg:
                for client in self.clients:
                    tg.create_task(
                        self._send_next_arrows(client, next_arrows, check_incomplete=check_incomplete)
                    )

            if len(self.arrow_intervals) > 0:
                self.next_arrows_time = time + self.arrow_intervals.pop(0)

    async def on_exit_exhibit(self, client):
        try:
            del client.attempted_dance

        except AttributeError:
            pass

        try:
            del client.completed_dance

        except AttributeError:
            pass

    async def start_new_round(self):
        self.arrow_groups = []
        for count in self.ARROW_COUNTS:
            arrows = [random.choice(self.ARROW_VALUES) for _ in range(count)]
            arrows.insert(0, count)

            self.arrow_groups.append(arrows)

        await super().start_new_round()

    async def on_round_end(self):
        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                if client.attempted_dance and not client.completed_dance:
                    tg.create_task(
                        self._report_incomplete(client)
                    )

    async def on_adventure_action(self, client, packet):
        if packet.action_id == 8:
            client.attempted_dance = True

            return

        # After this point, 'packet.action_id' will be '6'.
        #
        # NOTE: The client will not submit an incorrect
        # sequence of arrows, so while the official server
        # *does* verify the actual arrows the client sends,
        # we do not because we only care about standard clients.

        client.completed_dance = True

        await self._report_complete(client)
