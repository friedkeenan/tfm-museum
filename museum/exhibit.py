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
def round_time_listener(passed_time):
    def decorator(listener):
        listener._round_time_listener_passed_time = passed_time

        return listener

    return decorator

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

    incomplete = False

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

        self._round_time_listeners        = {}
        self._active_round_time_listeners = {}
        self._round_end           = 0

        self._check_round_timings_task = None

        for _, attr in inspect.getmembers(self, lambda x: hasattr(x, "_round_time_listener_passed_time")):
            self.register_round_time_listener(attr._round_time_listener_passed_time, attr)

    def close(self):
        if self._check_round_timings_task is not None:
            self._check_round_timings_task.cancel()

    async def wait_closed(self):
        if self._check_round_timings_task is not None:
            await self._check_round_timings_task

            self._check_round_timings_task = None

        await self.end_listener_tasks()

    def register_round_time_listener(self, passed_time, *listeners):
        self._round_time_listeners.setdefault(passed_time, []).extend(listeners)

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

    def player_info(self, client):
        return caseus.PlayerInfo(
            username     = client.username,
            session_id   = client.session_id,
            is_shaman    = client.is_shaman,
            activity     = client.activity,
            cheeses      = client.cheeses,
            outfit_code  = "1;0,0,0,0,0,0",
            shaman_color = self.shaman_color,
            name_color   = -1,
            context_id   = client.context_id,
        )

    async def broadcast_packet(self, packet_cls, **fields):
        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    client.write_packet(
                        packet_cls,

                        **fields,
                    )
                )

    async def broadcast_packet_except(self, client, packet_cls, **fields):
        async with asyncio.TaskGroup() as tg:
            for other_client in self.clients:
                if other_client is client:
                    continue

                tg.create_task(
                    other_client.write_packet(
                        packet_cls,

                        **fields,
                    )
                )

    async def xml_data(self):
        if self._map_xml_data is not None:
            return self._map_xml_data

        self._map_xml_data = await self.museum.data(self.map_xml_path)
        self._map_xml_data = self._map_xml_data.strip()

        return self._map_xml_data

    async def on_player_died(self, client):
        pass

    async def on_player_victory(self, client):
        pass

    async def on_get_cheese(self, client, packet):
        pass

    async def on_multi_emote(self, client, packet):
        pass

    async def server_message(self, translation_key, *translation_args, general_channel=True):
        await self.broadcast_packet(
            caseus.clientbound.ServerMessagePacket,

            general_channel  = general_channel,
            translation_key  = translation_key,
            translation_args = [str(arg) for arg in translation_args],
        )

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

            player                  = self.player_info(client),
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

    async def raise_inventory_item(self, client, item_id):
        if isinstance(client, int):
            session_id = client
        else:
            session_id = client.session_id

        await self.broadcast_packet(
            caseus.clientbound.RaiseItemPacket,

            session_id = session_id,
            item       = caseus.clientbound.RaiseItemPacket.InventoryItem(
                item_id = item_id,
            ),
        )

    async def give_meep(self, client, can_meep=True):
        await client.write_packet(
            caseus.clientbound.GiveMeepPacket,

            can_meep = can_meep,
        )

    async def add_npc_for_individual(
        self,
        client,
        *,
        session_id,
        name,
        title_id,
        feminine,
        outfit_code,
        x,
        y,
        facing_right,
        face_player = True,
        interface = caseus.enums.NPCInterface.OfficialEvent,
        periodic_message = "",
    ):
        await client.write_packet(
            caseus.clientbound.AddNPCPacket,

            session_id       = session_id,
            name             = name,
            title_id         = title_id,
            feminine         = feminine,
            outfit_code      = outfit_code,
            x                = x,
            y                = y,
            facing_right     = facing_right,
            face_player      = face_player,
            interface        = interface,
            periodic_message = periodic_message,
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
            players = [self.player_info(client) for client in self.clients]

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

    def _setup_round_timings(self):
        if self.round_duration <= 0:
            return

        time = asyncio.get_running_loop().time()

        self._round_end = time + self.round_duration

        # TODO: Should the time be dynamic with '_round_end' since that
        # can change if e.g. the round gets shortened? Or would that be
        # weird for the round to shorten and then have a bunch of things
        # happen? Leaning towards keeping the current situation of being
        # based on just when the round started.
        self._active_round_time_listeners = {
            time + passed_time: listeners for passed_time, listeners in self._round_time_listeners.items()
        }

        if self._check_round_timings_task is None:
            self._check_round_timings_task = asyncio.create_task(self._check_round_timings())

    async def _check_round_timings(self):
        # NOTE: This could maybe be adjusted to use a 'Timeout'
        # object, but that might be strange with the round time
        # listening functionality, and so we're currently sticking
        # with what we have.

        loop = asyncio.get_running_loop()

        try:
            while self.museum.is_serving():
                time = loop.time()

                if time >= self._round_end:
                    await self.start_new_round()

                    continue

                inactive_listner_times = []
                for listner_time, listeners in self._active_round_time_listeners.items():
                    if time >= listner_time:
                        await asyncio.gather(*[
                            listener() for listener in listeners
                        ])

                        inactive_listner_times.append(listner_time)

                for listner_time in inactive_listner_times:
                    self._active_round_time_listeners.pop(listner_time)

                await pak.util.yield_exec()

        except asyncio.CancelledError:
            return

    async def shorten_round(self, round_time=None):
        if round_time is None:
            round_time = self.ROUND_SHORTEN_TIME

        new_round_end = asyncio.get_running_loop().time() + round_time
        if new_round_end < self._round_end:
            await self.broadcast_packet(
                caseus.clientbound.SetRoundTimerPacket,

                seconds = round_time,
            )

            self._round_end = new_round_end

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

        await self.shorten_round()

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

            players.append(self.player_info(client))

        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    self.send_round(client, players=players, spawn_initial_objects=True, duration=self.round_duration)
                )

        self._setup_round_timings()

    def activity_for_new_client(self, client):
        return caseus.enums.PlayerActivity.Dead

    async def on_enter_exhibit(self, client):
        pass

    async def on_exit_exhibit(self, client):
        pass

    async def _warn_incomplete(self, client):
        if not self.incomplete:
            return

        await client.general_message("<B><R>Warning! This exhibit is <J>INCOMPLETE</J>!</R></B>")

    async def _reload_client(self, client):
        # The room name could have changed.
        await client.write_packet(
            caseus.clientbound.JoinedRoomPacket,

            official  = True,
            raw_name  = self.room_name,
            flag_code = self.museum.country,
        )

        # Not sure this is necessary but might as well send it.
        await client.write_packet(
            caseus.clientbound.StartRoundCountdownPacket,

            activate_countdown = False,
        )

        client.activity = self.activity_for_new_client(client)

        client.has_sent_anchors = False

        await self._warn_incomplete(client)

        await self.on_enter_exhibit(client)

    async def _on_reload(self):
        async with asyncio.TaskGroup() as tg:
            for client in self.clients:
                tg.create_task(
                    self._reload_client(client)
                )

        await self.start_new_round()
        await self.server_message("Reloaded exhibit")

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

        await self._warn_incomplete(client)

        await self.on_enter_exhibit(client)

        # No clients before.
        if len(self.clients) == 1:
            await self.start_new_round()

        else:
            await self.send_round(client)

            await self.broadcast_packet_except(
                client,

                caseus.clientbound.UpdatePlayerListPacket,

                player              = self.player_info(client),
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

            case ["reload"]:
                await self.museum.reload_exhibit(self)

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

    @pak.packet_listener(caseus.serverbound.ShowEmojiPacket)
    async def _on_show_emoji(self, client, packet):
        await self.broadcast_packet_except(
            client,

            caseus.clientbound.ShowEmojiPacket,

            session_id = client.session_id,
            emoji_id   = packet.emoji_id,
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

    @pak.packet_listener(caseus.serverbound.RoomMessagePacket)
    async def _on_room_message(self, client, packet):
        await self.broadcast_packet(
            caseus.clientbound.RoomMessagePacket,

            username = client.username,
            message  = packet.message,
        )

    @pak.packet_listener(caseus.serverbound.MeepPacket)
    async def _on_meep(self, client, packet):
        await self.broadcast_packet(
            caseus.clientbound.MeepExplosionPacket,

            session_id = client.session_id,
            x          = packet.x,
            y          = packet.y,
            power      = client.meep_power,
        )
