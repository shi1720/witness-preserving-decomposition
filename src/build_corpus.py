"""Build publication-evidence relations from exact PyPI wheel tag records.
Does NOT infer installability, source-build support, or transitive compatibility.
"""
import hashlib,itertools,json,random
from pathlib import Path
from packaging.utils import parse_wheel_filename
from packaging.version import Version,InvalidVersion
ROOT=Path(__file__).resolve().parents[1]
rng=random.Random(1720406)
relations=[];tasks=[];sources=[]
for f in sorted((ROOT/'data/pypi').glob('*.json')):
 d=json.loads(f.read_text());vs=[]
 for v,files in d['releases'].items():
  try:vv=Version(v)
  except InvalidVersion:continue
  if vv.is_prerelease or vv.is_devrelease:continue
  if any(x['filename'].endswith('.whl') and not x.get('yanked',False) for x in files):vs.append((vv,v))
 versions=[v for _,v in sorted(vs,reverse=True)[:8]]
 entries={};records=[]
 for v in versions:
  for artifact in d['releases'][v]:
   if not artifact['filename'].endswith('.whl') or artifact.get('yanked',False):continue
   _,_,_,tags=parse_wheel_filename(artifact['filename'])
   for tag in sorted(tags,key=str):
    if not tag.interpreter.startswith('cp'):continue
    tup=(v,tag.interpreter,tag.platform)
    entries.setdefault(tup,[]).append(artifact['filename'])
 R=set(entries)
 if not R:continue
 domains=[sorted({t[i] for t in R}) for i in range(3)]
 projections={s:{tuple(t[i] for i in s) for t in R} for s in [(0,1),(0,2),(1,2)]}
 ghosts=[t for t in itertools.product(*domains) if t not in R and all(tuple(t[i] for i in s) in proj for s,proj in projections.items())]
 relation_id=f.stem
 relations.append({'id':relation_id,'columns':['release','interpreter_tag','platform_tag'],'rows':[{'tuple':t,'files':entries[t]} for t in sorted(R)],'domains':domains,'pairwise_ghosts':len(ghosts),'rows_count':len(R),'universe_count':len(list(itertools.product(*domains)))})
 sources.append({'package':relation_id,'url':'https://pypi.org/pypi/'+relation_id+'/json','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'selected_versions':versions})
 # Matched support/unsupported table-context pairs; counterfactuals selected without model outputs.
 # For each 3-way ghost choose one witness for each 2-way projection. Add seeded distractors.
 rng.shuffle(ghosts)
 for j,t in enumerate(ghosts[:12]):
  witnesses=[]
  for s in [(0,1),(0,2),(1,2)]:
   candidates=sorted(x for x in R if all(x[i]==t[i] for i in s));witnesses.append(rng.choice(candidates))
  context=set(witnesses);others=sorted(R-context);rng.shuffle(others);context.update(others[:9])
  context=sorted(context)
  positive=rng.choice(witnesses)
  base={'package':relation_id,'relation_id':relation_id,'pair_id':f'{relation_id}-{j}','evidence':[{'id':f'E{i+1:02d}','release':x[0],'interpreter_tag':x[1],'platform_tag':x[2],'filename':sorted(entries[x])[0]} for i,x in enumerate(context)]}
  for truth,query in [(False,t),(True,positive)]:
   tasks.append(dict(base,id=base['pair_id']+('-no' if not truth else '-yes'),query=dict(zip(['release','interpreter_tag','platform_tag'],query)),reference=truth))
(ROOT/'data/relations.json').write_text(json.dumps(relations,indent=2))
(ROOT/'data/sources.json').write_text(json.dumps(sources,indent=2))
rng.shuffle(tasks);(ROOT/'data/tasks.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in tasks))
print(json.dumps({'packages':len(relations),'relation_rows':sum(x['rows_count'] for x in relations),'pairwise_ghosts':sum(x['pairwise_ghosts'] for x in relations),'packages_with_ghosts':sum(x['pairwise_ghosts']>0 for x in relations),'matched_tasks':len(tasks),'per_package':[{k:x[k] for k in ['id','rows_count','pairwise_ghosts']} for x in relations]},indent=2))
