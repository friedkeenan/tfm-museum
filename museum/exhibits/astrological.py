import caseus

import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Astrological(AdventureExhibit):
    adventure_id = 1

    map_code     = 2000
    map_xml_path = "Astrological/Food.xml"

    round_duration = 90

    has_synchronizer = True

    CHEESE_IDS = range(2212, 2224)

    async def setup_round(self, client):
        # NOTE: Originally the astrological cheeses a player
        # owned would show up around the cheese moon. Because
        # the museum has no persistent state, we instead tell
        # the player they have a random assortment of the
        # cheeses for them to show up around the moon.
        await client.write_packet(
            caseus.clientbound.LoadInventoryPacket,

            items = [
                # NOTE: Most values aren't based on anything really.
                dict(
                    item_id             = item_id,
                    quantity            = 1,
                    priority            = 0,
                    unk_boolean_4       = False,
                    can_use             = False,
                    can_equip           = False,
                    unk_boolean_7       = False,
                    category            = caseus.enums.ItemCategory.Adventure,
                    can_use_immediately = False,
                    can_use_when_dead   = False,
                    image_name          = None,
                    slot                = -1,
                )

                for item_id in random.sample(self.CHEESE_IDS, random.randrange(len(self.CHEESE_IDS) + 1))
            ],
        )

        await self.adventure_action(client, 2)

    async def on_multi_emote(self, client, packet):
        if packet.emote is not caseus.enums.Emote.Highfive_1:
            return

        # NOTE: Originally a player was only allowed
        # to get the reward from a high five once.
        # We don't do the same because we don't perform
        # any persistent change.

        await self.raise_inventory_item(client,                    random.choice(self.CHEESE_IDS))
        await self.raise_inventory_item(packet.partner_session_id, random.choice(self.CHEESE_IDS))
