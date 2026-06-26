# SSK Footcare ERP — PRD

## Original Problem Statement
Build a comprehensive local/cloud B2B footwear manufacturing ERP. Costing calculation based on raw-material yield, order management against styles, production floor tracking (9 stages) with kanban-style colour×size matrix, PO upload/extraction from PDF/Excel, multi-user/multi-role login, inventory, worker payroll ledger and productivity bonuses.

## User Personas
- Admin / Owner — full system control, settings, users, costing margins
- Manager — POs, production scheduling, payroll, reports
- Production lead — daily floor (kanban, assignments, defects, WhatsApp share)
- Sales — POs, styles, dispatch invoices

## Core Requirements (static)
1. Style master with BOM + yield-based costing + image
2. PO upload from PDF/Excel with auto job creation
3. Production floor with 9 stages, colour×size matrix
4. Inventory with auto-consumption on procurement→cutting
5. Worker (Karigar) master + assignment + ledger + bonus
6. Payroll with advances + payments + ledger reconciliation
7. PDFs: Production Card (with per-process tally), Dispatch Challan, Tax Invoice, Material Requirements, Wage Slip
8. Multi-user RBAC (admin/manager/production/sales)
9. Visual reports (variance, cycle time, defect, monthly, karigar)
10. Time-bound stages with overdue alerts (admin-configurable)
11. WhatsApp share for production cards

## What's been implemented
- 2026-06-25 (forks 1-9): Full ERP base, Auth, PO PDF parsing, Production kanban (color×size), BOM/Yield costing, Style image upload, Components tracking, Karigar assignment + DnD bulk re-assign, Karigar ledger + bonus + wage-slip PDF, Inventory auto-consume + reorder alerts, Dispatch Challan + Tax Invoice + Material Req PDFs.
- 2026-06-26 (this fork — iteration 10):
  • **P0 fix**: Payment recording 400 error in Payroll (`openLedger(ledgerFor.row)`)
  • **Settings/ETA**: `/api/settings/stage-durations` + `/settings` page — admin configures per-stage hours
  • **Time-bound stages**: `stage_entered_at` + `stage_deadline` saved on every transition + initial job creation
  • **Overdue alerts**: `/api/dashboard/overdue` + red banner on Dashboard + red `OVERDUE` strip on Production cards
  • **Visual Reports** (Recharts): Production Trend (line), Karigar Output (bar), Cost Variance (bar), Cycle Time (bar), Defect Analytics (bar + pie)
  • **Production Card PDF**: added `PROCESS TALLY` table — per-process × per-size grid (DONE/REJ/SIGN columns) for floor workers to fill in
  • **WhatsApp Share**: green WhatsApp button on every production card, dialog with karigar phone picker, downloads PDF locally + opens wa.me chat

## Prioritized Backlog
**P0** — none open
**P1** — Bulk pay multiple karigars at end-of-week (deferred per user)
**P2** — Server-side WhatsApp Cloud API for direct PDF upload (no manual drag-drop)
**P2** — Visual seed for testing overdue badge (job with past stage_deadline)
**P3** — Split `server.py` into modules (production / payroll / reports)

## Next Tasks
- (When user asks) Bulk pay multi-karigar payout flow
- (When user asks) WhatsApp Cloud API integration
