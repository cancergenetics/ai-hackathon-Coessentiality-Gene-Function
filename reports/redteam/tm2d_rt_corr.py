import pandas as pd, numpy as np
df=pd.read_csv('data/raw/depmap/CRISPRGeneEffect.csv',index_col=0)
df.columns=[c.split(' (')[0] for c in df.columns]
print(df.shape)
C=df.corr(min_periods=500) if False else None
genes=['TM2D1','TM2D2','TM2D3','JOSD1','AUP1','STUB1','CHIC2','PCNX1','PCNX3','ZDHHC6','MMD','ATP13A1','NOTCH1','NOTCH2','PSEN1','PSEN2','NCSTN','APH1A','PSENEN','ADAM10','APP','HSPA5','ERN1','ATF6','EIF2AK3','XBP1','DDIT3','ATF4','UFM1','UFL1','DDRGK1','EMC1','EMC3','SEL1L','SYVN1','UBE2G2','UBE2J1','DERL1','AMFR','FAF2','UBXN4']
genes=[g for g in genes if g in df.columns]
X=df[genes]
z=(df-df.mean())/df.std()
for g in ['TM2D1','TM2D2']:
    v=z[g]
    r=z.apply(lambda c: v.corr(c))
    r=r.drop(g).sort_values(ascending=False)
    print(g,'top20 raw r:', [(k,round(x,2)) for k,x in r.head(20).items()])
    for p in ['JOSD1','AUP1','STUB1','CHIC2','PCNX1','ZDHHC6','MMD','ATP13A1','TM2D3']:
        print('  ',p, round(r[p],3),'rank',list(r.index).index(p)+1)
    print('  Notch/gsec/UPR:',[(k,round(r[k],2)) for k in genes if k in r.index and k not in ['JOSD1','AUP1','STUB1','CHIC2']])
print(X[['JOSD1','AUP1','STUB1','CHIC2','PCNX1','ZDHHC6','MMD','ATP13A1']].corr().round(2))
