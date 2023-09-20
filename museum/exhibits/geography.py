import caseus

import asyncio
import random

from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Geography(AdventureExhibit):
    adventure_id = 22

    map_code     = 942
    map_author   = "_Classroom"
    map_xml_path = "School/Classroom.xml"

    map_category = caseus.enums.MapCategory.UserMadeVanilla

    round_duration = 120

    INITIAL_FLAG_TIME = 5
    FLAG_INTERVAL     = 14

    FLAGS_SHOWN = 8

    # NOTE: Taken from the names of the
    # children of the '$CarteMonde' object
    # contained within the client.
    COUNTRIES = [
        "JP",
        "TR",
        "ES",
        "VE",
        "US",
        "NO",
        "DE",
        "CL",
        "PH",
        "ZA",
        "EG",
        "FI",
        "CN",
        "CO",
        "ID",
        "PL",
        "IT",
        "BO",
        "DZ",
        "MA",
        "RO",
        "UY",
        "CA",
        "BR",
        "ARGENTINE",
        "TN",
        "SE",
        "FR",
        "RU",
        "PT",
        "LY",
        "MX",
        "UA",
        "AU",
    ]

    CORRECT_COUNTRY_TEMPLATE   = "<V>$RentreeBonPays</V>"
    INCORRECT_COUNTRY_TEMPLATE = "<R>$RentreeMauvaisPays</R>"

    NEEDED_COUNTRIES = 5
    PASSED_TEMPLATE  = "<V>$RentreeEpreuveReussie</V>"
    FAILED_TEMPLATE  = "<R>$RentreeEpreuveEchouee</R>"

    def setup_round_timings(self, round_start):
        self.next_flag_time = round_start + self.INITIAL_FLAG_TIME

    async def check_round_timings(self, time):
        if len(self.possible_countries) <= 0:
            return

        if time >= self.next_flag_time:
            self.active_country = self.possible_countries.pop()

            async with asyncio.TaskGroup() as tg:
                for client in self.clients:
                    tg.create_task(
                        self.adventure_action(client, 3, self.active_country)
                    )

            self.next_flag_time = time + self.FLAG_INTERVAL

    async def start_new_round(self):
        self.possible_countries = random.sample(self.COUNTRIES, self.FLAGS_SHOWN)
        self.active_country     = None

        await super().start_new_round()

    async def on_exit_exhibit(self, client):
        try:
            del client.correct_countries

        except AttributeError:
            pass

    async def setup_round(self, client):
        client.correct_countries = 0

    async def on_round_end(self):
        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                message = self.PASSED_TEMPLATE if client.correct_countries >= self.NEEDED_COUNTRIES else self.FAILED_TEMPLATE

                tg.create_task(
                    self.translated_general_message(client, message)
                )

    async def on_adventure_action(self, client, packet):
        # NOTE: Only action ID we receive will be ID '7'.

        if packet.str_argument(0) == self.active_country:
            client.correct_countries += 1

            await self.translated_general_message(client, self.CORRECT_COUNTRY_TEMPLATE)
            await self.adventure_action(client, 4, True)
        else:
            await self.translated_general_message(client, self.INCORRECT_COUNTRY_TEMPLATE)
            await self.adventure_action(client, 4, False)
