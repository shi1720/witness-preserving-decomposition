import argparse,hashlib,json,time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--output',required=True);p.add_argument('--limit',type=int,default=0);p.add_argument('--views',default='direct,unkeyed,keyed');a=p.parse_args()
tasks=[json.loads(x) for x in (ROOT/'data/tasks.jsonl').read_text().splitlines()]
if a.limit:tasks=tasks[:a.limit]
model,tok=load(a.model)
labelids=[tok.encode(x,add_special_tokens=False) for x in 'ABC'];assert all(len(x)==1 for x in labelids)
ix=mx.array([x[0] for x in labelids]);done=set();outpath=Path(a.output)
if outpath.exists():done={(r['id'],r['view']) for r in map(json.loads,outpath.read_text().splitlines())}
def make_prompt(t,view):
 cols=['release','interpreter_tag','platform_tag']; rows=t['evidence'];lines=[]
 if view=='direct':
  lines.append('Complete registry rows (each line describes one published artifact tag combination):')
  lines.append('source_id | '+' | '.join(cols))
  for r in rows:lines.append(r['id']+' | '+' | '.join(r[c] for c in cols))
 else:
  lines.append('Three workers returned complete projections of the SAME registry. A pair appearing in a projection means at least one registry row has that pair. No other registry information is available.')
  if view=='keyed':lines.append('source_id identifies the SAME original registry row across all worker outputs.')
  else:lines.append('Source row identities have been removed. Rows in different projections must not be assumed to describe the same artifact.')
  for pair in [(0,1),(0,2),(1,2)]:
   cs=[cols[i] for i in pair];lines.append('Worker view: '+ ' | '.join((['source_id'] if view=='keyed' else [])+cs))
   projected=set(tuple(([r['id']] if view=='keyed' else [])+[r[c] for c in cs]) for r in rows)
   for row in sorted(projected):lines.append(' | '.join(row))
 q=t['query']
 claim=f"The registry lists at least one artifact tag combination for {t['package']} release {q['release']} with interpreter tag {q['interpreter_tag']} and platform tag {q['platform_tag']}."
 text=('Audit this developer documentation claim against the supplied evidence only. '
       'A means the claim is supported by the evidence. B means the complete registry establishes no such combination. '
       'C means the available evidence is insufficient to decide whether such a combination exists. '
       'A claim requires all three fields to belong to the same registry row. '
       'Do not infer runtime installability. Return only A, B, or C.\n\n'+'\n'.join(lines)+'\n\nClaim: '+claim)
 return tok.apply_chat_template([{'role':'user','content':text}],tokenize=False,add_generation_prompt=True)
start=time.monotonic();n=0
with outpath.open('a') as out:
 for task in tasks:
  for view in a.views.split(','):
   if (task['id'],view) in done:continue
   prompt=make_prompt(task,view);tokens=tok.encode(prompt,add_special_tokens=False);tick=time.monotonic()
   logits=model(mx.array([tokens]))[0,-1,:].astype(mx.float32);mx.eval(logits)
   probs=mx.softmax(logits[ix]);mx.eval(probs);vals=probs.tolist();pred='ABC'[max(range(3),key=lambda i:vals[i])];top=int(mx.argmax(logits).item())
   r={'id':task['id'],'pair_id':task['pair_id'],'package':task['package'],'view':view,'reference':task['reference'],'prediction':pred,'probabilities':vals,'raw_top_token':tok.decode([top]),'input_tokens':len(tokens),'seconds':time.monotonic()-tick,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
   out.write(json.dumps(r)+'\n');out.flush();n+=1
   if n%30==0:print(n,'elapsed',round(time.monotonic()-start,1),flush=True)
