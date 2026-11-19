import re,sys
def sx(s):
    # tokenizer to nested lists
    tok=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s)
    st=[[]]
    for t in tok:
        if t=='(':st.append([])
        elif t==')':
            x=st.pop();st[-1].append(x)
        else: st[-1].append(t.strip('"') if t.startswith('"') else t)
    return st[0][0]
def find(n,k): return [c for c in n if isinstance(c,list) and c and c[0]==k]
def trace(path):
    t=sx(open(path).read())
    libs={}
    for ls in find(t,'lib_symbols'):
        for sym in find(ls,'symbol'):
            pins=[]
            def walk(n):
                for c in n:
                    if isinstance(c,list):
                        if c and c[0]=='pin' and len(c)>3 and isinstance(c[3],list) and c[3][0]=='at':
                            at=c[3];name=[x for x in c if isinstance(x,list) and x[0]=='name'][0][1]
                            num=[x for x in c if isinstance(x,list) and x[0]=='number'][0][1]
                            pins.append((float(at[1]),float(at[2]),float(at[3]) if len(at)>3 else 0,name,num,c[1]))
                        else: walk(c)
            walk(sym);libs[sym[1]]=pins
    P={} ;par={}
    def f(a):
        par.setdefault(a,a)
        while par[a]!=a:
            par[a]=par[par[a]];a=par[a]
        return a
    def u(a,b): par[f(a)]=f(b)
    R=lambda v:(round(v[0],2),round(v[1],2))
    wires=[]
    for w in find(t,'wire'):
        pts=find(w,'pts')[0]; xy=[R((float(p[1]),float(p[2]))) for p in pts[1:]]
        wires.append(xy); u(xy[0],xy[1])
    junc=[R((float(find(j,'at')[0][1]),float(find(j,'at')[0][2]))) for j in find(t,'junction')]
    for j in junc: f(j)
    # T connections: any wire interior containing a point that's junction or endpoint
    allpts=set(par)
    def on(w,p):
        (x1,y1),(x2,y2)=w;x,y=p
        if abs((x2-x1)*(y-y1)-(y2-y1)*(x-x1))>0.02:return False
        return min(x1,x2)-.01<=x<=max(x1,x2)+.01 and min(y1,y2)-.01<=y<=max(y1,y2)+.01
    labels=[]
    for l in find(t,'label')+find(t,'global_label'):
        a=find(l,'at')[0];labels.append((l[1],R((float(a[1]),float(a[2])))));f(R((float(a[1]),float(a[2]))))
    pinpts=[]
    for s in find(t,'symbol'):
        if len(s)<2 or not isinstance(s[1],list) or s[1][0]!='lib_id':continue
        lid=s[1][1];at=find(s,'at')[0];x0,y0=float(at[1]),float(at[2]);ang=float(at[3]) if len(at)>3 else 0
        mir=find(s,'mirror')
        props={p[1]:p[2] for p in find(s,'property')}
        ref=props.get('Reference')
        for (px,py,pa,name,num,ptype) in libs[lid]:
            import math
            a=math.radians(ang);rx=px*math.cos(a)-py*math.sin(a);ry=px*math.sin(a)+py*math.cos(a)
            if mir and mir[0][1]=='x': ry=-ry
            if mir and mir[0][1]=='y': rx=-rx
            p=R((x0+rx,y0-ry));f(p);pinpts.append((p,ref,num,name,props.get('Value'),lid))
    nc=[R((float(find(n,'at')[0][1]),float(find(n,'at')[0][2]))) for n in find(t,'no_connect')]
    for p in list(par):
        for w in wires:
            if on(w,p) and p not in w: 
                if p in junc or any(p==pp[0] for pp in pinpts): u(p,w[0])
    nets={}
    for p,ref,num,name,val,lid in pinpts:
        nets.setdefault(f(p),[]).append(f"{ref}.{num}[{name}]"+("(NC)" if p in nc else "")+(f"<{val}>" if lid.startswith('power') else ""))
    for l,p in labels: nets.setdefault(f(p),[]).append("LABEL:"+l)
    for k,v in sorted(nets.items(),key=lambda kv:str(kv[1])): print(k,v)
trace(sys.argv[1])
