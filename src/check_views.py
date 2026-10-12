import itertools,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'data/tasks.jsonl';tasks=[json.loads(x) for x in path.read_text().splitlines()]
cols=['release','interpreter_tag','platform_tag'];pairs=[(0,1),(0,2),(1,2)];summary={'tasks':len(tasks),'negative':0,'unkeyed_certain':0,'unkeyed_ambiguous':0,'checks_passed':0}
for task in tasks:
 R={tuple(row[c] for c in cols) for row in task['evidence']};q=tuple(task['query'][c] for c in cols)
 projs={s:{tuple(t[i] for i in s) for t in R} for s in pairs}
 ds=[sorted({t[i] for t in R}) for i in range(3)]
 J={t for t in itertools.product(*ds) if all(tuple(t[i] for i in s) in ps for s,ps in projs.items())}
 possible=q in J
 required=possible and any(sum(tuple(t[i] for i in s)==tuple(q[i] for i in s) for t in J)==1 for s in pairs)
 task['unkeyed_epistemic_reference']='A' if required else ('C' if possible else 'B')
 # Independent explicit SQL check; full row identity is required.
 con=sqlite3.connect(':memory:');con.execute('create table facts(release text, py text, plat text)');con.executemany('insert into facts values (?,?,?)',sorted(R));actual=con.execute('select count(*) from facts where release=? and py=? and plat=?',q).fetchone()[0]>0;con.close()
 assert actual==task['reference']==(q in R)
 sets=[{r['id'] for r in task['evidence'] if all(r[cols[i]]==q[i] for i in s)} for s in pairs]
 assert bool(set.intersection(*sets))==actual
 if not actual:
  assert all(sets) and not set.intersection(*sets)
  # Explicit indistinguishability: adding the joint tuple leaves all projections unchanged.
  assert all({tuple(t[i] for i in s) for t in R|{q}}==ps for s,ps in projs.items())
  summary['negative']+=1
 summary['unkeyed_certain']+=required;summary['unkeyed_ambiguous']+=possible and not required;summary['checks_passed']+=1
path.write_text(''.join(json.dumps(t)+'\n' for t in tasks));(ROOT/'results/verification_checks.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
