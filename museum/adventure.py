import pak
import caseus

from public import public

from .exhibit import Exhibit

@public
class AdventureExhibit(Exhibit):
    adventure_id = None

    @classmethod
    def _can_be_available(cls):
        return super()._can_be_available() and cls.adventure_id is not None

    async def add_collectible(self, client, *, individual_id, collectible_id, x, y):
        await client.write_packet(
            caseus.clientbound.AddCollectiblePacket,

            adventure_id   = self.adventure_id,
            individual_id  = individual_id,
            collectible_id = collectible_id,
            x              = x,
            y              = y,
        )

    async def add_area(self, client, *, area_id, x, y, width, height):
        if area_id == 0:
            raise ValueError("An area's ID should not be '0'")

        await client.write_packet(
            caseus.clientbound.AddAdventureAreaPacket,

            adventure_id = self.adventure_id,
            area_id      = area_id,
            x            = x,
            y            = y,
            width        = width,
            height       = height,
        )

    @staticmethod
    def _stringize_action_arg(arg):
        match arg:
            case int():
                return str(arg)

            case bool():
                return "true" if arg else "false"

            case _:
                return arg

    async def adventure_action(self, client, action_id, *args):
        stringized_args = [self._stringize_action_arg(arg) for arg in args]

        await client.write_packet(
            caseus.clientbound.AdventureActionPacket,

            adventure_id = self.adventure_id,
            action_id    = action_id,
            arguments    = stringized_args,
        )

    async def on_adventure_action(self, client, packet):
        pass

    async def on_get_collectible(self, client, packet):
        pass

    async def on_enter_area(self, client, packet):
        pass

    @pak.packet_listener(caseus.serverbound.AdventureActionPacket)
    async def _on_adventure_action(self, client, packet):
        if packet.adventure_id != self.adventure_id:
            return

        await self.on_adventure_action(client, packet)

    @pak.packet_listener(caseus.serverbound.GetCollectiblePacket)
    async def _on_get_collectible(self, client, packet):
        if packet.adventure_id != self.adventure_id:
            return

        await self.on_get_collectible(client, packet)

    @pak.packet_listener(caseus.serverbound.EnterAdventureAreaPacket)
    async def _on_enter_area(self, client, packet):
        if packet.adventure_id != self.adventure_id:
            return

        await self.on_enter_area(client, packet)

    async def on_enter_exhibit(self, client):
        await client.write_packet(
            caseus.clientbound.UpdateAdventuresPacket,

            adventure_id_list = [self.adventure_id],
            enable            = True,
        )

    async def on_exit_exhibit(self, client):
        await client.write_packet(
            caseus.clientbound.UpdateAdventuresPacket,

            adventure_id_list = [self.adventure_id],
            enable            = False,
        )
