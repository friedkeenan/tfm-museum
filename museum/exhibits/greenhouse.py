import pak
import caseus

import asyncio
import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Greenhouse(AdventureExhibit):
    adventure_id = 27

    map_code     = 2027
    map_xml_path = "Greenhouse/Greenhouse.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    has_synchronizer = True

    ORANGE_FLOWER = "x_transformice/x_evt/x_evt_27/fleur-orange.png"
    PURPLE_FLOWER = "x_transformice/x_evt/x_evt_27/fleur-violette.png"
    GREEN_FLOWER  = "x_transformice/x_evt/x_evt_27/fleur-verte.png"
    WHITE_FLOWER  = "x_transformice/x_evt/x_evt_27/fleur-blanche.png"

    NEEDED_FLOWER_X = 595
    NEEDED_FLOWER_Y = 157

    RED_SEED    = 67
    YELLOW_SEED = 68
    BLUE_SEED   = 69

    SEED_IMAGE_PATH_FMT = "x_transformice/x_aventure/x_recoltables/x_{id}.png"

    SEED_OFFSET_X = -24
    SEED_OFFSET_Y = -19

    SPROUT_IMAGE_PATH = "x_transformice/x_evt/x_evt_27/pousse.png"

    class Bounds:
        def __init__(self, top_left, bottom_right):
            self.top_left     = top_left
            self.bottom_right = bottom_right

        def contains(self, x, y):
            return (
                x >= self.top_left[0] and x <= self.bottom_right[0] and
                y >= self.top_left[1] and y <= self.bottom_right[1]
            )

    class Pot:
        def __init__(self, sprout_name, x, y):
            self.sprout_name = sprout_name

            self.x = x
            self.y = y

            self.bounds = Greenhouse.Bounds(
                # NOTE: Educated guesses.
                (x - 20, y - 15 - 30),
                (x + 20, y - 15),
            )

            self.left_seed  = None
            self.right_seed = None

            self._growth_start = None
            self.has_grown     = False

        @property
        def left_seed_x(self):
            return self.x - 19

        @property
        def right_seed_x(self):
            return self.x - 1

        @property
        def seed_y(self):
            return self.y - 2

        @property
        def sprout_x(self):
            return self.x - 22

        @property
        def sprout_y(self):
            return self.y - 60

        @property
        def flower_x(self):
            return self.x - 25

        @property
        def flower_y(self):
            return self.y - 60

        def plant_seed(self, seed):
            if self.left_seed is None:
                self.left_seed = seed

                return True

            if self.right_seed is None:
                self.right_seed = seed

                return True

            return False

        @property
        def flower(self):
            # NOTE: This requires that both seeds have been planted.

            if self.left_seed == self.right_seed:
                return Greenhouse.WHITE_FLOWER

            match (self.left_seed, self.right_seed):
                case (Greenhouse.RED_SEED, Greenhouse.YELLOW_SEED) | (Greenhouse.YELLOW_SEED, Greenhouse.RED_SEED):
                    return Greenhouse.ORANGE_FLOWER

                case (Greenhouse.RED_SEED, Greenhouse.BLUE_SEED) | (Greenhouse.BLUE_SEED, Greenhouse.RED_SEED):
                    return Greenhouse.PURPLE_FLOWER

                case (Greenhouse.YELLOW_SEED, Greenhouse.BLUE_SEED) | (Greenhouse.BLUE_SEED, Greenhouse.YELLOW_SEED):
                    return Greenhouse.GREEN_FLOWER

    # NOTE: Taken from the map XML.
    POT_POSITIONS = [
        (155, 363),
        (431, 361),
        (714, 363),
        (222, 207),
        (142, 88),
        (331, 87),
        (717, 82),
    ]

    POT_GROWTH_TIME = 8

    SEED_BAG_BOUNDS = Bounds(
        # NOTE: Educated guesses.
        (0,  302),
        (78, 380),
    )

    REWARD_ID = 2521

    def random_flower(self):
        return random.choice([self.ORANGE_FLOWER, self.PURPLE_FLOWER, self.GREEN_FLOWER])

    def random_seed(self):
        return random.choice([self.RED_SEED, self.YELLOW_SEED, self.BLUE_SEED])

    def seed_path(self, id):
        return self.SEED_IMAGE_PATH_FMT.format(id=id)

    async def on_exit_exhibit(self, client):
        try:
            del client.carrying_id

        except AttributeError:
            pass

    async def check_round_timings(self, time):
        for pot in self.pots:
            if pot._growth_start is None or pot.has_grown:
                continue

            if time >= pot._growth_start + self.POT_GROWTH_TIME:
                pot.has_grown = True

                await self.update_pot(pot)

    async def start_new_round(self):
        self.needed_flower = self.random_flower()

        self.active_white_flowers  = 0
        self.active_needed_flowers = 0

        # NOTE: Yes, the sprout names of 'p1', 'p2', ...
        # are all real names that the official server
        # sends the client. The 'p' likely stands for
        # 'pousse', French for 'sprout'.
        #
        # I find this insight into the official devs'
        # thought process incredibly fascinating.
        self.pots = [self.Pot(f"p{i + 1}", x, y) for i, (x, y) in enumerate(self.POT_POSITIONS)]

        # Players spawn with seeds already collected.
        for client in self.clients:
            client.carrying_id = self.random_seed()

        await super().start_new_round()

    async def setup_pot(self, client, pot):
        async with asyncio.TaskGroup() as tg:
            if pot.left_seed is not None:
                tg.create_task(
                    self.add_official_image_for_individual(
                        client,

                        image_path = self.SEED_IMAGE_PATH_FMT.format(id=pot.left_seed),
                        x          = pot.left_seed_x,
                        y          = pot.seed_y,
                    )
                )

            if pot.right_seed is not None:
                tg.create_task(
                    self.add_official_image_for_individual(
                        client,

                        image_path = self.SEED_IMAGE_PATH_FMT.format(id=pot.right_seed),
                        x          = pot.right_seed_x,
                        y          = pot.seed_y,
                    )
                )

                if pot.has_grown:
                    tg.create_task(
                        self.add_official_image_for_individual(
                            client,

                            image_path = pot.flower,
                            x          = pot.flower_x,
                            y          = pot.flower_y,
                        )
                    )

                else:
                    tg.create_task(
                        self.add_official_image_for_individual(
                            client,

                            image_path = self.SPROUT_IMAGE_PATH,
                            x          = pot.sprout_x,
                            y          = pot.sprout_y,
                            name       = pot.sprout_name,
                        )
                    )

    async def check_rewards(self, new_flower):
        if new_flower == self.WHITE_FLOWER:
            self.active_white_flowers += 1
        elif new_flower == self.needed_flower:
            self.active_needed_flowers += 1
        else:
            return

        if self.active_needed_flowers > 0 and self.active_white_flowers > 0:
            self.active_white_flowers  -= 1
            self.active_needed_flowers -= 1

            async with asyncio.TaskGroup() as tg:
                # NOTE: In the real event, even clients
                # who died would be given the reward, and
                # there were tickets in the rewards as well.
                #
                # We decline to mimic this because the museum
                # does not manage any inventory, nor does it
                # issue the gain item notifications like the
                # official server does, though perhaps it should.

                for client in self.alive_clients:
                    tg.create_task(
                        self.raise_inventory_item(client, self.REWARD_ID)
                    )

    async def update_pot(self, pot):
        if pot.has_grown:
            await self.remove_official_image(pot.sprout_name)

            new_flower = pot.flower

            await self.add_official_image(
                image_path = new_flower,
                x          = pot.flower_x,
                y          = pot.flower_y,
            )

            await self.check_rewards(new_flower)

            return

        if pot.right_seed is None:
            # Left seed was just planted.

            await self.add_official_image(
                image_path = self.SEED_IMAGE_PATH_FMT.format(id=pot.left_seed),
                x          = pot.left_seed_x,
                y          = pot.seed_y,
            )

            return

        # Right seed was just planted.

        await self.add_official_image(
            image_path = self.SEED_IMAGE_PATH_FMT.format(id=pot.right_seed),
            x          = pot.right_seed_x,
            y          = pot.seed_y,
        )

        await self.add_official_image(
            image_path = self.SPROUT_IMAGE_PATH,
            x          = pot.sprout_x,
            y          = pot.sprout_y,
            name       = pot.sprout_name,
        )

        pot._growth_start = asyncio.get_running_loop().time()

    async def setup_round(self, client):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                self.add_official_image_for_individual(
                    client,

                    image_path = self.needed_flower,
                    x          = self.NEEDED_FLOWER_X,
                    y          = self.NEEDED_FLOWER_Y,
                )
            )

            for pot in self.pots:
                tg.create_task(
                    self.setup_pot(client, pot)
                )

            for other_client in self.alive_clients:
                if other_client.carrying_id is None:
                    continue

                tg.create_task(
                    self.add_carrying_for_individual(
                        client,

                        carrying_client = other_client,
                        image_path      = self.seed_path(client.carrying_id),
                        offset_x        = self.SEED_OFFSET_X,
                        offset_y        = self.SEED_OFFSET_Y,
                        foreground      = False,
                    )
                )

    async def on_adventure_action(self, client, packet):
        x = packet.int_argument(0)
        y = packet.int_argument(1)

        if self.SEED_BAG_BOUNDS.contains(x, y) and client.carrying_id is None:
            client.carrying_id = self.random_seed()

            await self.add_carrying(
                client,

                image_path = self.seed_path(client.carrying_id),
                offset_x   = self.SEED_OFFSET_X,
                offset_y   = self.SEED_OFFSET_Y,
                foreground = False,
            )

            return

        if client.carrying_id is None:
            return

        for pot in self.pots:
            if not pot.bounds.contains(x, y):
                continue

            if pot.plant_seed(client.carrying_id):
                client.carrying_id = None
                await self.clear_carrying(client)

                await self.update_pot(pot)

            return
