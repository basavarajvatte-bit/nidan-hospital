-- PHASE 8c: chat with every department agent (applied as migration "phase8c_chat_all_agents")
insert into public.ai_chat_agents(agent_id, title, roles, tools) values
 ('boss','Boss AI','{doctor,admin}','{find_patient,list_beds,boss.daily_report,nurse.overdue_vitals,reception.today,appointment.today,operations.beds,pharmacy.stock,lab.pending,accountant.dues,followup.due}'),
 ('nurse','Sister AI','{doctor,admin,nurse}','{find_patient,latest_vitals,list_beds,nurse.overdue_vitals,operations.beds,followup.due,followup.schedule,operations.bed_status}'),
 ('reception','Reception AI','{doctor,admin,receptionist}','{find_patient,list_beds,reception.today,appointment.today,operations.beds,followup.due,followup.schedule}'),
 ('appointment','Appointment AI','{doctor,admin,receptionist}','{find_patient,appointment.today}'),
 ('lab','Lab AI','{doctor,admin,lab}','{find_patient,lab.pending}'),
 ('pharmacy','Pharmacy AI','{doctor,admin,pharmacist}','{pharmacy.stock}'),
 ('accountant','Accountant AI','{doctor,admin,accountant}','{accountant.dues}'),
 ('followup','Follow-up AI','{doctor,admin,receptionist,nurse}','{find_patient,followup.due,followup.schedule}'),
 ('operations','Bed / Operations AI','{doctor,admin,nurse,receptionist}','{list_beds,operations.beds,operations.bed_status}')
on conflict (agent_id) do update set title=excluded.title, roles=excluded.roles, tools=excluded.tools;
-- ai_chat_begin now also returns 'about' (agent responsibilities) and 'department' for the per-agent prompt.
