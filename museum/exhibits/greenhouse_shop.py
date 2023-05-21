import caseus

import asyncio
import random

from ..exhibit import available, Exhibit

@available
class Greenhouse_Shop(Exhibit):
    map_code = 2801
    map_xml_path = "Greenhouse/Shop_2023.xml"

    map_category   = caseus.enums.MapCategory.UserMadeVanilla
    round_duration = 60

    SEASHELL_VENDOR_X = 331
    SEASHELL_VENDOR_Y = 275

    # NOTE: The official server always sends the same session ID
    # for the same seashell vendor.
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

    # NOTE: The official server does not always send
    # the same session IDs for the same standard vendors,
    # however Indiana Mouse's session ID is always one
    # less than Fleur's.
    #
    # The session IDs used here are real values taken
    # from one instance of real communication.
    STANDARD_VENDORS = {
        "Fleur": dict(
            session_id = -20294,
            title_id   = 481,
            feminine   = True,
            look       = "96;44_f6ecd3+ffdbe2+e2917e,9_a5987e,0,0,0,26_ffe8bf+e2917e,0,1,0",
            x          = 595,
            y          = 275,
        ),

        "Indiana Mouse": dict(
            session_id = -20295,
            title_id   = 27,
            feminine   = False,
            look       = "45;0,0,0,0,0,0,0,0,0",
            x          = 753,
            y          = 101,
        ),
    }

    NPC_SHOPS = {
        "Fleur": [
            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.ShopItem,
                item_id       = 10265,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 25,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Cartouche,
                item_id       = 67,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 30,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Badge,
                item_id       = 418,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 20,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Title,
                item_id       = 559,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 40,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Emoji,
                item_id       = 20001,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 15,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2257,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 3,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2497,
                quantity      = 10,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2521,
                cost_quantity = 1,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2522,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 10,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2576,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 10,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2520,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 15,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2575,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 15,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2523,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 20,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2524,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2497,
                cost_quantity = 20,
            ),

            caseus.clientbound.OpenNPCShopPacket.ItemInfo(
                type          = caseus.enums.NPCItemType.Inventory,
                item_id       = 2488,
                quantity      = 1,
                cost_type     = caseus.enums.NPCItemType.Inventory,
                cost_id       = 2257,
                cost_quantity = 50,
            ),
        ],

        "Indiana Mouse": [
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
        ],

        "Luna": [
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
        ],

        "Mousini": [
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
        ],

        "Mauricette": [
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
        ],

        "Wu": [
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
        ],

        "Rob": [
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
        ],
    }

    async def on_enter_exhibit(self, client):
        await client.general_message("<B><BV>This exhibit is from the year <J>2023</J>.</BV></B>")

    async def setup_round(self, client):
        async with asyncio.TaskGroup() as tg:
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
