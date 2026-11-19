import sys,os,re,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sx import *
p=parse(open(sys.argv[1]).read())
print('## COPPER LAYERS:',[(l[1],l[2]) for l in (kid(p,'layers') or [])[1:] if isinstance(l,list) and 'Cu' in str(l[1])])
su=kid(kid(p,'setup') or [],'stackup')
if su:
    for l in kids(su,'layer'): print('  stackup',l[1],[c for c in l[2:] if isinstance(c,list) and c[0] in('type','thickness')])
nets={n[1]:(n[2] if len(n)>2 else '') for n in kids(p,'net')}
xs=[];ys=[]
for t in ('gr_rect','gr_line','gr_arc','gr_circle','gr_poly'):
    for g in kids(p,t):
        if val(g,'layer')=='Edge.Cuts':
            for k in ('start','end','mid','center'):
                q=kid(g,k)
                if q: xs.append(float(q[1])); ys.append(float(q[2]))
if xs: print(f'## BOARD OUTLINE bbox: {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} mm')
else: print('## BOARD OUTLINE: none found on Edge.Cuts')
print('\n## FOOTPRINTS (ref | footprint | x y rot | side | pads: num:net@(relx,rely) size [drill])')
for fp in kids(p,'footprint'):
    ref=''
    for q in kids(fp,'property'):
        if q[1]=='Reference': ref=q[2]
    if not ref:
        for q in kids(fp,'fp_text'):
            if q[1]=='reference': ref=q[2]
    at=kid(fp,'at'); lay=val(fp,'layer')
    pads=[]
    for pad in kids(fp,'pad'):
        n=kid(pad,'net'); a=kid(pad,'at'); sz=kid(pad,'size'); dr=kid(pad,'drill')
        pads.append(f"{pad[1]}:{(n[2] if n and len(n)>2 else '-')}@({a[1]},{a[2]}) {sz[1]}x{sz[2]}"+(f" d{dr[1]}" if dr and len(dr)>1 else ''))
    if len(pads)>40: pads=pads[:40]+['...(%d pads total)'%len(kids(fp,'pad'))]
    print(f"{ref} | {fp[1]} | {' '.join(at[1:])} | {lay} | "+'; '.join(pads))
w=collections.defaultdict(collections.Counter)
for s in kids(p,'segment')+kids(p,'arc'):
    w[nets.get(val(kid(s,'net') and s,'net'),'?')][(val(s,'width'),val(s,'layer'))]+=1
print('\n## TRACK WIDTHS PER NET (width mm, layer): segment count')
for n in sorted(w): print(' ',n or '(no net)',dict(w[n]))
print('\n## VIAS:',dict(collections.Counter((val(v,'size'),val(v,'drill')) for v in kids(p,'via'))))
print('## ZONES:')
for z in kids(p,'zone'):
    print('  net',repr(val(z,'net_name')),'layers',(kid(z,'layer') or kid(z,'layers') or ['',''])[1:],'filled polygons',len(kids(z,'filled_polygon')),'keepout' if kid(z,'keepout') else '')
print('## SILK/USER TEXT:')
for g in kids(p,'gr_text'): print('  ',repr(g[1]),val(g,'layer'))
