"""Carte métier des neuf domaines, inspirée de SCHEMAS_EXPLICATIFS.md."""
import html, json, math, hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from relational_page import FONT, BOLD

ROOT=Path(__file__).resolve().parents[1]
BG='#F3F6FA'; INK='#142B46'; W=2480; H=2120

def add_overview(doc):
    model=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
    tables={t['name']:t for t in model['tables']}
    for old in list(doc.getroot()):
        if old.get('id')=='page13':doc.getroot().remove(old)
    page=ET.SubElement(doc.getroot(),'diagram',id='page13',name='Vue d’ensemble — comprendre le modèle')
    graph=ET.SubElement(page,'mxGraphModel',grid='0',page='0',pageWidth=str(W),pageHeight=str(H),background=BG,connect='1')
    root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    im=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(im)
    def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
    def txt(s,x,y,size=20,color=INK,bold=False):draw.text((x,y),s,font=font(size,bold),fill=color)
    def cell(id,value,x,y,w,h,style,parent='1'):
        c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent=parent)
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        return c
    def text(id,s,x,y,w,size=20,color=INK,bold=False):
        cell(id,html.escape(s),x,y,w,size+14,f'text;html=1;align=left;verticalAlign=top;spacing=0;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};')
        txt(s,x,y,size,color,bold)
    text('title','Le modèle DOD / STR en un coup d’œil',70,40,2340,40,bold=True)
    text('subtitle','9 domaines · 34 tables · Les liens principaux pour comprendre et expliquer le dossier.',70,102,2340,24)
    domains={d['name']:d for d in model['domains']}
    layouts={
        'Rapport':(930,185,620,390),
        'Définitions':(80,700,680,400),
        'Transactions':(900,700,680,300),
        'Audit':(1720,700,680,400),
        'Identité':(40,1220,350,280),
        'Entité':(470,1220,350,280),
        'Bénéficiaires effectifs':(40,1600,780,405),
        'Rôles':(900,1140,680,420),
        'Comptes':(1720,1220,680,300),
    }
    questions={
        'Rapport':'Quel dossier transmet-on ?',
        'Définitions':'De qui parle-t-on ?',
        'Transactions':'Que s’est-il passé ?',
        'Audit':'Qu’a-t-on envoyé et reçu ?',
        'Identité':'Comment les identifier ?',
        'Entité':'Comment est-elle constituée ?',
        'Bénéficiaires effectifs':'Qui dirige ou détient l’entité ?',
        'Rôles':'Qui fait quoi dans l’opération ?',
        'Comptes':'Par quels comptes ou adresses passent les fonds ?',
    }
    ids={name:'domain'+str(i) for i,name in enumerate(layouts)}
    for name,(x,y,w,h) in layouts.items():
        d=domains[name];color=d['color']
        rgb=tuple(int(color[i:i+2],16) for i in (1,3,5));fill='#'+''.join(f'{round(v*.07+255*.93):02X}' for v in rgb)
        title=name+' · '+str(len(d['tables']))
        value=f'<b>{html.escape(title)}</b><br><span style="font-size:18px;color:#506378">{html.escape(questions[name])}</span>'
        cell(ids[name],value,x,y,w,h,f'rounded=1;arcSize=5;html=1;container=1;collapsible=0;recursiveResize=0;align=left;verticalAlign=top;spacing=0;spacingTop=18;spacingLeft=20;fillColor={fill};strokeColor={color};strokeWidth=2;fontFamily=Arial;fontSize=25;fontColor={color};')
        draw.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=fill,outline=color,width=2)
        txt(title,x+20,y+18,25,color,True);txt(questions[name],x+20,y+51,18,'#506378')
    # Une seule carte par table. La position est relative au domaine dans draw.io.
    placements={
        'REPORT':(1100,275,280),'PPP_PROJECT':(950,380,280),'RELATED_REPORT':(1250,380,280),'RELATED_REPORT_TXN_REF':(1250,485,280),
        'DEFINITION':(280,790,280),'PERSON':(100,900,300),'ENTITY':(440,900,300),'EMPLOYER_INFO':(100,1015,300),
        'TRANSACTION':(1100,790,280),'STARTING_ACTION':(920,915,300),'COMPLETING_ACTION':(1250,915,300),
        'API_SUBMISSION':(1920,790,280),'SUBMITTED_PAYLOAD':(1740,910,300),'VALIDATION_ERROR':(2070,910,300),'AUDIT_EVENT':(1740,1015,300),
        'ADDRESS':(60,1315,310),'IDENTIFICATION':(60,1420,310),
        'REGISTRATION_INCORPORATION':(490,1315,310),'AUTHORIZED_PERSON':(490,1420,310),
        'CONDUCTOR':(920,1240,300),'ON_BEHALF_OF':(920,1345,300),'SOURCE_OF_FUNDS':(920,1470,300),
        'INVOLVEMENT':(1250,1240,300),'BENEFICIARY':(1250,1345,300),
        'ACCOUNT':(1740,1315,300),'ACCOUNT_HOLDER':(1740,1420,300),'VC_DATA':(2070,1315,300),
        'DIRECTOR':(60,1695,355),'SHARE_OWNER':(445,1695,355),'TRUSTEE':(60,1770,355),'SETTLOR':(445,1770,355),
        'TRUST_UNIT_OWNER':(60,1845,355),'TRUST_BENEFICIARY':(445,1845,355),'OTHER_ENTITY_OWNER':(60,1920,355),
    }
    rects={}; internal=[]; concept=[]
    def edge(id,source,target,points,color='#64748B',dashed=False,label=None,labelpos=None):
        sx,sy,sw,sh=rects[source];tx,ty,tw,th=rects[target]
        start,end=points[0],points[-1]
        assert (start[0]-sx)/sw in (0,1) or (start[1]-sy)/sh in (0,1)
        assert (end[0]-tx)/tw in (0,1) or (end[1]-ty)/th in (0,1)
        style=f'edgeStyle=none;rounded=0;html=1;strokeColor={color};strokeWidth={2 if dashed else 2.5};endArrow=block;endFill=1;endSize=10;exitX={(start[0]-sx)/sw};exitY={(start[1]-sy)/sh};exitPerimeter=0;entryX={(end[0]-tx)/tw};entryY={(end[1]-ty)/th};entryPerimeter=0;'+('dashed=1;dashPattern=6 5;' if dashed else '')
        c=ET.SubElement(root,'mxCell',id=id,style=style,edge='1',parent='1',source=source,target=target)
        geo=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
        for x,y in points[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        for a,b in zip(points,points[1:]):
            assert a[0]==b[0] or a[1]==b[1]
            if dashed:
                dist=math.dist(a,b)
                for k in range(0,int(dist),18):
                    f=k/max(1,dist);g=min(k+10,dist)/max(1,dist)
                    draw.line((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,a[0]+(b[0]-a[0])*g,a[1]+(b[1]-a[1])*g),fill=color,width=2)
            else:draw.line((a,b),fill=color,width=3)
        a,b=points[-2:];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        draw.polygon([b,(b[0]-11*ux+5*uy,b[1]-11*uy-5*ux),(b[0]-11*ux-5*uy,b[1]-11*uy+5*ux)],fill=color)
        if label:
            lx,ly=labelpos;lw=draw.textlength(label,font=font(20))+16
            draw.rectangle((lx-8,ly-2,lx+lw,ly+27),fill=BG)
            cell(id+'label',html.escape(label),lx-8,ly-2,lw+8,31,f'rounded=0;html=1;align=center;spacing=0;fillColor={BG};strokeColor=none;fontFamily=Arial;fontSize=20;fontColor={color};')
            txt(label,lx,ly,20,color)
        if source.startswith('STR_'):internal.append((source,target,points))
        else:concept.append((source,target,points))
    rects.update({ids[n]:v for n,v in layouts.items()})
    rects.update({'STR_'+n:(x,y,w,60) for n,(x,y,w) in placements.items()})
    # Les flèches entre domaines expriment le parcours de lecture, pas des FK supplémentaires.
    edge('flow1',ids['Rapport'],ids['Définitions'],[(930,380),(420,380),(420,700)],'#2563EB',label='Décrit les personnes et les entités',labelpos=(90,600))
    edge('flow2',ids['Rapport'],ids['Transactions'],[(1240,575),(1240,700)],'#2563EB',label='Décrit les opérations',labelpos=(1270,620))
    edge('flow3',ids['Rapport'],ids['Audit'],[(1550,380),(2060,380),(2060,700)],'#2563EB',label='Garde la trace des envois',labelpos=(2110,600))
    edge('flow4',ids['Définitions'],ids['Identité'],[(215,1100),(215,1220)],'#15803D')
    edge('flow5',ids['Définitions'],ids['Entité'],[(645,1100),(645,1220)],'#15803D')
    edge('flow6',ids['Définitions'],ids['Bénéficiaires effectifs'],[(760,940),(850,940),(850,1740),(820,1740)],'#15803D')
    edge('flow7',ids['Transactions'],ids['Rôles'],[(1240,1000),(1240,1140)],'#C76C12',label='Les intervenants',labelpos=(1270,1050))
    edge('flow8',ids['Transactions'],ids['Comptes'],[(1580,850),(1640,850),(1640,1175),(2060,1175),(2060,1220)],'#C76C12',label='Les moyens utilisés',labelpos=(1770,1140))
    edge('flow9',ids['Rôles'],ids['Définitions'],[(900,1360),(875,1360),(875,1130),(790,1130),(790,1060),(760,1060)],'#7C3AED',True)
    # Sélection vérifiée des relations entre tables; elles restent volontairement peu nombreuses.
    specs=[
        ('REPORT','PPP_PROJECT',[(1100,305),(1090,305),(1090,380)]),
        ('REPORT','RELATED_REPORT',[(1380,305),(1390,305),(1390,380)]),
        ('RELATED_REPORT','RELATED_REPORT_TXN_REF',[(1390,440),(1390,485)]),
        ('DEFINITION','PERSON',[(350,850),(350,875),(250,875),(250,900)]),
        ('DEFINITION','ENTITY',[(490,850),(490,875),(590,875),(590,900)]),
        ('PERSON','EMPLOYER_INFO',[(250,960),(250,1015)]),
        ('TRANSACTION','STARTING_ACTION',[(1170,850),(1170,885),(1070,885),(1070,915)]),
        ('TRANSACTION','COMPLETING_ACTION',[(1310,850),(1310,885),(1400,885),(1400,915)]),
        ('API_SUBMISSION','SUBMITTED_PAYLOAD',[(1990,850),(1990,880),(1890,880),(1890,910)]),
        ('API_SUBMISSION','VALIDATION_ERROR',[(2130,850),(2130,880),(2220,880),(2220,910)]),
        ('CONDUCTOR','ON_BEHALF_OF',[(1070,1300),(1070,1345)]),
        ('ACCOUNT','ACCOUNT_HOLDER',[(1890,1375),(1890,1420)]),
    ]
    relset={(r['parent'],r['child']) for r in model['relationships']}
    for i,(a,b,pts) in enumerate(specs):
        a='STR_'+a;b='STR_'+b;assert (a,b) in relset
        edge('tablelink'+str(i),a,b,pts,tables[a]['color'])
    for short,(x,y,w) in placements.items():
        n='STR_'+short;t=tables[n];dx,dy,_,_=layouts[t['domain']];color=t['color']
        label=t['label'];technical=n
        assert draw.textlength(label,font=font(18,True))<w-24,(n,label)
        assert draw.textlength(technical,font=font(12))<w-24,n
        value=f'<b style="font-size:18px;line-height:25px">{html.escape(label)}</b><br><span style="font-size:12px;line-height:20px;color:{color}">{technical}</span>'
        cell(n,value,x-dx,y-dy,w,60,f'rounded=1;arcSize=12;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacingLeft=12;spacingRight=8;fillColor=#FFFFFF;strokeColor={color};strokeWidth=1;fontFamily=Arial;fontColor={INK};',ids[t['domain']])
        draw.rounded_rectangle((x,y,x+w,y+60),radius=7,fill='white',outline=color,width=1)
        txt(label,x+12,y+8,18,INK,True);txt(technical,x+12,y+34,12,color)
    notes=[
        ('La fiche et le rôle sont deux choses différentes.', 'On décrit une personne une fois dans Définitions. Elle peut ensuite avoir plusieurs rôles dans les opérations.'),
        ('Une correction et un nouvel essai d’envoi sont différents.', 'Le rapport porte la version. Audit conserve les tentatives d’envoi et les réponses reçues.'),
        ('Cette page montre le chemin, pas toutes les clés.', 'Les flèches entre domaines guident la lecture. Les liens entre tables sont une sélection du modèle.'),
        ('Pour passer au détail', 'Page 13 : les PK/FK et les cardinalités. Page 12 : toutes les colonnes. Les 77 relations y sont disponibles.'),
    ]
    cell('reading-note','',920,1660,1480,345,'rounded=1;arcSize=5;fillColor=#FFFFFF;strokeColor=#CBD5E1;strokeWidth=1;')
    draw.rounded_rectangle((920,1660,2400,2005),radius=12,fill='white',outline='#CBD5E1',width=1)
    for i,(title,body) in enumerate(notes):
        yy=1680+i*79
        text('note-title'+str(i),title,945,yy,1410,22,bold=True)
        text('note-body'+str(i),body,945,yy+31,1410,19,'#506378')
    text('foot','Lecture : partir du rapport, puis suivre les branches. Le trait violet pointillé rappelle que les rôles réutilisent les fiches.',70,2050,2340,21,'#506378')
    assert set('STR_'+n for n in placements)==set(tables)
    for name,d in domains.items():
        assert {n for n,t in tables.items() if t['domain']==name}==set(d['tables'])
    # Aucune flèche ne doit couper une carte de table.
    for source,target,pts in internal+concept:
        for a,b in zip(pts,pts[1:]):
            for n,(x,y,w,h) in rects.items():
                if not n.startswith('STR_'):continue
                hit=(x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)) if a[0]==b[0] else (y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w))
                assert not hit,(source,target,n,a,b)
    im.save(ROOT/'diagrams/images/14-vue-ensemble.png',optimize=True)
    stats=dict(page_id='page13',domains=9,tables=34,main_domain_links=len(concept),selected_table_relations=len(internal),all_table_relations_match_model=True,no_connector_crosses_a_table=True,canvas=[W,H])
    (ROOT/'quality/vue-ensemble.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return stats

if __name__=='__main__':
    path=ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio';doc=ET.parse(path)
    before=[ET.tostring(p) for p in doc.findall('diagram')[:13]]
    stats=add_overview(doc)
    assert before==[ET.tostring(p) for p in doc.findall('diagram')[:13]]
    ET.indent(doc);doc.write(path,encoding='utf-8',xml_declaration=False)
    qpath=ROOT/'quality/edition-simple.json';q=json.loads(qpath.read_text(encoding='utf-8'))
    q.update(total_pages=len(doc.findall('diagram')),overview_page=stats,first_13_pages_preserved=True)
    qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=True))
