import random
import asyncio

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

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

async def handle_join(sio, sid, data):
    room = data.get("room")
    username = data.get("username", sid)
    if room not in rooms:
        rooms[room] = {"players": {}, "dealer_hand": [], "deck": [], "turn_index": 0, "turn_order": []}
    rooms[room]["players"][sid] = {
        "username": username,
        "hand": [],
        "bet": 0,
        "status": "waiting",
        "balance": 1000
    }
    await sio.enter_room(sid, room)
    await sio.emit("joined", {"sid": sid, "username": username}, room=room)

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
            state["turn_order"] = list(state["players"].keys())
            state["turn_index"] = 0

            for pid, player in state["players"].items():
                player["hand"] = [state["deck"].pop(), state["deck"].pop()]
                if is_blackjack(player["hand"]):
                    player["status"] = "blackjack"
                else:
                    player["status"] = "playing"

            await broadcast_game_state(sio, room)

            if all(p["status"] != "playing" for p in state["players"].values()):
                await dealer_play(sio, room)
            else:
                await start_turn_timer(sio, room)
            break

async def handle_hit(sio, sid):
    for room, state in rooms.items():
        if sid in state["players"] and sid == current_player_sid(state):
            player = state["players"][sid]
            if player["status"] == "playing":
                player["hand"].append(state["deck"].pop())
                if hand_value(player["hand"]) > 21:
                    player["status"] = "busted"
                    await next_turn(sio, room)
                await broadcast_game_state(sio, room)
            break

async def handle_stand(sio, sid):
    for room, state in rooms.items():
        if sid in state["players"] and sid == current_player_sid(state):
            player = state["players"][sid]
            if player["status"] == "playing":
                player["status"] = "stood"
                await broadcast_game_state(sio, room)
                await next_turn(sio, room)
            break

def current_player_sid(state):
    if 0 <= state["turn_index"] < len(state["turn_order"]):
        return state["turn_order"][state["turn_index"]]
    return None

async def next_turn(sio, room):
    state = rooms[room]
    state["turn_index"] += 1
    if state["turn_index"] >= len(state["turn_order"]):
        await dealer_play(sio, room)
    else:
        await broadcast_game_state(sio, room)
        await start_turn_timer(sio, room)

async def broadcast_game_state(sio, room):
    state = rooms[room]
    current = current_player_sid(state)
    await sio.emit("round_result", {
        "dealer": [state["dealer_hand"][0], "??"],
        "players": {
            sid: {
                "hand": p["hand"],
                "value": hand_value(p["hand"]),
                "username": p["username"],
                "status": p["status"]
            } for sid, p in state["players"].items()
        },
        "current_turn": current
    }, room=room)

async def start_turn_timer(sio, room, timeout=15):
    state = rooms[room]
    sid = current_player_sid(state)
    await asyncio.sleep(timeout)
    if sid == current_player_sid(state):  # still their turn?
        state["players"][sid]["status"] = "stood"
        await next_turn(sio, room)

async def dealer_play(sio, room):
    state = rooms[room]
    while hand_value(state["dealer_hand"]) < 17:
        state["dealer_hand"].append(state["deck"].pop())
    dealer_val = hand_value(state["dealer_hand"])
    results = {}

    for sid, player in state["players"].items():
        player_val = hand_value(player["hand"])
        if player["status"] == "busted":
            outcome = "lose"
        elif player["status"] == "blackjack":
            if is_blackjack(state["dealer_hand"]):
                player["balance"] += player["bet"]  # push
                outcome = "push"
            else:
                player["balance"] += int(player["bet"] * 2.5)  # 3:2 payout
                outcome = "blackjack"
        elif is_blackjack(state["dealer_hand"]):
            outcome = "lose"
        elif player_val > dealer_val or dealer_val > 21:
            player["balance"] += player["bet"] * 2
            outcome = "win"
        elif player_val == dealer_val:
            player["balance"] += player["bet"]
            outcome = "push"
        else:
            outcome = "lose"

        results[sid] = {"outcome": outcome, "balance": player["balance"]}

    await sio.emit("dealer_done", {
        "dealer": state["dealer_hand"],
        "results": results
    }, room=room)

async def remove_player(sid):
    for room, state in rooms.items():
        if sid in state["players"]:
            del state["players"][sid]
            break
