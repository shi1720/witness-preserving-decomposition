"""Score raw controls; deterministic field/value normalization is post hoc."""
import collections,json
from pathlib import Path
from witness import Registry,COLUMNS,render
ROOT=Path(__file__).resolve().parents[1]
ts={t['id']:t for t in map(json.loads,(ROOT/'data/tasks.jsonl').read_text().splitlines())}
rs=list(map(json.loads,(ROOT/'results/reasoned.jsonl').read_text().splitlines()));assert len(rs)==84
stats={}
for v in ['direct','unkeyed','keyed']:
 a=[r for r in rs if r['view']==v]
 stats[v]={'n':len(a),'negatives':sum(not r['reference'] for r in a),'correct':sum(r['prediction']==('A' if r['reference'] else 'B') for r in a),'epistemic_correct':sum(r['prediction']==(ts[r['id']]['unkeyed_epistemic_reference'] if v=='unkeyed' else ('A' if r['reference'] else 'B')) for r in a),'false_accepts':sum(r['prediction']=='A' and not r['reference'] for r in a),'abstentions':sum(r['prediction']=='C' for r in a),'invalid':sum(r['prediction'] not in ['A','B','C'] for r in a)}
plans=list(map(json.loads,(ROOT/'results/workflow.jsonl').read_text().splitlines()));normalized=[]
for r in plans:
 t=ts[r['id']];p=r['plan']['parsed'];groups=p.get('groups') if isinstance(p,dict) else None
 try:
  conditions=[]
  for g in groups:
   if all(isinstance(x,str) for x in g):c={x:t['query'][x] for x in g}
   else:
    assert all(isinstance(x,list) and len(x)==2 and x[0] in COLUMNS and x[1]==t['query'][x[0]] for x in g)
    assert len({x[0] for x in g})==len(g);c=dict(g)
   assert c;conditions.append(c)
  reg=Registry(t['evidence'],t['package']);rr=[reg.lookup(c) for c in conditions];d=reg.bind(t['query'],rr)
  normalized.append({'id':r['id'],'conditions':conditions,'full_row_plan':any(set(c)==set(COLUMNS) for c in conditions),'status':d.status,'correct':d.status==('listed' if t['reference'] else 'not_listed'),'document_sentence':render(t['package'],t['query'],d,reg.snapshot)})
 except (AssertionError,TypeError,KeyError,ValueError):normalized.append({'id':r['id'],'invalid':True})
summary={'reasoned':stats,'planner':{'n':len(plans),'strict_schema_valid':sum(r['valid_plan'] for r in plans),'normalized_valid':sum('invalid' not in r for r in normalized),'normalized_full_row':sum(r.get('full_row_plan',False) for r in normalized),'normalized_correct':sum(r.get('correct',False) for r in normalized),'normalization_post_hoc':True}}
(ROOT/'results/control_summary.json').write_text(json.dumps(summary,indent=2));(ROOT/'results/normalized_documents.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in normalized));print(json.dumps(summary,indent=2))
