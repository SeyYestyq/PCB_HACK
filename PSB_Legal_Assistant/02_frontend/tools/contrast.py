"""WCAG 2.2 contrast check for docs/04-brand tokens. Run: python3 tools/contrast.py"""
def L(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def C(a,b):
    la,lb=sorted([L(a),L(b)],reverse=True); return (la+0.05)/(lb+0.05)
PAIRS=[("ink on surface","3E3E59","FFFFFF",4.5),("ink on canvas","3E3E59","F8F8FC",4.5),("ink-2 on surface","5C5C73","FFFFFF",4.5),
("ink-2 on surface-2","5C5C73","F0F0F7",4.5),("ink-3 on surface","646872","FFFFFF",4.5),("on-accent","FFFFFF","2B2C84",4.5),
("on-accent hover","FFFFFF","22236B",4.5),("accent on tint","2B2C84","EDEDF7",4.5),("ink on evidence","3E3E59","E4E4F3",4.5),
("grounded badge","4E621C","EEF2E4",4.5),("attention badge","9A3A0E","FDF0E9",4.5),("neutral badge","646872","F0F0F7",4.5),
("danger badge","BB3E45","FBECEC",4.5),("danger on surface","BB3E45","FFFFFF",4.5),("on-danger","FFFFFF","BB3E45",4.5),
("control border","8D8DA6","FFFFFF",3.0),("orange 172C non-text","EA5614","FFFFFF",3.0),
("dark ink","E8E8F2","12132B",4.5),("dark ink-2","B4B4CC","12132B",4.5),("dark accent","A9AAF0","12132B",4.5),
("dark grounded","A8C46A","12132B",4.5),("dark attention","FF8A4C","12132B",4.5),("dark danger","F08A90","12132B",4.5),("dark control border","6E6F8F","12132B",3.0)]
ok=True
for n,a,b,t in PAIRS:
    c=C(a,b); flag="OK" if c>=t else "FAIL"; ok&=c>=t
    print(f"{flag:4} {c:5.2f}:1 (min {t}) {n}: #{a} on #{b}")
print("ALL PASS" if ok else "SOME FAIL")
