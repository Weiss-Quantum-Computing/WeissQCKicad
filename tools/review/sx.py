import re
def parse(s):
    tok=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+',s)
    st=[[]]
    for k in tok:
        if k=='(': st.append([])
        elif k==')':
            x=st.pop(); st[-1].append(x)
        else: st[-1].append(k[1:-1] if k.startswith('"') else k)
    return st[0][0]
def kids(n,name): return [c for c in n if isinstance(c,list) and c and c[0]==name]
def kid(n,name):
    k=kids(n,name); return k[0] if k else None
def val(n,name,d=''):
    k=kid(n,name); return k[1] if k and len(k)>1 else d
