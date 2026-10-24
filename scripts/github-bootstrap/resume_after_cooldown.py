"""Bounded cooldown resume. Uses the same account and API; no limit evasion.
Refreshes durable IDs on every attempt; never counts a failed creation.
"""
from api import *
import datetime
not_before=datetime.datetime(2026,10,24,3,32,tzinfo=datetime.timezone.utc)
print('Content creation paused until',not_before.isoformat(),flush=True)
while datetime.datetime.now(datetime.timezone.utc)<not_before:
 time.sleep(min(30,max(1,(not_before-datetime.datetime.now(datetime.timezone.utc)).total_seconds())))
for attempt in range(4):
 print('Resuming with fresh issue readback',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
 r=subprocess.run(['python3',str(ROOT/'scripts/github-bootstrap/reconcile.py'),'--phase','issues'])
 if r.returncode==0:print('All manifest issues created',flush=True);break
 if attempt==3:raise SystemExit('Content creation remains blocked; consult failures and live audit.')
 print('Service still blocking creation; cooldown five minutes before refreshed retry',flush=True)
 for _ in range(10):time.sleep(30)
