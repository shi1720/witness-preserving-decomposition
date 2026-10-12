"""Exhaustively verify evidence-relative labels over the binary ternary universe."""
import itertools,json
from pathlib import Path
U=list(itertools.product(range(2),repeat=3));pairs=[(0,1),(0,2),(1,2)]
def projections(R):return tuple(frozenset(tuple(t[i] for i in s) for t in R) for s in pairs)
relations=[frozenset(t for i,t in enumerate(U) if mask>>i&1) for mask in range(256)]
classes={}
for R in relations:classes.setdefault(projections(R),[]).append(R)
checks=0
for views,worlds in classes.items():
 J=set().union(*worlds)
 actualJ={q for q in U if all(tuple(q[i] for i in s) in P for s,P in zip(pairs,views))};assert J==actualJ
 for q in U:
  certain=q in J and any(sum(tuple(t[i] for i in s)==tuple(q[i] for i in s) for t in J)==1 for s in pairs)
  assert certain==all(q in R for R in worlds)
  assert (q in J)==any(q in R for R in worlds)
  checks+=1
out={'universe_tuples':8,'relations':256,'view_equivalence_classes':len(classes),'query_class_checks':checks,'passed':True}
(Path(__file__).resolve().parents[1]/'results/exhaustive.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
