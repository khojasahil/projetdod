"""Deux vues de lecture, sans réécrire les onze pages déjà livrées."""
import html, json, math, heapq, hashlib
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from relational_page import FONT, BOLD

ROOT = Path(__file__).resolve().parents[1]
BG = '#F3F6FA'
SECTIONS = [
    ('01', 'Le dossier et les envois', 'Une version du rapport peut faire l’objet de plusieurs tentatives d’envoi.', [
        ['REPORT'], ['PPP_PROJECT', 'RELATED_REPORT', 'AUDIT_EVENT'],
        ['RELATED_REPORT_TXN_REF', 'API_SUBMISSION'], ['SUBMITTED_PAYLOAD', 'VALIDATION_ERROR']]),
    ('02', 'Les personnes et les organisations', 'La fiche décrit la personne ou l’entité; les tables de propriété précisent qui la dirige ou la détient.', [
        ['DEFINITION', 'ADDRESS'], ['PERSON', 'ENTITY', 'IDENTIFICATION'],
        ['EMPLOYER_INFO', 'REGISTRATION_INCORPORATION', 'AUTHORIZED_PERSON', 'DIRECTOR', 'SHARE_OWNER'],
        ['TRUSTEE', 'SETTLOR', 'TRUST_UNIT_OWNER', 'TRUST_BENEFICIARY', 'OTHER_ENTITY_OWNER']]),
    ('03', 'Les opérations, les rôles et les comptes', 'Suivez l’opération, puis l’action, puis les personnes et les comptes qui interviennent.', [
        ['TRANSACTION'], ['STARTING_ACTION', 'COMPLETING_ACTION'],
        ['CONDUCTOR', 'SOURCE_OF_FUNDS', 'INVOLVEMENT', 'BENEFICIARY'],
        ['ON_BEHALF_OF', 'ACCOUNT', 'ACCOUNT_HOLDER', 'VC_DATA']]),
]

def build_page(doc, model, keys_only):
    tables = {t['name']: t for t in model['tables']}
    rels = model['relationships']
    page_id = 'page12' if keys_only else 'page11'
    slug = '13-relations-pk-fk' if keys_only else '12-modele-aere'
    title = 'Relations — PK et FK seulement' if keys_only else 'Modèle complet — lecture aérée'
    for old in list(doc.getroot()):
        if old.get('id') == page_id: doc.getroot().remove(old)
    fk = {n: set() for n in tables}; referenced = {n: set() for n in tables}
    for r in rels:
        fk[r['child']].update(r['foreign_key'].split(', '))
        referenced[r['parent']].update(r['parent_key'].split(', '))
    fields = {}
    for n,t in tables.items():
        selected = {t['pk']} | fk[n] | referenced[n]
        # Les clés restent en tête, les autres attributs suivent dans l’ordre du dictionnaire.
        fields[n] = [t['pk']] + [c for c in t['columns'] if c != t['pk'] and c in selected]
        if not keys_only: fields[n] += [c for c in t['columns'] if c not in selected]
    width = 570 if keys_only else 800
    gap = 200
    W = 2*100 + 4*width + 3*gap
    positions = {}; headings = []; y = 520
    for num,label,note,lanes in SECTIONS:
        headings.append((num,label,note,y))
        ends = []
        for lane,names in enumerate(lanes):
            yy = y + 125
            for name in names:
                n = 'STR_'+name; height = 142 + 30*len(fields[n])
                positions[n] = (100 + lane*(width+gap), yy, width, height)
                yy += height + 120
            ends.append(yy)
        y = max(ends) + 110
    H = y + 310
    assert set(positions) == set(tables)
    # Les chemins sont orthogonaux et évitent les rectangles des tables.
    step = 20; blocked = set(); used = defaultdict(int)
    for x,y,w,h in positions.values():
        for gx in range(math.ceil((x-20)/step), math.floor((x+w+20)/step)+1):
            for gy in range(math.ceil((y-20)/step), math.floor((y+h+20)/step)+1): blocked.add((gx,gy))
    def route(start,goal):
        queue=[(0,0,*start,-1)]; best={(*start,-1):0}; prev={}; last=None
        while queue:
            _,cost,x,y,d=heapq.heappop(queue); state=(x,y,d)
            if cost != best.get(state): continue
            if (x,y)==goal: last=state; break
            for nd,(dx,dy) in enumerate(((1,0),(-1,0),(0,1),(0,-1))):
                xx,yy=x+dx,y+dy
                if not (1<=xx<W//step and 24<=yy<H//step) or (xx,yy) in blocked: continue
                nc=cost+10+(16 if d!=-1 and d!=nd else 0)+min(used[xx,yy]*12,60)
                ns=(xx,yy,nd)
                if nc < best.get(ns,float('inf')):
                    best[ns]=nc;prev[ns]=state
                    heapq.heappush(queue,(nc+10*(abs(xx-goal[0])+abs(yy-goal[1])),nc,xx,yy,nd))
        assert last is not None, (start,goal)
        path=[]
        while last in prev: path.append(last[:2]);last=prev[last]
        path.append(start);path.reverse()
        for pt in path:used[pt]+=1
        reduced=[path[0]]
        for a,b,c in zip(path,path[1:],path[2:]):
            if (b[0]-a[0],b[1]-a[1])!=(c[0]-b[0],c[1]-b[1]):reduced.append(b)
        reduced.append(path[-1])
        return [(x*step,y*step) for x,y in reduced]
    def port(n,key,side):
        x,y,w,h=positions[n];parts=key.split(', ')
        field=next((c for c in parts if c!='str_report_id'),parts[0])
        xx=x if side==0 else x+w;yy=y+127+30*fields[n].index(field)
        gx=math.floor((xx-50)/step) if side==0 else math.ceil((xx+50)/step)
        return (xx,yy),(gx,round(yy/step)),(side,(yy-y)/h)
    def layer(r):
        if r['parent']=='STR_REPORT':return 'report-links'
        if r['parent']=='STR_DEFINITION' and ',' in r['parent_key']:return 'role-links'
        return 'business-links'
    edges=[]
    for i in sorted(range(len(rels)),key=lambda i:layer(rels[i])!='business-links'):
        r=rels[i];a=r['parent'];b=r['child'];ax=positions[a][0];bx=positions[b][0]
        sa,sb=(1,0) if ax<bx else (0,1) if ax>bx else (0,0)
        ap,ag,aa=port(a,r['parent_key'],sa);bp,bg,ba=port(b,r['foreign_key'],sb)
        mid=route(ag,bg);pts=[ap,(mid[0][0],ap[1])]+mid+[(mid[-1][0],bp[1]),bp]
        pts=[p for j,p in enumerate(pts) if j==0 or p!=pts[j-1]]
        edges.append(dict(id=f'R{i+1:02}',r=r,pts=pts,aa=aa,ba=ba,layer=layer(r)))
    page=ET.SubElement(doc.getroot(),'diagram',id=page_id,name=title)
    graph=ET.SubElement(page,'mxGraphModel',grid='0',page='0',pageWidth=str(W),pageHeight=str(H),background=BG,connect='1',guides='1')
    root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0')
    for id,label,visible in [('report-links','À afficher · rattachement au rapport (34 liens)',False),('role-links','À afficher · fiches des intervenants (6 liens)',False),('business-links','Relations métier (37 liens)',True),('1','Tables et mode de lecture',True)]:
        ET.SubElement(root,'mxCell',id=id,value=label,parent='0',visible='1' if visible else '0')
    im=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(im)
    def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
    def txt(s,x,y,size=20,color='#24364B',bold=False):draw.text((x,y),s,font=font(size,bold),fill=color)
    def cell(id,value,x,y,w,h,style):
        c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        return c
    def text(id,s,x,y,size=22,bold=False,color='#24364B'):
        cell(id,html.escape(s),x,y,W-200,size+14,f'text;html=1;align=left;verticalAlign=top;spacing=0;fontFamily=Arial;fontSize={size};fontStyle={1 if bold else 0};fontColor={color};')
        txt(s,x,y,size,color,bold)
    text('title',title,100,45,38,True,'#142B46')
    count=sum(map(len,fields.values()))
    text('subtitle',f'34 tables · {count} '+('champs de clés' if keys_only else 'colonnes')+' · 77 relations disponibles · Une table = un bloc de texte.',100,108,23)
    notes=[
        'Commencez par les 37 liens métier affichés. Les deux autres familles de liens sont accessibles dans Vue > Calques.',
        'Le champ str_report_id rattache chaque ligne à STR_REPORT. Ses 34 liens sont masqués au départ pour éviter les longues traversées.',
        'Les 6 liens des rôles vers DEFINITION sont également dans un calque séparé. Aucune relation n’a été supprimée.',
        'PK = clé primaire · FK = clé étrangère · UK* = composant de la clé unique référencée de DEFINITION.',
        'Les extrémités indiquent 1, zéro ou un (0..1), ou zéro à plusieurs (0..N). R01–R77 renvoient au registre des relations.',
        'Les couleurs identifient les neuf domaines. Parcourez les trois sections de haut en bas, puis les tables de gauche à droite.'
    ]
    for j,s in enumerate(notes):text('note'+str(j),s,100,168+j*43,21)
    for num,label,note,yy in headings:
        draw.rounded_rectangle((75,yy,W-75,yy+92),radius=12,fill='#E3EBF4')
        cell('section'+num,f'<b>{num} — {html.escape(label)}</b><br><span style="font-size:20px">{html.escape(note)}</span>',75,yy,W-150,92,'rounded=1;arcSize=12;html=1;align=left;verticalAlign=middle;spacingLeft=25;fillColor=#E3EBF4;strokeColor=none;fontFamily=Arial;fontSize=27;fontColor=#142B46;')
        txt(num+' — '+label,100,yy+12,27,'#142B46',True);txt(note,100,yy+52,20)
    for e in edges:
        r=e['r'];visible=e['layer']=='business-links';color=tables[r['parent']]['color'] if visible else '#8796AA'
        sx,sy=e['aa'];tx,ty=e['ba']
        start='ERzeroToOne' if r['optional_fk'] else 'ERone';end='ERzeroToMany' if r['cardinality']=='0..N' else 'ERzeroToOne'
        style=f'edgeStyle=none;rounded=0;html=1;strokeColor={color};strokeWidth=2;startArrow={start};endArrow={end};startSize=16;endSize=16;exitX={sx};exitY={sy};exitPerimeter=0;entryX={tx};entryY={ty};entryPerimeter=0;fontSize=14;fontColor={color};labelBackgroundColor={BG};'+('dashed=1;' if not visible else '')
        c=ET.SubElement(root,'mxCell',id=e['id'],value=e['id'],style=style,edge='1',parent=e['layer'],source=r['parent'],target=r['child'])
        g=ET.SubElement(c,'mxGeometry',x='0.8',y='-10',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in e['pts'][1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        if visible:
            draw.line(e['pts'],fill=color,width=2)
            # Cardinalités textuelles sur l’aperçu; symboles ER natifs dans draw.io.
            x,y=e['pts'][-2];txt(e['id']+' '+r['cardinality'],x+4,y-21,14,color)
    for n,t in tables.items():
        x,y,w,h=positions[n];color=t['color']
        label=f'<div style="font-size:24px;line-height:32px;font-weight:bold;color:#142B46">{html.escape(t["label"])}</div>'
        label+=f'<div style="font-size:16px;line-height:26px;font-weight:bold;color:{color}">{n}</div>'
        label+=f'<div style="font-size:14px;line-height:22px;color:#5E7185;margin-bottom:16px">{html.escape(t["domain"])}</div>'
        draw.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='white',outline=color,width=2)
        txt(t['label'],x+20,y+16,24,'#142B46',True);txt(n,x+20,y+48,16,color,True);txt(t['domain'],x+20,y+74,14,'#5E7185')
        values=[]
        for j,col in enumerate(fields[n]):
            flags=[]
            if col==t['pk']:flags.append('PK')
            if col in fk[n]:flags.append('FK')
            if n=='STR_DEFINITION' and col in referenced[n] and col!=t['pk']:flags.append('UK*')
            s=('['+'/'.join(flags)+'] ' if flags else '')+col
            if not keys_only:s+=' : '+t['columns'][col]['type']
            assert draw.textlength(s,font=font(18,col==t['pk'])) < w-40,(n,s)
            values.append('<b>'+html.escape(s)+'</b>' if col==t['pk'] else html.escape(s))
            txt(s,x+20,y+112+j*30,18,'#24364B',col==t['pk'])
        label+='<div style="font-size:18px;line-height:30px">'+'<br>'.join(values)+'</div>'
        cell(n,label,x,y,w,h,f'rounded=1;arcSize=5;whiteSpace=wrap;html=1;overflow=visible;align=left;verticalAlign=top;spacing=0;spacingTop=16;spacingLeft=20;spacingRight=20;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;fontFamily=Arial;fontSize=18;fontColor=#24364B;')
    foot=H-250
    for j,s in enumerate([
        'À retenir pour expliquer le modèle',
        'DEFINITION : UK* désigne ensemble (str_report_id, type_code, ref_id). Aucune de ces colonnes n’est unique à elle seule.',
        'Les liens vers un sous-objet restent dans la même version du rapport. Une correction crée une nouvelle version; un nouvel essai crée un envoi.',
        'ACCOUNT et VC_DATA : renseigner une seule action, initiale ou finale. Les deux FK facultatives représentent cette alternative.',
        'Une ligne de champ suffit pour modifier une table. Les connecteurs restent attachés aux clés; le registre précise les clés composites.'
    ]):text('footer'+str(j),s,100,foot+j*40,21,j==0)
    # Cohérence du contenu et des points d’attache, indépendamment de l’affichage.
    cells={c.get('id'):c for c in root.findall('mxCell')}
    assert len([c for c in cells.values() if c.get('edge')=='1'])==77
    assert sum(e['layer']=='business-links' for e in edges)==37
    assert sum(e['layer']=='report-links' for e in edges)==34
    assert sum(e['layer']=='role-links' for e in edges)==6
    for n,t in tables.items():
        expected={t['pk']} | fk[n] | referenced[n] if keys_only else set(t['columns'])
        assert set(fields[n])==expected and len(fields[n])==len(expected)
        assert cells[n].get('vertex')=='1'
    for i,r in enumerate(rels):
        c=cells[f'R{i+1:02}'];assert c.get('source')==r['parent'] and c.get('target')==r['child']
        assert set(r['foreign_key'].split(', ')) <= set(fields[r['child']])
        assert set(r['parent_key'].split(', ')) <= set(fields[r['parent']])
    for e in edges:
        for a,b in zip(e['pts'],e['pts'][1:]):
            assert a[0]==b[0] or a[1]==b[1]
            for n,(x,y,w,h) in positions.items():
                hit=(x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)) if a[0]==b[0] else (y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w))
                assert not hit,(e['id'],n)
    im.save(ROOT/f'diagrams/images/{slug}.png',optimize=True)
    return dict(page_id=page_id,tables=len(tables),columns=count,connectors=len(edges),visible_connectors=37,report_links_in_optional_layer=34,role_links_in_optional_layer=6,no_connector_crosses_a_table=True,canvas=[W,H])

def add_pages(doc):
    model=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
    stats=[build_page(doc,model,False),build_page(doc,model,True)]
    (ROOT/'quality/vues-lisibles.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return stats

if __name__=='__main__':
    path=ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio';doc=ET.parse(path)
    before=[ET.tostring(p) for p in doc.findall('diagram')[:11]]
    original=ROOT/'diagrams/CANAFE_DOD.drawio';digest=hashlib.sha256(original.read_bytes()).hexdigest()
    stats=add_pages(doc)
    assert before==[ET.tostring(p) for p in doc.findall('diagram')[:11]]
    ET.indent(doc);doc.write(path,encoding='utf-8',xml_declaration=False)
    assert hashlib.sha256(original.read_bytes()).hexdigest()==digest
    qpath=ROOT/'quality/edition-simple.json';quality=json.loads(qpath.read_text(encoding='utf-8'))
    quality.update(total_pages=len(doc.findall('diagram')),readable_pages=stats,first_11_pages_preserved=True)
    qpath.write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=True))
