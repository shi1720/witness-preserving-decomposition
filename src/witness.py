"""Source-row binding for typed, conjunctive documentation claims.

This is a source-relative protocol, not a natural-language entailment oracle.
Projection replies must be issued by the trusted adapter. Generative prose is
not admitted as a factual certificate. Classical relational provenance provides
the underlying semantics; no new database theorem is claimed.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import FrozenSet, Mapping, Tuple
COLUMNS=('release','interpreter_tag','platform_tag')
@dataclass(frozen=True)
class Reply:
    snapshot: str
    conditions: Tuple[Tuple[str,str],...]
    witnesses: FrozenSet[str]
    complete: bool
@dataclass(frozen=True)
class Decision:
    status: str
    witness: str | None
    reason: str
class Registry:
    def __init__(self,rows,namespace='registry'):
        self.rows={}
        for row in rows:
            vals={k:str(row[k]) for k in COLUMNS}
            key=str(row['id'])
            if key in self.rows:raise ValueError('Source row identifiers must be unique')
            self.rows[key]=vals
        self.snapshot=sha256(json.dumps({'namespace':namespace,'rows':self.rows},sort_keys=True).encode()).hexdigest()
    def lookup(self,conditions:Mapping[str,str],complete=True):
        if not conditions or not set(conditions)<=set(COLUMNS):raise ValueError('Unknown or empty condition')
        matches=frozenset(k for k,row in self.rows.items() if all(row[c]==v for c,v in conditions.items()))
        return Reply(self.snapshot,tuple(sorted(conditions.items())),matches,complete)
    def bind(self,query:Mapping[str,str],replies):
        if set(query)!=set(COLUMNS):raise ValueError('A full typed claim is required')
        if not replies:return Decision('unknown',None,'No subtask evidence')
        coverage=set();sets=[]
        for reply in replies:
            if reply.snapshot!=self.snapshot:raise ValueError('Mixed source snapshots')
            conditions=dict(reply.conditions)
            if not conditions or any(c not in query or query[c]!=v for c,v in conditions.items()):raise ValueError('Subtask changed the claim')
            coverage.update(conditions)
            expected=self.lookup(conditions).witnesses
            if not reply.witnesses<=expected:raise ValueError('Invalid row witness')
            if reply.complete and reply.witnesses!=expected:raise ValueError('Unwarranted completeness assertion')
            sets.append(reply.witnesses)
        if coverage!=set(query):return Decision('unknown',None,'Unbound claim fields')
        common=set.intersection(*(set(s) for s in sorted(sets,key=len)))
        if common:
            key=min(common)
            assert all(self.rows[key][c]==query[c] for c in COLUMNS)
            return Decision('listed',key,'One source row binds all conditions')
        if all(r.complete for r in replies):return Decision('not_listed',None,'Complete subtask views have empty common witness set')
        return Decision('unknown',None,'Incomplete views cannot certify absence')

def render(package,query,decision,snapshot):
    prefix=f"In registry snapshot {snapshot[:12]}, {package} release {query['release']}"
    target=f"interpreter tag {query['interpreter_tag']} and platform tag {query['platform_tag']}"
    if decision.status=='listed':return f"{prefix} lists an artifact tag combination with {target} (source row {decision.witness})."
    if decision.status=='not_listed':return f"{prefix} has no listed artifact tag combination with {target}."
    return f"The supplied evidence is insufficient to determine whether {package} release {query['release']} lists an artifact tag combination with {target}."
