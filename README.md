## 🔧 **System Split: Frontend vs Backend**

### 🖥️ **Frontend Responsibilities**

* Login screen (username & password)
* Join/create room UI (enter room code)
* Visual table UI (top-down layout with player spots)
* Show:

  * Player cards
  * Bet input
  * Buttons: Hit, Stand, Double, Start Round
  * Balance + countdown timer
  * PFPs
* State syncing via WebSocket
* Handle player input
* Show results per round (win/loss/blackjack)

---

### 🐍 **Backend Responsibilities**

* WebSocket server (per room instance)
* User auth (login, register, store credentials securely)
* Room code generation and table management
* Game state management (deck, bets, hands, turns)
* Turn timer logic + auto-stand
* Server-side dealer behavior (draws, resolves hands)
* Player reconnect logic (with time limit)
* Player data persistence (MySQL): balance, login, pfp path
* Kick player functionality (room owner only)

---

## 🗺️ **Roadmap: Development Phases**

### ✅ **Phase 1 – Core MVP**

> Focus: Get one full game round playable

**Backend**

* Set up WebSocket server
* User registration/login
* Room creation & joining (by code)
* Deck shuffling & card dealing
* Game logic: bets, hit, stand, double, resolve outcomes
* Payout logic
* MySQL schema for users and balances

**Frontend**

* Basic UI: login, join/create room
* Table view with cards as images
* Buttons: Bet, Hit, Stand, Double
* Display own and others’ cards & balances
* Timer countdown per turn
* Room creator: "Start Round" button

---

### 🧩 **Phase 2 – Advanced Logic**

> Focus: Handling edge cases, user session management

**Backend**

* Turn timeouts → auto-stand
* Reconnect handling (store/reclaim state)
* Profile picture upload handling (store image path)
* Kick player command (for room owner)
* Dealer logic improvements (handle edge hands)

**Frontend**

* Show disconnect state / reconnection prompt
* Profile picture upload & display
* More robust room status (waiting/playing/ended)
* Show who's turn it is visually
* UI state syncing (disable buttons when not your turn)

---

### ✨ **Phase 3 – Polish & UX**

> Focus: Nice-to-haves and interface quality

**Backend**

* More secure password handling (hashing/salting)
* Logging and basic admin tools (optional)
* Game logs or round history (if desired)

**Frontend**

* Card dealing animations (later)
* Sound effects (later)
* Player avatars: preview, default placeholder
* Visual table polish (shadows, hover effects, etc.)
* Optional keyboard shortcuts

---

## Blackjack Rules

### 🎯 **Goal**

Get a hand value as close to **21** as possible **without going over**. Try to beat the **dealer's hand**.

---

### 🃏 **Card Values**

* Number cards (2–10): Worth their face value.
* Face cards (J, Q, K): Worth **10** points.
* Aces: Worth **1 or 11**, whichever helps your hand more.

---

### 🧑‍🤝‍🧑 **How to Play**

1. **You and the dealer** each get two cards.

   * You see both your cards.
   * One of the dealer’s cards is **face-up**, the other is **face-down**.

2. **Your turn**:

   * **Hit**: Take another card.
   * **Stand**: Keep your hand and end your turn.
   * You can hit as many times as you want—just don’t go **over 21** (that's called a **bust**).

3. **Dealer’s turn**:

   * Dealer reveals their face-down card.
   * Dealer **must hit** until they have **17 or more**.
   * Dealer stands at 17 or higher.

---

### 🏆 **Winning**

* If you’re closer to 21 than the dealer → **You win!**
* If you get exactly 21 with two cards (an Ace + 10) → That’s a **Blackjack** (usually pays extra).
* If you bust (go over 21) → **You lose**.
* If the dealer busts and you didn’t → **You win**.
* If both hands are the same value → It’s a **tie** (or “push”).