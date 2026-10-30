import pandas as pd, numpy as np
from scipy.stats import spearmanr
want={'TM2D1','TM2D2','TM2D3'}
gh=pd.read_csv('data/raw/depmap/CRISPRGeneEffect.csv',nrows=0).columns
ge=pd.read_csv('data/raw/depmap/CRISPRGeneEffect.csv',usecols=[gh[0]]+[c for c in gh if c.split(' (')[0] in want],index_col=0)
ge.columns=[c.split(' (')[0] for c in ge.columns]
ch=pd.read_csv('data/raw/depmap/OmicsCNGeneWGS.csv',nrows=0).columns
cn=pd.read_csv('data/raw/depmap/OmicsCNGeneWGS.csv',usecols=['ModelID','IsDefaultEntryForModel']+[c for c in ch if c.split(' (')[0] in want])
cn=cn[cn.IsDefaultEntryForModel.astype(str).isin(['Yes','True'])].drop_duplicates('ModelID').set_index('ModelID').drop(columns='IsDefaultEntryForModel')
cn.columns=[c.split(' (')[0] for c in cn.columns]
j=ge.join(cn,rsuffix='_cn',how='inner')
print('n',len(j))
for g in want:
    r=spearmanr(j[g],j[g+'_cn'],nan_policy='omit')
    lo=j[j[g+'_cn']<0.75][g]; hi=j[j[g+'_cn']>=0.75][g]
    print(g,'rho(effect,ownCN)=%.3f p=%.2g'%(r.correlation,r.pvalue),'mean eff CN<0.75: %.3f (n=%d) vs >=0.75: %.3f (n=%d)'%(lo.mean(),len(lo),hi.mean(),len(hi)))
    # dependent lines CN
    d=j[j[g]<-0.5][g+'_cn']; print('   median CN in dependent lines %.2f vs all %.2f'%(d.median(),j[g+'_cn'].median()))
