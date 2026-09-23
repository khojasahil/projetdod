"""Page pédagogique : exemples de lecture, sans modifier le catalogue de données."""
import html,json,math
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from relational_page import FONT,BOLD

ROOT=Path(__file__).resolve().parents[1]
BG='#F3F6FA';INK='#142B46';W=2480;H=1950

def add_explanation(doc):
    model=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
    tables={t['name']:t for t in model['tables']}
    for name,cols in {
        'STR_DEFINITION':['str_report_id','ref_id','type_code'],
        'STR_CONDUCTOR':['str_report_id','ref_id','type_code','starting_action_id'],
        'STR_ACCOUNT':['starting_action_id','completing_action_id'],
        'STR_REPORT':['str_report_id','report_group_id','version_number','previous_report_id'],
        'STR_API_SUBMISSION':['str_report_id','initial_submission_id'],
    }.items():assert set(cols)<=set(tables[name]['columns'])
    for old in list(doc.getroot()):
        if old.get('id')=='page14':doc.getroot().remove(old)
    page=ET.SubElement(doc.getroot(),'diagram',id='page14',name='Comprendre les liens — quatre exemples')
    graph=ET.SubElement(page,'mxGraphModel',grid='0',page='0',background=BG,pageWidth=str(W),pageHeight=str(H),connect='1')
    root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    im=Image.new('RGB',(W,H),BG);draw=ImageDraw.Draw(im);rects={};edges=[]
    def font(s,b=False):return ImageFont.truetype(str(BOLD if b else FONT),s)
    def txt(s,x,y,size=20,color=INK,bold=False):draw.text((x,y),s,font=font(size,bold),fill=color)
    def cell(id,value,x,y,w,h,style):
        c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    def text(id,s,x,y,w=1100,size=21,color=INK,bold=False):
        assert draw.textlength(s,font=font(size,bold))<=w,(id,s)
        cell(id,html.escape(s),x,y,w,size+12,f'text;html=1;align=left;verticalAlign=top;spacing=0;fontFamily=Arial;fontSize={size};fontStyle={1 if bold else 0};fontColor={color};')
        txt(s,x,y,size,color,bold)
    def panel(id,title,sub,x,y,color):
        cell(id,'',x,y,1140,740,f'rounded=1;arcSize=4;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;')
        draw.rounded_rectangle((x,y,x+1140,y+740),radius=15,fill='white',outline=color,width=2)
        text(id+'title',title,x+25,y+22,1090,28,color,True)
        text(id+'sub',sub,x+25,y+70,1090,21,'#506378')
    boxes=[]
    def box(id,title,lines,x,y,w,h,color):
        rects[id]=(x,y,w,h);boxes.append((id,title,lines,x,y,w,h,color))
    def edge(id,source,target,pts,color,dashed=False):
        edges.append((id,source,target,pts,color,dashed))
    text('title','Comprendre les liens avec quatre exemples',60,40,2350,38,bold=True)
    text('sub','Exemple fictif : Camille effectue deux opérations pour la société A. Les extraits servent uniquement à expliquer le modèle.',60,102,2350,23)
    panel('p1','1 · Une fiche, plusieurs participations','La fiche décrit Camille. Chaque rôle décrit sa participation à une action.',60,200,'#15803D')
    panel('p2','2 · Une opération, des actions et des rôles','On précise ce qui se passe, puis qui intervient à chaque étape.',1280,200,'#C76C12')
    panel('p3','3 · Un compte appartient à une seule action','Le rattachement est initial OU final, jamais les deux à la fois.',60,1040,'#059669')
    panel('p4','4 · Une version n’est pas une tentative d’envoi','Le contenu et les appels ont des historiques distincts.',1280,1040,'#2563EB')
    box('fiche','La définition de Camille',['STR_DEFINITION → STR_PERSON','str_report_id = R-V1','ref_id = camille-5 · type_code = 5'],420,345,420,145,'#15803D')
    box('role-a','Camille exécute l’action A',['STR_CONDUCTOR · action initiale A','R-V1 · camille-5 · type 5'],100,600,480,110,'#7C3AED')
    box('role-b','Camille exécute l’action B',['STR_CONDUCTOR · action initiale B','R-V1 · camille-5 · type 5'],660,600,480,110,'#7C3AED')
    edge('cite-a','role-a','fiche',[(340,600),(340,540),(500,540),(500,490)],'#7C3AED',True)
    edge('cite-b','role-b','fiche',[(900,600),(900,540),(760,540),(760,490)],'#7C3AED',True)
    text('cite','Les deux rôles citent la même fiche, dans la même version.',235,745,920,22,bold=True)
    text('same1','Le contrôle utilise ensemble la version, le type et le refId.',90,815,1080,21)
    text('same2','Un autre type de rôle peut exiger une autre définition de Camille.',90,853,1080,21)
    text('same3','Exemple : un titulaire de compte de type 1 ne cite pas cette fiche de type 5.',90,891,1080,20,'#506378')
    box('txn','L’opération',['STR_TRANSACTION'],1690,345,360,75,'#C76C12')
    box('start','L’action initiale A',['STR_STARTING_ACTION'],1320,490,450,80,'#C76C12')
    box('end','L’action finale',['STR_COMPLETING_ACTION'],1910,490,450,80,'#C76C12')
    box('conductor','Camille effectue l’action',['STR_CONDUCTOR · cite sa fiche de type 5'],1320,640,450,80,'#7C3AED')
    box('obo','Pour le compte de la société A',['STR_ON_BEHALF_OF · cite une fiche de type 6'],1320,790,450,80,'#7C3AED')
    box('benef','Le bénéficiaire déclaré',['STR_BENEFICIARY · fiche de type 3 ou 4'],1910,640,450,80,'#7C3AED')
    edge('ts','txn','start',[(1770,420),(1770,455),(1545,455),(1545,490)],'#C76C12')
    edge('te','txn','end',[(1970,420),(1970,455),(2135,455),(2135,490)],'#C76C12')
    edge('sc','start','conductor',[(1545,570),(1545,640)],'#C76C12')
    edge('co','conductor','obo',[(1545,720),(1545,790)],'#7C3AED')
    edge('eb','end','benef',[(2135,570),(2135,640)],'#C76C12')
    text('op-note1','On peut avoir plusieurs actions de chaque côté.',1850,800,500,20)
    text('op-note2','Le dessin montre une sélection des rôles.',1850,836,500,20,'#506378')
    text('op-note3','La société représentée n’est pas automatiquement la source des fonds.',1310,898,1080,20,'#506378')
    box('option-start','Action initiale A',['STR_STARTING_ACTION'],100,1180,450,90,'#C76C12')
    box('option-end','Action finale B',['STR_COMPLETING_ACTION'],680,1180,450,90,'#C76C12')
    box('account','Le compte de l’action',['STR_ACCOUNT','starting_action_id OU completing_action_id','Une seule de ces deux clés est renseignée.'],380,1400,490,145,'#059669')
    edge('acc-start','option-start','account',[(325,1270),(325,1350),(500,1350),(500,1400)],'#059669',True)
    edge('acc-end','option-end','account',[(905,1270),(905,1350),(750,1350),(750,1400)],'#059669',True)
    text('xor','Choisir un seul rattachement',420,1310,520,23,'#059669',True)
    text('account1','Si le compte est lié à A : starting_action_id = A, l’autre clé reste vide.',90,1605,1080,21)
    text('account2','S’il est lié à B : completing_action_id = B, l’autre clé reste vide.',90,1647,1080,21)
    text('account3','La même règle s’applique aux données de monnaie virtuelle (STR_VC_DATA).',90,1698,1080,20,'#506378')
    box('v1','Le rapport, version 1',['STR_REPORT · str_report_id = R-V1','report_group_id = DOSSIER-A','version_number = 1'],1320,1180,450,150,'#2563EB')
    box('v2','Le rapport corrigé, version 2',['STR_REPORT · str_report_id = R-V2','Même groupe · version_number = 2','previous_report_id = R-V1'],1930,1180,450,150,'#2563EB')
    edge('correction','v1','v2',[(1770,1255),(1930,1255)],'#2563EB')
    text('corr-label','Correction',1790,1210,130,20,'#2563EB')
    box('calls1','Les appels liés à R-V1',['STR_API_SUBMISSION','1 ligne pour l’envoi','1 autre ligne pour la consultation du résultat'],1320,1430,450,150,'#64748B')
    box('calls2','L’appel lié à R-V2',['STR_API_SUBMISSION','1 ligne pour l’envoi de la correction','Les appels de R-V1 restent conservés.'],1930,1430,450,150,'#64748B')
    edge('v1calls','v1','calls1',[(1545,1330),(1545,1430)],'#64748B')
    edge('v2calls','v2','calls2',[(2155,1330),(2155,1430)],'#64748B')
    text('versions1','Corriger un contenu gelé crée une nouvelle version et ses propres lignes enfants.',1310,1640,1080,21)
    text('versions2','Consulter le résultat ajoute un appel, sans créer une nouvelle version.',1310,1680,1080,21)
    text('versions3','Une réponse HTTP positive ne suffit pas à prouver l’acceptation du rapport.',1310,1720,1080,20,'#506378')
    # Flèches pédagogiques. Les sens « cite » et « contient » sont explicités par les panneaux.
    for id,s,t,pts,color,dashed in edges:
        sx,sy,sw,sh=rects[s];tx,ty,tw,th=rects[t];a=pts[0];b=pts[-1]
        style=f'edgeStyle=none;rounded=0;strokeWidth=2;strokeColor={color};endArrow=block;endFill=1;endSize=10;exitX={(a[0]-sx)/sw};exitY={(a[1]-sy)/sh};exitPerimeter=0;entryX={(b[0]-tx)/tw};entryY={(b[1]-ty)/th};entryPerimeter=0;'+('dashed=1;' if dashed else '')
        c=ET.SubElement(root,'mxCell',id=id,edge='1',parent='1',source=s,target=t,style=style)
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        for a,b in zip(pts,pts[1:]):
            assert a[0]==b[0] or a[1]==b[1]
            dist=math.dist(a,b)
            if dashed:
                for k in range(0,int(dist),18):
                    f=k/max(1,dist);ff=min(k+10,dist)/max(1,dist)
                    draw.line((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,a[0]+(b[0]-a[0])*ff,a[1]+(b[1]-a[1])*ff),fill=color,width=2)
            else:draw.line((a,b),fill=color,width=2)
            for n,(x,y,w,h) in rects.items():
                hit=(x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)) if a[0]==b[0] else (y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w))
                assert not hit,(id,n)
        a,b=pts[-2:];dist=math.dist(a,b);ux=(b[0]-a[0])/dist;uy=(b[1]-a[1])/dist
        draw.polygon([b,(b[0]-10*ux+5*uy,b[1]-10*uy-5*ux),(b[0]-10*ux-5*uy,b[1]-10*uy+5*ux)],fill=color)
    for id,title,lines,x,y,w,h,color in boxes:
        assert draw.textlength(title,font=font(21,True))<w-32,(id,title)
        for line in lines:assert draw.textlength(line,font=font(18))<w-32,(id,line)
        assert 18+30+len(lines)*27<=h,(id,h)
        val=f'<b style="font-size:21px;line-height:30px">{html.escape(title)}</b><br><span style="font-size:18px;line-height:27px">'+'<br>'.join(html.escape(s) for s in lines)+'</span>'
        cell(id,val,x,y,w,h,f'rounded=1;arcSize=8;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingTop=12;spacingLeft=16;spacingRight=12;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;fontFamily=Arial;fontColor={INK};')
        draw.rounded_rectangle((x,y,x+w,y+h),radius=9,fill='white',outline=color,width=2)
        txt(title,x+16,y+12,21,INK,True)
        for j,line in enumerate(lines):txt(line,x+16,y+46+j*27,18)
    text('foot1','À retenir : la fiche décrit qui; le rôle décrit la participation; la version fixe le contenu; l’appel garde la trace de la transmission.',60,1830,2350,23,bold=True)
    text('foot2','Pour les autres sujets : SCHEMAS_EXPLICATIFS.md explique aussi les types de fiches, les adresses, la propriété et la traçabilité Swagger.',60,1880,2350,22,'#506378')
    im.save(ROOT/'diagrams/images/15-comprendre-les-liens.png',optimize=True)
    stats=dict(page_id='page14',teaching_panels=4,example_cards=len(boxes),teaching_connectors=len(edges),model_fields_checked=True,no_connector_crosses_a_card=True,canvas=[W,H])
    (ROOT/'quality/page-pedagogique.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return stats

if __name__=='__main__':
    path=ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio';doc=ET.parse(path)
    before=[ET.tostring(p) for p in doc.findall('diagram')[:14]]
    stats=add_explanation(doc)
    assert before==[ET.tostring(p) for p in doc.findall('diagram')[:14]]
    ET.indent(doc);doc.write(path,encoding='utf-8',xml_declaration=False)
    qpath=ROOT/'quality/edition-simple.json';q=json.loads(qpath.read_text(encoding='utf-8'))
    q.update(total_pages=len(doc.findall('diagram')),explanation_page=stats,first_14_pages_preserved=True)
    qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=True))
