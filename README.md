# Vatte Hospital OS

AI-powered hospital management app, with a team of AI agents (Sister, Reception, Accountant, Pharmacy, Lab, HR…) supervised by a Boss AI that reports to the doctor.

- Runs as an installable web app (PWA) on phone, iPad and computer.
- Frontend: plain HTML/JS on GitHub Pages. Backend: Supabase (Postgres, Auth, Row Level Security).
- AI never diagnoses or prescribes on its own; the doctor decides.
- Develop only with dummy (synthetic) patients. Never send real patient data to a free-tier AI API.

## 20-phase roadmap
1. ✅ Base app, login, roles, audit log
2. ✅ Database (all core tables, per-hospital isolation, tamper-proof records)
3. ✅ Reception: registration, UHID, duplicate check, search, OPD, IPD admit/discharge, beds
4. ✅ Doctor dashboard (15 live numbers, OPD line, alerts)
5. ✅ Nursing Sister: vitals, abnormal alerts to doctor, orders, medication records, notes, handover
6. ✅ Nidan history engine — 15 systems, 97 complaints, 716 questions (Hutchison 24e), red-flag alerts, doctor report
7. ✅ Agent engine: 13 agents registry, 12 actions (low / controlled / high risk), approvals, tamper-proof logs, Boss AI report, schedules (pg_cron)
8. ✅ AI chat: Sister AI + Reception AI (Gemini free tier via `agent-chat` edge function; tools use the user's own login; patient names masked as codes before reaching the AI)
9. ✅ Appointment AI + OPD token line (free slots, safe booking / reschedule / cancel, auto tokens with emergency & 65+ priority, TV token screen, night job, AI chat booking)
10. ✅ Accounts: rate list, server-calculated bills, payments / refunds / expenses as append-only ledger, discount rules, day book, cash close, receipts; Accountant AI (read-only)
11. ✅ Pharmacy AI: medicine list (OTC / H / H1 / X), stock in with batch + expiry + MRP checks, sale with earliest-expiry-first batch and server price, H1 register, append-only stock ledger, sale cancel, damage correction, expiry / low-stock alerts, reorder list, AI order list (with approval), pharmacist takes payment for pharmacy bills
12. ✅ Lab AI: test list with parameters, units, male / female normal ranges and critical limits (20 starter tests), write tests (urgent alert), sample no., result entry with server-side High / Low / CRITICAL flags, append-only results with amended reports, printable report, critical alert to Doctor + Sister repeated every 30 min until acknowledged, lab tests auto-added to bills; Lab AI (pending / late tests, today, patient reports)
13. ✅ HR + Operations + Procurement AI: staff list linked to app login, daily attendance + self check-in / out, leave requests & approval, server-calculated salary sheet and salary payment (goes into day book), equipment register with service due, repair / complaint tickets, non-medicine purchase requests with approval → received → paid (day book); AI: HR today, salary due, repairs & service, purchases pending
14. ✅ Medical Records + Follow-up + Quality AI: doctor visit note + prescription in one save (server allergy check, override needs reason), printable Rx, versioned notes, discharge summary (auto lab results, print), documents upload (private storage), follow-up call / WhatsApp list (visit auto-closes it), daily checklists (hand hygiene, BMW, crash cart, fridge, cleaning, fire), incident reporting (can hide name) + review, quality numbers; AI: records pending, quality today, quality numbers
15. Boss AI
16. Voice (Hindi / English / Hinglish)
17. Automation + notifications
18. Security & privacy testing
19. Full trial with dummy patients
20. Live launch (paid AI tier, monitoring)

## Setup (Phase 1)
1. Create a free Supabase project.
2. Supabase → SQL Editor → run `supabase/phase1.sql`.
3. Put the Project URL and anon key in `config.js`.
4. Open the site. The **first account** created becomes the Doctor (owner). Everyone after that is "Pending" until the doctor gives them a role in **Staff & Roles**.
