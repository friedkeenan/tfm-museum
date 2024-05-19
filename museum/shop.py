import caseus

import asyncio
import random

from public import public

from .exhibit import Exhibit

@public
class Shops:
    LUNA_GREENHOUSE_2023 = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 29,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 30,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2330,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2351,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2241,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2522,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2576,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    LUNA_BACK_TO_SCHOOL_2023 = [
        *LUNA_GREENHOUSE_2023,

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2581,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2585,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    LUNA_CHRISTMAS_2023 = [
        *LUNA_BACK_TO_SCHOOL_2023,

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2591,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    LUNA_GROUNDHOG_2024 = [
        *LUNA_CHRISTMAS_2023,

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2609,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    LUNA_NINJA_2024 = [
        *LUNA_GROUNDHOG_2024,

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2612,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    MOUSINI = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2232,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2255,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 33,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 18,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 4,
        ),
    ]

    MAURICETTE = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2262,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 5,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 28,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 22,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 4,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 35,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 2,
        ),
    ]

    WU = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 3,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 23,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 16,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),
    ]

    ROB = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 4,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 1,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2349,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2379,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2256,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2252,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2513,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2514,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 3,
        ),
    ]

    INDIANA_MOUSE = [
        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2473,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2472,
            cost_quantity = 5,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 2472,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2257,
            cost_quantity = 50,
        ),

        caseus.clientbound.OpenNPCShopPacket.ItemInfo(
            type          = caseus.enums.NPCItemType.Inventory,
            item_id       = 22,
            quantity      = 1,
            cost_type     = caseus.enums.NPCItemType.Inventory,
            cost_id       = 2497,
            cost_quantity = 4,
        ),
    ]

@public
class ShopExhibit(Exhibit):
    SEASHELL_VENDOR_X = None
    SEASHELL_VENDOR_Y = None

    # NOTE: The official server always sends the
    # same session ID for the same seashell vendor.
    #
    # This holds true even across events.
    SEASHELL_VENDORS = {
        "Luna": dict(
            session_id = -9,
            title_id   = 296,
            feminine   = False,
            look       = "31;0,36_8f3831+95b6c9,1_e5ac91,51_8f3831+963336+7d3335+e5ac91+732124,0,25_734435,34_8f3831+e5ac91+8f3831+e5ac91,25,0",
        ),

        "Mousini": dict(
            session_id = -8,
            title_id   = 101,
            feminine   = False,
            look       = "139;192_28292d+f8f1e9,0,0,1_18181a,0,0,27_f35431+f8f1e9,0,13_ffa171+e1d0bc",
        ),

        "Mauricette": dict(
            session_id = -7,
            title_id   = 403,
            feminine   = False,
            look       = "101;51_47372c,9_ed9416,29_855237+47372c+b7834f+ed9416+39281c+855237+b7834f,0,39_47372c,37_39281c+855237+b7834f,8_f1d3b5+946a3f+47372c+946a3f,12,0",
        ),

        "Wu": dict(
            session_id = -6,
            title_id   = 418,
            feminine   = False,
            look       = "27;127_891b11+c0382c,0,0,33_b9ab8b+c67f13,0,3_b87941,16_bba87d+921f15+e29d33,1,0",
        ),

        "Rob": dict(
            session_id = -5,
            title_id   = 260,
            feminine   = False,
            look       = "64;123_322e21,0,0,20,0,0,0,0,0,0,0",
        ),
    }

    STANDARD_VENDORS = None

    NPC_SHOPS = None

    SEASHELL_SHOPS = {

    }

    @classmethod
    def _can_be_available(cls):
        return (
            super()._can_be_available() and

            (
                len(cls.SEASHELL_VENDORS) <= 0 or

                (
                    cls.SEASHELL_VENDOR_X is not None and
                    cls.SEASHELL_VENDOR_Y is not None
                )
            ) and

            cls.STANDARD_VENDORS is not None and

            cls.NPC_SHOPS is not None
        )

    async def setup_round(self, client):
        async with asyncio.TaskGroup() as tg:
            if len(self.SEASHELL_VENDORS) > 0:
                name, attributes = random.choice(list(self.SEASHELL_VENDORS.items()))
                tg.create_task(
                    self.add_npc_for_individual(
                        client,

                        name = name,
                        x    = self.SEASHELL_VENDOR_X,
                        y    = self.SEASHELL_VENDOR_Y,

                        **attributes,
                    )
                )

            for name, attributes in self.STANDARD_VENDORS.items():
                tg.create_task(
                    self.add_npc_for_individual(
                        client,

                        name = name,
                        **attributes,
                    )
                )

    async def on_click_npc(self, client, npc_name):
        if npc_name not in self.NPC_SHOPS:
            return

        await client.write_packet(
            caseus.clientbound.OpenNPCShopPacket,

            name  = npc_name,
            items = self.NPC_SHOPS[npc_name],
        )
