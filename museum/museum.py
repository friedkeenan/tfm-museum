import pak
import caseus

import aiofiles
import asyncio
import importlib
import random

from pathlib import Path

from public import public

from .exhibits import lobby as fallback_exhibit

@public
class Museum(caseus.MinimalServer):
    # NOTE: We do not bother with a satellite server.

    MAX_SESSION_ID = 2**31 - 1

    class Connection(caseus.MinimalServer.Connection):
        username   = caseus.MinimalServer.Connection.SynchronizedAttr(None)
        session_id = caseus.MinimalServer.Connection.SynchronizedAttr(None)

        exhibit = caseus.MinimalServer.Connection.SynchronizedAttr(None)

        is_shaman  = caseus.MinimalServer.Connection.SynchronizedAttr(False)
        activity   = caseus.MinimalServer.Connection.SynchronizedAttr(caseus.enums.PlayerActivity.Inert)
        cheeses    = caseus.MinimalServer.Connection.SynchronizedAttr(0)
        context_id = caseus.MinimalServer.Connection.SynchronizedAttr(0)

        meep_power = caseus.MinimalServer.Connection.SynchronizedAttr(5)

        can_teleport = caseus.MinimalServer.Connection.SynchronizedAttr(False)

        async def wait_closed(self):
            old_exhibit = self.exhibit
            self.exhibit = None

            if old_exhibit is not None:
                await old_exhibit.new_synchronizer()

                if self.activity is caseus.enums.PlayerActivity.Alive:
                    await old_exhibit.kill(self, only_others=True)

            await super().wait_closed()

        async def account_error(self, *, error_code=2, **kwargs):
            await self.write_packet(
                caseus.clientbound.AccountErrorPacket,

                error_code = error_code,

                **kwargs,
            )

        async def general_message(self, message):
            await self.write_packet(
                caseus.clientbound.GeneralMessagePacket,

                message = message,
            )

        async def join_room(self, room_name):
            fallback, exhibit = self.server.find_exhbit(room_name.lower())

            if fallback:
                await self.general_message(f"<B><ROSE>Could not find exhibit '{room_name}', falling back to {exhibit.room_name}...</ROSE></B>")

            if exhibit is self.exhibit:
                return

            old_exhibit  = self.exhibit
            self.exhibit = exhibit

            if old_exhibit is not None:
                await old_exhibit._on_exit_exhibit(self)

            await self.exhibit._on_enter_exhibit(self)

        def __repr__(self):
            return f"{type(self).__qualname__}(username={repr(self.username)})"

    def __init__(
        self,
        *,
        data_dir = Path("data"),

        language               = "int",
        country                = "int",
        right_to_left          = False,
        has_special_characters = False,
        font                   = "",

        community = caseus.enums.Community.EN,

        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data_dir = data_dir

        self.language               = language
        self.country                = country
        self.right_to_left          = right_to_left
        self.has_special_characters = has_special_characters
        self.font                   = font

        self.community = community

        self._last_session_id = 0

        self.exhibits = []

    def close(self):
        for exhibit in self.exhibits:
            exhibit.close()

        super().close()

    async def wait_closed(self):
        async with asyncio.TaskGroup() as tg:
            for exhibit in self.exhibits:
                tg.create_task(
                    exhibit.wait_closed()
                )

        await super().wait_closed()

    async def _swap_exhibit(self, client, new_exhibit):
        # Stop the client from thinking it's a synchronizer.
        if client is client.exhibit.synchronizer:
            await client.write_packet(caseus.clientbound.DisableSynchronizationPacket)

        # NOTE: We don't call '_on_exit_exhibit'
        # because that will do more than is necessary
        # for reloading. Perhaps we should have more
        # specific methods?
        await client.exhibit.on_exit_exhibit(client)

        client.exhibit = new_exhibit

    async def reload_exhibit(self, exhibit):
        module = importlib.import_module(exhibit.__module__)
        importlib.reload(module)

        # Reloading a module does not delete global variables.
        if module._available_exhibit is type(exhibit):
            del module._available_exhibit

        if not hasattr(module, "_available_exhibit"):
            # TODO: Error message?

            async with asyncio.TaskGroup() as tg:
                for client in exhibit.clients:
                    tg.create_task(
                        client.join_room(fallback_exhibit.__name__.rsplit(".", 1)[1])
                    )

            self.exhibits.remove(exhibit)

            return

        new_exhibit = module._available_exhibit(self)

        async with asyncio.TaskGroup() as tg:
            for client in exhibit.clients:
                tg.create_task(
                    self._swap_exhibit(client, new_exhibit)
                )

        self.exhibits.remove(exhibit)
        self.exhibits.append(new_exhibit)

        await new_exhibit._on_reload()

    def _find_or_add_exhibit(self, exhibit_cls):
        for exhibit in self.exhibits:
            # NOTE: We compare types this way to
            # allow subclasses of exhibits.
            if type(exhibit) is exhibit_cls:
                return exhibit

        exhibit = exhibit_cls(self)
        self.exhibits.append(exhibit)

        return exhibit

    def find_exhbit(self, name):
        # TODO: Have a way to list exhibits
        # to use in the room list menu.

        fallback = False

        try:
            module = importlib.import_module(f".exhibits.{name}", package=__package__)

        except ModuleNotFoundError:
            module   = fallback_exhibit
            fallback = True

        if not hasattr(module, "_available_exhibit"):
            module = fallback_exhibit
            fallback = True

        return fallback, self._find_or_add_exhibit(module._available_exhibit)

    async def data(self, path, *, binary=False):
        path = Path(self.data_dir, path)

        if binary:
            mode = "rb"
        else:
            mode = "r"

        async with aiofiles.open(path, mode) as f:
            return await f.read()

    @pak.packet_listener(caseus.serverbound.SetLanguagePacket)
    async def on_set_language(self, client, packet):
        await client.write_packet(
            caseus.clientbound.SetLanguagePacket,

            language               = self.language,
            country                = self.country,
            right_to_left          = self.right_to_left,
            has_special_characters = self.has_special_characters,
            font                   = self.font,
        )

    async def on_login(self, client, packet):
        if packet.username in (x.username for x in self.main_clients if x.logged_in):
            await client.account_error(error_code=1)

            return

        # NOIE: This system does not make
        # stale session IDs available again.
        # However I believe the official
        # server uses the same system.
        if self._last_session_id >= self.MAX_SESSION_ID:
            await client.account_error()

            return

        client.username = packet.username

        self._last_session_id += 1
        client.session_id = self._last_session_id

        client.logged_in = True

        await client.write_packet(
            caseus.clientbound.LoginSuccessPacket,

            global_id   = 0,
            username    = client.username,
            played_time = 4 * 60 * 60,
            community   = self.community,
            session_id  = client.session_id,
            registered  = True,
        )

        await client.write_packet(
            caseus.clientbound.SetTribulleProtocolPacket,

            new_protocol = True,
        )

        await client.write_packet(caseus.clientbound.AvailableEmojisPacket)

        await client.join_room(packet.start_room)

    @pak.packet_listener(caseus.serverbound.JoinRoomPacket)
    async def _on_join_room(self, client, packet):
        await client.join_room(packet.name)

    @pak.packet_listener(caseus.Packet)
    async def _dispatch_to_exhibit(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet, outgoing=False)

    @pak.packet_listener(caseus.Packet, outgoing=True)
    async def _dispatch_outgoing_to_exhibit(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet, outgoing=True)

    @pak.packet_listener(caseus.serverbound.LegacyWrapperPacket)
    async def _dispatch_to_exhibit_legacy(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(caseus.clientbound.LegacyWrapperPacket, outgoing=True)
    async def _dispatch_outgoing_to_exhibit_legacy(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=True)

    @pak.packet_listener(caseus.serverbound.TribulleWrapperPacket)
    async def _dispatch_to_exhibit_tribulle(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(caseus.clientbound.TribulleWrapperPacket, outgoing=True)
    async def _dispatch_outgoing_to_exhibit_tribulle(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=True)

    @pak.packet_listener(caseus.serverbound.ExtensionWrapperPacket)
    async def _dispatch_to_exhibit_extension(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=False)

    @pak.packet_listener(caseus.clientbound.ExtensionWrapperPacket, outgoing=True)
    async def _dispatch_outgoing_to_exhibit_extension(self, client, packet):
        if client.exhibit is None:
            return

        await client.exhibit._listen_to_packet(client, packet.nested, outgoing=True)
