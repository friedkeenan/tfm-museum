import caseus

from ..exhibit import Exhibit, available

@available
class Lobby(Exhibit):
    map_code   = 19
    map_author = "~19"

    round_duration = 0

    def activity_for_new_client(self, client):
        return caseus.enums.PlayerActivity.Alive

    async def on_player_died(self, client, packet):
        await self.respawn(client)

    async def on_player_victory(self, client, packet):
        await self.respawn(client)
