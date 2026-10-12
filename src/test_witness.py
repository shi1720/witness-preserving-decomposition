import itertools,json,unittest
from dataclasses import replace
from pathlib import Path
from witness import Registry,COLUMNS,render
class WitnessTests(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':'a','release':'r0','interpreter_tag':'p0','platform_tag':'o1'},{'id':'b','release':'r0','interpreter_tag':'p1','platform_tag':'o0'},{'id':'c','release':'r1','interpreter_tag':'p0','platform_tag':'o0'}]
  self.reg=Registry(self.rows);self.q=dict(zip(COLUMNS,['r0','p0','o0']))
 def replies(self):return [self.reg.lookup({COLUMNS[i]:self.q[COLUMNS[i]] for i in p}) for p in [(0,1),(0,2),(1,2)]]
 def test_all_pairs_true_joint_false(self):
  rr=self.replies();self.assertTrue(all(r.witnesses for r in rr));self.assertEqual(self.reg.bind(self.q,rr).status,'not_listed')
 def test_same_source_row_required(self):
  q={k:self.rows[0][k] for k in COLUMNS};rr=[self.reg.lookup({k:q[k]}) for k in COLUMNS];d=self.reg.bind(q,rr);self.assertEqual(d.status,'listed');self.assertEqual(d.witness,'a')
 def test_incomplete_absence_abstains(self):self.assertEqual(self.reg.bind(self.q,[replace(r,complete=False) for r in self.replies()]).status,'unknown')
 def test_omitted_field_abstains(self):self.assertEqual(self.reg.bind(self.q,[self.reg.lookup({'release':'r0'})]).status,'unknown')
 def test_unknown_id_rejected(self):
  rr=self.replies();rr[0]=replace(rr[0],witnesses=frozenset(['made_up']))
  with self.assertRaises(ValueError):self.reg.bind(self.q,rr)
 def test_stale_snapshot_rejected(self):
  rr=self.replies();rr[0]=replace(rr[0],snapshot='old')
  with self.assertRaises(ValueError):self.reg.bind(self.q,rr)
 def test_changed_intent_rejected(self):
  rr=self.replies();rr[0]=self.reg.lookup({'release':'r1'})
  with self.assertRaises(ValueError):self.reg.bind(self.q,rr)
 def test_fake_completeness_rejected(self):
  rr=self.replies();rr[0]=replace(rr[0],witnesses=frozenset())
  with self.assertRaises(ValueError):self.reg.bind(self.q,rr)
 def test_duplicate_row_identity_rejected(self):
  with self.assertRaises(ValueError):Registry(self.rows+[dict(self.rows[0],platform_tag='other')])
 def test_real_corpus_all_partitions(self):
  tasks=[json.loads(x) for x in (Path(__file__).resolve().parents[1]/'data/tasks.jsonl').read_text().splitlines()]
  partitions=[[(0,),(1,),(2,)],[(0,1),(2,)],[(0,),(1,2)],[(0,2),(1,)],[(0,1,2)],[(0,1),(0,2),(1,2)]]
  for t in tasks:
   reg=Registry(t['evidence'],t['package'])
   for part in partitions:
    replies=[reg.lookup({COLUMNS[i]:t['query'][COLUMNS[i]] for i in group}) for group in part]
    self.assertEqual(reg.bind(t['query'],replies).status,'listed' if t['reference'] else 'not_listed')
if __name__=='__main__':unittest.main()
