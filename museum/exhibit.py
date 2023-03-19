import pak
import caseus

import asyncio
import inspect
import random

from public import public

@public
def available(cls):
    if not cls._can_be_available():
        raise ValueError(f"Exhibit '{cls.__qualname__}' cannot be made available")

    last_frame = inspect.currentframe().f_back

    last_frame.f_globals["_available_exhibit"] = cls

    return cls

@public
class Exhibit(pak.AsyncPacketHandler):
    map_code     = None
    map_xml_path = None
    map_author   = "Transformice"
    map_category = caseus.enums.MapCategory.Prime

    round_duration = 120

    has_shaman       = False
    has_synchronizer = False

    shaman_color = 0x95D9D6

    ROUND_SHORTEN_TIME = 20

    _UNSPECIFIED = pak.util.UniqueSentinel("UNSPECIFIED")

    @classmethod
    def _can_be_available(cls):
        return cls.map_code is not None

    def __init__(self, museum):
        super().__init__()

        self.museum = museum

        self.round_id     = 0
        self.shaman       = None
        self.synchronizer = None
        self.anchors      = []

        self._map_xml_data = None

        self._has_player_won         = False
        self._round_end              = 0
        self._check_round_ended_task = None

    def close(self):
        if self._check_round_ended_task is not None:
            self._check_round_ended_task.cancel()

    async def wait_closed(self):
        if self._check_round_ended_task is not None:
            await self._check_round_ended_task

            self._check_round_ended_task = None

        await self.end_listener_tasks()

    def register_packet_listener(self, listener, *packet_types, outgoing=False, **flags):
        super().register_packet_listener(listener, *packet_types, outgoing=outgoing, **flags)

    async def _listen_to_packet(self, client, packet, *, outgoing):
        listeners = self.listeners_for_packet(packet, outgoing=outgoing)
        if len(listeners) <= 0:
            return

        packet = packet.immutable_copy()

        async with self.listener_task_group(listen_sequentially=False) as group:
            for listener in listeners:
                group.create_task(listener(client, packet))

    @property
    def room_name(self):
        return type(self).__qualname__

    @property
    def clients(self):
        return [client for client in self.museum.main_clients if client.exhibit is self]

    @property
    def num_active_clients(self):
        return sum(1 if client.activity is not caseus.enums.PlayerActivity.Inert else 0 for client in self.clients)

    @property
    def alive_clients(self):
        return [
            client

            for client in self.museum.main_clients

            if client.exhibit is self and client.activity is caseus.enums.PlayerActivity.Alive
        ]

    def client_with_session_id(self, session_id):
        for client in self.museum.main_clients:
            if client.exhibit is not self:
                continue

            if client.session_id == session_id:
                return client

        return None

    def player_description(self, client):
        return dict(
            username       = client.username,
            session_id     = client.session_id,
            is_shaman      = client.is_shaman,
            activity       = client.activity,
            score          = 0,
            cheeses        = client.cheeses,
            title_id       = 0,
            title_stars    = 0,
            gender         = caseus.enums.Gender.Unknown,
            unk_string_10  = "0",
            outfit_code    = "1;0,0,0,0,0,0",
            unk_boolean_12 = False,
            mouse_color    = 0,
            shaman_color   = self.shaman_color,
            unk_int_15     = 0,
            name_color     = -1,
            context_id     = client.context_id,
        )

    async def broadcast_packet(self, packet_cls, **fields):
        # TODO: TaskGroup in Python 3.11.
        await asyncio.gather(*[
            client.write_packet(
                packet_cls,

                **fields,
            )

            for client in self.clients
        ])

    async def broadcast_packet_except(self, client, packet_cls, **fields):
        # TODO: TaskGroup in Python 3.11.
        await asyncio.gather(*[
            other_client.write_packet(
                packet_cls,

                **fields,
            )

            for other_client in self.clients if other_client is not client
        ])

    async def xml_data(self):
        if self._map_xml_data is not None:
            return self._map_xml_data

        self._map_xml_data = await self.museum.data(self.map_xml_path)

        return self._map_xml_data

    async def on_player_died(self, client):
        pass

    async def on_player_victory(self, client):
        pass

    async def on_get_cheese(self, client, packet):
        pass

    async def on_multi_emote(self, client, packet):
        pass

    async def kill(self, client, *, only_others=False, type=caseus.enums.DeathType.Normal):
        await self.broadcast_packet_except(
            client if only_others else None,

            caseus.clientbound.LegacyWrapperPacket,

            nested = caseus.clientbound.PlayerDiedPacket(
                session_id = client.session_id,
                unk_attr_2 = "",
                score      = 0,
                type       = type,
            ),
        )

        client.activity = caseus.enums.PlayerActivity.Dead

        await self.check_shorten_round()

        if not only_others:
            await self.on_player_died(client)

    async def victory(self, client):
        await self.broadcast_packet(
            caseus.clientbound.PlayerVictoryPacket,

            session_id = client.session_id,
        )

        client.activity = caseus.enums.PlayerActivity.Dead
        client.cheeses  = 0

        await self.check_shorten_round()

        self._has_player_won = True

        await self.on_player_victory(client)

    async def respawn(self, client):
        client.activity   = caseus.enums.PlayerActivity.Alive
        client.context_id = (client.context_id + 1) % 20

        await self.broadcast_packet(
            caseus.clientbound.UpdatePlayerListPacket,

            player                  = self.player_description(client),
            skip_prepare_animations = True,
        )

    async def set_can_collect(self, client, can_collect):
        await client.write_packet(
            caseus.clientbound.CollectibleActionPacket,

            action = caseus.clientbound.CollectibleActionPacket.SetCanCollect(
                can_collect = can_collect,
            ),
        )

    async def add_carrying_for_individual(
        self,
        client,
        *,
        carrying_client = _UNSPECIFIED,
        image_path,
        offset_x,
        offset_y,
        foreground,
        size_percentage = 100,
        angle = 0,
    ):
        if carrying_client is self._UNSPECIFIED:
            carrying_client = client

        await client.write_packet(
            caseus.clientbound.CollectibleActionPacket,

            action = caseus.clientbound.CollectibleActionPacket.AddCarrying(
                session_id      = 0 if carrying_client is None else carrying_client.session_id,
                image_path      = image_path,
                offset_x        = offset_x,
                offset_y        = offset_y,
                foreground      = foreground,
                size_percentage = size_percentage,
                angle           = angle,
            ),
        )

    async def add_carrying(
        self,
        client,
        *,
        image_path,
        offset_x,
        offset_y,
        foreground,
        size_percentage = 100,
        angle = 0,
    ):
        await self.broadcast_packet(
            caseus.clientbound.CollectibleActionPacket,

            action = caseus.clientbound.CollectibleActionPacket.AddCarrying(
                session_id      = 0 if client is None else client.session_id,
                image_path      = image_path,
                offset_x        = offset_x,
                offset_y        = offset_y,
                foreground      = foreground,
                size_percentage = size_percentage,
                angle           = angle,
            ),
        )

    async def clear_carrying(self, client):
        await self.broadcast_packet(
            caseus.clientbound.CollectibleActionPacket,

            action = caseus.clientbound.CollectibleActionPacket.ClearCarrying(
                session_id = 0 if client is None else client.session_id,
            ),
        )

    def _new_shaman(self):
        clients = self.clients

        if not self.has_shaman or len(clients) <= 0:
            return None

        if len(clients) == 1:
            return clients[0]

        while True:
            new_shaman = random.choice(clients)

            if new_shaman is not self.shaman:
                return new_shaman

    def _new_synchronizer(self):
        if not self.has_synchronizer or len(self.clients) <= 0:
            return None

        if self.shaman is not None:
            return self.shaman

        return self.clients[0]

    async def new_synchronizer(self, *, spawn_initial_objects=False):
        new_synchronizer = self._new_synchronizer()

        if self.synchronizer is new_synchronizer:
            return

        self.synchronizer = new_synchronizer
        if new_synchronizer is None:
            return

        await self.broadcast_packet(
            caseus.clientbound.LegacyWrapperPacket,

            nested = caseus.clientbound.SetSynchronizerPacket(
                session_id            = new_synchronizer.session_id,
                spawn_initial_objects = spawn_initial_objects,
            ),
        )

    async def setup_round(self, client):
        pass

    def round_time(self):
        time = asyncio.get_running_loop().time()
        if time >= self._round_end:
            return 0

        return int(self._round_end - time)

    async def send_round(self, client, *, players=None, spawn_initial_objects=False, duration=None):
        await client.write_packet(
            caseus.clientbound.NewRoundPacket,

            map_code    = self.map_code,
            num_players = self.num_active_clients,
            round_id    = self.round_id,
            xml         = "" if self.map_xml_path is None else await self.xml_data(),
            author      = self.map_author,
            category    = self.map_category,
        )

        if players is None:
            players = [self.player_description(client) for client in self.clients]

        await client.write_packet(
            caseus.clientbound.SetPlayerListPacket,

            players = players,
        )

        if self.synchronizer is not None:
            await client.write_packet(
                caseus.clientbound.LegacyWrapperPacket,

                nested = caseus.clientbound.SetSynchronizerPacket(
                    session_id            = self.synchronizer.session_id,
                    spawn_initial_objects = spawn_initial_objects,
                ),
            )

        if duration is None:
            duration = self.round_time()

        await client.write_packet(
            caseus.clientbound.SetRoundTimerPacket,

            seconds = duration,
        )

        if self.shaman is None:
            await client.write_packet(caseus.clientbound.ShamanInfoPacket)
        else:
            await client.write_packet(
                caseus.clientbound.ShamanInfoPacket,

                blue_session_id = self.shaman.session_id,
                blue_level      = 1,
            )

        await self.setup_round(client)

    async def _check_round_ended(self):
        # TODO: Make this use a 'Timeout' in Python 3.11?

        loop = asyncio.get_running_loop()

        try:
            while self.museum.is_serving():
                while self.museum.is_serving() and loop.time() < self._round_end:
                    await pak.util.yield_exec()

                await self.start_new_round()

        except asyncio.CancelledError:
            return

    async def check_shorten_round(self):
        num_alive_clients = len(self.alive_clients)

        if num_alive_clients <= 0:
            # Let the check round ended task handle the new round.
            self._round_end = 0

            return

        if (
            (not self.has_shaman or any(client.is_shaman for client in self.alive_clients)) and

            num_alive_clients > 2
        ):
            return

        new_round_end = asyncio.get_running_loop().time() + self.ROUND_SHORTEN_TIME
        if new_round_end < self._round_end:
            await self.broadcast_packet(
                caseus.clientbound.SetRoundTimerPacket,

                seconds = self.ROUND_SHORTEN_TIME,
            )

            self._round_end = asyncio.get_running_loop().time() + self.ROUND_SHORTEN_TIME

    async def start_new_round(self):
        self.round_id     = (self.round_id + 1) % 127
        self.shaman       = self._new_shaman()
        self.synchronizer = self._new_synchronizer()
        self.anchors      = []

        self._has_player_won = False

        players = []
        for client in self.clients:
            client.activity   = caseus.enums.PlayerActivity.Alive
            client.cheeses    = 0
            client.context_id = (client.context_id + 1) % 20

            if client is self.shaman:
                client.is_shaman = True

            client.has_sent_anchors = True

            players.append(self.player_description(client))

        # TODO: TaskGroup in Python 3.11.
        await asyncio.gather(*[
            self.send_round(client, players=players, spawn_initial_objects=True, duration=self.round_duration)

            for client in self.clients
        ])

        if self.round_duration != 0:
            self._round_end = asyncio.get_running_loop().time() + self.round_duration

            if self._check_round_ended_task is None:
                self._check_round_ended_task = asyncio.create_task(self._check_round_ended())

    def activity_for_new_client(self, client):
        return caseus.enums.PlayerActivity.Dead

    async def on_enter_exhibit(self, client):
        pass

    async def on_exit_exhibit(self, client):
        pass

    async def _on_enter_exhibit(self, client):
        await client.write_packet(
            caseus.clientbound.JoinedRoomPacket,

            official  = True,
            raw_name  = self.room_name,
            flag_code = self.museum.country,
        )

        await client.write_packet(
            caseus.clientbound.StartRoundCountdownPacket,

            activate_countdown = False,
        )

        client.activity = self.activity_for_new_client(client)

        client.has_sent_anchors = False

        await self.on_enter_exhibit(client)

        # No clients before.
        if len(self.clients) == 1:
            await self.start_new_round()

        else:
            await self.send_round(client)

            await self.broadcast_packet_except(
                client,

                caseus.clientbound.UpdatePlayerListPacket,

                player              = self.player_description(client),
                refresh_player_menu = True,
            )

    async def _on_exit_exhibit(self, client):
        if client is self.synchronizer:
            # Stop the client from thinking it's a synchronizer.
            await client.write_packet(
                caseus.clientbound.LegacyWrapperPacket,

                nested = caseus.clientbound.SetSynchronizerPacket(
                    session_id            = 0,
                    spawn_initial_objects = False,
                ),
            )

        await self.new_synchronizer()
        await self.kill(client, only_others=True)

        await self.on_exit_exhibit(client)

    @pak.packet_listener(caseus.serverbound.CommandPacket)
    async def _on_command(self, client, packet):
        # TODO: More scalable command system?

        match packet.command.split():
            case ["mort", *_]:
                await self.kill(client)

    @pak.packet_listener(caseus.serverbound.ObjectSyncPacket)
    async def _on_object_sync(self, client, packet):
        if client is not self.synchronizer:
            return

        if packet.round_id != self.round_id:
            return

        await self.broadcast_packet_except(
            client,

            caseus.clientbound.ObjectSyncPacket,

            objects = [obj.clientbound(add_if_missing=True) for obj in packet.objects]
        )

        for client in self.clients:
            if client.has_sent_anchors:
                continue

            await client.write_packet(
                caseus.clientbound.LegacyWrapperPacket,

                nested = caseus.clientbound.AddAnchorsPacket(
                    self.anchors
                ),
            )

            client.has_sent_anchors = True

    @pak.packet_listener(caseus.serverbound.AddAnchorsPacket)
    async def _on_add_anchors(self, client, packet):
        if client is not self.synchronizer:
            return

        self.anchors.extend(packet.anchors)

        await self.broadcast_packet(
            caseus.clientbound.LegacyWrapperPacket,

            nested = caseus.clientbound.AddAnchorsPacket(
                packet.anchors,
            ),
        )

        await self.broadcast_packet(
            caseus.clientbound.PlayShamanInvocationSoundPacket,

            shaman_object_id = -1,
        )

    @pak.packet_listener(caseus.serverbound.PlayerMovementPacket)
    async def _on_player_movement(self, client, packet):
        if packet.round_id != self.round_id:
            return

        await self.broadcast_packet_except(
            client,

            caseus.clientbound.PlayerMovementPacket,

            session_id          = client.session_id,
            round_id            = self.round_id,
            moving_right        = packet.moving_right,
            moving_left         = packet.moving_left,
            x                   = packet.x,
            y                   = packet.y,
            velocity_x          = packet.velocity_x,
            velocity_y          = packet.velocity_y,
            jumping             = packet.jumping,
            jumping_frame_index = packet.jumping_frame_index,
            entered_portal      = packet.entered_portal,
            rotation_info       = packet.rotation_info,
        )

    @pak.packet_listener(caseus.serverbound.PlayerActionPacket)
    async def _on_player_animation(self, client, packet):
        await self.broadcast_packet_except(
            client,

            caseus.clientbound.PlayerActionPacket,

            session_id = client.session_id,
            animation  = packet.animation,
            allow_self = False,
        )

    @pak.packet_listener(caseus.serverbound.PlayerDiedPacket)
    async def _on_player_died(self, client, packet):
        if packet.round_id != self.round_id:
            return

        await self.kill(client, type=packet.type)

    @pak.packet_listener(caseus.serverbound.EnterHolePacket)
    async def _on_enter_hole(self, client, packet):
        if packet.round_id != self.round_id:
            return

        await self.victory(client)

    @pak.packet_listener(caseus.serverbound.GetCheesePacket)
    async def _on_get_cheese(self, client, packet):
        if packet.round_id != self.round_id:
            return

        if packet.context_id != client.context_id:
            return

        client.cheeses += 1

        await self.broadcast_packet(
            caseus.clientbound.SetCheesesPacket,

            session_id = client.session_id,
            cheeses    = client.cheeses,
        )

        await self.on_get_cheese(client, packet)

    @pak.packet_listener(caseus.serverbound.ShamanObjectPreviewPacket)
    async def _on_shaman_object_preview(self, client, packet):
        # The coordinate ranges of the clientbound packet
        # are not the same as the serverbound ranges.

        if packet.x > 32767:
            return

        if packet.x < -32768:
            return

        if packet.y > 32767:
            return

        if packet.y < -32768:
            return

        await self.broadcast_packet_except(
            client,

            caseus.clientbound.ShamanObjectPreviewPacket,

            session_id       = client.session_id,
            shaman_object_id = packet.shaman_object_id,
            x                = packet.x,
            y                = packet.y,
            angle            = packet.angle,
            child_offsets    = packet.child_offsets,
            is_spawning      = packet.is_spawning,
        )

    @pak.packet_listener(caseus.serverbound.RemoveShamanObjectPreviewPacket)
    async def _on_remove_shaman_object_preview(self, client, packet):
        await self.broadcast_packet_except(
            client,

            caseus.clientbound.RemoveShamanObjectPreviewPacket,

            session_id = client.session_id,
        )

    @pak.packet_listener(caseus.serverbound.AddShamanObjectPacket)
    async def _add_shaman_object(self, client, packet):
        if packet.round_id != self.round_id:
            return

        await self.broadcast_packet_except(
            client,

            caseus.clientbound.AddShamanObjectPacket,

            object_id        = packet.object_id,
            shaman_object_id = packet.shaman_object_id,
            x                = packet.x,
            y                = packet.y,
            angle            = packet.angle,
            velocity_x       = packet.velocity_x,
            velocity_y       = packet.velocity_y,
            mice_collidable  = packet.mice_collidable,
        )

        if packet.spawned_by_player:
            await self.broadcast_packet(
                caseus.clientbound.PlayShamanInvocationSoundPacket,

                shaman_object_id = caseus.game.shaman_object_id_parts(packet.shaman_object_id)[0],
            )

    @pak.packet_listener(caseus.serverbound.UseIceCubePacket)
    async def _on_use_ice_cube(self, client, packet):
        if not self._has_player_won:
            return

        affected_client = self.client_with_session_id(packet.session_id)
        if affected_client is client:
            return

        # TODO: Check if client hasn't run out of ice cubes.

        if affected_client.is_shaman:
            return

        await self.kill(affected_client)

        await self.synchronizer.write_packet(
            caseus.clientbound.AddShamanObjectPacket,

            object_id        = -1,
            shaman_object_id = 54,
            x                = packet.x,
            y                = packet.y,
            mice_collidable  = True,
        )

    @pak.packet_listener(caseus.serverbound.ShowEmoticonPacket)
    async def _on_show_emoticon(self, client, packet):
        await self.broadcast_packet_except(
            client,

            caseus.clientbound.ShowEmoticonPacket,

            session_id = client.session_id,
            emoticon   = packet.emoticon,
        )

    @pak.packet_listener(caseus.serverbound.PlayEmotePacket)
    async def _on_play_emote(self, client, packet):
        if packet.partner_session_id == -1:
            await self.broadcast_packet_except(
                client,

                caseus.clientbound.PlayEmotePacket,

                session_id = client.session_id,
                emote      = packet.emote,
                argument   = packet.argument,
                from_lua   = False,
            )

            return

        await self.broadcast_packet_except(
            client,

            caseus.clientbound.PlayEmotePacket,

            session_id = client.session_id,
            emote      = packet.emote,
            argument   = packet.argument,
            from_lua   = False,
        )

        await self.broadcast_packet(
            caseus.clientbound.PlayEmotePacket,

            session_id = packet.partner_session_id,
            emote      = packet.emote.partner_emote,
            argument   = packet.argument,
            from_lua   = False,
        )

        if packet.emote is caseus.enums.Emote.RockPaperScissors_1:
            await self.broadcast_packet(
                caseus.clientbound.SetRockPaperScissorsChoicesPacket,

                first_session_id  = client.session_id,
                first_choice      = caseus.enums.RockPaperScissorsChoice.random(),
                second_session_id = packet.partner_session_id,
                second_choice     = caseus.enums.RockPaperScissorsChoice.random(),
            )

        await self.on_multi_emote(client, packet)
