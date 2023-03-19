import caseus

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Dragon(AdventureExhibit):
    adventure_id = 6

    map_code     = 2005
    map_xml_path = "Dragon/Climb.xml"

    has_synchronizer = True

    LANTERN_ID = 6

    # NOTE: Very educated guesses which I'm 85% sure are dead on.
    LANTERN_X = 130
    LANTERN_Y = 320

    # NOTE: Other items were awarded to players upon
    # collecting the lantern, however I have only ever
    # seen players raise the cheese coin item, and the
    # other items awarded do not have any visual display
    # beyond the notification that they were awarded.
    #
    # Perhaps in the future the pseudo-awarding of items
    # could be added to the museum, but I'm not sure that
    # that is necessarily within the scope of reliving the
    # event an exhibit is for.
    REWARD_ID = 800

    async def setup_round(self, client):
        await self.add_collectible(
            client,

            # NOTE: Individual ID not based on anything.
            individual_id  = 0,
            collectible_id = self.LANTERN_ID,
            x              = self.LANTERN_X,
            y              = self.LANTERN_Y,
        )

    async def on_get_collectible(self, client, packet):
        await self.broadcast_packet(
            caseus.clientbound.RaiseItemPacket,

            session_id = client.session_id,
            item       = caseus.clientbound.RaiseItemPacket.InventoryItem(
                item_id = self.REWARD_ID,
            ),
        )
