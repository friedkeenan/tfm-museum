import caseus

import asyncio
import random

from ..exhibit import available
from ..shop    import Shops, ShopExhibit

@available
class Greenhouse_Shop(ShopExhibit):
    map_code     = 2801
    map_xml_path = "Greenhouse/Shop_2023.xml"

    map_category   = caseus.enums.MapCategory.UserMadeVanilla
    round_duration = 60

    original_year = 2023

    SEASHELL_VENDOR_X = 331
    SEASHELL_VENDOR_Y = 275

    # NOTE: The official server does not always send
    # the same session IDs for the same standard vendors,
    # however Indiana Mouse's session ID is always one
    # less than Fleur's.
    #
    # The standard vendors' session IDs seem to decrement
    # around 1000 each shop map, for instance from '-4652'
    # to '-5953'. This decrement varies however, I have
    # often seen decrements of around 1300, one time of
    # around 2000, and a few times of less than 1000.
    # These variances seem to correspond to overall player
    # activity, and from some rudimentary calculations
    # it seems to me like the session IDs could decrement
    # by one each time an event map appears in a room,
    # regardless of whether it's the shop map or not.
    #
    # The session IDs also seem to only be reset when
    # the server restarts, seemingly to 0. The session
    # IDs additionally seem to be per-satellite server
    # and not global.
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

        "Indiana Mouse": Shops.INDIANA_MOUSE,
        "Luna":          Shops.LUNA_GREENHOUSE_2023,
        "Mousini":       Shops.MOUSINI,
        "Mauricette":    Shops.MAURICETTE,
        "Wu":            Shops.WU,
        "Rob":           Shops.ROB,
    }
