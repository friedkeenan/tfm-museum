from ..adventure import AdventureExhibit
from ..exhibit   import available

@available
class Wizard(AdventureExhibit):
    # This exhibit poses a unique challenge to recreate
    # because it cumulated globally, with the whole
    # community reaching milestones together, which
    # resulted in different maps being served. It seems
    # only the initial map XML has been archived, but
    # I am choosing to include this exhibit so that
    # at least part of the event may be relived.

    adventure_id = 25

    map_code     = 2021
    map_xml_path = "Wizard/Initial_Hograts.xml"

    has_synchronizer = True
    has_shaman       = True

    incomplete = True

    # TODO: Resource enum stuff.

    async def collect_resource(self, client, resource):
        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    self.adventure_action(2, client.session_id, resource.value)
                )

    async def on_adventure_action(self, client, packet):
        # Only action ID 1 should ever be sent.
        if packet.action_id != 1:
            return

        # The client sends action ID 1 when they
        # go in water while carrying resources.

        # TODO: Also clear their server-tracked resources.
        await self.clear_carrying(client)
