<!-- sync: 196ae2dd -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/jornada-do-ue-linguagem-simples.md`](../../jornada-do-ue-linguagem-simples.md). All languages: [INDEX](INDEX.md).

# The UE's Journey in plain language

> Pocket guide to keep open on the side while you click through the **UE's Journey**
> (in the panel: **Topology → "UE's Journey" button**). Each screen of the journey is a
> row down here — **no jargon**. The technical names show up only in
> parentheses, so you can recognize what's on the screen.

## The idea in one sentence

A phone joining the network is like **a person arriving at a building**: they show up,
identify themselves, go through security, get the **key to a room** and an
**address**, and then they can **send and receive mail**. That's all it is — the rest
is just details about "who does what".

---

## Project 2 (OAI + RIC) — the 16 screens

| On the screen | What's happening (simply) |
|---|---|
| **1. The phone turns on** | The person arrives at the building's door. The phone wakes up and is going to try to join the network. |
| **2. Radio — physical connection** | They step up to the front desk. This is the physical contact (the "radio") between the phone and the antenna. |
| **3. gNB ↔ Core — control** | The front desk (antenna) calls the building's management (the network core): "someone's here". |
| **4. UE registration** | The person introduces themselves: "I'm so-and-so, I'd like to come in". |
| **5. The Core's directory (NRF)** | Management checks the building's internal list: "who handles security? who hands out the keys?". |
| **6. Authentication** | Security checks the ID — is it really you? If it doesn't match, you don't get in. |
| **7. Data session request** | Approved, you ask for a "line" to send and receive things. |
| **8. Programs the user plane** | Management tells the delivery hallway: "get the path ready for this person's mail". |
| **9. The UE gets an IP** | You get the **room key** and an **address** — now you can receive mail. |
| **10. Data — outbound** | You send a letter out. |
| **11. Exit — internet / call** | The letter leaves the building for the outside world (the internet). |
| **12. Data — inbound** | The reply arrives and comes back up to you. |
| **13. Data collection (RIC)** | A **smart supervisor** starts noting down how things are going (speed, how crowded it is) — the numbers come straight from the antenna. |
| **14. Action on the antenna (RIC)** | The supervisor decides and **adjusts the flow in real time** (opens up more room, changes the queue). It's them "tweaking the antenna" from a distance. |
| **15. Long-term planner** | A planner studies the history and sends **rules** to the supervisor. This is where **artificial intelligence** comes in. |
| **16. The complete path** | The whole building at once: what's mandatory and what's the "smart" extra. |

---

## Two colors, two kinds of step

- 🟢 **mandatory** — it has to happen, otherwise you don't get in or you can't browse. It's the
  **lifeline** (screens 2 to 12).
- 🔵 **optional** — the "smart" extra (the supervisor and the planner, screens 13 to
  15). The network works without it — but this is where the AI lives.

## The most important insight: "who decides" ≠ "who carries"

In the building, **management** (which decides, authorizes, organizes) is **separate** from the
**hallways** (where the letters actually travel). This has an ugly name (CUPS),
but the idea is simple and powerful: you can **swap out a hallway without stopping
management**. That's what enables the next trick 👇

---

## Project 1 (Open5GS) — almost the same, with 2 differences

The story is the same (the phone arriving at the building). Only this changes:

1. **There's no smart supervisor** (the RIC). P1 goes from screen 1 all the way to "the complete
   path", without the intelligence parts.
2. **There's an extra ending: the backup hallway** (the *failover*). If the delivery
   hallway goes down, management **switches to a backup hallway on the spot** — and
   you keep browsing without noticing. It's the proof that separating "who decides"
   from "who carries" pays off.

---

## How to make it click

1. Open the **UE's Journey** in the panel and this guide on the side.
2. Click **Next** slowly, reading the screen's caption **and** the row here.
3. Go through it **2 or 3 times**. On the second pass, you'll already anticipate what's coming.
4. Only after that, if you want, look at the technical names — now they have a place in the
   story, they're no longer loose acronyms.

> Tip: the same diagram has a **"Data flow"** mode (little dots moving) and a
> **"Tour"** through the layers. The **Journey** is the step-by-step, guided version — start
> with it.
