# SVG diagrams for the brand book. Colors are product tokens.
BLUE="#2B2C84"; ORANGE="#EA5614"; INK="#3E3E59"; INK2="#5C5C73"; INK3="#646872"
LINE="#E6E6EF"; LINES="#C7C7D9"; CTRL="#8D8DA6"; CANVAS="#F8F8FC"; S2="#F0F0F7"; S3="#E6E6EF"
TINT="#EDEDF7"; EVID="#E4E4F3"; DANGER="#BB3E45"; KHAKI="#4E621C"; KBG="#EEF2E4"
F="font-family:'Golos Text';"

def t(x,y,s,size=11,fill=INK,w=400,anchor="start"):
    return f'<text x="{x}" y="{y}" style="{F}font-size:{size}px;font-weight:{w}" fill="{fill}" text-anchor="{anchor}">{s}</text>'

def dim_v(x,y1,y2,label,side="right",color=BLUE):
    tx = x+6 if side=="right" else x-6
    an = "start" if side=="right" else "end"
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" stroke-width="1"/>'
            f'<line x1="{x-3}" y1="{y1}" x2="{x+3}" y2="{y1}" stroke="{color}"/>'
            f'<line x1="{x-3}" y1="{y2}" x2="{x+3}" y2="{y2}" stroke="{color}"/>'
            + t(tx,(y1+y2)/2+4,label,10,color,500,an))

def phone(ox,oy,good=True):
    W,H=230,470; s=[]
    s.append(f'<rect x="{ox}" y="{oy}" width="{W}" height="{H}" rx="34" fill="{CANVAS}" stroke="{INK3}" stroke-width="2"/>')
    # header bleeds under island
    s.append(f'<path d="M{ox+1} {oy+60} L{ox+1} {oy+34} Q{ox+1} {oy+1} {ox+34} {oy+1} L{ox+W-34} {oy+1} Q{ox+W-1} {oy+1} {ox+W-1} {oy+34} L{ox+W-1} {oy+60} Z" fill="#FFFFFF"/>')
    s.append(f'<line x1="{ox+1}" y1="{oy+60}" x2="{ox+W-1}" y2="{oy+60}" stroke="{LINE}"/>')
    s.append(f'<rect x="{ox+W/2-42}" y="{oy+10}" width="84" height="22" rx="11" fill="#111"/>')
    s.append(t(ox+14,oy+52,"Юридический ассистент",10,INK,600))
    # feed lines
    for i,wd in enumerate([170,150,180,120,160]):
        s.append(f'<rect x="{ox+14}" y="{oy+80+i*18}" width="{wd}" height="8" rx="2" fill="{S3}"/>')
    # guide 34 -> scale 1px = 1pt approx; phone height 470 ~ 844*0.557; use scale 0.557
    k=0.557
    guide_y = oy+H-34*k*2.2  # exaggerate for readability
    hb_y = oy+H-12
    s.append(f'<rect x="{ox+W/2-45}" y="{hb_y-3}" width="90" height="5" rx="2.5" fill="#111"/>')
    if good:
        gy = oy+H-40
        s.append(f'<line x1="{ox-10}" y1="{gy}" x2="{ox+W+10}" y2="{gy}" stroke="{ORANGE}" stroke-dasharray="4 3"/>')
        # composer zone
        cy = gy-8-60
        s.append(f'<rect x="{ox+10}" y="{cy}" width="{W-20}" height="60" rx="8" fill="#fff" stroke="{CTRL}"/>')
        s.append(t(ox+20,cy+34,"Вопрос по базе...",10,INK2))
        s.append(f'<rect x="{ox+W-20-8-80}" y="{cy+8}" width="80" height="44" rx="4" fill="{BLUE}"/>')
        s.append(t(ox+W-20-8-40,cy+34,"Спросить",10,"#fff",500,"middle"))
        s.append(dim_v(ox+W+18,gy,oy+H,"34"))
        s.append(dim_v(ox+W+18,cy+60,gy,"8"))
        s.append(dim_v(ox-14,cy+52,cy+60,"12",side="left"))
    else:
        cy = oy+H-62
        s.append(f'<rect x="{ox+10}" y="{cy}" width="{W-20}" height="60" rx="8" fill="#fff" stroke="{CTRL}"/>')
        s.append(t(ox+20,cy+26,"Вопрос по базе...",10,INK2))
        s.append(f'<rect x="{ox+W-20-8-80}" y="{cy+14}" width="80" height="44" rx="4" fill="{BLUE}"/>')
        s.append(t(ox+W-20-8-40,cy+40,"Спросить",10,"#fff",500,"middle"))
        s.append(f'<rect x="{ox+W-20-8-86}" y="{cy+8}" width="92" height="56" fill="none" stroke="{DANGER}" stroke-width="2"/>')
        s.append(f'<rect x="{ox+W/2-45}" y="{hb_y-3}" width="90" height="5" rx="2.5" fill="#111"/>')
    return "".join(s)

def safe_area():
    s=[f'<svg viewBox="0 0 700 540" xmlns="http://www.w3.org/2000/svg" width="100%">']
    s.append(t(40,24,"Ошибка: кнопка на полоске",12,DANGER,600))
    s.append(t(370,24,"Наша спецификация",12,KHAKI,600))
    s.append(phone(40,40,False)); s.append(phone(370,40,True))
    s.append(t(40,530,"Тап у края читается системой как свайп «домой»",10,INK2))
    s.append(t(370,530,"max(16px, env(safe-area-inset-bottom) + 8px)",10,BLUE,500))
    s.append('</svg>'); return "".join(s)

def desktop_grid():
    s=[f'<svg viewBox="0 0 660 330" xmlns="http://www.w3.org/2000/svg" width="100%">']
    k=660/1440
    W=1440*k; H=300
    s.append(f'<rect x="0" y="10" width="{W}" height="{H}" fill="{CANVAS}" stroke="{LINES}"/>')
    s.append(f'<rect x="0" y="10" width="{W}" height="{56*k*1.6}" fill="#fff" stroke="{LINE}"/>')
    hh=56*k*1.6
    s.append(t(8,10+hh/2+4,"Шапка 56",9,INK,600))
    x1=264*k; x2=W-400*k
    s.append(f'<rect x="0" y="{10+hh}" width="{x1}" height="{H-hh}" fill="#fff" stroke="{LINE}"/>')
    s.append(f'<rect x="{x2}" y="{10+hh}" width="{400*k}" height="{H-hh}" fill="#fff" stroke="{LINE}"/>')
    s.append(t(x1/2,160,"История 264",10,INK,600,"middle"))
    s.append(t(x2+200*k,160,"Источники 400",10,INK,600,"middle"))
    s.append(t(x2+200*k,176,"(640 с документом)",9,INK2,400,"middle"))
    cx=(x1+x2)/2; cw=680*k
    s.append(f'<rect x="{cx-cw/2}" y="{10+hh+12}" width="{cw}" height="{H-hh-90}" fill="#fff" stroke="{BLUE}" stroke-dasharray="3 3"/>')
    s.append(t(cx,140,"Колонка ответа max 680",10,BLUE,600,"middle"))
    s.append(t(cx,156,"поля 32 по бокам",9,INK2,400,"middle"))
    s.append(f'<rect x="{cx-cw/2}" y="{H-60}" width="{cw}" height="{100*k*1.2}" rx="4" fill="#fff" stroke="{CTRL}"/>')
    s.append(t(cx,H-60+30,"Композер 680, высота от 100",9,INK,500,"middle"))
    s.append(t(cx,H-60+56+8,"нижний отступ 16",8,INK2,400,"middle"))
    s.append('</svg>'); return "".join(s)

def answer_anatomy():
    rows=[("Ассистент · 22:41",32,"meta",None),(None,8,None,None),("[✓ Подтверждено базой]   4 источника",24,"badge",None),(None,16,None,None),
          ("Согласование запускает руководитель подразделения",24,"head",None),(None,8,None,None),
          ("Обоснование 16/26 с чипами [1] [2] ...",26,"body",None),("...второй строкой абзаца",26,"body",None),(None,16,None,None),
          ("Баннер (если есть)",56,"banner",None),(None,24,None,None),("Основания",20,"label",None),(None,8,None,None),
          ("[1] Регламент согласования договоров ред. 2025 · п. 1.3",56,"row",None),(None,4,None,None),("[2] Регламент ... · п. 2.2",56,"row",None)]
    total=sum(r[1] for r in rows); k=1.0
    s=[f'<svg viewBox="0 0 660 {total+20}" xmlns="http://www.w3.org/2000/svg" width="100%">']
    y=10; X=120
    for label,h,kind,_ in rows:
        if kind is None:
            s.append(f'<rect x="{X}" y="{y}" width="460" height="{h}" fill="{ORANGE}" fill-opacity="0.12"/>')
            s.append(t(X-10,y+h/2+4,f"{h}",10,ORANGE if False else BLUE,600,"end"))
        else:
            if kind=="meta":
                s.append(t(X,y+20,label,11,INK2,500)); s.append(f'<rect x="{X+340}" y="{y}" width="80" height="32" rx="4" fill="none" stroke="{LINE}"/>'); s.append(t(X+380,y+20,"Копировать",10,INK2,500,"middle")); s.append(f'<rect x="{X+428}" y="{y}" width="32" height="32" rx="4" fill="none" stroke="{LINE}"/>'); s.append(t(X+444,y+20,"⋯",12,INK2,500,"middle"))
            elif kind=="badge":
                s.append(f'<rect x="{X}" y="{y}" width="168" height="24" rx="4" fill="{KBG}"/>'); s.append(t(X+8,y+16,"✓ Подтверждено базой",11,KHAKI,500)); s.append(t(X+180,y+16,"4 источника",10,INK2))
            elif kind=="head":
                s.append(t(X,y+17,label,13,INK,600))
            elif kind=="body":
                s.append(t(X,y+17,label,12,INK,400))
            elif kind=="banner":
                s.append(f'<rect x="{X}" y="{y}" width="460" height="{h}" rx="6" fill="{S2}"/><rect x="{X}" y="{y}" width="4" height="{h}" fill="{INK3}"/>'); s.append(t(X+40,y+30,label,11,INK,600))
            elif kind=="label":
                s.append(t(X,y+14,label,11,INK2,500))
            elif kind=="row":
                s.append(f'<rect x="{X}" y="{y}" width="460" height="{h}" rx="4" fill="#fff" stroke="{LINE}"/>'); s.append(t(X+12,y+24,label,10,INK,500)); s.append(t(X+12,y+42,"п. 1.3 · действующая редакция",9,INK2))
            s.append(t(X+470,y+h/2+4,f"{h}",9,INK3,400))
        y+=h
    s.append(t(10,24,"зазоры, px",9,BLUE,500)); s.append(t(612,24,"высоты",9,INK3,500))
    s.append('</svg>'); return "".join(s)

def card_vs_skeleton():
    k=0.75
    def card(ox,sk):
        out=[f'<g transform="translate({ox},20) scale({k})">']
        out.append(f'<rect x="0" y="0" width="368" height="202" rx="8" fill="#fff" stroke="{LINES}"/>')
        if not sk:
            out.append(t(16,32,"[1] НК РФ, ст. 164 «Налоговые ставки»",14,INK,500))
            out.append(t(16,54,"п. 3 · действующая редакция · выгр. 10.10.2026",12,INK2))
            out.append(f'<rect x="16" y="68" width="2" height="72" fill="{BLUE}"/>')
            for i,l in enumerate(["«Налогообложение производится","по налоговой ставке 22 процента","в случаях, не указанных...»"]):
                out.append(f'<text x="30" y="{86+i*24}" style="font-family:\'PT Serif\';font-size:15px" fill="{INK}">{l}</text>')
            out.append(f'<rect x="16" y="154" width="170" height="32" rx="4" fill="#fff" stroke="{CTRL}"/>'); out.append(t(101,175,"Открыть в документе",13,BLUE,500,"middle"))
            out.append(f'<rect x="320" y="154" width="32" height="32" rx="4" fill="none" stroke="{LINE}"/>')
        else:
            out.append(f'<rect x="16" y="20" width="235" height="12" rx="2" fill="{S2}"/>')
            out.append(f'<rect x="16" y="44" width="150" height="10" rx="2" fill="{S2}"/>')
            out.append(f'<rect x="16" y="68" width="2" height="72" fill="{S3}"/>')
            for i,wd in enumerate([1.0,0.96,0.6]):
                out.append(f'<rect x="30" y="{74+i*24}" width="{322*wd}" height="12" rx="2" fill="{S2}"/>')
            out.append(f'<rect x="16" y="154" width="160" height="32" rx="4" fill="{S2}"/>')
        out.append('</g>'); return "".join(out)
    s=[f'<svg viewBox="0 0 660 200" xmlns="http://www.w3.org/2000/svg" width="100%">']
    s.append(t(20,12,"Карточка, 202 px",11,INK,600)); s.append(t(350,12,"Скелетон, те же 202 px",11,INK,600))
    s.append(card(20,False)); s.append(card(350,True))
    s.append('</svg>'); return "".join(s)

def timeline():
    s=[f'<svg viewBox="0 0 660 190" xmlns="http://www.w3.org/2000/svg" width="100%">']
    X0=40; X1=640
    def xs(sec):  # piecewise: 0-10s takes 75%, 10-60 takes 25%
        return X0+(sec/10)*(X1-X0)*0.75 if sec<=10 else X0+(X1-X0)*0.75+((sec-10)/50)*(X1-X0)*0.25
    s.append(f'<line x1="{X0}" y1="150" x2="{X1}" y2="150" stroke="{INK3}"/>')
    for sec in [0,1,1.5,4,5,10,60]:
        x=xs(sec); s.append(f'<line x1="{x}" y1="146" x2="{x}" y2="154" stroke="{INK3}"/>'); s.append(t(x,170,f"{sec} с".replace(".",","),9,INK2,400,"middle"))
    bars=[(0,1.5,"Ищу положения в базе",BLUE,30),(1.5,4,"Сверяю ответ",BLUE,30),(4,10,"Проверяю ссылки",BLUE,30),
          (0,5,"спиннер вращается",ORANGE,62),(5,60,"статичная иконка",INK3,62),(10,60,"progress.slow",INK2,94),(0,10,"3 скелетона карточек в панели",S3,120)]
    for a,b,l,c,y in bars:
        x=xs(a); w=xs(b)-xs(a)
        s.append(f'<rect x="{x}" y="{y}" width="{w-2}" height="20" rx="2" fill="{c}" fill-opacity="{0.9 if c!=S3 else 1}"/>')
        s.append(t(x+6,y+14,l,9,"#fff" if c in (BLUE,INK3,INK2,ORANGE) else INK,500))
    s.append(t(xs(60),20,"60 с: timeout",9,DANGER,600,"end"))
    s.append(t(X0,20,"Таймеры 1,5 с и 4 с только без событий SSE",9,INK2))
    s.append('</svg>'); return "".join(s)

def motion_chart():
    items=[("Hover, pressed (M1, M2)",120),("Фокус-кольцо (M3)",0),("Реплика, стадия, поповер, тултип",120),("Ответ целиком, бейдж, скелетон → карточки",200),
           ("Раскрытие цитаты (M16)",200),("Панель, лист, drawer: вход",240),("Панель, лист, drawer: выход",200),("Прокрутка к фрагменту (цель)",300),("Подсветка карточки: удержание + затухание",1200)]
    s=[f'<svg viewBox="0 0 660 {len(items)*26+30}" xmlns="http://www.w3.org/2000/svg" width="100%">']
    X=290; scale=300/400
    for i,(l,ms) in enumerate(items):
        y=10+i*26
        s.append(t(X-10,y+14,l,10,INK,400,"end"))
        w=min(ms,400)*scale
        if ms==1200:
            s.append(f'<rect x="{X}" y="{y+2}" width="{400*scale*0.33}" height="16" fill="{EVID}"/><rect x="{X+400*scale*0.33}" y="{y+2}" width="{400*scale*0.67}" height="16" fill="{TINT}"/>')
            s.append(t(X+400*scale+6,y+14,"400 + 800 мс (вне шкалы)",9,INK2))
        else:
            s.append(f'<rect x="{X}" y="{y+2}" width="{max(w,1.5)}" height="16" fill="{BLUE if ms>0 else INK3}"/>')
            s.append(t(X+max(w,2)+6,y+14,f"{ms} мс",9,INK2))
    y=10+len(items)*26
    for ms in [0,100,200,300,400]:
        x=X+ms*scale; s.append(f'<line x1="{x}" y1="6" x2="{x}" y2="{y}" stroke="{LINE}"/>')
    s.append('</svg>'); return "".join(s)

def spacing_ruler():
    steps=[4,8,12,16,20,24,32,40,48,64]
    s=[f'<svg viewBox="0 0 660 110" xmlns="http://www.w3.org/2000/svg" width="100%">']
    x=10
    for i,v in enumerate(steps):
        s.append(f'<rect x="{x}" y="{70-v}" width="{v}" height="{v}" fill="{BLUE}" fill-opacity="0.85"/>')
        s.append(t(x+v/2,88,str(v),10,INK,600,"middle"))
        s.append(t(x+v/2,102,f"space-{[1,2,3,4,5,6,8,10,12,16][i]}",8,INK2,400,"middle"))
        x+=v+26
    s.append('</svg>'); return "".join(s)

def banner_anatomy():
    s=[f'<svg viewBox="0 0 660 200" xmlns="http://www.w3.org/2000/svg" width="100%">']
    X,Y,W,H=30,20,560,160
    s.append(f'<rect x="{X}" y="{Y}" width="{W}" height="{H}" rx="8" fill="{S2}"/><rect x="{X}" y="{Y}" width="4" height="{H}" fill="{INK3}"/>')
    s.append(f'<circle cx="{X+4+16+10}" cy="{Y+16+12}" r="9" fill="none" stroke="{INK3}" stroke-width="1.5"/><line x1="{X+23}" y1="{Y+35}" x2="{X+37}" y2="{Y+21}" stroke="{INK3}" stroke-width="1.5"/>')
    tx=X+4+16+20+12
    s.append(t(tx,Y+16+17,"В базе знаний нет оснований для достоверного ответа",13,INK,600))
    s.append(t(tx,Y+16+24+4+14,"Ассистент не делает выводов без подтверждающих положений",11,INK))
    s.append(t(tx,Y+16+24+4+20+12+14,"Чего не хватает",11,INK,600))
    s.append(t(tx+10,Y+16+24+4+20+12+20+4+14,"релевантные документы по теме вопроса",11,INK))
    s.append(f'<circle cx="{tx+3}" cy="{Y+16+24+4+20+12+20+4+10}" r="2" fill="{INK3}"/>')
    by=Y+16+24+4+20+12+20+4+20+16-6
    s.append(f'<rect x="{tx}" y="{by}" width="190" height="28" rx="4" fill="#fff" stroke="{CTRL}"/>'); s.append(t(tx+95,by+18,"Переформулировать вопрос",10,BLUE,500,"middle"))
    s.append(f'<rect x="{tx+198}" y="{by}" width="200" height="28" rx="4" fill="none"/>'); s.append(t(tx+298,by+18,"Показать найденные фрагменты",10,INK2,500,"middle"))
    # dims
    s.append(t(X+2,Y-6,"4",9,ORANGE,600)); s.append(t(X+14,Y-6,"16",9,BLUE,600)); s.append(t(X+30,Y-6,"20",9,BLUE,600)); s.append(t(X+46,Y-6,"12",9,BLUE,600))
    s.append(dim_v(X+W+14,Y,Y+16,"16"))
    s.append(dim_v(X+W+14,by+28,Y+H,"16"))
    s.append(t(tx+398+8,by+18,"↔ 8",9,BLUE,600))
    s.append('</svg>'); return "".join(s)

# ---------- chat layout, generation (added 09.11.2026 night) ----------
def _r(x,y,w,h,fill="#fff",stroke=LINE,rx=0,extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'

def chat_layout():
    s=['<svg viewBox="0 0 660 400" xmlns="http://www.w3.org/2000/svg" width="100%">']
    s.append(_r(0,0,660,390,CANVAS,LINES))
    s.append(_r(0,0,660,34,"#fff",LINE)); s.append(t(10,22,"ПСБ  |  Юридический ассистент",10,INK,600)); s.append(t(650,22,"База: 21 документ   ?",9,INK2,400,"end"))
    # history
    s.append(_r(0,34,120,356,"#fff",LINE))
    s.append(t(8,50,"СЛЕВА: история · 264",8,BLUE,600))
    s.append(_r(8,58,104,26,"#fff",CTRL,4)); s.append(t(60,75,"+ Новый диалог",9,BLUE,500,"middle"))
    s.append(t(8,100,"Сегодня",8,INK3,500))
    s.append(_r(8,106,104,22,TINT,"none",4)); s.append(f'<rect x="8" y="106" width="2" height="22" fill="{BLUE}"/>'); s.append(t(14,121,"Кто должен запуст…",8.5,INK))
    s.append(t(14,143,"Срок оплаты по П-1…",8.5,INK)); s.append(t(14,165,"НДС по договору…",8.5,INK))
    s.append(t(8,186,"Ранее",8,INK3,500)); s.append(t(14,204,"Испытательный срок…",8.5,INK))
    s.append(t(8,380,"пункт 44, 2 уровня",7.5,INK2))
    # sources
    s.append(_r(470,34,190,356,"#fff",LINE))
    s.append(t(478,50,"СПРАВА: источники · 400",8,BLUE,600))
    s.append(t(478,70,"Источники",11,INK,600)); s.append(_r(538,60,16,14,S2,"none",4)); s.append(t(546,71,"4",8,INK2,500,"middle"))
    s.append(t(478,86,"К ответу от 22:41",8,INK3))
    for i,(tt,q) in enumerate([("Регламент согласования…","«Инициатором согласования"),("Положение о закупках…","«Договор подписывает")]):
        y=94+i*112
        s.append(_r(478,y,174,104,"#fff",LINES,8))
        s.append(t(486,y+16,tt,8.5,INK,500)); s.append(t(486,y+29,"п. 1.3 · действующая ред.",7.5,INK2))
        s.append(f'<line x1="487" y1="{y+38}" x2="487" y2="{y+70}" stroke="{BLUE}" stroke-width="2"/>')
        s.append(f'<text x="494" y="{y+50}" style="font-family:\'PT Serif\';font-size:8.5px" fill="{INK}">{q}</text>')
        s.append(f'<text x="494" y="{y+63}" style="font-family:\'PT Serif\';font-size:8.5px" fill="{INK}">является руководитель…»</text>')
        s.append(_r(486,y+78,96,18,"#fff",CTRL,4)); s.append(t(534,y+90,"Открыть в документе",7.5,BLUE,500,"middle"))
        s.append(_r(632,y+78,18,18,"#fff","none",4)); s.append(t(641,y+90,"⎘",9,INK2,400,"middle"))
    s.append(t(478,380,"карточка 202, зазор 8, радиус 8",7.5,INK2))
    # feed column
    cx0=140; cw=310
    s.append(t(cx0,50,"ЦЕНТР: лента · колонка max 680",8,BLUE,600))
    s.append(f'<line x1="{cx0}" y1="56" x2="{cx0}" y2="330" stroke="{ORANGE}" stroke-dasharray="3 3"/>')
    s.append(t(cx0,70,"Вы",8,INK3,500)); s.append(t(cx0+cw,70,"22:41",8,INK3,400,"end"))
    s.append(_r(cx0,76,cw,30,S2,"none",8)); s.append(t(cx0+10,95,"Кто должен запустить согласование договора?",9,INK))
    s.append(f'<line x1="{cx0}" y1="118" x2="{cx0+cw}" y2="118" stroke="{LINE}"/>'); s.append(t(cx0+cw+4,121,"16+1+16",7,ORANGE,500))
    s.append(t(cx0,138,"Ассистент · 22:41",8,INK2,500)); s.append(t(cx0+cw,138,"Копировать  ⋯",8,INK2,400,"end"))
    s.append(_r(cx0,146,112,16,KBG,"none",4)); s.append(t(cx0+6,158,"✓ Подтверждено базой",8,KHAKI,500)); s.append(t(cx0+120,158,"4 источника",8,INK2))
    s.append(t(cx0,180,"Согласование запускает руководитель",10,INK,600)); s.append(t(cx0,193,"подразделения.",10,INK,600))
    s.append(t(cx0,211,"Это установлено п. 1.3 регламента",9,INK)); s.append(_r(cx0+156,202,14,13,TINT,"none",4)); s.append(t(cx0+163,212,"1",8,BLUE,500,"middle"))
    s.append(t(cx0,234,"Основания",8.5,INK2,500))
    s.append(_r(cx0,240,cw,22,"#fff",LINE,4)); s.append(t(cx0+8,255,"[1] Регламент согласования договоров · п. 1.3",8.5,INK))
    s.append(f'<path d="M{cx0+cw} 251 C 455 251, 460 140, 478 140" fill="none" stroke="{BLUE}" stroke-dasharray="2 2"/>')
    s.append(t(cx0+cw,276,"↕ 48 до следующего обмена",7.5,ORANGE,500,"end"))
    s.append(_r(cx0,300,cw,44,"#fff",CTRL,8)); s.append(t(cx0+10,326,"Уточнение или следующий вопрос",9,INK2))
    s.append(_r(cx0+cw-78,308,70,28,BLUE,"none",4)); s.append(t(cx0+cw-43,326,"↑ Спросить",8.5,"#fff",500,"middle"))
    s.append(t(cx0,358,"Ответы ограничены базой знаний. Выводы сверяйте с цитатами",7.5,INK3))
    s.append(t(cx0,380,"Вопрос и ответ на одной левой оси (оранжевая линия)",8,ORANGE,600))
    s.append('</svg>'); return "".join(s)

def chat_do_dont():
    s=['<svg viewBox="0 0 660 170" xmlns="http://www.w3.org/2000/svg" width="100%">']
    s.append(t(0,14,"Правильно: протокол запроса",11,KHAKI,600)); s.append(t(350,14,"Нельзя: мессенджер",11,DANGER,600))
    s.append(_r(0,24,310,140,"#fff",LINE))
    s.append(t(10,42,"Вы · 22:41",8,INK3)); s.append(_r(10,48,290,26,S2,"none",8)); s.append(t(18,65,"Какой срок оплаты по договору П-17/2024?",8.5,INK))
    s.append(f'<line x1="10" y1="84" x2="300" y2="84" stroke="{LINE}"/>')
    s.append(t(10,100,"Ассистент · 22:41",8,INK2,500)); s.append(_r(10,106,104,15,KBG,"none",4)); s.append(t(16,117,"✓ Подтверждено базой",7.5,KHAKI,500))
    s.append(t(10,138,"30 календарных дней с даты поставки.",9.5,INK,600)); s.append(t(10,154,"Пункт 4.2 договора [1]",8.5,INK))
    s.append(f'<line x1="10" y1="30" x2="10" y2="160" stroke="{ORANGE}" stroke-dasharray="3 3"/>')
    s.append(_r(350,24,310,140,"#fff",LINE))
    s.append(f'<circle cx="368" cy="58" r="9" fill="{S3}"/>'); s.append(t(368,80,"аватар",7,INK3,400,"middle"))
    s.append(_r(470,38,180,26,BLUE,"none",14)); s.append(t(480,55,"Какой срок оплаты по П-17?",8.5,"#fff"))
    s.append(_r(382,74,200,40,S2,"none",14)); s.append(t(392,92,"Отличный вопрос! Срок оплаты",8.5,INK)); s.append(t(392,106,"составляет 30 дней!",8.5,INK))
    s.append(_r(382,124,46,22,S2,"none",11))
    for i in range(3): s.append(f'<circle cx="{394+i*11}" cy="135" r="3" fill="{INK3}"/>')
    s.append(t(440,139,"← «печатает…»: нет",8,DANGER,500))
    s.append(f'<line x1="352" y1="26" x2="658" y2="162" stroke="{DANGER}" stroke-width="1.5" opacity=".55"/>')
    s.append('</svg>'); return "".join(s)

def gen_storyboard():
    W,H=320,232
    frames=[("L0 · 0 с","Ищу положения в базе",True,"spin",3,None),
            ("L2 · событие или 4 с","Проверяю ссылки",True,"spin",3,None),
            ("L4 · 10 с","Проверяю ссылки",True,"static",3,"Ответ готовится дольше обычного."),
            ("L5 · ответ проверен",None,False,None,2,None)]
    s=[f'<svg viewBox="0 0 660 {2*H+24}" xmlns="http://www.w3.org/2000/svg" width="100%">']
    for k,(title,stage,busy,sp,nc,slow) in enumerate(frames):
        ox=(k%2)*(W+20); oy=(k//2)*(H+12)
        s.append(_r(ox,oy,W,H,"#fff",LINES))
        s.append(_r(ox,oy,W,22,S2,"none")); s.append(t(ox+8,oy+15,title,9.5,BLUE,600))
        fx=ox+10; fw=180
        s.append(t(fx,oy+40,"Вы · 22:41",7.5,INK3)); s.append(_r(fx,oy+45,fw,20,S2,"none",6)); s.append(t(fx+6,oy+59,"Кто должен запустить…",8,INK))
        s.append(f'<line x1="{fx}" y1="{oy+73}" x2="{fx+fw}" y2="{oy+73}" stroke="{LINE}"/>')
        s.append(t(fx,oy+88,"Ассистент" + ("" if busy else " · 22:41"),7.5,INK2,500))
        if busy:
            if sp=="spin":
                s.append(f'<circle cx="{fx+6}" cy="{oy+100}" r="5" fill="none" stroke="{LINE}" stroke-width="2"/><path d="M{fx+6} {oy+95} A5 5 0 0 1 {fx+11} {oy+100}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
            else:
                s.append(f'<circle cx="{fx+6}" cy="{oy+100}" r="5" fill="none" stroke="{INK3}" stroke-width="1.5" stroke-dasharray="2 1.6"/>')
            s.append(t(fx+16,oy+104,stage,8.5,INK2))
            if slow: s.append(t(fx+16,oy+120,slow,7.5,INK2)); s.append(t(fx+16,oy+131,"Можно остановить и уточнить вопрос",7.5,INK2))
            s.append(t(fx,oy+150 if slow else oy+128,"текста ответа ещё нет: исход неизвестен",7,INK3))
            s.append(_r(fx,oy+H-34,fw,24,"#fff",LINES,6)); s.append(_r(fx+fw-62,oy+H-31,58,18,"#fff",CTRL,4)); s.append(t(fx+fw-33,oy+H-18,"■ Остановить",7,BLUE,500,"middle"))
        else:
            s.append(_r(fx,oy+94,88,13,KBG,"none",3)); s.append(t(fx+4,oy+104,"✓ Подтверждено базой",7,KHAKI,500))
            s.append(t(fx,oy+122,"Согласование запускает",9,INK,600)); s.append(t(fx,oy+134,"руководитель подразделения.",9,INK,600))
            s.append(t(fx,oy+150,"Пункт 1.3 регламента [1]",8,INK))
            s.append(t(fx,oy+168,"Основания: [1] [2]",7.5,INK2,500))
            s.append(_r(fx,oy+H-34,fw,24,"#fff",CTRL,6)); s.append(_r(fx+fw-62,oy+H-31,58,18,BLUE,"none",4)); s.append(t(fx+fw-33,oy+H-18,"↑ Спросить",7,"#fff",500,"middle"))
        # panel
        px=ox+200; pw=110
        s.append(f'<line x1="{px-6}" y1="{oy+22}" x2="{px-6}" y2="{oy+H}" stroke="{LINE}"/>')
        s.append(t(px,oy+38,"Источники",8.5,INK,600)); s.append(t(px,oy+50,"К ответу от 22:41",6.5,INK3))
        for i in range(nc):
            y=oy+58+i*54
            if busy:
                s.append(_r(px,y,pw,48,"#fff",LINE,6))
                s.append(_r(px+6,y+7,70,6,S2,"none",2)); s.append(_r(px+6,y+17,44,5,S2,"none",2))
                s.append(f'<line x1="{px+7}" y1="{y+27}" x2="{px+7}" y2="{y+42}" stroke="{S3}" stroke-width="2"/>')
                s.append(_r(px+12,y+28,90,5,S2,"none",2)); s.append(_r(px+12,y+36,60,5,S2,"none",2))
            else:
                s.append(_r(px,y,pw,48,"#fff",LINES,6)); s.append(t(px+6,y+12,"Регламент…",7,INK,500)); s.append(t(px+6,y+22,"п. 1.3 · действ.",6,INK2))
                s.append(f'<line x1="{px+7}" y1="{y+27}" x2="{px+7}" y2="{y+42}" stroke="{BLUE}" stroke-width="2"/>')
                s.append(f'<text x="{px+12}" y="{y+37}" style="font-family:\'PT Serif\';font-size:7px" fill="{INK}">«Инициатором…»</text>')
        s.append(t(px,oy+H-10,"3 скелетона по 202, статичные" if busy else "скелетоны → карточки, 200 ms",6.5,INK2))
    s.append('</svg>'); return "".join(s)

def gen_timeline():
    s=['<svg viewBox="0 0 660 250" xmlns="http://www.w3.org/2000/svg" width="100%">']
    X0=150; X1=650
    def xs(sec): return X0+(sec/10)*(X1-X0)*0.8 if sec<=10 else X0+(X1-X0)*0.8+((sec-10)/50)*(X1-X0)*0.2
    rows=[("Лента: строка стадии",30),("Лента: значок",62),("Лента: задержка",94),("Справа: панель",126)]
    for l,y in rows: s.append(t(0,y+14,l,9,INK,600))
    bars=[(0,1.5,"1",BLUE,30),(1.5,4,"2",BLUE,30),(4,60,"3  до ответа",BLUE,30),
          (0,5,"спиннер вращается ≤ 5 с",ORANGE,62),(5,60,"статичная иконка",INK3,62),
          (10,60,"4  progress.slow",INK2,94),(0,60,"3 статичных скелетона карточек, 202 px",S3,126)]
    for a,b,l,c,y in bars:
        x=xs(a); w=xs(b)-xs(a)
        s.append(f'<rect x="{x}" y="{y}" width="{w-2}" height="20" rx="2" fill="{c}"/>')
        s.append(t(x+6,y+14,l,9,INK if c==S3 else "#fff",600))
    s.append(f'<line x1="{X0}" y1="160" x2="{X1}" y2="160" stroke="{INK3}"/>')
    for sec,lab in [(0,"0"),(1.5,"1,5 с"),(4,"4 с"),(5,"5 с"),(10,"10 с"),(60,"60 с")]:
        x=xs(sec); s.append(f'<line x1="{x}" y1="156" x2="{x}" y2="164" stroke="{INK3}"/>'); s.append(t(x,176,lab,8.5,INK2,400,"middle"))
    s.append(t(X1,20,"60 с: системная ошибка timeout",8.5,DANGER,600,"end"))
    leg=[("1","progress.search","Ищу положения в базе"),("2","progress.verify","Сверяю ответ с найденными фрагментами"),("3","progress.cite","Проверяю ссылки"),("4","progress.slow","Ответ готовится дольше обычного. Можно остановить и уточнить вопрос")]
    for i,(n,k,v) in enumerate(leg):
        y=196+i*14; s.append(t(0,y,n,9,BLUE,600)); s.append(t(14,y,k,8.5,INK2,500)); s.append(t(120,y,"«"+v+"»",9,INK))
    s.append('</svg>'); return "".join(s)
