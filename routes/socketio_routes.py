from services import game_services

def register_handlers(sio):
    @sio.event
    async def connect(sid, environ):
        print(f"[+] Connected: {sid}")

    @sio.event
    async def disconnect(sid):
        print(f"[-] Disconnected: {sid}")
        await game_services.remove_player(sid)

    @sio.event
    async def join(sid, data):
        await game_services.handle_join(sio, sid, data)

    @sio.event
    async def bet(sid, data):
        await game_services.handle_bet(sio, sid, data)

    @sio.event
    async def start_round(sid, data):            # ← add the `data` parameter
        await game_services.handle_start_round(sio, sid)

    @sio.event
    async def hit(sid):
        await game_services.handle_hit(sio, sid)

    @sio.event
    async def stand(sid):
        await game_services.handle_stand(sio, sid)