"""Exploratory natural-planner control; preserves raw generations and prompts."""
import argparse,hashlib,json,time
from pathlib import Path
from mlx_lm import load,generate
from mlx_lm.sample_utils import make_sampler
from witness import Registry,COLUMNS,render
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--limit-packages',type=int,default=14);a=p.parse_args()
alltasks=[json.loads(x) for x in (ROOT/'data/tasks.jsonl').read_text().splitlines()]
# One matched pair per package, chosen lexicographically before model inference.
chosen={}
for t in alltasks:
 if t['package'] not in chosen or t['pair_id']<chosen[t['package']]:chosen[t['package']]=t['pair_id']
tasks=sorted([t for t in alltasks if t['pair_id']==chosen[t['package']]],key=lambda t:t['id'])[:2*a.limit_packages]
model,tok=load(a.model);sampler=make_sampler(temp=0)
outpath=ROOT/'results/workflow.jsonl';done=set()
if outpath.exists():done={r['id'] for r in map(json.loads,outpath.read_text().splitlines())}
def call(prompt):
 text=tok.apply_chat_template([{'role':'user','content':prompt}],tokenize=False,add_generation_prompt=True)
 tick=time.monotonic();raw=generate(model,tok,prompt=text,max_tokens=160,sampler=sampler,verbose=False)
 try:
  start=raw.index('{');end=raw.rindex('}')+1;parsed=json.loads(raw[start:end])
 except (ValueError,json.JSONDecodeError):parsed=None
 return {'prompt':text,'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'raw':raw,'parsed':parsed,'seconds':time.monotonic()-tick}
with outpath.open('a') as out:
 for t in tasks:
  if t['id'] in done:continue
  q=t['query'];reg=Registry(t['evidence'],t['package'])
  prompt=('Plan exact registry checks for this documentation claim. The registry contains release, interpreter_tag, platform_tag on each artifact row. '
          'Return JSON {"groups":[["field",...],...]}. Each group is one conjunctive lookup on a row. '
          'Choose the checks you would actually use; all three fields must describe the same artifact. '
          'You may use one lookup with all fields, or multiple checks. Do not answer the claim.\nPackage: '+t['package']+'\nClaim fields: '+json.dumps(q))
  plan=call(prompt);parsed=plan['parsed'];groups=parsed.get('groups') if isinstance(parsed,dict) else None
  valid=isinstance(groups,list) and bool(groups) and all(isinstance(g,list) and bool(g) and all(c in COLUMNS for c in g) and len(set(g))==len(g) for g in groups)
  record={'id':t['id'],'pair_id':t['pair_id'],'package':t['package'],'reference':t['reference'],'plan':plan,'valid_plan':valid}
  if valid:
   rr=[reg.lookup({c:q[c] for c in g}) for g in groups];decision=reg.bind(q,rr)
   record.update(groups=groups,bound_decision=decision.status,rendered=render(t['package'],q,decision,reg.snapshot),snapshot=reg.snapshot)
   responses=[]
   for r in rr:responses.append({'conditions':dict(r.conditions),'found':bool(r.witnesses),'complete':r.complete,'snapshot':r.snapshot,'witness_ids':sorted(r.witnesses)})
   record['responses']=responses
   for mode in ['boolean','witness']:
    supplied=responses if mode=='witness' else [{k:v for k,v in r.items() if k!='witness_ids'} for r in responses]
    record[mode]=call('Decide whether the supplied complete registry checks establish this exact same-artifact claim. '
      'A=supported, B=not listed, C=insufficient evidence. Separate successful lookups need not share a row. '
      'Shared witness IDs, if supplied, identify the same source row. '
      'Return JSON {"decision":"A or B or C","reason":"brief reason"}.\nClaim: '+json.dumps(q)+'\nChecks: '+json.dumps(supplied))
  out.write(json.dumps(record)+'\n');out.flush();print(t['id'],flush=True)
