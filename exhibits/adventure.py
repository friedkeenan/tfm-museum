import pak
import caseus

from .exhibit import Exhibit

class AdventureExhibit(Exhibit):
    adventure_id = None

    class ServerConnection(Exhibit.ServerConnection):
        @property
        def active_adventures(self):
            return self.main.client._active_adventures

    class ClientConnection(Exhibit.ClientConnection):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self._active_adventures = set()

        @property
        def active_adventures(self):
            return self.main.client._active_adventures

        async def add_collectable(self, *, individual_id, collectable_id, x, y):
            await self.write_packet(
                caseus.clientbound.AddCollectablePacket,

                adventure_id   = self.proxy.adventure_id,
                individual_id  = individual_id,
                collectable_id = collectable_id,
                x              = x,
                y              = y,
            )

        async def add_area(self, *, area_id, x, y, width, height):
            if area_id == 0:
                raise ValueError("An area's ID should not be '0'")

            await self.write_packet(
                caseus.clientbound.AddAdventureAreaPacket,

                adventure_id = self.proxy.adventure_id,
                area_id      = area_id,
                x            = x,
                y            = y,
                width        = width,
                height       = height,
            )

        async def adventure_action(self, action_id, *args):
            stringized_args = []
            for arg in args:
                match arg:
                    case int():
                        stringized_args.append(str(arg))

                    case bool():
                        stringized_args.append("true" if arg else "false")

                    case _:
                        stringized_args.append(arg)

            await self.write_packet(
                caseus.clientbound.AdventureActionPacket,

                adventure_id = self.proxy.adventure_id,
                action_id    = action_id,
                arguments    = stringized_args,
            )

    def __init__(self, **kwargs):
        if self.adventure_id is None:
            raise ValueError("The 'adventure_id' attribute is not set")

        super().__init__(**kwargs)

    @pak.packet_listener(caseus.clientbound.UpdateAdventuresPacket)
    async def _on_update_adventures(self, source, packet):
        if packet.enable:
            source.active_adventures.update(packet.adventure_id_list)

            return self.FORWARD_PACKET

        source.active_adventures.difference_update(packet.adventure_id_list)

        if self.adventure_id in packet.adventure_id_list:
            return self.DO_NOTHING

    async def on_adventure_action(self, client, packet):
        raise NotImplementedError

    async def on_get_collectable(self, client, packet):
        raise NotImplementedError

    async def on_enter_area(self, client, packet):
        raise NotImplementedError

    @pak.packet_listener(caseus.serverbound.AdventureActionPacket)
    async def _on_adventure_action(self, source, packet):
        if not source.in_exhibit or packet.adventure_id != self.adventure_id:
            return self.FORWARD_PACKET

        await self.on_adventure_action(source, packet)

        return self.REPLACE_PACKET

    @pak.packet_listener(caseus.serverbound.GetCollectablePacket)
    async def _on_get_collectable(self, source, packet):
        if not source.in_exhibit or packet.adventure_id != self.adventure_id:
            return self.FORWARD_PACKET

        await self.on_get_collectable(source, packet)

        return self.REPLACE_PACKET

    @pak.packet_listener(caseus.serverbound.EnterAdventureAreaPacket)
    async def _on_enter_adventure_area(self, source, packet):
        if not source.in_exhibit or packet.adventure_id != self.adventure_id:
            return self.FORWARD_PACKET

        await self.on_enter_area(source, packet)

        return self.REPLACE_PACKET

    async def enter_exhibit(self, client):
        await super().enter_exhibit(client)

        # NOTE: The game functions fine if you enable
        # the same adventure twice, so we don't need
        # to care if the game already enabled it.
        await client.write_packet(
            caseus.clientbound.UpdateAdventuresPacket,

            adventure_id_list = [self.adventure_id],
            enable            = True,
        )

    async def exit_exhibit(self, client):
        await super().exit_exhibit(client)

        if self.adventure_id not in client.active_adventures:
            await client.write_packet(
                caseus.clientbound.UpdateAdventuresPacket,

                adventure_id_list = [self.adventure_id],
                enable            = False,
            )
