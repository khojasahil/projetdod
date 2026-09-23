"""Page relationnelle complète : 34 formes, 365 champs et 77 connecteurs.

Les chemins passent dans les espaces entre les tables. Le calcul de parcours
ne dépend d’aucun service externe et ne modifie aucune autre page.
"""
import html,json,math,heapq,hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
STEP=20;CW=950;TOP=600;BG='#F3F6FA'
FONT=Path('C:/Windows/Fonts/arial.ttf');BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
if not FONT.exists():FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');BOLD=FONT.with_name('DejaVuSans-Bold.ttf')

def add_page(doc):
    model=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
    scene=json.loads((ROOT/'model/presentation.json').read_text(encoding='utf-8'))[-1]
    tables={t['name']:t for t in model['tables']};relations=model['relationships']
    for old in list(doc.getroot()):
        if old.get('id')=='page10':doc.getroot().remove(old)
    positions={}
    for i in scene['items']:
        if i['id'] in tables and i['kind']=='rect':
            t=tables[i['id']]
            positions[t['name']]=(round(i['x']*1.35)+80,i['y'],CW,159+30*len(t['columns']))
    W=math.ceil((max(x+w for x,y,w,h in positions.values())+200)/STEP)*STEP
    H=math.ceil((max(y+h for x,y,w,h in positions.values())+160)/STEP)*STEP
    nx=W//STEP;ny=H//STEP
    blocked=set()
    for x,y,w,h in positions.values():
        for gx in range(math.ceil((x-18)/STEP),math.floor((x+w+18)/STEP)+1):
            for gy in range(math.ceil((y-18)/STEP),math.floor((y+h+18)/STEP)+1):blocked.add((gx,gy))
    used=defaultdict(int)
    def route(start,goal):
        # Le changement de direction et les voies déjà occupées ont un coût.
        q=[(0,0,start[0],start[1],-1)];best={(start[0],start[1],-1):0};prev={};last=None
        while q:
            _,cost,x,y,d=heapq.heappop(q);state=(x,y,d)
            if cost!=best.get(state):continue
            if (x,y)==goal:last=state;break
            for nd,(dx,dy) in enumerate(((1,0),(-1,0),(0,1),(0,-1))):
                xx,yy=x+dx,y+dy
                if not(1<=xx<nx and TOP//STEP<=yy<ny) or (xx,yy) in blocked:continue
                nc=cost+10+(8 if d!=-1 and d!=nd else 0)+min(used[(xx,yy)]*7,35)
                ns=(xx,yy,nd)
                if nc<best.get(ns,float('inf')):
                    best[ns]=nc;prev[ns]=state
                    heuristic=10*(abs(xx-goal[0])+abs(yy-goal[1]))
                    heapq.heappush(q,(nc+heuristic,nc,xx,yy,nd))
        assert last is not None,('Aucun passage',start,goal)
        path=[]
        while last in prev:path.append(last[:2]);last=prev[last]
        path.append(start);path.reverse()
        for pt in path:used[pt]+=1
        reduced=[path[0]]
        for a,b,c in zip(path,path[1:],path[2:]):
            if (b[0]-a[0],b[1]-a[1])!=(c[0]-b[0],c[1]-b[1]):reduced.append(b)
        reduced.append(path[-1]);return [(x*STEP,y*STEP) for x,y in reduced]
    def port(table,key,side):
        x,y,w,h=positions[table];cols=list(tables[table]['columns'])
        keyparts=key.split(', ');field=next((k for k in keyparts if k!='str_report_id'),keyparts[0])
        yy=y+132+cols.index(field)*30;xx=x if side=='left' else x+w
        gx=math.floor((xx-48)/STEP) if side=='left' else math.ceil((xx+48)/STEP)
        gy=round(yy/STEP)
        assert (gx,gy) not in blocked
        return (xx,yy),(gx,gy),(0 if side=='left' else 1,(yy-y)/h)
    edges=[]
    # Liens métier routés en premier; liens de portée routés ensuite et affichés dessous.
    order=sorted(range(len(relations)),key=lambda i:relations[i]['parent']=='STR_REPORT')
    for i in order:
        r=relations[i];a=r['parent'];b=r['child'];ax,ay,aw,ah=positions[a];bx,by,bw,bh=positions[b]
        if ax<bx:sa,sb='right','left'
        elif ax>bx:sa,sb='left','right'
        else:sa=sb='left' if ax<W/2 else 'right'
        ap,ag,aa=port(a,r['parent_key'],sa);bp,bg,ba=port(b,r['foreign_key'],sb)
        mid=route(ag,bg)
        pts=[ap,(mid[0][0],ap[1])]+mid+[(mid[-1][0],bp[1]),bp]
        # Enlever les doublons; les routes conservent leur orthogonalité.
        pts=[pt for j,pt in enumerate(pts) if j==0 or pt!=pts[j-1]]
        edges.append(dict(index=i,id=f'R{i+1:02}',relation=r,points=pts,exit=aa,entry=ba,scope=a=='STR_REPORT'))
    diagram=ET.SubElement(doc.getroot(),'diagram',id='page10',name='Relations complètes — PK, FK et cardinalités')
    graph=ET.SubElement(diagram,'mxGraphModel',grid='0',page='0',pageWidth=str(W),pageHeight=str(H),background=BG,connect='1',guides='1')
    root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0')
    ET.SubElement(root,'mxCell',id='scope',value='Liens vers la version du rapport',parent='0')
    ET.SubElement(root,'mxCell',id='relations',value='Relations métier et audit',parent='0')
    ET.SubElement(root,'mxCell',id='1',value='Tables et explications',parent='0')
    im=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(im)
    def draw_text(s,x,y,size=17,color='#24364B',bold=False):draw.text((x,y),s,font=ImageFont.truetype(str(BOLD if bold else FONT),size),fill=color)
    def cell(id,value,x,y,w,h,style):
        c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'});return c
    def text(id,s,x,y,w,size=20,color='#142B46',bold=False):
        cell(id,html.escape(s),x,y,w,size+16,f'text;html=1;align=left;verticalAlign=top;spacing=0;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};')
        draw_text(s,x,y,size,color,bold)
    text('title','Toutes les relations du modèle DOD / STR',80,45,W-160,38,bold=True)
    text('sub','34 tables · 365 colonnes · 77 connecteurs attachés aux clés · Chaque table reste un seul bloc éditable.',80,110,W-160,22)
    note_lines=[
        'PK : clé primaire. FK : clé étrangère. Une ligne peut porter plusieurs repères lorsqu’elle participe à plusieurs liens.',
        'Chaque trait relie la clé du parent à la clé portée par l’enfant. R01 à R77 permettent de retrouver la relation dans le registre.',
        'Côté parent : 1 si la clé enfant est requise, 0..1 si elle est facultative. Côté enfant : 0..1 ou 0..N selon le nombre de lignes possibles.',
        'Les traits bleus pointillés rattachent les données à la version du rapport. Les traits colorés montrent les autres relations.',
        'Tous les liens sont visibles. Dans les calques, vous pouvez masquer temporairement les liens vers le rapport pour lire les autres relations.',
        'Les références composites des rôles portent sur (str_report_id, type_code, ref_id). Les clés de parents sont contrôlées dans la même version.',
        'ACCOUNT et VC_DATA : une seule clé d’action est renseignée, initiale ou finale. Les obligations avant envoi restent celles du dictionnaire.'
    ]
    for j,s in enumerate(note_lines):text('note'+str(j),s,80,180+j*43,W-160,21)
    x=80
    for d in model['domains']:
        title=d['name'];text('domain-'+title,title,x,525,1100,20,d['color'],True);x+=max(530,len(title)*15)
    # Toutes les relations existent en tant que vrais connecteurs, aucune n’est masquée.
    for e in sorted(edges,key=lambda e:not e['scope']):
        r=e['relation'];color='#9BAEC6' if e['scope'] else tables[r['parent']]['color'];pts=e['points']
        dashed='dashed=1;dashPattern=5 4;' if e['scope'] else ''
        start='ERzeroToOne' if r['optional_fk'] else 'ERone';end='ERzeroToMany' if r['cardinality']=='0..N' else 'ERzeroToOne'
        sx,sy=e['exit'];tx,ty=e['entry']
        style=f'edgeStyle=none;rounded=0;html=1;strokeColor={color};strokeWidth=1.5;{dashed}startArrow={start};endArrow={end};startSize=14;endSize=14;exitX={sx};exitY={sy};exitPerimeter=0;entryX={tx};entryY={ty};entryPerimeter=0;fontSize=14;fontColor={color};labelBackgroundColor={BG};'
        c=ET.SubElement(root,'mxCell',id=e['id'],value=e['id']+' · '+r['cardinality'],style=style,edge='1',parent='scope' if e['scope'] else 'relations',source=r['parent'],target=r['child'])
        g=ET.SubElement(c,'mxGeometry',x='0.65',y='-12',relative='1',attrib={'as':'geometry'})
        arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        if e['scope']:
            for a,b in zip(pts,pts[1:]):
                distance=abs(a[0]-b[0])+abs(a[1]-b[1])
                for offset in range(0,int(distance),18):
                    f=offset/max(distance,1);ff=min(offset+10,distance)/max(distance,1)
                    draw.line((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,a[0]+(b[0]-a[0])*ff,a[1]+(b[1]-a[1])*ff),fill=color,width=2)
        else:draw.line(pts,fill=color,width=2)
        # L’aperçu utilise des extrémités textuelles; draw.io utilise les symboles ER.
        px,py=pts[-2];draw_text(e['id']+' '+r['cardinality'],px+3,py-18,12,color)
    for n,t in tables.items():
        x,y,w,h=positions[n];color=t['color'];cols=list(t['columns'])
        label=f'<div style="font-size:23px;line-height:30px;font-weight:bold;color:#142B46;margin-bottom:7px;">{html.escape(t["label"])}</div>'
        label+=f'<div style="font-size:16px;line-height:23px;font-weight:bold;color:{color};margin-bottom:5px;">{n}</div>'
        label+=f'<div style="font-size:14px;line-height:21px;color:#5E7185;margin-bottom:14px;">{t["domain"]}</div>'
        values=[]
        draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='#FFFFFF',outline=color,width=2)
        draw_text(t['label'],x+22,y+17,23,'#142B46',True);draw_text(n,x+22,y+54,16,color,True);draw_text(t['domain'],x+22,y+82,14,'#5E7185')
        for j,col in enumerate(cols):
            fk=any(r['child']==n and col in r['foreign_key'].split(', ') for r in relations)
            flags=('PK' if col==t['pk'] else '')+(', FK' if col==t['pk'] and fk else 'FK' if fk else '')
            s=col+' : '+t['columns'][col]['type']+(' ['+flags+']' if flags else '')
            values.append('<b>'+html.escape(s)+'</b>' if col==t['pk'] else html.escape(s))
            draw_text(s,x+22,y+117+j*30,17,'#24364B',col==t['pk'])
        label+='<div style="font-size:17px;line-height:30px;">'+'<br>'.join(values)+'</div>'
        cell(n,label,x,y,w,h,f'rounded=1;arcSize=6;whiteSpace=wrap;html=1;overflow=visible;align=left;verticalAlign=top;spacing=0;spacingTop=17;spacingLeft=22;spacingRight=18;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;fontFamily=Arial;fontSize=17;fontColor=#24364B;')
    # Contrôle indépendant des segments : aucun trait ne passe dans une autre table.
    for e in edges:
        for a,b in zip(e['points'],e['points'][1:]):
            assert a[0]==b[0] or a[1]==b[1]
            for n,(x,y,w,h) in positions.items():
                if a[0]==b[0]:hit=x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)
                else:hit=y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w)
                assert not hit,(e['id'],n,a,b)
    assert len(edges)==77 and len(positions)==34
    xmlcells={c.get('id'):c for c in root.findall('mxCell')}
    assert len([c for c in xmlcells.values() if c.get('edge')=='1'])==len(relations)
    for n,t in tables.items():
        value=html.unescape(xmlcells[n].get('value'))
        for col in t['columns']:
            assert col+' :' in value
            rendered=col+' : '+t['columns'][col]['type']
            if col==t['pk']:assert rendered+' [PK' in value
            if any(r['child']==n and col in r['foreign_key'].split(', ') for r in relations):assert rendered+' [FK]' in value or rendered+' [PK, FK]' in value
    for i,r in enumerate(relations):
        c=xmlcells[f'R{i+1:02}']
        assert c.get('source')==r['parent'] and c.get('target')==r['child']
        assert c.get('visible')!='0' and xmlcells[c.get('parent')].get('visible')!='0'
    im.save(ROOT/'diagrams/images/11-relations-completes.png',optimize=True)
    lines=['# Relations de la page 11','', 'Les identifiants R01 à R77 correspondent aux connecteurs du fichier simple. Les clés vers un sous-objet sont aussi contrôlées dans la même version du rapport.','',
           '| Trait | Parent | Clé parent | Enfant | Clé étrangère | Parents par enfant | Enfants par parent |','|---|---|---|---|---|---|---|']
    for i,r in enumerate(relations):lines.append('| '+' | '.join([f'R{i+1:02}',r['parent'],r['parent_key'],r['child'],r['foreign_key'],'0..1' if r['optional_fk'] else '1',r['cardinality']])+' |')
    (ROOT/'docs/RELATIONS_PAGE11.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    stats={'page_id':'page10','tables':34,'columns':sum(len(t['columns']) for t in tables.values()),'connectors':len(edges),'all_relations_visible':True,'one_shape_per_table':True,'no_connector_crosses_a_table':True,'canvas':[W,H]}
    (ROOT/'quality/page-relationnelle.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return stats

if __name__=='__main__':
    path=ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio';doc=ET.parse(path)
    before=[ET.tostring(p) for p in doc.findall('diagram')[:10]]
    stats=add_page(doc)
    assert before==[ET.tostring(p) for p in doc.findall('diagram')[:10]]
    ET.indent(doc);doc.write(path,encoding='utf-8',xml_declaration=False)
    print(json.dumps(stats,ensure_ascii=True))
