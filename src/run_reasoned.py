"""Free-generation control, one preselected matched pair per package."""
import argparse,ast,json,hashlib,time
from pathlib import Path
from mlx_lm import load,generate
from mlx_lm.sample_utils import make_sampler
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--model',required=True);a=p.parse_args()
model,tok=load(a.model)
# Reuse the exact evidence formatting of the registered pilot.
tree=ast.parse((ROOT/'src/run_views.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='make_prompt')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<evidence formatter>','exec'))
tasks=list(map(json.loads,(ROOT/'data/tasks.jsonl').read_text().splitlines()));chosen={}
for t in tasks:chosen[t['package']]=min(chosen.get(t['package'],t['pair_id']),t['pair_id'])
tasks=sorted([t for t in tasks if t['pair_id']==chosen[t['package']]],key=lambda t:t['id'])
outpath=ROOT/'results/reasoned.jsonl';done=set()
if outpath.exists():done={(r['id'],r['view']) for r in map(json.loads,outpath.read_text().splitlines())}
with outpath.open('a') as out:
 for t in tasks:
  for view in ['direct','unkeyed','keyed']:
   if (t['id'],view) in done:continue
   prompt=make_prompt(t,view).replace('Return only A, B, or C.','Reason carefully about same-row binding. Return JSON with keys "reason" (brief explanation) and "decision" (A, B, or C).')
   tick=time.monotonic();raw=generate(model,tok,prompt=prompt,max_tokens=256,sampler=make_sampler(temp=0),verbose=False)
   try:parsed=json.loads(raw[raw.index('{'):raw.rindex('}')+1]);pred=parsed.get('decision')
   except (ValueError,json.JSONDecodeError):parsed=None;pred=None
   r={'id':t['id'],'pair_id':t['pair_id'],'package':t['package'],'view':view,'reference':t['reference'],'prediction':pred,'parsed':parsed,'raw':raw,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'seconds':time.monotonic()-tick}
   out.write(json.dumps(r)+'\n');out.flush();print(t['id'],view,pred,flush=True)
