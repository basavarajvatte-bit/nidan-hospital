# Nidan Hospital OS

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
5. Nursing Sister: vitals, notes, abnormal alerts
6. Nidan triage questions + medical book PDF
7. Agent engine: registry, tasks, logs, permissions, approvals
8. AI chat: Sister AI + Reception AI
9. Appointment AI + OPD queue
10. Accountant AI: billing, payments, immutable ledger
11. Pharmacy AI
12. Lab AI
13. HR + Operations + Procurement AI
14. Medical Records + Follow-up + Quality AI
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
