"""Run python analysis.py. Requires numpy, matplotlib, Pillow.
Fits and plots are reproduced from 数据/measurements.csv; blanks are never interpolated.
"""
from pathlib import Path
import csv, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'代码'/'数据'; FIG=ROOT/'图片'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':['SimSun','Times New Roman'],'mathtext.fontset':'stix','axes.unicode_minus':False,'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':360})
groups=['X','Y','M']; labels={'X':'横向电偏转','Y':'纵向电偏转','M':'磁偏转'}
xlabels={'X':r'偏转电压 $U_{dx}$ / V','Y':r'偏转电压 $U_{dy}$ / V','M':r'励磁电流 $I_m$ / mA'}
colors={1000:'#254b77',900:'#9b5a21',800:'#277359'}; markers={1000:'o',900:'s',800:'^'}
rows=list(csv.DictReader((DATA/'measurements.csv').open(encoding='utf-8-sig')))
result={'fits':{},'comparisons':{},'method':'OLS D=s*x+b; inverse OLS checked separately','missing_points':[r for r in rows if not r['reading']],'n_observed':sum(bool(r['reading']) for r in rows)}; series={}
for g in groups:
 for u in [1000,900,800]:
  rr=[r for r in rows if r['group']==g and int(r['U2_V'])==u and r['reading']]
  x=np.array([float(r['reading']) for r in rr]); y=np.array([float(r['D_mm']) for r in rr]); n=len(x)
  xm=x.mean(); ym=y.mean(); sxx=((x-xm)**2).sum(); sxy=((x-xm)*(y-ym)).sum()
  s=float(sxy/sxx); b=float(ym-s*xm); residual=y-s*x-b; sse=float(residual@residual); sd=float(np.sqrt(sse/(n-2)))
  se=float(sd/np.sqrt(sxx)); be=float(sd*np.sqrt(1/n+xm*xm/sxx)); r2=float(1-sse/((y-ym)**2).sum())
  s0=float((x@y)/(x@x)); inv=float(((y-ym)**2).sum()/sxy); k=s*(u if g!='M' else math.sqrt(u))
  common=12 if g!='M' else 9; xl=float(x[y==-common][0]); xh=float(x[y==common][0]); chord=2*common/(xh-xl)
  pairs=[]
  for d in sorted(y[y>0]):
   if np.any(y==-d):
    xp=float(x[y==d][0]); xn=float(x[y==-d][0]); pairs.append({'D_mm':float(d),'reading_center':(xp+xn)/2,'half_span':(xp-xn)/2})
  f={'n':n,'slope':s,'intercept':b,'slope_se':se,'intercept_se':be,'r2':r2,'residual_sd_mm':sd,'max_residual_mm':float(max(abs(residual))),
     'through_origin_slope':s0,'inverse_fit_slope':inv,'inverse_difference_pct':(inv/s-1)*100,'constant':k,'constant_se':se*(u if g!='M' else math.sqrt(u)),
     'slope_mm_per_A':s*1000 if g=='M' else s,'fitted_points':{'x1':float(x.min()),'D1':s*float(x.min())+b,'x2':float(x.max()),'D2':s*float(x.max())+b},
     'measured_chord':chord,'pairs':pairs,'Sxx':float(sxx),'Sxy':float(sxy),'sum_x':float(x.sum()),'sum_D':float(y.sum()),'SSE':sse}
  key=f'{g}{u}'; result['fits'][key]=f; series[key]=(x,y,residual)
for g in groups:
 fs=[result['fits'][f'{g}{u}'] for u in [1000,900,800]]; ks=np.array([f['constant'] for f in fs]); mean=float(ks.mean())
 actual=fs[2]['slope']/fs[0]['slope']; theory=1.25 if g!='M' else math.sqrt(1.25)
 result['comparisons'][g]={'mean_constant':mean,'range_pct':float((ks.max()-ks.min())/mean*100),'ratio_800_1000':actual,'theory_ratio':theory,'ratio_deviation_pct':(actual/theory-1)*100,'origin_change_max_pct':max(abs(f['through_origin_slope']/f['slope']-1)*100 for f in fs)}
e=1.602189e-19; m=9.10953e-31; speed=math.sqrt(2*e*1000/m); bg=50e-6; length=.10; radius=m*speed/(e*bg)
result['earth_example']={'U2_V':1000,'B_T':bg,'path_m':length,'speed_m_s':speed,'speed_1e7_m_s':speed/1e7,'radius_m':radius,'D_mm':radius*(1-math.cos(length/radius))*1000,'angle_rad':length/radius,'a_m_s2':e*speed*bg/m}
(DATA/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for g,name in [('X','01_横向电偏转'),('Y','02_纵向电偏转'),('M','03_磁偏转')]:
 fig,ax=plt.subplots(figsize=(6.1,4.15),layout='constrained')
 for u in [1000,900,800]:
  key=f'{g}{u}'; x,y,_=series[key]; f=result['fits'][key]; ax.scatter(x,y,color=colors[u],marker=markers[u],s=32,label=f'{u} V 测量'); xx=np.linspace(x.min(),x.max(),120); ax.plot(xx,f['slope']*xx+f['intercept'],color=colors[u],lw=1.3,label=f'{u} V 拟合')
 ax.set(xlabel=xlabels[g],ylabel=r'偏转量 $D$ / mm',title=labels[g]+'的测量与线性拟合'); ax.grid(alpha=.23); ax.legend(ncol=2,fontsize=9); fig.savefig(FIG/(name+'.png')); plt.close(fig)
for mode,filename in [('residual','04_拟合残差.png'),('constant','05_灵敏度标度检验.png'),('symmetry','06_正负方向对称性.png')]:
 fig,axs=plt.subplots(3,1,figsize=(6.1,7.3),layout='constrained')
 for g,ax in zip(groups,axs):
  if mode=='residual':
   for u in [1000,900,800]:
    x,y,res=series[f'{g}{u}']; ax.scatter(x,res,c=colors[u],marker=markers[u],s=27,label=f'{u} V')
   ax.axhline(0,color='black',lw=.7); ax.set(xlabel=xlabels[g],ylabel='残差 / mm')
  elif mode=='constant':
   us=np.array([800,900,1000]); fs=[result['fits'][f'{g}{u}'] for u in us]; mean=result['comparisons'][g]['mean_constant']; ax.errorbar(us,[f['constant']/mean for f in fs],yerr=[f['constant_se']/mean for f in fs],fmt='o',capsize=4,color=colors[1000],label='常数及回归标准误'); ax.axhline(1,color='gray',ls='--',lw=1,label='平均值'); ax.set(xlabel=r'加速电压 $U_2$ / V',ylabel='常数 / 平均值'); ax.set_xticks(us)
  else:
   for u in [1000,900,800]:
    pp=result['fits'][f'{g}{u}']['pairs']; ax.plot([p['D_mm'] for p in pp],[p['reading_center'] for p in pp],marker=markers[u],c=colors[u],lw=1,label=f'{u} V')
   ax.axhline(0,color='gray',lw=.7); ax.set(xlabel=r'对称偏转幅度 $|D|$ / mm',ylabel='电流中心 / mA' if g=='M' else '电压中心 / V')
  ax.set_title(labels[g]); ax.grid(alpha=.22)
  if mode!='residual': ax.legend(ncol=3 if mode!='constant' else 1,fontsize=9)
 if mode=='residual': fig.legend(*axs[0].get_legend_handles_labels(),loc='outside upper center',ncol=3,fontsize=10)
 fig.savefig(FIG/filename); plt.close(fig)
for k,f in result['fits'].items(): print(f"{k}: n={f['n']}, s={f['slope']:.7f}, b={f['intercept']:.5f}, R2={f['r2']:.6f}, se={f['slope_se']:.7f}, K={f['constant']:.5f}")
print(json.dumps(result['comparisons'],ensure_ascii=False))
