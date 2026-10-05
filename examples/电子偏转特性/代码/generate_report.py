"""Assemble the editable report using the supplied repository template.
Run analysis.py first, then python generate_report.py --work-dir PATH.
The transient assembly JSON stays outside the final deliverable directory.
"""
from pathlib import Path
import argparse, csv, json, tempfile
import build_report
P=Path(__file__).resolve().parent; ROOT=P.parent
parser=argparse.ArgumentParser()
parser.add_argument('--work-dir',type=Path,help='Directory for temporary assembly files')
parser.add_argument('--output',type=Path,help='Output DOCX; defaults to the supplied report path')
parser.add_argument('--source-pages',type=Path,nargs='*',default=[],help='Optional original lecture page images for later review')
args=parser.parse_args()
source_pages=[p.resolve() for p in args.source_pages]
for page in source_pages:
    if not page.is_file():
        parser.error(f'Source page does not exist: {page}')
work=(args.work_dir or Path(tempfile.mkdtemp(prefix='physics-report-'))).resolve(); work.mkdir(parents=True,exist_ok=True)
R=json.loads((P/'数据/results.json').read_text(encoding='utf-8')); S={str(i):[] for i in range(1,9)}
def sub(a,b):return {'sub':[a,b]}
def sup(a,b):return {'sup':[a,b]}
def frac(a,b):return {'frac':[a,b]}
def seq(*a):return {'seq':[x for x in a if not isinstance(x,str) or x.strip()]}
def sqrt(a):return {'sqrt':a}
def im(x):return '{{math:'+json.dumps(x,ensure_ascii=False)+'}}'
def rv(key,fmt='.5f'):return '{{result:r.'+key+':'+fmt+'}}'
def tx(sec,s):S[str(sec)].append({'text':s})
def hd(sec,s):S[str(sec)].append({'heading':{'text':s,'level':2}})
def eq(sec,s):S[str(sec)].append({'equation':s})
def tb(sec,title,headers,rows,note=None):
 v={'caption':title,'headers':headers,'rows':rows}
 if note:v['note']=note
 S[str(sec)].append({'table':v})
def fg(sec,name,caption,tall=False,note=None):
 v={'path':str(ROOT/'图片'/name),'caption':caption,'width_inches':5.2,'max_height_inches':6.25 if tall else 3.3}
 if note:v['note']=note
 S[str(sec)].append({'figure':v})
U2=sub('U','2'); Udx=sub('U','dx'); Udy=sub('U','dy'); Im=sub('I','m'); ex=sub('ε','x'); ey=sub('ε','y'); dm=sub('δ','m')

tx(1,'本实验利用电子束在横向电场和磁场中的偏转，测量不同加速电压下的偏转特性。通过横向、纵向电偏转及磁偏转三组测量，求出偏转曲线的斜率，分析加速电压对偏转灵敏度的影响。')
tx(1,'了解电子枪、栅极、聚焦阳极、加速阳极、偏转板及荧光屏的作用，掌握辉度、聚焦与光点调零的基本方法；将电场力、洛伦兹力与运动轨迹联系起来，区分电偏转和磁偏转对电子速度的不同依赖。')
tx(1,'以正、负两个偏转方向的数据检查线性和对称性，结合残差与标度常数判断理论近似的适用程度。认识电子束控制在示波器、电子光学及显像系统中的应用。')

hd(2,'2.1 示波管结构与电子加速')
tx(2,'阴极受热发射电子，栅极调节进入电子枪的电子数目，聚焦阳极形成静电透镜，使电子束在荧光屏上形成较小光点；第二阳极提供加速电压。两组相互垂直的偏转板分别控制水平与竖直位移，荧光屏把电子束落点转换为可观察的光点。')
tx(2,'以下用正数电子电量表示电荷绝对值，电子实际电荷为其负值。忽略发射初速度与加速过程中的能量损失，电场所做的功转化为电子动能。')
eq(2,seq(frac(seq('m',sup('v','2')),'2'),'=e',U2,'，v=',sqrt(frac(seq('2e',U2),'m'))))
tx(2,'在本实验电压范围内，电子速率远小于光速，采用非相对论运动方程可获得适用的近似。加速电压增大使电子通过偏转区域的时间缩短，是灵敏度下降的主要原因。')
hd(2,'2.2 电偏转轨迹与灵敏度')
tx(2,'设偏转板长度为 '+im('l')+'，板间距为 '+im('d')+'，偏转板出口到荧光屏的距离为 '+im('L')+'。偏转板内电场近似均匀，板外电场忽略，电子纵向速度保持近似恒定。在偏转板内，电子横向作匀加速运动；离开板后沿出口速度方向作直线运动。')
eq(2,seq('E=',frac(sub('U','d'),'d'),'，t=',frac('l','v'),'，|',sub('a','y'),'|=',frac('eE','m')))
eq(2,seq(sub('y','1'),'=',frac(seq('eE',sup('l','2')),seq('2m',sup('v','2'))),'=',frac(seq(sub('U','d'),sup('l','2')),seq('4',U2,'d'))))
eq(2,seq('tanθ=',frac(seq('eEl'),seq('m',sup('v','2'))),'=',frac(seq(sub('U','d'),'l'),seq('2',U2,'d'))))
tx(2,'屏上总偏转量是板内横向位移与板外漂移位移之和。取正偏转方向与实际记录的电压极性对应，得到有符号的线性关系；电子所受力的方向仍与电场方向相反。')
eq(2,seq('D=',sub('y','1'),'+Ltanθ=',frac(seq(sub('U','d'),'l'),seq('2',U2,'d')),'(', 'L+',frac('l','2'),')'))
eq(2,seq('ε=',frac('ΔD',seq('Δ',sub('U','d'))),'=',frac('l','2d'),'(', 'L+',frac('l','2'),')',frac('1',U2),'=',frac(sub('k','e'),U2)))
tx(2,'电偏转灵敏度的单位为毫米每伏。横向与纵向偏转板所处位置及几何参数不同，其灵敏度可有差别，不要求两方向的斜率相等；对于同一组偏转板，在几何参数保持不变时，灵敏度与加速电压成反比。')
hd(2,'2.3 磁偏转轨迹与灵敏度')
tx(2,'电子以速度垂直进入横向磁场，洛伦兹力始终与瞬时速度垂直，只改变运动方向而不改变速率。在均匀磁场区域内电子沿圆弧运动，离开磁场后沿圆弧切线运动。设磁场区域有效长度为 '+im(sub('l','m'))+'，出口到荧光屏的距离为 '+im(sub('L','m'))+'。')
eq(2,seq('evB=',frac(seq('m',sup('v','2')),'R'),'，R=',frac('mv','eB'),'，sinθ=',frac(sub('l','m'),'R')))
eq(2,seq('D=R(1−cosθ)+',sub('L','m'),'tanθ'))
tx(2,'当偏转角较小时，正弦和正切可近似为偏转角，余弦保留到二阶项；圆弧内的偏转也必须计入，不能只计算离开磁场后的漂移。磁场与励磁电流的比例系数用 '+im('K')+' 表示，其数值由线圈几何结构及匝数决定。')
eq(2,seq('D≈',frac(seq('eB',sub('l','m')),'mv'),'(',sub('L','m'),'+',frac(sub('l','m'),'2'),')，B=K',Im))
eq(2,seq('D≈K',sub('l','m'),'(',sub('L','m'),'+',frac(sub('l','m'),'2'),')',sqrt(frac('e','2m')),frac(Im,sqrt(U2))))
eq(2,seq(dm,'=|',frac('ΔD',seq('Δ',Im)),'|=',frac(sub('k','m'),sqrt(U2))))
tx(2,'磁偏转灵敏度可用毫米每安培或毫米每毫安表示。同一偏转量所需励磁电流随加速电压的平方根增加。小角度近似、磁场有效长度稳定和磁场对励磁电流的线性，是检验这一标度关系的前提。')
hd(2,'2.4 两类偏转的物理区别')
tx(2,'电场力在相同偏转电压下不依赖电子速度，板内偏转主要随作用时间的平方变化，因此电偏转灵敏度与加速电压成反比。磁场力本身随电子速度增大，部分抵消作用时间缩短的效果，所以磁偏转灵敏度仅与加速电压的平方根成反比。两种偏转均应在加速电压降低时变得更灵敏，但变化幅度并不相同。')

tx(3,'实验装置为电子束实验仪、示波管、横向和纵向偏转板、磁偏转线圈及连接导线。仪器含阳极电压调节、电聚焦调节、辉度调节、偏转电压测量、励磁电流测量与两方向调零功能。')
tb(3,'表1 仪器与测量用途',['组成','测量或调节用途'],[['电子束实验仪','提供加速、聚焦、辉度及偏转所需电源'],['示波管和荧光屏','观察光点位置并读出偏转量'],['偏转电压表','测量两组偏转板的电压'],['磁偏转电流表和线圈','测量励磁电流并产生横向磁场'],['连接导线和换向接头','完成并联电压测量、串联电流测量及磁场换向']])
tx(3,'加速电压采用 1000、900、800 V 三档；电偏转位置取 −16 至 16 mm、间隔 4 mm；磁偏转用于处理的有效位置为 −9 至 9 mm、间隔 3 mm。读取位置时以光点中心为准，减少光斑尺寸和视差造成的判断差异。')

hd(4,'4.1 预热聚焦与光点调零')
tx(4,'接通电源，选择电子束工作模式，调节适当辉度，再调节聚焦，使荧光屏上光点尽量细小。辉度不宜过大，以免影响位置判读或损伤荧光屏。')
tx(4,'将水平偏转输出接至电偏转电压表，先调节水平偏转电压为零，再调节水平调零旋钮使光点位于竖直中线；按相同方法调节竖直方向，使零电压时光点位于屏中心。改变阳极电压后重新检查聚焦及零位。')
hd(4,'4.2 测量横向和纵向电偏转')
tx(4,'给定第一档加速电压，将电压表并联在待测方向的偏转输出端。依次调节偏转旋钮，使光点中心落在规定位置，记录对应的偏转电压，保留电压和位移的正负号。')
tx(4,'对另一个方向重复测量，然后改变加速电压至其余两档，每一档分别记录两方向的数据。保持装置位置不变，注意调节后的读数稳定性；正、负位置均测量，避免仅凭单方向数据判断灵敏度。')
hd(4,'4.3 测量磁偏转')
tx(4,'将磁偏转电源、磁偏转电流表与磁偏转线圈串联。令励磁电流为零，检查光点中心与屏中心重合；给定加速电压后调节励磁电流，记录正方向各偏转位置对应的电流。')
tx(4,'先将励磁电流调为零，再交换线圈的连接方向，重新检查零位，测量反向偏转对应的电流，反向电流记为负值。其余两档加速电压按相同程序测量。避免带有较大电流时直接换线，减少换向瞬态和零位变化。')
tx(4,'完成测量后将调节量恢复至适当位置并关闭电源。后续处理保持每档加速电压独立，不把不同档的数据混为一条直线。')

tx(5,'记录位移与电压或电流的对应关系，电偏转电压以伏为单位，磁偏转励磁电流以毫安为单位。各组测量值按偏转位置列于下表。')
raw=list(csv.DictReader((P/'数据/measurements.csv').open(encoding='utf-8-sig')))
for g,num,name,var in [('X',2,'横向电偏转',Udx),('Y',3,'纵向电偏转',Udy),('M',4,'磁偏转',Im)]:
 ds=[-12,-9,-6,-3,0,3,6,9,12] if g=='M' else [-16,-12,-8,-4,0,4,8,12,16]
 rows=[]
 for d in ds:
  vals=[next(r['reading'] for r in raw if r['group']==g and int(r['U2_V'])==u and float(r['D_mm'])==d) for u in [1000,900,800]]
  rows.append([f'{d:.1f}']+vals)
 tb(5,f'表{num} {name}测量值',[im('D / mm')]+[im(seq(U2,f'={u} V，',var,' / '+('mA' if g=='M' else 'V'))) for u in [1000,900,800]],rows)

hd(6,'6.1 处理方法与单位')
tx(6,'分别在同一坐标系中绘制三档加速电压对应的位移与偏转电压曲线，以及位移与励磁电流曲线。横坐标为电压或电流，纵坐标为位移，因此直线斜率直接给出偏转灵敏度。使用带截距的最小二乘直线，以保留可能存在的零点偏移。')
eq(6,seq('D=sx+b，s=',frac(seq('Σ(',sub('x','i'),'−',sub('x','均'),')(',sub('D','i'),'−',sub('D','均'),')'),seq('Σ',sup(seq('(',sub('x','i'),'−',sub('x','均'),')'),'2'))),'，b=',sub('D','均'),'−s',sub('x','均')))
tx(6,'式中自变量依次为横向偏转电压、纵向偏转电压和励磁电流。电偏转斜率的单位是 mm/V，磁偏转斜率的单位是 mm/mA。磁偏转换算为 mm/A 时，数值乘以 1000。零点数据参与拟合，但不据此强迫所有曲线通过原点。')
eq(6,seq(dm,'[mm/A]=1000',dm,'[mm/mA]'))
tx(6,'按作图法的要求，从拟合直线上选取相距较远的两点，计算位移增量除以横坐标增量。选点取拟合线在观测区间两端的位置，避免使用相邻原始点放大读数波动。另计算原始数据在共同正、负端点间的弦斜率作交叉检查。')
eq(6,seq('s=',frac(seq(sub('D','B'),'−',sub('D','A')),seq(sub('x','B'),'−',sub('x','A')))))
hd(6,'6.2 横向电偏转灵敏度')
fg(6,'01_横向电偏转.png','图1 横向电偏转的三档测量与拟合')
tx(6,'三组散点均接近直线，800 V 曲线斜率最大。以 1000 V 为例，对全部九个点求和，得到横坐标离均差平方和及位移与电压的离均差乘积和：')
eq(6,seq(sub('S','xx'),'=',rv('fits.X1000.Sxx','.2f'),' ',sup('V','2'),'，',sub('S','xD'),'=',rv('fits.X1000.Sxy','.2f'),' V·mm'))
eq(6,seq(ex,'=',frac(rv('fits.X1000.Sxy','.2f'),rv('fits.X1000.Sxx','.2f')),'=',rv('fits.X1000.slope','.5f'),' mm/V，b=',rv('fits.X1000.intercept','.5f'),' mm'))
tx(6,'横向在 800 V 时截距为正，表明同一组数据整体存在零点偏移或正负方向不完全对称。带截距拟合能够区分平移和斜率变化，但不能自动消除随幅度变化的系统偏差。')
hd(6,'6.3 纵向电偏转灵敏度')
fg(6,'02_纵向电偏转.png','图2 纵向电偏转的三档测量与拟合')
tx(6,'纵向灵敏度也随加速电压降低而增大，在相同加速电压下均大于横向灵敏度。900 V 组在两端的残差相对较大，采用全部数据拟合可减少单一端点对结果的影响。')
hd(6,'6.4 磁偏转灵敏度')
fg(6,'03_磁偏转.png','图3 磁偏转的三档测量与拟合')
tx(6,'磁偏转每组使用七个测量点，位移覆盖 −9 至 9 mm。正、负励磁电流对应相反的偏转方向，三条拟合线斜率均为正。以 1000 V 为例，计算结果为：')
eq(6,seq(dm,'=',frac(rv('fits.M1000.Sxy','.2f'),rv('fits.M1000.Sxx','.2f')),'=',rv('fits.M1000.slope','.5f'),' mm/mA=',rv('fits.M1000.slope_mm_per_A','.2f'),' mm/A'))
tx(6,'减小加速电压使相同励磁电流对应更大的偏转。每档曲线的良好线性只检验固定加速电压下的响应关系，不能独立证明跨档的平方根标度关系。')
hd(6,'6.5 拟合参数与作图法计算汇总')
tb(6,'表5 各组直线拟合参数',['测量组',im(U2)+' / V','斜率','截距 / mm',im(sup('R','2'))],[[g,str(u),rv(f'fits.{g}{u}.slope','.5f'),rv(f'fits.{g}{u}.intercept','.4f'),rv(f'fits.{g}{u}.r2','.6f')] for g in ['X','Y','M'] for u in [1000,900,800]],'前六行斜率单位为毫米每伏，后三行单位为毫米每毫安。')
tx(6,'表6给出拟合线的两端选点。表中的横坐标和位移保留三位小数用于展示，斜率计算使用未舍入结果；因此用表中舍入数值手算时，末位可能略有差别。')
tb(6,'表6 拟合直线上两点求斜率',['组别',im(sub('x','A')),im(sub('D','A'))+' / mm',im(sub('x','B')),im(sub('D','B'))+' / mm','斜率'],[[f'{g} {u}',rv(f'fits.{g}{u}.fitted_points.x1','.3f'),rv(f'fits.{g}{u}.fitted_points.D1','.3f'),rv(f'fits.{g}{u}.fitted_points.x2','.3f'),rv(f'fits.{g}{u}.fitted_points.D2','.3f'),rv(f'fits.{g}{u}.slope','.5f')] for g in ['X','Y','M'] for u in [1000,900,800]],'电偏转横坐标单位为伏，磁偏转横坐标单位为毫安；两点来自拟合直线。')
tx(6,'例如横向 1000 V 的两点计算为：')
eq(6,seq(ex,'=',frac(seq(rv('fits.X1000.fitted_points.D2','.5f'),'−(',rv('fits.X1000.fitted_points.D1','.5f'),')'),seq('37−(−37)')),'=',rv('fits.X1000.slope','.5f'),' mm/V'))
tx(6,'用原始横向 1000 V 的正、负 12 mm 两点直接计算，得到 24/(28+27.5)=0.43243 mm/V，与全点拟合接近。纵向与磁偏转采用相同方法检查；原始端点弦斜率与全点拟合的差别反映局部读数波动及可能的非线性。')
tb(6,'表7 原始对称端点弦斜率对照',['组别','原始端点斜率','全点拟合斜率'],[[f'{g} {u}',rv(f'fits.{g}{u}.measured_chord','.5f'),rv(f'fits.{g}{u}.slope','.5f')] for g in ['X','Y','M'] for u in [1000,900,800]],'电偏转取正负十二毫米端点，磁偏转取正负九毫米端点；单位同表5。')
hd(6,'6.6 残差与回归精度')
eq(6,seq(sub('r','i'),'=',sub('D','i'),'−(s',sub('x','i'),'+b)，',sub('σ','r'),'=',sqrt(frac(seq('Σ',sup(sub('r','i'),'2')),'n−2')),'，',sub('u','s'),'=',frac(sub('σ','r'),sqrt(sub('S','xx')))))
tx(6,'回归斜率标准误由残差散布给出，描述既定线性模型和观测区间内斜率估计的统计精度。它不包含电压表、电流表校准误差、位置刻度误差、加速电压误差或零点漂移等全部测量影响，不能直接作为灵敏度的完整合成不确定度。')
tb(6,'表8 回归散布指标',['组别','斜率标准误','残差标准差 / mm','最大绝对残差 / mm'],[[f'{g} {u}',rv(f'fits.{g}{u}.slope_se','.5f'),rv(f'fits.{g}{u}.residual_sd_mm','.4f'),rv(f'fits.{g}{u}.max_residual_mm','.4f')] for g in ['X','Y','M'] for u in [1000,900,800]],'斜率标准误的单位与对应斜率相同。')
tx(6,'残差图显示纵向 900 V 组的散布较大；磁偏转 1000 V 组在负方向内侧和正方向内侧的残差有相反符号，提示正负响应的不对称及局部斜率差异。仅凭较高的决定系数，不能排除这些结构。')
tx(6,'实验以指定位置为目标，电压和电流同样存在读数误差。把电压或电流作为自变量的普通最小二乘是一种描述性拟合；对反向回归后斜率取倒数作检查，两种斜率的最大相对差为 0.353%，不足以解释后面的较大标度偏差。')
fg(6,'04_拟合残差.png','图4 三类偏转的拟合残差',True)

hd(7,'7.1 灵敏度随加速电压的变化')
tx(7,'三档加速电压下，横向电偏转灵敏度分别为 '+rv('fits.X1000.slope','.4f')+'、'+rv('fits.X900.slope','.4f')+'、'+rv('fits.X800.slope','.4f')+' mm/V；纵向分别为 '+rv('fits.Y1000.slope','.4f')+'、'+rv('fits.Y900.slope','.4f')+'、'+rv('fits.Y800.slope','.4f')+' mm/V；磁偏转分别为 '+rv('fits.M1000.slope_mm_per_A','.2f')+'、'+rv('fits.M900.slope_mm_per_A','.2f')+'、'+rv('fits.M800.slope_mm_per_A','.2f')+' mm/A。三类灵敏度均随加速电压降低而增加。')
tx(7,'电偏转理论预言，800 V 与 1000 V 的灵敏度之比为 1000/800=1.25；磁偏转理论预言该比值为两档加速电压比的平方根。实际比值及相对理论比例的偏差如下。')
tb(7,'表9 两档灵敏度比值与理论比例',['偏转类型','实测比值','理论比值','相对理论偏差 / %'],[[name,rv(f'comparisons.{g}.ratio_800_1000','.4f'),rv(f'comparisons.{g}.theory_ratio','.4f'),rv(f'comparisons.{g}.ratio_deviation_pct','.2f')] for g,name in [('X','横向电偏转'),('Y','纵向电偏转'),('M','磁偏转')]])
tx(7,'纵向电偏转的比值最接近反比关系，横向存在约 6.09% 的比例偏差；磁偏转比例偏差约为 15.91%。因此，本次数据支持灵敏度随加速电压增大而下降的趋势，但磁偏转数据尚不能在定量上充分支持严格的平方根反比关系。上述百分数是相对理论比例的偏差，不是仪器误差或合成不确定度。')
hd(7,'7.2 标度常数检验')
eq(7,seq(sub('k','ex'),'=',ex,U2,'，',sub('k','ey'),'=',ey,U2,'，',sub('k','m'),'=',dm,sqrt(U2)))
tb(7,'表10 三档标度常数',[im(U2)+' / V',im(sub('k','ex'))+' / mm',im(sub('k','ey'))+' / mm',im(seq(sub('k','m'),' / (mm·',sqrt('V'),'/mA)'))],[[str(u),rv(f'fits.X{u}.constant','.2f'),rv(f'fits.Y{u}.constant','.2f'),rv(f'fits.M{u}.constant','.4f')] for u in [1000,900,800]])
tx(7,'三档常数的极差相对于平均值，横向为 '+rv('comparisons.X.range_pct','.2f')+'%，纵向为 '+rv('comparisons.Y.range_pct','.2f')+'%，磁偏转为 '+rv('comparisons.M.range_pct','.2f')+'%。这一检验直接比较理论所要求的不变量，比观察三条直线是否都很直更能反映跨档标度关系。')
fg(7,'05_灵敏度标度检验.png','图5 三类偏转的归一化标度常数',True,'误差棒仅表示回归斜率标准误传播后的数值，不代表完整测量不确定度。')
tx(7,'纵向常数较稳定，横向 800 V 常数偏高，磁偏转常数随加速电压降低而明显升高。三个电压档及单次位置读数不足以独立拟合可靠的幂律指数，更不宜把趋势上的一致表述为对理论指数的精确验证。')
hd(7,'7.3 正负方向与零点偏移')
eq(7,seq(sub('x','中心'),'=',frac(seq('x(+D)+x(−D)'),'2')))
tx(7,'理想反对称测量中，同一偏转幅度对应的正、负电压或电流之和应为零。其平均值可以检查读数中心是否偏移；若中心随幅度变化，单一截距修正不能解释所有不对称。')
fg(7,'06_正负方向对称性.png','图6 正负偏转对应的电压或电流中心',True)
tx(7,'横向 800 V 的电压中心从约 −1.1 V 变化到 −2.0 V；磁偏转 1000 V 的电流中心依次约为 −2.5、−4.25、−2.0 mA。各组的中心变化不完全相同，可能与调零、换向、判读以及电路或场分布有关。仅凭当前数据，不能确定具体原因。')
tx(7,'强制通过原点的拟合与带截距拟合比较，斜率变化最大分别约为横向 0.473%、纵向 0.036%、磁偏转 0.096%。这说明去掉截距不足以消除磁偏转约 15.91% 的跨档比例偏差，也不能把偏差全部归因于恒定的零点位移。')
hd(7,'7.4 误差来源与改进')
tx(7,'光点大小和视差影响位置判读，指针表读数、调节后的稳定时间和阳极电压实际值影响电压与电流记录。改变加速电压后聚焦状态和零位可能变化，正负方向换接也可能产生新的零点或接触差异。磁场边缘分布及电子束在场中的有效作用长度，可能使简单均匀场模型与实际装置不同。')
tx(7,'改进时，应优先复测磁偏转各档的正、负方向，记录每次换向前后的零点和实际阳极电压；以相同位移范围重复扫描，检验迟滞、漂移及重复性。其次保持辉度适中、光斑细小，统一读数方向与等待时间，采用尽量宽但仍符合近似条件的偏转范围。')
tx(7,'如需给出完整测量不确定度，应记录仪表量程、分度或分辨率、准确度及位置判读限，并进行重复测量，再分别评估随机散布与仪器校准等分量。小角度近似和均匀场模型引入的系统影响应单独讨论，不应用残差标准差替代所有误差。')

hd(8,'8.1 电偏转灵敏度与加速电压的关系')
tx(8,'对于同一组偏转板，理论上电偏转灵敏度与加速电压成反比，其乘积为由几何结构决定的常数。本实验两方向均表现为加速电压越低，灵敏度越大；纵向的常数变化较小，横向 800 V 组偏离较明显。结论应分别区分理论关系、观测趋势和定量一致程度。')
eq(8,seq('ε=',frac(sub('k','e'),U2),'，ε',U2,'=',sub('k','e')))
hd(8,'8.2 偏转量与光点亮度的关系')
tx(8,'在加速电压、偏转电压或磁场以及几何条件保持不变时，理想单电子轨迹不依赖束流强度，因此单独调节控制电子数目的辉度，原则上不改变光点中心的偏转量。亮度主要由到达荧光屏的电子数及每个电子的能量共同决定。')
tx(8,'实际装置中，过高辉度可能引起空间电荷效应、焦斑扩大或视觉判读偏差，并可能伴随电极工作状态变化。如果亮度变化来自加速电压改变，偏转灵敏度会同时变化，不能据此认定亮度直接导致偏转变化。因此比较亮度影响时，必须保持加速电压和偏转条件不变。')
hd(8,'8.3 地磁场对电子运动的影响')
tx(8,'地磁场虽然较弱，电子的荷质比很大且速率较高，仍会受到可观的洛伦兹力。决定偏转的是地磁场中垂直于电子速度的分量；平行分量不产生该方向的磁力。地表磁场常见强度量级为 25 至 65 μT，是否可以忽略还取决于电子束路程和测量精度。')
tx(8,'作数量级估算，取加速电压 1000 V，假设横向磁场分量为 50 μT、在该场中运动路程为 0.10 m。这些量用于说明效应的可能大小。由能量关系和圆轨道半径公式得：')
eq(8,seq('v=',rv('earth_example.speed_1e7_m_s','.3f'),'×',sup('10','7'),' m/s，R=',frac('mv','eB'),'≈',rv('earth_example.radius_m','.2f'),' m'))
eq(8,seq('D≈',frac(sup(sub('L','总'),'2'),'2R'),'≈',rv('earth_example.D_mm','.2f'),' mm'))
tx(8,'这一毫米量级偏移与本实验位置刻度相比并不必然很小，不能笼统忽略。固定方向、固定加速电压下，静态地磁影响可部分体现为零点偏移并通过调零抵消；改变仪器朝向或加速电压后，该补偿未必仍然适用。较精密电子光学系统宜采用磁屏蔽或补偿线圈，并控制邻近带电导线和磁性物体。')
hd(8,'8.4 电聚焦与电子光学拓展')
tx(8,'聚焦阳极之间的非均匀电场可形成静电透镜，使发散电子束在荧光屏处会聚。调节聚焦电压改变电子束包络，主要影响光斑尺寸；加速电压改变后应重新聚焦，以减少位置判读误差。聚焦清晰和偏转灵敏度高是不同性能指标，应分别调节和检验。')
tx(8,'本实验观察的是电子束的宏观轨迹，可由经典力学和电磁学解释。电子的波动性可用德布罗意关系描述，但本次偏转数据本身不是电子衍射或干涉证据。电子显微镜利用较短电子波长并结合电子透镜成像，示波器则利用电子束偏转把电信号转换为空间位置。')
eq(8,seq('λ=',frac('h','mv'),'=',frac('h',sqrt(seq('2me',U2)))))

payload={'experiment':'电子偏转特性的测量','questions_provided':True,'sections':S,
 'template_file':str(P/'模板/实验报告模板.docx'),'data_photos':[str(ROOT/'图片/原始实验数据.jpg')],
 'visual_sources':[str(p) for p in source_pages],
 'data_files':[str(P/'数据/measurements.csv')],'result_files':{'r':str(P/'数据/results.json')},'missing':[],
 'explanation_notes':['磁偏转正负十二毫米处六个空格未测，保持空白；现有七点每组足以拟合。','Y轴1000V正16mm=21.3V、800V正16mm=17V由用户确认。','无仪器准确度和重复测量，回归标准误不作为完整测量不确定度。']}
inp=work/'report.json'; inp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
output=(args.output or ROOT/'电子偏转特性_实验报告.docx').resolve()
output.parent.mkdir(parents=True,exist_ok=True)
audit=build_report.build(payload,output,None,False)
(work/'assembly-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('Report:',output); print('Input:',inp); print('status:',audit['status'],'equations:',audit.get('equations'),'images:',audit.get('images'))
