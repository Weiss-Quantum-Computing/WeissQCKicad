import re,sys
def parse(fn):
    t=open(fn,errors='ignore').read()
    comps={}
    for m in re.finditer(r'\(comp \(ref "?([^")\s]+)"?\)\s*\(value "([^"]*)"\)(?:\s*\(footprint "([^"]*)"\))?',t):
        comps[m.group(1)]=(m.group(2),m.group(3))
    nets={}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)',t,re.S):
        pins=sorted(re.findall(r'\(node \(ref "?([^")\s]+)"?\) \(pin "?([^")\s]+)"?',m.group(2)))
        nets[m.group(1)]=pins
    return comps,nets
def pinmap(nets):
    d={}
    for n,p in nets.items():
        for r,pin in p: d[(r,pin)]=n
    return d
def groups(nets):
    return {frozenset(p) for p in nets.values() if len(p)>1}
a,b=sys.argv[1:3]
ca,na=parse(a);cb,nb=parse(b)
print(len(ca),len(cb),len(na),len(nb))
for r in sorted(set(ca)|set(cb)):
    if ca.get(r,(None,))[0]!=cb.get(r,(None,))[0]: print('VAL',r,ca.get(r),cb.get(r))
ga,gb=groups(na),groups(nb)
for g in sorted(ga-gb,key=lambda s:sorted(s)): print('ONLY A',sorted(g))
for g in sorted(gb-ga,key=lambda s:sorted(s)): print('ONLY B',sorted(g))
