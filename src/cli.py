"""Run a typed developer-documentation query from a frozen task file."""
import argparse,json
from pathlib import Path
from witness import Registry,COLUMNS,render
p=argparse.ArgumentParser();p.add_argument('--task-id',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
tasks=list(map(json.loads,(root/'data/tasks.jsonl').read_text().splitlines()))
t=next((t for t in tasks if t['id']==a.task_id),None)
if t is None:p.error('Unknown task id')
reg=Registry(t['evidence'],t['package']);q=t['query']
replies=[reg.lookup({COLUMNS[i]:q[COLUMNS[i]] for i in pair}) for pair in [(0,1),(0,2),(1,2)]]
decision=reg.bind(q,replies)
print(json.dumps({'status':decision.status,'snapshot':reg.snapshot,'witness':decision.witness,'sentence':render(t['package'],q,decision,reg.snapshot)},indent=2))
