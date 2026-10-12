import collections,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
tasks={t['id']:t for t in map(json.loads,(ROOT/'data/tasks.jsonl').read_text().splitlines())}
results={}
for label,file in [('Qwen3-4B','qwen3-views-pilot.jsonl'),('Qwen2.5-Coder-7B','qwen25-coder-views.jsonl')]:
 rows=list(map(json.loads,(ROOT/'results'/file).read_text().splitlines()));stats={}
 for view in ['direct','unkeyed','keyed']:
  rs=[r for r in rows if r['view']==view];neg=[r for r in rs if not r['reference']]
  epistemic=lambda r:tasks[r['id']]['unkeyed_epistemic_reference'] if view=='unkeyed' else ('A' if r['reference'] else 'B')
  stats[view]={'n':len(rs),'negatives':len(neg),'correct':sum(r['prediction']==('A' if r['reference'] else 'B') for r in rs),'epistemic_correct':sum(r['prediction']==epistemic(r) for r in rs),'false_accepts':sum(r['prediction']=='A' for r in neg),'abstentions':sum(r['prediction']=='C' for r in rs),'raw_label_tokens':sum(r['raw_top_token'] in 'ABC' and len(r['raw_top_token'])==1 for r in rs),'median_tokens':statistics.median(r['input_tokens'] for r in rs)}
 results[label]=stats
(ROOT/'results/model_summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
