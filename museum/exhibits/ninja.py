import asyncio

import caseus

from ..adventure import AdventureExhibit
from ..shop      import Shops, ShopExhibit
from ..exhibit   import available

@available
class Ninja(AdventureExhibit, ShopExhibit):
    adventure_id = 18

    map_code     = 2017
    map_xml_path = "Ninja/Training.xml"

    has_shaman       = True
    has_synchronizer = True

    SCROLL_ID = 26

    SCROLL_X = 64
    SCROLL_Y = 105

    TURTLE_SHELL_PATH = "x_transformice/x_evt/x_evt_18/sdnjqj/carapace.png"

    TURTLE_OFFSET_X = -20
    TURTLE_OFFSET_Y = -22

    REWARD_ID = 2257

    SEASHELL_VENDOR_X = 736
    SEASHELL_VENDOR_Y = 246

    # NOTE: These session IDs are taken from a real
    # example, however these session IDs change much
    # the same as the ones for the Greenhouse shop,
    # seeming to globally decrement per satellite server.
    STANDARD_VENDORS = {
        "Mayonaka": dict(
            session_id = -14306,
            title_id   = 571,
            feminine   = False,
            look       = '291;46_80587C+1A1007,0,129_A3936B+80587C+A3936B+493457+493457+80587C+FFFFFF+DFDFDF+493457,0,78_EFF7F3+EFF7F3+A3936B+A3936B,63_241F1F+728A8F+493457+493457+493457,0,105,75_A7BCB2+728A8F+1A272E+728A8F+493457+80587C,0,0,0',
            x          = 832,
            y          = 575,
        ),

        "Indiana Mouse": dict(
            session_id = -14307,
            title_id   = 27,
            feminine   = False,
            look       = '45;0,0,0,0,0,0,0,0,0',
            x          = 1244,
            y          = 216,
        )
    }

    NPC_SHOPS = {
        "Mayonaka": [
            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.ShopItem,
                item_id       = 30129,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2611,
                cost_quantity = 25,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Cartouche,
                item_id       = 73,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2611,
                cost_quantity = 30,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Title,
                item_id       = 571,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2611,
                cost_quantity = 40,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2612,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 5,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2479,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2257,
                cost_quantity = 50,
            )
        ],

        "Indiana Mouse": Shops.INDIANA_MOUSE,
        "Luna":          Shops.LUNA_NINJA_2024,
        "Mousini":       Shops.MOUSINI,
        "Mauricette":    Shops.MAURICETTE,
        "Wu":            Shops.WU,
        "Rob":           Shops.ROB,
    }

    async def setup_round(self, client):
        await self.add_collectible(
            client,

            # NOTE: Individual ID is from a real example, however these
            # IDs would increment with each map per satellite server.
            individual_id  = 1978,
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

        await super().setup_round(client)

    async def on_get_collectible(self, client, packet):
        await self.raise_inventory_item(client, self.REWARD_ID)
