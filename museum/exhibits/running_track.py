import caseus

import asyncio
import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Running_Track(AdventureExhibit):
    adventure_id = 22

    map_code     = 940
    map_author   = "_Running Track"
    map_xml_path = "School/RunningTrack.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    round_duration = 60

    # NOTE: This map does have a synchronizer, but
    # the only objects that will exist are cannonballs,
    # and the client will neglect to sync any cannonballs
    # on this map. And so we do not bother with having
    # a synchronizer.

    # NOTE: Educated guesses based on very
    # many samples. These durations do appear
    # to be discrete choices of only whole
    # numbers, and not continuous ranges.
    INITIAL_CANNON_TIMES = range(4, 6 + 1)
    CANNON_INTERVALS     = range(1, 4 + 1)

    CANNON_X          = 1535
    CANNON_Y          = 356
    CANNON_ANGLE      = 270
    CANNON_VELOCITY_X = -90
    CANNON_VELOCITY_Y = 0

    PASS_TIME            = 30
    PASS_TEMPLATE        = "<V>$RentreeEpreuveReussie</V>"
    ALMOST_PASS_TEMPLATE = "<R>$RentreePasAssezRapide</R>"
    FAIL_TEMPLATE        = "<R>$RentreeEpreuveEchouee</R>"

    async def launch_cannon(self):
        await self.broadcast_packet(
            caseus.clientbound.AddShamanObjectPacket,

            object_id            = self.next_cannon_id,
            shaman_object_id     = 17,
            x                    = self.CANNON_X,
            y                    = self.CANNON_Y,
            angle                = self.CANNON_ANGLE,
            velocity_x           = self.CANNON_VELOCITY_X,
            velocity_y           = self.CANNON_VELOCITY_Y,
            has_contact_listener = False,
            mice_collidable      = True,
            colors               = [],
        )

        self.next_cannon_id += 1

        self.schedule(random.choice(self.CANNON_INTERVALS), self.launch_cannon)

    def perform_initial_scheduling(self):
        self.schedule(random.choice(self.INITIAL_CANNON_TIMES), self.launch_cannon)

    async def on_player_victory(self, client, victory_time):
        if victory_time <= self.PASS_TIME:
            await self.translated_general_message(client, self.PASS_TEMPLATE)
        else:
            await self.translated_general_message(client, self.ALMOST_PASS_TEMPLATE)

    async def on_round_end(self):
        # Inform the remaining players that they failed the test.
        #
        # NOTE: The official server appears to only
        # send this to players who moved in the round.

        async with asyncio.TaskGroup() as tg:
            for client in self.alive_clients:
                tg.create_task(
                    self.translated_general_message(client, self.FAIL_TEMPLATE)
                )

    async def start_new_round(self):
        # Due to a field not getting reset in the client's adventure handler,
        # there can be a situation where upon loaading the running track again,
        # the player is unable to move either at all or until a cannon moves them
        # first.
        #
        # We hackily solve this by disabling and re-enabling the adventure
        # so that the relevant field of the adventure handler gets reset.
        await self.reset_adventure()

        # NOTE: The object IDs for the cannons used here
        # are the exact same as what the official server uses.
        self.next_cannon_id = 1

        await super().start_new_round()
