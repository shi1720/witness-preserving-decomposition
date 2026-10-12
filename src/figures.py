import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'paper/figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
corpus=json.loads((ROOT/'results/corpus_summary.json').read_text());ps=[p for p in corpus['per_package'] if p['pairwise_ghosts']]
fig,ax=plt.subplots(figsize=(6.7,2.5));ax.bar(range(len(ps)),[p['pairwise_ghosts'] for p in ps],color='#206a8a');ax.set_xticks(range(len(ps)));ax.set_xticklabels([p['id'] for p in ps],rotation=40,ha='right',fontsize=8);ax.set_ylabel('Absent triples with all pairs present');ax.set_ylim(0,25);fig.tight_layout();fig.savefig(OUT/'corpus.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.7,1.8));ax.set(xlim=(0,10),ylim=(0,2));ax.axis('off')
boxes=[(.1,.55,2.2,.9,'Typed claim\nrelease + interpreter + platform'),(2.8,.55,2.0,.9,'Subtask replies\nconditions + snapshot + row IDs'),(5.3,.55,1.9,.9,'Deterministic binding\ncommon row required'),(7.7,.55,2.2,.9,'Controlled rendering\nlisted / absent / unknown')]
for x,y,w,h,s in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.05',edgecolor='#206a8a',facecolor='#eaf2f5'));ax.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=8)
for x,z in [(2.35,2.75),(4.85,5.25),(7.25,7.65)]:ax.add_patch(FancyArrowPatch((x,1),(z,1),arrowstyle='->',mutation_scale=12,color='#206a8a'))
ax.text(5,.15,'Guarantee applies to the typed claim and frozen source, not arbitrary prose or installability.',ha='center',fontsize=8);fig.tight_layout(pad=.2);fig.savefig(OUT/'architecture.pdf');plt.close(fig)
s=json.loads((ROOT/'results/model_summary.json').read_text());fig,axs=plt.subplots(1,2,figsize=(6.7,2.2),sharey=True)
for ax,(m,stats) in zip(axs,s.items()):
 views=list(stats);den=next(iter(stats.values()))['negatives'];vals=[stats[v]['false_accepts']/den for v in views];bars=ax.bar(views,vals,color=['#547a8b','#b76e4b','#398675']);ax.set_title(m+' (n- = '+str(den)+')',fontsize=9);ax.set_ylim(0,1.17)
 for b,v in zip(bars,views):ax.text(b.get_x()+b.get_width()/2,b.get_height()+.02,str(stats[v]['false_accepts'])+'/'+str(den),ha='center',fontsize=8)
axs[0].set_ylabel('Unsupported claims accepted');fig.tight_layout();fig.savefig(OUT/'pilot.pdf');plt.close(fig)
