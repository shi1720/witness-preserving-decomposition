import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];s=json.loads((R/'results/model_summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(3.25,2.0));vs=['direct','unkeyed','keyed'];w=.34
for j,(m,ss) in enumerate(s.items()):
 vals=[ss[v]['false_accepts']/ss[v]['negatives'] for v in vs];xs=[i+(j-.5)*w for i in range(3)];bs=ax.bar(xs,vals,width=w,label=m,color=['#206a8a','#b76e4b'][j])
 for b,v in zip(bs,vs):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.015,f"{ss[v]['false_accepts']}/{ss[v]['negatives']}",ha='center',fontsize=6.5)
ax.set_xticks(range(3));ax.set_xticklabels(vs);ax.set_ylim(0,1.35);ax.set_ylabel('Unsupported claims accepted');ax.legend(loc='upper center',ncol=1,frameon=False,fontsize=7);fig.tight_layout(pad=.5);fig.savefig(R/'paper/figures/pilot.pdf')
