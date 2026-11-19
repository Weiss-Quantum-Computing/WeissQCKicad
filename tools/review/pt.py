import re,sys
def parse(fn):
    comps={};nets={}
    sec=None
    for l in open(fn):
        l=l.rstrip('\n')
        if l.startswith('## COMP'): sec='c';continue
        if l.startswith('## NETS'): sec='n';continue
        if sec=='c' and '|' in l:
            p=[x.strip() for x in l.split('|')]; comps[p[0]]=(p[1],p[2],p[3])
        elif sec=='n' and ' : ' in l:
            n,rest=l.split(' : ',1)
            nets[n]=sorted(re.findall(r'([A-Za-z_0-9]+)\.(\w+)\[',rest))
    return comps,nets
a,b=sys.argv[1:3]
ca,na=parse(a);cb,nb=parse(b)
print('comps',len(ca),len(cb))
for r in sorted(set(ca)|set(cb)):
    if ca.get(r)!=cb.get(r): print('COMP',r,ca.get(r),'->',cb.get(r))
ga={frozenset(p):n for n,p in na.items() if len(p)>1}
gb={frozenset(p):n for n,p in nb.items() if len(p)>1}
for g in ga:
    if g not in gb: print('A-only',ga[g],sorted(g))
for g in gb:
    if g not in ga: print('B-only',gb[g],sorted(g))
