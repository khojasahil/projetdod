"""Même composition pour les images du README et les objets modifiables draw.io."""
import html,json,math,textwrap
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
T={x['name']:x for x in M['tables']}
NAVY='#142B46';INK='#24364B';MUTED='#5E7185';LINE='#D8E2EC';BG='#F3F6FA'
FONT=Path('C:/Windows/Fonts/arial.ttf');BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
if not FONT.exists():FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');BOLD=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
PAGES=[]
def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
def wrap(s,width,size=18,bold=False):
    f=font(size,bold);lines=[]
    for paragraph in s.split('\n'):
        line=''
        for word in paragraph.split():
            v=(line+' '+word).strip()
            if f.getlength(v)>width and line:lines.append(line);line=word
            else:line=v
        lines.append(line)
    return lines
class Page:
    def __init__(self,slug,title,subtitle,num,w=1600,h=1100):
        self.slug=slug;self.title=title;self.w=w;self.h=h;self.items=[];self.cards={};self.edges=[]
        self.rect('background',0,0,w,h,BG,BG,0)
        self.text('kicker','CANAFE  /  DOD–STR  /  MODÈLE DE DONNÉES',48,28,1300,14,MUTED,True)
        self.text('title',title,48,64,1480,36,NAVY,True)
        self.text('subtitle',subtitle,48,114,1480,19,MUTED)
        self.text('footer',f'PROJET DOD   •   Architecture reprise de projet-io   |   {num:02}',48,h-32,1480,13,MUTED)
    def rect(self,id,x,y,w,h,fill='#FFFFFF',stroke=LINE,radius=12):self.items.append(dict(kind='rect',id=id,x=x,y=y,w=w,h=h,fill=fill,stroke=stroke,radius=radius))
    def text(self,id,value,x,y,w,size=18,color=INK,bold=False):
        ls=wrap(value,w,size,bold);self.items.append(dict(kind='text',id=id,value='\n'.join(ls),x=x,y=y,w=w,h=len(ls)*(size+7),size=size,color=color,bold=bold));return len(ls)*(size+7)
    def card(self,suffix,x,y,w=440,fields=(),h=None,context=False,detail=False):
        n=suffix if suffix.startswith('STR_') else 'STR_'+suffix;t=T[n]
        for c in fields:assert c in t['columns'],(n,c)
        titlelines=wrap(t['label'],w-36,23,True)
        h=h or (112+len(fields)*39+(len(titlelines)-1)*29)
        self.rect(n,x,y,w,h,'#FFFFFF' if not context else '#F5F7FA',LINE)
        self.rect(n+'-bar',x,y,7,h,t['color'],t['color'],0)
        dh=self.text(n+'-label',t['label'],x+22,y+17,w-40,23,NAVY,True)
        self.text(n+'-name',n,x+22,y+24+dh,w-38,14,t['color'],True)
        cy=y+63+dh
        for i,c in enumerate(fields):
            label=c
            if detail:
                meta=t['columns'][c]
                key=' [PK]' if c==t['pk'] else (' [FK]' if any(c in r['foreign_key'].split(', ') and r['child']==n for r in M['relationships']) else '')
                label=c+' : '+meta['type']+key
            self.text(n+'-field'+str(i),label,x+22,cy,w-40,17,INK,c==t['pk'])
            cy+=39
        self.cards[n]=(x,y,w,h)
        return n
    def note(self,id,title,body,x,y,w=700,h=135):
        self.rect(id,x,y,w,h,'#EAF0F7','#EAF0F7',12)
        dh=self.text(id+'-t',title,x+22,y+18,w-44,21,NAVY,True)
        self.text(id+'-b',body,x+22,y+26+dh,w-44,18,INK)
    def edge(self,a,b,label='',route=None,start='bottom',end='top',label_at=None):
        a='STR_'+a if not a.startswith('STR_') else a;b='STR_'+b if not b.startswith('STR_') else b
        def anchor(k,side):
            x,y,w,h=self.cards[k];return {'top':(x+w/2,y),'bottom':(x+w/2,y+h),'left':(x,y+h/2),'right':(x+w,y+h/2)}[side]
        p1=anchor(a,start);p2=anchor(b,end)
        if route is None:
            if start in ('left','right'):mid=(p1[0]+p2[0])/2;route=[(mid,p1[1]),(mid,p2[1])]
            else:mid=(p1[1]+p2[1])/2;route=[(p1[0],mid),(p2[0],mid)]
        self.edges.append(dict(a=a,b=b,points=[p1]+route+[p2],label=label,start=start,end=end,label_at=label_at))

def scenes():
    p=Page('01-domaines','Les neuf domaines du modèle','34 tables pour suivre une déclaration, des faits rapportés jusqu’à la réponse de CANAFE.',1)
    for i,d in enumerate(M['domains']):
        x=48+(i%3)*505;y=177+(i//3)*280
        p.rect('domain'+str(i),x,y,477,254)
        p.rect('stripe'+str(i),x,y,6,254,d['color'],d['color'],0)
        p.text('domtitle'+str(i),d['name']+'  ·  '+str(len(d['tables']))+' tables',x+20,y+18,435,24,d['color'],True)
        p.text('question'+str(i),d['question'],x+20,y+56,435,17,NAVY)
        names='\n'.join(n.removeprefix('STR_') for n in d['tables'])
        p.text('names'+str(i),names,x+20,y+101,435,14,INK)
    p.text('legend','Préfixe STR_ commun à toutes les tables. Cette carte présente les domaines; les liens sont détaillés dans les pages suivantes.',48,1030,1490,15,MUTED)
    PAGES.append(p)
    p=Page('02-rapport','Le rapport donne le contexte','Domaine Rapport · 4 tables. Les liens vers d’autres déclarations ne créent pas de copies de leurs opérations.',2)
    p.card('REPORT',48,190,540,('str_report_id','report_group_id','version_number','re_report_reference','suspicious_activity_desc'),340)
    p.card('PPP_PROJECT',830,185,670,('ppp_id','str_report_id','project_name_code'),240)
    p.card('RELATED_REPORT',830,520,670,('related_report_id','str_report_id','re_report_reference'),240)
    p.card('RELATED_REPORT_TXN_REF',830,845,670,('related_report_id','txn_reference'),180)
    p.edge('REPORT','PPP_PROJECT','projets · 0..N',start='right',end='left',route=[(700,360),(700,305)],label_at=(720,305))
    p.edge('REPORT','RELATED_REPORT','rapports liés · 0..N',start='right',end='left',route=[(670,360),(670,640)],label_at=(704,500))
    p.edge('RELATED_REPORT','RELATED_REPORT_TXN_REF','précise leurs opérations · 0..N')
    p.note('version','Une correction ne remplace pas le passé','Une ligne de STR_REPORT représente une version. La version 2 garde le même report_group_id et pointe vers la version 1.',48,620,540,190)
    p.note('story','À dire en réunion','« Le rapport rassemble les faits et les raisons du soupçon. Les autres domaines viennent préciser ce récit. »',48,844,540,180)
    PAGES.append(p)
    p=Page('03-personnes-identite','Une identité, plusieurs usages','Domaines Définitions et Identité · 6 tables. Un rôle cite une définition; il ne recopie pas toute la fiche.',3)
    p.card('DEFINITION',568,180,465,('definition_id','ref_id','type_code'),238)
    p.card('PERSON',48,492,465,('person_id','definition_id','surname','given_name'),265)
    p.card('ENTITY',1086,492,465,('entity_id','definition_id','name_of_entity'),265)
    p.card('EMPLOYER_INFO',48,830,465,('person_id','name'),180)
    p.card('ADDRESS',568,492,465,('address_id','type_code','city','country_code'),265)
    p.card('IDENTIFICATION',1086,830,465,('definition_id','identifier_type_code','number'),200)
    p.edge('DEFINITION','PERSON','personne · types 1, 3 ou 5',route=[(800,452),(280,452)])
    p.edge('DEFINITION','ENTITY','entité · types 2, 4 ou 6',route=[(800,452),(1318,452)])
    p.edge('PERSON','EMPLOYER_INFO','employeur · type 5 seulement')
    p.note('identity','Comment lire les deux tables d’identité','ADDRESS porte une adresse liée à son propriétaire. IDENTIFICATION porte une pièce liée à la définition. Les liens détaillés figurent dans le dictionnaire.',568,815,465,215)
    PAGES.append(p)
    p=Page('04-entite','Ce que l’on sait de l’organisation','Domaine Entité · 2 tables, rattachées à ENTITY dans le domaine Définitions.',4)
    p.card('ENTITY',567,190,466,('entity_id','name_of_entity','nature_of_principal_business'),255,True)
    p.card('REGISTRATION_INCORPORATION',48,565,715,('entity_id','type_code','number','jurisdiction_country_code'),290)
    p.card('AUTHORIZED_PERSON',837,565,715,('entity_id','surname','given_name'),290)
    p.edge('ENTITY','REGISTRATION_INCORPORATION','enregistrements · 0..N',route=[(800,500),(405,500)])
    p.edge('ENTITY','AUTHORIZED_PERSON','personnes autorisées · 0..N',route=[(800,500),(1194,500)])
    p.note('authorized','Autorisation et propriété sont deux renseignements différents','Une personne peut être autorisée à agir pour une entreprise sans en être propriétaire. Les propriétaires et les dirigeants sont présentés dans le domaine suivant.',48,905,1504,140)
    PAGES.append(p)
    p=Page('05-propriete','Qui dirige ou détient l’entité ?','Domaine Bénéficiaires effectifs · 7 tables. Ces listes concernent les définitions d’entité de type 6.',5)
    cats=[('DIRECTOR','entity_id','surname','given_name'),('SHARE_OWNER','entity_id','surname','given_name'),('TRUSTEE','entity_id','surname','given_name'),('SETTLOR','entity_id','surname','given_name'),('TRUST_UNIT_OWNER','entity_id','surname','given_name'),('TRUST_BENEFICIARY','entity_id','surname','given_name'),('OTHER_ENTITY_OWNER','entity_id','surname','given_name')]
    for i,cs in enumerate(cats):p.card(cs[0],48+(i%4)*384,228+(i//4)*320,352,cs[1:],280)
    p.note('same-parent','Leur point commun','Chaque ligne appartient à une seule ENTITY. Les noms ne sont pas des références vers DEFINITION dans ces listes.',1200,548,352,280)
    p.note('bo-note','Ne pas confondre les bénéficiaires','TRUST_BENEFICIARY décrit une personne bénéficiaire d’une fiducie. BENEFICIARY, dans le domaine Rôles, décrit le bénéficiaire d’une opération.',48,888,1504,150)
    PAGES.append(p)
    p=Page('06-transactions','Décrire le mouvement des fonds','Domaine Transactions · 3 tables. Une opération peut avoir plusieurs actions initiales et plusieurs actions finales.',6)
    p.card('TRANSACTION',565,190,470,('transaction_id','re_txn_reference','date_of_transaction','attempted_indicator'),300)
    p.card('STARTING_ACTION',48,610,675,('transaction_id','direction','fund_type_code','amount','currency_code'),325)
    p.card('COMPLETING_ACTION',877,610,675,('transaction_id','disposition_code','amount','currency_code','value_in_cad'),325)
    p.edge('TRANSACTION','STARTING_ACTION','actions initiales · 0..N',route=[(800,551),(386,551)])
    p.edge('TRANSACTION','COMPLETING_ACTION','actions finales · 0..N',route=[(800,551),(1214,551)])
    p.text('txn-example','Exemple fictif : une opération de change commence par la remise de fonds et se termine par la remise de la devise achetée.',48,995,1504,19,NAVY)
    PAGES.append(p)
    p=Page('07-roles','La même personne peut tenir plusieurs rôles','Domaine Rôles · 5 tables. Les informations personnelles restent dans les définitions; le rôle décrit la participation.',7)
    positions=[('SOURCE_OF_FUNDS',48,210),('CONDUCTOR',566,210),('ON_BEHALF_OF',1084,210),('INVOLVEMENT',48,620),('BENEFICIARY',566,620)]
    for n,x,y in positions:
        pk={'SOURCE_OF_FUNDS':'starting_action_id','CONDUCTOR':'starting_action_id','ON_BEHALF_OF':'conductor_id','INVOLVEMENT':'completing_action_id','BENEFICIARY':'completing_action_id'}[n]
        p.card(n,x,y,466,(pk,'type_code','ref_id'),268)
    p.edge('CONDUCTOR','ON_BEHALF_OF','agit pour · 0..N',start='bottom',end='bottom',route=[(799,530),(1317,530)])
    p.note('role-example','Un exemple pour l’expliquer','Camille effectue le dépôt pour la société A : Camille est l’exécutante; A est le tiers représenté. La source des fonds est une information distincte.',1084,620,466,268)
    p.text('role-line1','Rattachés à l’action initiale',48,177,1504,19,'#C76C12',True)
    p.text('role-line2','Rattachés à l’action finale',48,577,950,19,'#C76C12',True)
    p.text('role-note','ref_id retrouve la fiche. type_code précise le niveau de renseignement attendu pour ce rôle.',48,974,1504,20,NAVY)
    PAGES.append(p)
    p=Page('08-comptes','Les comptes et la monnaie virtuelle','Domaine Comptes · 3 tables. Les données décrivent une action précise, au moment de la déclaration.',8)
    p.card('ACCOUNT',48,230,680,('account_id','starting_action_id','completing_action_id','number','currency_code'),325)
    p.card('ACCOUNT_HOLDER',48,730,680,('account_id','type_code','ref_id'),240)
    p.card('VC_DATA',870,230,682,('starting_action_id','completing_action_id','data_type','value','ordinal'),325)
    p.edge('ACCOUNT','ACCOUNT_HOLDER','titulaires · 0..N')
    p.note('xor','Un rattachement sans ambiguïté','Un compte ou une donnée de monnaie virtuelle appartient soit à une action initiale, soit à une action finale. On renseigne une seule des deux clés.',870,615,682,165)
    p.note('vc','Trois types de données dans VC_DATA','Un identifiant de transaction, une adresse émettrice ou une adresse réceptrice. data_type indique quelle liste reconstruire.',870,815,682,155)
    PAGES.append(p)
    p=Page('09-audit','Retrouver ce qui a été envoyé','Domaine Audit · 4 tables. La version du rapport, le contenu transmis et la réponse restent reliés.',9)
    p.card('API_SUBMISSION',48,220,690,('submission_id','str_report_id','operation','http_status_code','processing_status'),325)
    p.card('SUBMITTED_PAYLOAD',910,220,642,('submission_id','payload_json','payload_hash_sha256'),270)
    p.card('VALIDATION_ERROR',48,705,690,('submission_id','severity','instance_path','message_fr'),275)
    p.card('AUDIT_EVENT',910,705,642,('str_report_id','event_type','event_user','event_timestamp'),275)
    p.edge('API_SUBMISSION','SUBMITTED_PAYLOAD','contenu · 0..1',start='right',end='left',label_at=(824,382))
    p.edge('API_SUBMISSION','VALIDATION_ERROR','messages reçus · 0..N')
    p.text('audit-note','Un nouvel essai d’envoi n’est pas une nouvelle version. Une correction du contenu, oui.',48,1020,1504,20,NAVY)
    PAGES.append(p)

def export_page(p,mx,index,png=True):
    diagram=ET.SubElement(mx,'diagram',id='page'+str(index),name=p.title)
    graph=ET.SubElement(diagram,'mxGraphModel',grid='0',guides='1',connect='1',page='0',pageWidth=str(p.w),pageHeight=str(p.h),background='#F3F6FA')
    root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width=str(p.w),height=str(p.h),viewBox=f'0 0 {p.w} {p.h}')
    ET.SubElement(svg,'title').text=p.title
    # Raster plus SVG : chaque texte provient des mêmes lignes calculées.
    im=Image.new('RGB',(p.w*2,p.h*2),BG);draw=ImageDraw.Draw(im)
    def paint_shape(i):
        x,y,w,h=i['x'],i['y'],i['w'],i['h']
        if i['kind']=='rect':
            ET.SubElement(svg,'rect',x=str(x),y=str(y),width=str(w),height=str(h),rx=str(i['radius']),fill=i['fill'],stroke=i['stroke'],attrib={'stroke-width':'1'})
            draw.rounded_rectangle((x*2,y*2,(x+w)*2,(y+h)*2),radius=i['radius']*2,fill=i['fill'],outline=i['stroke'],width=2)
            style=f"rounded={int(bool(i['radius']))};arcSize=8;fillColor={i['fill']};strokeColor={i['stroke']};"
            val=''
        else:
            size=i['size'];lh=size+7
            for j,line in enumerate(i['value'].split('\n')):
                txt=ET.SubElement(svg,'text',x=str(x),y=str(y+size+j*lh),fill=i['color'],attrib={'font-family':'Arial, sans-serif','font-size':str(size),'font-weight':'700' if i['bold'] else '400'});txt.text=line
                draw.text((x*2,(y+j*lh)*2),line,font=font(size*2,i['bold']),fill=i['color'])
            style=f"text;html=1;whiteSpace=wrap;overflow=hidden;align=left;verticalAlign=top;spacing=0;fontFamily=Arial;fontSize={size};fontColor={i['color']};fontStyle={1 if i['bold'] else 0};"
            val='<div style="line-height:'+str(lh)+'px">'+html.escape(i['value']).replace('\n','<br>')+'</div>'
        c=ET.SubElement(root,'mxCell',id=i['id'],value=val,style=style,vertex='1',parent='1');ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
    # Fond, puis liens, puis cartes et textes : les relations ne traversent pas les libellés.
    paint_shape(p.items[0])
    for j,e in enumerate(p.edges):
        pts=e['points'];path='M '+' L '.join(f'{x},{y}' for x,y in pts)
        ET.SubElement(svg,'path',d=path,fill='none',stroke='#8BA0B6',attrib={'stroke-width':'2'})
        draw.line([(x*2,y*2) for x,y in pts],fill='#8BA0B6',width=4)
        a,b=pts[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0]);tri=[b,(b[0]-10*math.cos(angle-.4),b[1]-10*math.sin(angle-.4)),(b[0]-10*math.cos(angle+.4),b[1]-10*math.sin(angle+.4))]
        ET.SubElement(svg,'polygon',points=' '.join(f'{x},{y}' for x,y in tri),fill='#8BA0B6');draw.polygon([(x*2,y*2) for x,y in tri],fill='#8BA0B6')
        anchor={'bottom':(0.5,1),'top':(0.5,0),'left':(0,0.5),'right':(1,0.5)};sx,sy=anchor[e['start']];ex,ey=anchor[e['end']]
        c=ET.SubElement(root,'mxCell',id='edge'+str(j),value='',edge='1',parent='1',source=e['a'],target=e['b'],style=f'edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#8BA0B6;strokeWidth=2;endArrow=block;exitX={sx};exitY={sy};entryX={ex};entryY={ey};')
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(g,'Array',attrib={'as':'points'})
        for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        if e['label']:
            # Placer la légende sur le plus long segment, avec fond opaque.
            aa,bb=max(zip(pts,pts[1:]),key=lambda z:abs(z[0][0]-z[1][0])+abs(z[0][1]-z[1][1]));cx=(aa[0]+bb[0])/2;cy=(aa[1]+bb[1])/2
            if e.get('label_at'):cx,cy=e['label_at']
            lines=wrap(e['label'],250,14);tw=max(font(14).getlength(s) for s in lines)+14;th=len(lines)*21+6
            ii=dict(kind='rect',id='edge-label-bg'+str(j),x=cx-tw/2,y=cy-th/2,w=tw,h=th,fill=BG,stroke=BG,radius=3);paint_shape(ii)
            paint_shape(dict(kind='text',id='edge-label'+str(j),value='\n'.join(lines),x=cx-tw/2+7,y=cy-th/2+2,w=tw-14,h=th,size=14,color=MUTED,bold=False))
    for i in p.items[1:]:paint_shape(i)
    if png:
        d=ROOT/'diagrams/images';d.mkdir(parents=True,exist_ok=True)
        ET.indent(svg);(d/(p.slug+'.svg')).write_text(ET.tostring(svg,encoding='unicode')+'\n',encoding='utf-8')
        im.save(d/(p.slug+'.png'),optimize=True)

def main():
    scenes();mx=ET.Element('mxfile',host='app.diagrams.net',version='24.7.17')
    for i,p in enumerate(PAGES):export_page(p,mx,i)
    ET.indent(mx);(ROOT/'diagrams/CANAFE_DOD.drawio').write_text(ET.tostring(mx,encoding='unicode')+'\n',encoding='utf-8')
    # Annexe de construction : toutes les colonnes, une table par page.
    full=ET.Element('mxfile',host='app.diagrams.net',version='24.7.17')
    for i,t in enumerate(T.values()):
        n=t['name'];cols=list(t['columns'])
        refs=[r for r in M['relationships'] if r['child']==n]
        reftext='\n'.join(r['foreign_key']+' → '+r['parent'] for r in refs) or 'Table de rapport : point d’entrée de la version.'
        refheight=max(190,len(wrap(reftext,468,18))*25+85)
        rulestext='\n'.join(t['rules'][:3]) or 'Voir DICTIONNAIRE.md pour les obligations des champs.'
        rulesheight=max(270,len(wrap(rulestext,468,18))*25+80)
        h=max(1100,390+len(cols)*39,430+refheight+rulesheight+100)
        p=Page('detail-'+str(i),t['label'],n+'  ·  '+t['domain']+'  ·  toutes les colonnes',i+1,h=h)
        p.card(n,48,185,930,cols,h=112+len(cols)*39,detail=True)
        p.note('detail-note','Rôle de cette table',t['reason'],1040,185,512,175)
        p.note('refs','Liens à dessiner',reftext,1040,400,512,refheight)
        p.note('rules','Points à vérifier',rulestext,1040,430+refheight,512,rulesheight)
        export_page(p,full,i,False)
    ET.indent(full);(ROOT/'diagrams/CANAFE_DOD_DETAIL.drawio').write_text(ET.tostring(full,encoding='unicode')+'\n',encoding='utf-8')
    (ROOT/'model/presentation.json').write_text(json.dumps([{'slug':p.slug,'title':p.title,'width':p.w,'height':p.h,'items':p.items,'edges':p.edges,'tables':list(p.cards)} for p in PAGES],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('9 vues métier, 9 images PNG et SVG, 34 pages de détail.')

if __name__=='__main__':main()
