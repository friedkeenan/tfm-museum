import pak
import caseus

import aiofiles

from pathlib import Path

class Exhibit(caseus.Proxy):
    map_code     = None
    map_xml_path = None
    map_author   = "Transformice"
    map_category = caseus.enums.MapCategory.Prime

    has_shaman = False

    class ServerConnection(caseus.Proxy.ServerConnection):
        @property
        def in_exhibit(self):
            return self.main.client._in_exhibit

        @in_exhibit.setter
        def in_exhibit(self, value):
            self.main.client._in_exhibit = value

    class ClientConnection(caseus.Proxy.ClientConnection):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self._in_exhibit = False

        @property
        def in_exhibit(self):
            return self.main.client._in_exhibit

        @in_exhibit.setter
        def in_exhibit(self, value):
            self.main.client._in_exhibit = value

        async def set_can_collect(self, can_collect):
            await self.write_packet(
                caseus.clientbound.CollectableActionPacket,

                action = caseus.clientbound.CollectableActionPacket.SetCanCollect(
                    can_collect = can_collect,
                ),
            )

        async def add_carrying(self, *, all=False, image_path, offset_x, offset_y, foreground, size_percentage=100, angle=0):
            await self.write_packet(
                caseus.clientbound.CollectableActionPacket,

                action = caseus.clientbound.CollectableActionPacket.AddCarrying(
                    session_id      = 0 if all else self.session_id,
                    image_path      = image_path,
                    offset_x        = offset_x,
                    offset_y        = offset_y,
                    foreground      = foreground,
                    size_percentage = size_percentage,
                    angle           = angle,
                ),
            )

        async def clear_carrying(self, *, all=False):
            await self.write_packet(
                caseus.clientbound.CollectableActionPacket,

                action = caseus.clientbound.CollectableActionPacket.ClearCarrying(
                    session_id = 0 if all else self.session_id,
                ),
            )

    def __init__(self, *, data_dir=Path("data"), **kwargs):
        if self.map_code is None:
            raise ValueError("The 'map_code' attribute is not set")

        if self.map_xml_path is None:
            raise ValueError("The 'map_xml_path' attribute is not set")

        super().__init__(**kwargs)

        self.data_dir   = data_dir
        self._map_cache = (None, None)

    async def new_main_connection(self, client_reader, client_writer):
        if len(self.main_clients) != 0:
            client_writer.close()
            await client_writer.wait_closed()

            return

        await super().new_main_connection(client_reader, client_writer)

    async def xml_data(self, path):
        path = Path(self.data_dir, "maps", path)

        if path == self._map_cache[0]:
            return self._map_cache[1]

        async with aiofiles.open(path) as f:
            data = await f.read()

        self._map_cache = (path, data)

        return data

    async def enter_exhibit(self, client):
        pass

    async def exit_exhibit(self, client):
        pass

    # TODO: Should we have a 'cleanup_round'?
    async def setup_round(self, client):
        pass

    @pak.packet_listener(caseus.clientbound.NewRoundPacket)
    async def _on_new_round(self, source, packet):
        # Player not in the map editor.
        if packet.map_code != -1:
            if source.in_exhibit:
                await self.exit_exhibit(source.destination)

            source.in_exhibit = False

            return self.FORWARD_PACKET

        source.in_exhibit = True

        await self.enter_exhibit(source.destination)

        await source.destination.write_packet_instance(
            packet.copy(
                map_code = self.map_code,
                xml      = await self.xml_data(self.map_xml_path),
                author   = self.map_author,
                category = self.map_category,
            )
        )

        await self.setup_round(source.destination)

        return self.DO_NOTHING

    @pak.packet_listener(caseus.clientbound.ShamanInfoPacket)
    async def _suppress_shaman(self, source, packet):
        if not source.in_exhibit or self.has_shaman:
            return self.FORWARD_PACKET

        await source.destination.write_packet(caseus.clientbound.ShamanInfoPacket)

        return self.DO_NOTHING

    @pak.packet_listener(caseus.serverbound.CommandPacket)
    async def _on_command(self, source, packet):
        # TODO: More generic command system?

        if not source.in_exhibit:
            return self.FORWARD_PACKET

        match packet.command.split():
            case ["editor", *_] | ["editeur", *_]:
                # Since we override the map category from the original
                # value of 'MapEditor', the button to go back to the
                # editor is missing. Therefore we allow sending the
                # 'editor' command to effectively click the button
                # for the client.

                await source.satellite.server.write_packet(
                    caseus.serverbound.LegacyWrapperPacket,

                    nested = caseus.serverbound.ReturnToMapEditorPacket(),
                )

            case _:
                return self.FORWARD_PACKET

        return self.REPLACE_PACKET
