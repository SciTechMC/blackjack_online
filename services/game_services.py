import random

rooms = {}
suits = ["♠", "♥", "♦", "♣"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

def generate_deck():
    return [f"{r}{s}" for r in ranks for s in suits] * 6

def hand_value(hand):
    value, aces = 0, 0
    for card in hand:
        rank = card[:-1]
        if rank in ["J", "Q", "K"]:
            value += 10
        elif rank == "A":
            aces += 1
            value += 11
        else:
            value += int(rank)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

async def handle_join(sio, sid, data):
    room = data.get("room")
    username = data.get("username", sid)
    if room not in rooms:
        rooms[room] = {"players": {}, "dealer_hand": [], "deck": []}
    rooms[room]["players"][sid] = {"username": username, "hand": [], "bet": 0, "status": "waiting", "balance": 1000}
    await sio.enter_room(sid, room)
    await sio.emit("joined", {"sid": sid}, room=room)

async def handle_bet(sio, sid, data):
    for room, state in rooms.items():
        if sid in state["players"]:
            player = state["players"][sid]
            amount = data.get("amount", 0)
            if player["balance"] >= amount:
                player["bet"] = amount
                player["balance"] -= amount
                player["status"] = "betting"
                await sio.emit("bet_ack", {"status": "ok", "amount": player["bet"], "balance": player["balance"]}, to=sid)
            else:
                await sio.emit("bet_ack", {"status": "error", "message": "Insufficient balance"}, to=sid)
            break

async def handle_start_round(sio, sid):
    for room, state in rooms.items():
        if sid in state["players"]:
            state["deck"] = generate_deck()
            random.shuffle(state["deck"])
            state["dealer_hand"] = [state["deck"].pop(), state["deck"].pop()]
            for pid, player in state["players"].items():
                player["hand"] = [state["deck"].pop(), state["deck"].pop()]
                player["status"] = "playing"
            result = {
                "dealer": [state["dealer_hand"][0], "??"],
                "players": {
                    pid: {"hand": p["hand"], "value": hand_value(p["hand"])}
                    for pid, p in state["players"].items()
                }
            }
            await sio.emit("round_result", result, room=room)
            break

async def handle_hit(sio, sid):
    for room, state in rooms.items():
        if sid in state["players"]:
            player = state["players"][sid]
            if player["status"] == "playing":
                player["hand"].append(state["deck"].pop())
                if hand_value(player["hand"]) > 21:
                    player["status"] = "busted"
                await sio.emit("round_result", {
                    "dealer": [state["dealer_hand"][0], "??"],
                    "players": {
                        pid: {"hand": p["hand"], "value": hand_value(p["hand"])}
                        for pid, p in state["players"].items()
                    }
                }, room=room)
                await check_if_round_over(sio, room)
            break

async def handle_stand(sio, sid):
    for room, state in rooms.items():
        if sid in state["players"]:
            player = state["players"][sid]
            if player["status"] == "playing":
                player["status"] = "stood"
                await check_if_round_over(sio, room)
            break

async def check_if_round_over(sio, room):
    state = rooms[room]
    if all(p["status"] in ["busted", "stood"] for p in state["players"].values()):
        while hand_value(state["dealer_hand"]) < 17:
            state["dealer_hand"].append(state["deck"].pop())
        dealer_val = hand_value(state["dealer_hand"])
        results = {}
        for sid, player in state["players"].items():
            player_val = hand_value(player["hand"])
            if player["status"] == "busted":
                results[sid] = {"outcome": "lose", "balance": player["balance"]}
            elif player_val > dealer_val or dealer_val > 21:
                winnings = player["bet"] * 2
                player["balance"] += winnings
                results[sid] = {"outcome": "win", "balance": player["balance"]}
            elif player_val == dealer_val:
                player["balance"] += player["bet"]
                results[sid] = {"outcome": "push", "balance": player["balance"]}
            else:
                results[sid] = {"outcome": "lose", "balance": player["balance"]}
        await sio.emit("dealer_done", {
            "dealer": state["dealer_hand"],
            "results": results
        }, room=room)

async def remove_player(sid):
    for room, state in rooms.items():
        if sid in state["players"]:
            del state["players"][sid]
            break