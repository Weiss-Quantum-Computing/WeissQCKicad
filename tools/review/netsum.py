import sys,os,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sx import *
p=parse(open(sys.argv[1]).read())
def natkey(s): return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',s)]
print('## COMPONENTS (ref | value | footprint | lib part | sheet)')
comps=kids(kid(p,'components') or [], 'comp')
for c in sorted(comps,key=lambda c:natkey(val(c,'ref'))):
    ls=kid(c,'libsource'); sp=kid(c,'sheetpath')
    props={q[1][1]:q[2][1] for q in kids(c,'property') if len(q)>2 and isinstance(q[1],list) and isinstance(q[2],list) and len(q[2])>1}
    extra=' '.join(f'{k}={v}' for k,v in props.items() if k.lower() in('dnp','sim.device','tolerance','voltage','power','mpn','manufacturer_part_number','digi-key_pn'))
    print(f"{val(c,'ref')} | {val(c,'value')} | {val(c,'footprint')} | {val(ls,'part') if ls else ''} | {val(sp,'names') if sp else ''} {extra}")
print('\n## NETS (net : ref.pin[pin name|pin type], ...)')
for n in kids(kid(p,'nets') or [],'net'):
    nodes=[]
    for nd in kids(n,'node'):
        nodes.append(f"{val(nd,'ref')}.{val(nd,'pin')}[{val(nd,'pinfunction')}|{val(nd,'pintype')}]")
    print(val(n,'name'),':',', '.join(sorted(nodes,key=natkey)))
