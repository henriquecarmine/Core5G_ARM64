<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/03-relatorio-entrega-avaliacao.md`](../../../labs/03-relatorio-entrega-avaliacao.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Report — submission, structure and evaluation criteria (Open5GS + UERANSIM)

This document guides **students** (what to submit) and **instructors** (how to evaluate).

**Video material:** [list of lab videos](video_seq_report.md). The [full walkthrough](https://youtu.be/ic3_CIllb9o) covers lab guides 01–03 and shows how to finalize evidence (including PCAP / Wireshark) for submission.

---

## 1. Submission format

- **Accepted format:** a single PDF **or** a `.zip`/`.7z` file with the PDF + attachments (logs in `.txt`; large PCAPs may be omitted with a justification and a *hash* or description of the capture).
- **Identification on the first page:** full name, enrollment number or ID, class, date, suggested title: "Open5GS + UERANSIM Lab — Interfaces and Protocols".
- **Repository version (recommended):** output of `git rev-parse --short HEAD` at the root of the clone (if applicable).

---

## 2. Suggested report structure

1. **Summary** (10–15 lines): objectives, what was executed, main results.
2. **Environment:** OS, `docker` / `docker compose` versions, relevant RAM (image *pull*).
3. **Lab Guide 01 — Core:** cross-reference with evidence ([01-core-open5gs.md](01-core-open5gs.md)).
4. **Lab Guide 02 — UERANSIM:** same ([02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)).
5. **Discussion:**
  - Role of the **N2** (NGAP/SCTP) and **N3** (GTP-U) interfaces in the containerized scenario.
  - Differences relative to a monolithic gNB *vs.* a CU/DU *split* (conceptual reference; this lab uses integrated UERANSIM).
  - Limitations (*emulation*, no real RF, cell *stub*, etc.).
6. **Conclusion** (5–8 lines).
7. **Appendices** (numbered): A — command outputs; B — logs; C — *screenshots*; D — PCAPs.

**Suggested length:** 8–15 pages **without** excessive appendices.

---

## 3. Minimum evidence inventory (student)


| ID  | Evidence                                                                    | Lab guide |
| --- | --------------------------------------------------------------------------- | --------- |
| E1  | `docker --version` and `docker compose version`                             | 01        |
| E2  | `docker compose ps` (healthy core)                                          | 01        |
| E3  | Confirmation of `core_net-sbi` / `core_net-n2` / `core_net-n3` networks and subnets | 01 |
| E4  | Subscriber created (WebUI, script or `mongosh`) aligned with `ue.yaml`      | 01        |
| E5  | Complete `healthcheck.sh` output (without RAN or with a note about limitations) | 01    |
| E6  | Sample logs NRF + AMF + SMF + UPF                                           | 01        |
| E7  | `docker ps` with `ueransim` **Up**                                          | 02        |
| E8  | Relevant excerpts `gnb.yaml` / `ue.yaml`                                    | 02        |
| E9  | UERANSIM + AMF logs with N2 / NG Setup                                      | 02        |
| E10 | (Advanced optional) PCAP or N2 Wireshark *screenshot* (`sctp.port == 38412`) | 02      |
| E11 | (Advanced optional) N3 PCAP or GTP-U Wireshark *screenshot* (`udp.port == 2152`) | 02  |
| E12 | Complete `test_ue_connection.sh` output                                     | 02        |
| E13 | `healthcheck.sh` with the RAN up                                            | 02        |


A missing **mandatory evidence** item flagged in the lab guides → deduction in the "Completeness" rubric.

---

## 4. Screenshots and screen captures

- **Open5GS WebUI:** 1 *screenshot* (after login or with a visible screen, no password).
- **Terminal:** *screenshot* or monospaced text; searchable text is preferable.
- **Wireshark:** *screenshots* with a **visible filter** — N2: `sctp.port == 38412`; N3: `udp.port == 2152`.

**Rule:** **legible** images; captioned crops.

---

## 5. Good practices with logs

- Do not put multi-megabyte logs in the PDF; attach `.txt` or use `tail -n 80`.
- Indicate the **date/time** of collection and the **container** (`docker logs <nome>`).
- On failures, include the **first** complete error message.

---

## 6. Suggested rubric (100 points)


| Criterion                | Weight | Description                                                                   |
| ------------------------ | ------ | ---------------------------------------------------------------------------- |
| **Completeness**         | 25     | Lab guides 01 and 02; evidence E1–E13 where applicable; appendices cited in the text. |
| **Technical correctness**| 30     | Commands and IPs consistent with the project; N2/N3 discussed without serious errors. |
| **Analysis**             | 25     | Lab limitations; connection to 5G SA **interfaces and protocols**.           |
| **Clarity**              | 15     | Structure, numbered figures, acceptable spelling.                            |
| **Defense / extra**      | 5      | Optional N2 PCAP; documented *troubleshooting*; answers during the defense.  |


---

## 7. Discussion questions

1. What does **N2** carry relative to **N3**?
2. Why does the UERANSIM compose depend on the external networks `core_net-n2` and `core_net-n3`?
3. What is **PFCP** at the SMF–UPF junction and how does it relate to the PDU Session?
4. What would change if the IMSI in the core did not match the `supi` in `ue.yaml`?

---

## 8. Final checklist before submitting

- PDF with complete identification  
- Figures/tables numbered and cited  
- Appendices with clear names (`anexoA-compose-ps.txt`, …)  
- No password or *token* in the logs  
- References (Open5GS, UERANSIM, 3GPP, when applicable)
