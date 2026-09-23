"""Modèle DOD avec référentiels : une livraison distincte, sans toucher aux anciens draw.io.

Les codes proviennent exclusivement des enums atteintes par le mapping DOD.
Les réponses brutes et les branches ouvertes ne deviennent pas des FK fermées.
"""
import copy, csv, hashlib, html, json, re, textwrap
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from relational_page import FONT, BOLD

ROOT = Path(__file__).resolve().parents[1]
MODEL = json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
SPEC = json.loads((ROOT/'source/openapi.json').read_text(encoding='utf-8'))
SHA = hashlib.sha256((ROOT/'source/swaggerExternal.yaml').read_bytes()).hexdigest()
BASE = '#/components/schemas/'
REPO = 'https://github.com/khojasahil/projetdod/blob/main/'
BG, INK, REF = '#F3F6FA', '#142B46', '#0369A1'
TARGET = ROOT/'diagrams/CANAFE_DOD_AVEC_REFERENTIELS.drawio'

def node(pointer):
    obj=SPEC
    for part in pointer[2:].split('/'):
        obj=obj[int(part)] if isinstance(obj,list) else obj[part.replace('~1','/').replace('~0','~')]
    return obj

def write(path, text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8',newline='\n')

def dump(path, value):write(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def csv_out(path, rows, fields):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

# Un nom métier par sens, jamais un référentiel global appelé TYPE_CODE.
NAMES = {
 'reportTypeCode':('TYPE_RAPPORT','Type de déclaration'),
 'submitTypeCode':('TYPE_SOUMISSION','Nature de la demande'),
 'activitySectorCode':('SECTEUR_ACTIVITE','Secteur du déclarant'),
 'ministerialDirectiveCode':('DIRECTIVE','Directive ministérielle'),
 'STRReport/properties/detailsOfSuspicion/properties/suspicionTypeCode':('TYPE_SOUPCON','Catégorie du soupçon'),
 'STRReport/properties/detailsOfSuspicion/properties/publicPrivatePartnershipProjectNameCodes/items':('PROJET_PPP','Projet de partenariat'),
 'CountryCode':('PAYS','Pays'),
 'addressTypeCode':('TYPE_ADRESSE','Forme de l’adresse'),
 'StructuredAddress/properties/typeCode':('TYPE_ADRESSE','Forme de l’adresse'),
 'UnstructuredAddress/properties/typeCode':('TYPE_ADRESSE','Forme de l’adresse'),
 'personIdentificationWithJurisdiction/properties/identifierTypeCode':('TYPE_IDENTIFICATION','Document d’identification'),
 'entityIdentificationWithJurisdiction/properties/identifierTypeCode':('TYPE_IDENTIFICATION','Document d’identification'),
 'IncorporationRegistrationTypeCode':('TYPE_ENREGISTREMENT','Enregistrement ou constitution'),
 'entityAndBeneficialOwnershipDetails/properties/structureTypeCode':('STRUCTURE_ENTITE','Structure de l’entité'),
 'STRReport/properties/transactions/items/properties/suspiciousTransactionDetails/properties/methodCode':('METHODE_OPERATION','Méthode de l’opération'),
 'STRReport/properties/transactions/items/properties/startingActions/items/properties/details/properties/direction':('SENS_ACTION','Sens du mouvement'),
 'STRReport/properties/transactions/items/properties/startingActions/items/properties/details/properties/fundAssetVirtualCurrencyTypeCode':('NATURE_FONDS','Nature des fonds'),
 'CurrencyCode':('DEVISE','Devise'),
 'VirtualCurrencyCode':('MONNAIE_VIRTUELLE','Monnaie virtuelle'),
 'strAccount/properties/typeCode':('TYPE_COMPTE','Type de compte'),
 'accountStatusAtTimeOfTransaction':('STATUT_COMPTE','État du compte pendant l’opération'),
 'typeOfDeviceCode':('TYPE_APPAREIL','Appareil utilisé'),
 'relationshipOfConductorCodeWithVendor':('RELATION_TIERS','Lien entre l’exécutant et le tiers'),
 'STRReport/properties/transactions/items/properties/completingActions/items/properties/details/properties/dispositionCode':('DISPOSITION','Utilisation des fonds'),
}
DEFS=['PersonName','EntityName','PersonDetails','EntityDetails','personAndEmployerDetails','entityAndBeneficialOwnershipDetails']
for name in DEFS:NAMES[name+'/properties/typeCode']=('TYPE_DEFINITION','Forme de la fiche')
for name in ['definitionType12','definitionType34','definitionType56']:NAMES[name]=('TYPE_DEFINITION','Forme de la fiche')

def labels(pointer):
    """Extrait les libellés publiés sans réécrire les erreurs de la source."""
    desc=node(pointer).get('description','');out={}
    for line in desc.splitlines():
        m=re.match(r"\s*\*\s*[`'\"]?([A-Za-z0-9-]+)[`'\"]?\s*-\s*(.+)",line)
        if m:
            en,sep,fr=m[2].partition(' / ')
            out[m[1]]={'libelle_fr':fr.strip() if sep else '', 'libelle_en':en.strip(), 'libelle_source_pointer':pointer}
    return out

def catalog():
    refs={};bindings={};coverage=[]
    for f in MODEL['mappings']:
        if 'enum' not in f['constraints']:continue
        p=f['resolved_pointer'];short=p.removeprefix(BASE)
        if f['storage']!='colonne' or f['table'] in ('STR_API_SUBMISSION','STR_SUBMITTED_PAYLOAD','STR_VALIDATION_ERROR'):
            mode='LECTURE_REPONSE_OU_ARCHIVE';name=''
        elif short.startswith('ProvinceStateCode/'):
            mode='BRANCHE_OUVERTE_SANS_FK';name=''
        else:
            assert short in NAMES,short
            suffix,label=NAMES[short];name='REF_'+suffix;mode='FK_VERSIONNEE'
            ref=refs.setdefault(name,{'name':name,'label':label,'pointers':[],'rows':{},'type':f['constraints'].get('type','integer')})
            if p not in ref['pointers']:ref['pointers'].append(p)
            lb=labels(p)
            if name=='REF_TYPE_DEFINITION':
                for q in ['definitionType12','definitionType34','definitionType56']:lb.update(labels(BASE+q))
            if name=='REF_TYPE_ADRESSE':lb.update(labels(BASE+'addressTypeCode'))
            family=('PERSON' if short.startswith('personIdentification') else 'ENTITY') if name=='REF_TYPE_IDENTIFICATION' else ''
            for code in f['constraints']['enum']:
                key=(family,str(code))
                row={'schema_sha256':SHA,'code':code,'identification_family':family,
                     'libelle_fr':'','libelle_en':'','libelle_source_pointer':'',
                     'source_pointer':p,**lb.get(str(code),{})}
                if key not in ref['rows'] or (not ref['rows'][key]['libelle_fr'] and row['libelle_fr']):ref['rows'][key]=row
            key=(f['table'],f['column'],name)
            b=bindings.setdefault(key,{'table':f['table'],'column':f['column'],'reference':name,'mappings':[], 'allowed_by_mapping':{}})
            b['mappings'].append(f['id']);b['allowed_by_mapping'][f['id']]=f['constraints']['enum']
        coverage.append({'mapping_id':f['id'],'table':f['table'],'column':f['column'],'source_pointer':p,'traitement':mode,'reference':name})
    for r in refs.values():
        r['rows']=list(r['rows'].values())
        assert all(x['libelle_en'] or x['libelle_fr'] for x in r['rows']),r['name']
    return refs,list(bindings.values()),coverage

REFS,BINDINGS,COVERAGE=catalog()
TABLES={t['name']:t for t in MODEL['tables']}
AFFECTED=sorted({b['table'] for b in BINDINGS})
REF_COLS=['schema_sha256','code','libelle_fr','libelle_en','source_pointer','libelle_source_pointer']
SCHEMA_COLS=['schema_sha256','openapi_version','api_version','archived_on','source_url','archive_path']

def cols(ref):
    return ['schema_sha256','identification_family','code',*REF_COLS[2:]] if ref=='REF_TYPE_IDENTIFICATION' else REF_COLS

def examples(ref,limit=3):
    rows=REFS[ref]['rows']
    if ref=='REF_PAYS':rows=sorted(rows,key=lambda r:r['code'] not in ['CA','US','FR'])
    if ref=='REF_TYPE_IDENTIFICATION':rows=[r for r in rows if r['code']==1]
    result=[]
    for r in rows[:limit]:
        prefix=(r['identification_family']+' / ') if r['identification_family'] else ''
        result.append(prefix+str(r['code'])+' = '+(r['libelle_fr'] or r['libelle_en']))
    return result

def constraint_note(ref):
    return {
      'REF_TYPE_RAPPORT':'La liste officielle couvre plusieurs déclarations. Ici, le rapport DOD utilise uniquement le code 102.',
      'REF_TYPE_SOUMISSION':'La demande et le point de terminaison doivent correspondre : 1 = soumettre, 2 = mettre à jour, 5 = supprimer.',
      'REF_TYPE_DEFINITION':'Le rôle limite le choix : source, titulaire et implication = 1/2; bénéficiaire = 3/4; exécutant et tiers = 5/6.',
      'REF_TYPE_IDENTIFICATION':'Le code 1 ne désigne pas le même document pour une personne et une entité. La famille fait partie de la clé.',
      'REF_NATURE_FONDS':'La liste seule ne suffit pas : les choix permis dépendent aussi du sens Entrée / Sortie.',
      'REF_TYPE_ADRESSE':'Le code porté par le propriétaire et celui de l’adresse restent deux champs distincts. Il faut vérifier leur cohérence.',
      'REF_PAYS':'La liste est celle du Swagger archivé. On ne la remplace pas automatiquement par une liste ISO plus récente.',
      'REF_DEVISE':'Conserver les codes de la version CANAFE utilisée, même si certains ne figurent plus dans une liste externe récente.',
      'REF_MONNAIE_VIRTUELLE':'Le schéma publie une longue liste. Le catalogue fournit toutes les valeurs; seuls des exemples figurent ici.',
    }.get(ref,'Cette liste explique le code. La présence obligatoire du champ et les conditions métier se vérifient séparément.')

class Page:
    """Une forme avec du texte multiligne par carte; rendu PNG de la même scène."""
    def __init__(self,doc,id,title,subtitle,width=1900):
        self.id=id;self.width=width;self.items=[];self.rects={};self.edges=[]
        self.page=ET.SubElement(doc,'diagram',id=id,name=title)
        self.graph=ET.SubElement(self.page,'mxGraphModel',grid='0',page='0',background=BG,connect='1')
        self.root=ET.SubElement(self.graph,'root');ET.SubElement(self.root,'mxCell',id='0');ET.SubElement(self.root,'mxCell',id='1',parent='0')
        self.box('title',title,[subtitle],60,35,width-120,'#142B46',title_size=34,size=21,border=False)
    @staticmethod
    def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)
    def wrap(self,text,width,size,bold=False):
        font=self.font(size,bold);lines=[]
        for para in text.split('\n'):
            line=''
            for word in para.split(' '):
                candidate=(line+' '+word).strip()
                if font.getlength(candidate)>width and line:lines.append(line);line=word
                else:line=candidate
                assert font.getlength(word)<=width,word
            lines.append(line)
        return lines
    def box(self,id,title,lines,x,y,w,color=REF,size=20,title_size=23,border=True,fill='white',link=None):
        ts=self.wrap(title,w-40,title_size,True);body=[]
        for s in lines:body.extend(self.wrap(s,w-40,size))
        h=36+len(ts)*(title_size+8)+14+len(body)*(size+8)
        value=f'<div style="font-size:{title_size}px;line-height:{title_size+8}px;color:{color};font-weight:bold">'+ '<br>'.join(html.escape(s) for s in ts)+'</div>'
        value+=f'<div style="height:14px"></div><div style="font-size:{size}px;line-height:{size+8}px">'+'<br>'.join(html.escape(s) for s in body)+'</div>'
        style=f'rounded=1;arcSize=6;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacing=0;spacingTop=18;spacingLeft=20;spacingRight=20;fontFamily=Arial;fontColor={INK};fillColor={fill if border else BG};strokeColor={color if border else "none"};strokeWidth=2;'
        c=ET.SubElement(self.root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1')
        if link:c.set('link',link)
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        self.rects[id]=(x,y,w,h);self.items.append((ts,body,x,y,w,h,color,size,title_size,border,fill));return h
    def edge(self,id,src,dst,label='FK · même version',dashed=False):
        x,y,w,h=self.rects[src];xx,yy,ww,hh=self.rects[dst]
        points=[(x+w,y+h/2),((x+w+xx)/2,y+h/2),((x+w+xx)/2,yy+hh/2),(xx,yy+hh/2)]
        style='edgeStyle=none;rounded=0;html=1;strokeColor=#64748B;strokeWidth=2;endArrow=block;endSize=10;exitX=1;exitY=0.5;entryX=0;entryY=0.5;fontSize=17;fontFamily=Arial;labelBackgroundColor='+BG+';'+('dashed=1;' if dashed else '')
        c=ET.SubElement(self.root,'mxCell',id=id,value=html.escape(label),style=style,edge='1',parent='1',source=src,target=dst)
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});a=ET.SubElement(g,'Array',attrib={'as':'points'})
        for px,py in points[1:-1]:ET.SubElement(a,'mxPoint',x=str(px),y=str(py))
        self.edges.append((points,label,dashed))
    def finish(self,filename=None):
        H=int(max(y+h for x,y,w,h in self.rects.values())+65)
        self.graph.set('pageWidth',str(self.width));self.graph.set('pageHeight',str(H))
        # Vérifie les blocs : aucune superposition ni sortie de page.
        rects=list(self.rects.items())
        for i,(a,(x,y,w,h)) in enumerate(rects):
            assert x>=0 and x+w<=self.width,(self.id,a)
            for b,(xx,yy,ww,hh) in rects[i+1:]:
                assert x+w<=xx or xx+ww<=x or y+h<=yy or yy+hh<=y,(self.id,a,b)
        if filename:
            im=Image.new('RGB',(self.width,H),BG);draw=ImageDraw.Draw(im)
            for pts,label,dashed in self.edges:
                draw.line(pts,fill='#64748B',width=2)
                x,y=pts[-1];draw.polygon([(x,y),(x-12,y-6),(x-12,y+6)],fill='#64748B')
                # Le libellé figure au-dessus du segment horizontal sortant.
                x,y=pts[0];draw.text((x+12,y-26),label,font=self.font(17),fill='#64748B')
            for ts,body,x,y,w,h,color,size,title_size,border,fill in self.items:
                if border:draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=fill,outline=color,width=2)
                cy=y+18
                for t in ts:draw.text((x+20,cy),t,font=self.font(title_size,True),fill=color);cy+=title_size+8
                cy+=14
                for t in body:draw.text((x+20,cy),t,font=self.font(size),fill=INK);cy+=size+8
            im.save(ROOT/'diagrams/images'/filename)
        return {'id':self.id,'name':self.page.get('name'),'blocks':len(self.rects),'edges':len(self.edges),'height':H}

def ref_lines(name,full=True):
    ls=[]
    if full:
        for c in cols(name):ls.append(('PK / FK  ' if c=='schema_sha256' else 'PK  ' if c in ['code','identification_family'] else '     ')+c)
        ls.append('')
    ls+=['Exemples de valeurs :',*examples(name),f"{len(REFS[name]['rows'])} valeurs dans le catalogue."]
    return ls

def intro(doc):
    p=Page(doc,'ref-intro','Comprendre les référentiels','Le rapport garde le code. Le référentiel explique ce code et rattache sa signification au Swagger utilisé.')
    p.box('account','Le compte déclaré',['STR_ACCOUNT — extrait','PK  account_id','FK  schema_sha256','FK  type_code = 1','', 'Le compte contient la valeur 1.'],70,205,580,'#059669')
    p.box('ref','La liste qui explique le code',['REF_TYPE_COMPTE','PK  schema_sha256 + code','',*examples('REF_TYPE_COMPTE',5)],1040,205,770,REF)
    p.edge('e1','account','ref','type_code → code')
    y=max(p.rects['account'][1]+p.rects['account'][3],p.rects['ref'][1]+p.rects['ref'][3])+70
    p.box('why','Ce que cela change pour nous',['Nous savons quelles valeurs proposer à la saisie et comment les expliquer.','Une valeur absente de la liste est repérée avant la transmission.','Le code transmis à CANAFE reste identique; les libellés servent à notre lecture.'],70,y,1740,'#2563EB')
    y+=p.rects['why'][3]+45
    p.box('limits','La liste ne décide pas de tout',['Un code peut exister sans être permis pour un rôle donné. Exemple : un bénéficiaire utilise une fiche de type 3 ou 4.','Les dates, les montants et les textes ont des règles de format. Nous ne créons pas une table de référence pour chacun.','Les réponses reçues sont conservées même si elles contiennent un code encore inconnu.'],70,y,1740,'#B7791F')
    y+=p.rects['limits'][3]+45
    p.box('reading','Comment lire ce fichier',[f"34 tables métier conservées + {len(REFS)} tables de codes + REF_SCHEMA_VERSION.",'Commencez ici, puis regardez la page « Version du Swagger et clés ».','Les pages par thème montrent les champs codifiés. La dernière page contient toutes les tables et colonnes.','Un bloc = une table ou un extrait. Double-cliquez pour modifier les lignes comme dans un document.'],70,y,1740,REF)
    return p.finish('referentiels-01-comprendre.png')

def version_page(doc):
    p=Page(doc,'ref-version','Version du Swagger et clés','Une correction future du catalogue ne doit pas changer la lecture d’une ancienne déclaration.')
    p.box('report','STR_REPORT — version du rapport',['PK  str_report_id','FK  schema_sha256','     version_number','     report_type_code = 102'],60,210,650,'#2563EB')
    p.box('schema','REF_SCHEMA_VERSION',['PK  schema_sha256','     openapi_version','     api_version','     archived_on','     source_url','     archive_path'],1100,210,720,REF)
    p.edge('a','report','schema','version utilisée')
    p.box('account','STR_ACCOUNT — extrait',['PK  account_id','FK  str_report_id','FK  schema_sha256 [ajout]','FK  type_code','', 'Même empreinte que le rapport parent.'],60,630,650,'#059669')
    p.box('codes','REF_TYPE_COMPTE',['PK / FK  schema_sha256','PK       code','         libelle_fr','         libelle_en','         source_pointer','         libelle_source_pointer'],1100,630,720,REF)
    p.edge('b','account','codes','(schema_sha256, type_code)')
    y=1060
    p.box('rules','Les clés, en langage simple',['Chaque liste est conservée avec la copie exacte du Swagger dont elle provient.','La référence du compte porte sur deux champs : la version du Swagger et le code. Le code seul ne suffit pas.','Chaque table métier enrichie garde la même empreinte que son rapport : FK (str_report_id, schema_sha256) vers STR_REPORT.','Dans le rapport, le couple (str_report_id, schema_sha256) est une clé unique. Les codes sont validés avant le gel.'],60,y,1760,REF)
    y+=p.rects['rules'][3]+45
    p.box('idnote','Attention aux documents d’identification',['Pour une personne : code 1 = certificat de naissance. Pour une entité : code 1 = acte d’association.','REF_TYPE_IDENTIFICATION utilise donc la clé (schema_sha256, identification_family, code).','La nouvelle colonne identification_family vaut PERSON ou ENTITY selon la définition propriétaire. Elle ne part pas dans le JSON.','Cette cohérence est une règle métier à contrôler avec STR_DEFINITION; une FK de catalogue ne la prouve pas à elle seule.'],60,y,1760,'#B7791F')
    return p.finish('referentiels-02-version.png')

def focus_pages(doc):
    stats=[]
    for i,d in enumerate(MODEL['domains']):
        bindings=[b for b in BINDINGS if b['table'] in d['tables']]
        if not bindings:continue
        p=Page(doc,'ref-domain-'+str(i),d['name']+' — champs et listes','Extraits de tables. Une table peut réapparaître pour expliquer un autre champ. Toutes les colonnes sont dans la dernière page.',2300)
        y=205
        for j,name in enumerate(dict.fromkeys(b['reference'] for b in bindings)):
            group=[b for b in bindings if b['reference']==name];by_table=defaultdict(list)
            for b in group:by_table[b['table']].append(b['column'])
            rid='ref'+str(j)
            rh=p.box(rid,name+' · '+REFS[name]['label'],ref_lines(name)+['',constraint_note(name)],1430,y,790,REF)
            ly=y
            for k,(tn,fields) in enumerate(by_table.items()):
                t=TABLES[tn];ls=['PK  '+t['pk'],'FK  schema_sha256']
                if name=='REF_TYPE_IDENTIFICATION':ls+=['FK  identification_family [ajout]']
                ls+=['FK  '+f for f in fields]
                allowed=sorted({str(v) for b in group if b['table']==tn for vv in b['allowed_by_mapping'].values() for v in vv})
                if name=='REF_TYPE_DEFINITION':ls+=['Choix pour ce rôle / cette fiche : '+', '.join(allowed)]
                sid=f's{j}-{k}';lh=p.box(sid,tn+' · '+t['label'],ls,60,ly,960,t['color']);p.edge(f'e{j}-{k}',sid,rid,'code + version')
                ly+=lh+35
            y=max(ly,y+rh)+75
        p.box('note','Pour ne pas confondre les deux types de lien',['Les flèches de cette page vont du champ vers sa liste de valeurs. Elles ne remplacent pas les relations entre personnes, opérations et comptes.','Une FK contrôle l’existence du code dans la bonne version. Les restrictions de rôle, de direction ou de présence restent des règles distinctes.'],60,y,2160,d['color'])
        stats.append(p.finish('referentiels-03-comptes.png' if d['name']=='Comptes' else None))
    return stats

def catalog_pages(doc):
    names=list(REFS);stats=[]
    for i in range(0,len(names),6):
        p=Page(doc,'ref-catalog-'+str(i//6),'Catalogue des listes · '+str(i//6+1),'Chaque carte représente une table de référence. Les exemples ne remplacent pas les listes exhaustives du catalogue.',2200)
        y=205
        for j in range(i,min(i+6,len(names)),2):
            heights=[]
            for k,name in enumerate(names[j:j+2]):
                heights.append(p.box(name,name+' · '+REFS[name]['label'],ref_lines(name)+['','Liste complète et source : ouvrir le lien de cette carte.'],60+k*1090,y,990,REF,link=REPO+'docs/REFERENTIELS_CANAFE.md#'+name.lower()))
            y+=max(heights)+50
        stats.append(p.finish())
    return stats

def full_page(doc):
    """Reprend la vue complète aérée; les nouveaux connecteurs ont leur propre calque."""
    source=ET.parse(ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio')
    page=copy.deepcopy(next(p for p in source.getroot() if p.get('id')=='page11'))
    page.set('id','ref-full');page.set('name','Modèle complet — tables, colonnes et référentiels');doc.append(page)
    graph=page.find('mxGraphModel');root=graph.find('root');cells={c.get('id'):c for c in root.findall('mxCell')}
    # IDs of the existing table cells are stable across editions.
    for n in AFFECTED:
        c=cells[n];value=c.get('value','')
        fields=sorted({b['column'] for b in BINDINGS if b['table']==n},key=len,reverse=True)
        for field in fields:
            # Prefix a reference marker without deleting the original PK/FK indication.
            value=re.sub(r'(?<![A-Za-z0-9_])'+re.escape(field)+r'(?![A-Za-z0-9_])',field+' [REF]',value)
        additions=[]
        if n!='STR_REPORT':additions.append('FK  schema_sha256 [ajout]')
        if n=='STR_IDENTIFICATION':additions.append('FK  identification_family [ajout]')
        if additions:
            # Même rectangle et mêmes points de passage que l’original. Le texte
            # reste dans un seul bloc; l’interligne absorbe les nouveaux champs.
            end=value.rfind('</div>')
            value=value[:end]+'<br><span style="color:#0369A1">'+'<br>'.join(additions)+'</span>'+value[end:]
            value=value.replace('line-height:30px','line-height:26px')
        if n=='STR_REPORT':value=value.replace('schema_sha256 :','[FK / UK] schema_sha256 :')
        c.set('value',value)
    W=int(graph.get('pageWidth'));H=int(graph.get('pageHeight'))
    # New tables are outside the existing routing area, so original connectors stay intact.
    x=W+370;ry=550;w=850
    ET.SubElement(root,'mxCell',id='refs-layer',value='Référentiels — liens de codes (afficher au besoin)',parent='0',visible='0')
    ET.SubElement(root,'mxCell',id='versions-layer',value='Référentiels — liens de version (afficher au besoin)',parent='0',visible='0')
    def box(id,title,fields,x,y,h):
        v=f'<b style="font-size:25px;color:{REF}">{html.escape(title)}</b><br><br>'+'<br>'.join(html.escape(f) for f in fields)
        c=ET.SubElement(root,'mxCell',id=id,value=v,style=f'rounded=1;html=1;align=left;verticalAlign=top;spacing=20;fontFamily=Arial;fontSize=21;fillColor=#FFFFFF;strokeColor={REF};strokeWidth=2;',vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'});return c
    box('refs-title','Les référentiels CANAFE',[f'{len(REFS)} listes de codes + leur version de Swagger.','Les champs [REF] pointent vers une liste.','Affichez les liens dans Vue > Calques.','Les pages précédentes expliquent chaque lien.'],x,180,300)
    box('REF_SCHEMA_VERSION','REF_SCHEMA_VERSION',['PK  '+SCHEMA_COLS[0],*SCHEMA_COLS[1:]],x,ry,310);ry+=380
    for name in REFS:
        fields=[('PK / FK  ' if f=='schema_sha256' else 'PK  ' if f in ('code','identification_family') else '    ')+f for f in cols(name)]
        box(name,name,fields,x,ry,340);ry+=410
    def edge(id,src,dst,label,layer):
        c=ET.SubElement(root,'mxCell',id=id,value=label,source=src,target=dst,parent=layer,edge='1',style=f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;fontSize=17;labelBackgroundColor={BG};strokeColor={REF};endArrow=ERone;startArrow=none;exitX=1;exitY=0.5;entryX=0;entryY=0.5;')
        ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
    relationships=[]
    for i,b in enumerate(BINDINGS):
        fk=['schema_sha256']+(['identification_family'] if b['reference']=='REF_TYPE_IDENTIFICATION' else [])+[b['column']]
        pk=['schema_sha256']+(['identification_family'] if b['reference']=='REF_TYPE_IDENTIFICATION' else [])+['code']
        edge('ref-fk-'+str(i),b['table'],b['reference'],', '.join(fk),'refs-layer')
        relationships.append({'child':b['table'],'foreign_key':fk,'parent':b['reference'],'parent_key':pk,'kind':'CODE','nullable':'Selon le champ et la variante Swagger'})
    for i,name in enumerate(REFS):
        edge('ref-version-'+str(i),name,'REF_SCHEMA_VERSION','schema_sha256','versions-layer')
        relationships.append({'child':name,'foreign_key':['schema_sha256'],'parent':'REF_SCHEMA_VERSION','parent_key':['schema_sha256'],'kind':'VERSION'})
    edge('report-version','STR_REPORT','REF_SCHEMA_VERSION','schema_sha256','versions-layer')
    relationships.append({'child':'STR_REPORT','foreign_key':['schema_sha256'],'parent':'REF_SCHEMA_VERSION','parent_key':['schema_sha256'],'kind':'VERSION'})
    for i,name in enumerate(AFFECTED):
        if name=='STR_REPORT':continue
        edge('child-version-'+str(i),name,'STR_REPORT','str_report_id, schema_sha256','versions-layer')
        relationships.append({'child':name,'foreign_key':['str_report_id','schema_sha256'],'parent':'STR_REPORT','parent_key':['str_report_id','schema_sha256'],'kind':'COHERENCE_VERSION'})
    graph.set('pageWidth',str(x+w+100));graph.set('pageHeight',str(max(H,ry+100)))
    # Update inherited titles to describe this copy accurately.
    for c in cells.values():
        if c.get('vertex')=='1' and c.get('id') not in TABLES:
            v=c.get('value','')
            v=v.replace('Modèle complet — lecture aérée','Modèle complet — avec référentiels')
            v=v.replace('365 colonnes',f'365 colonnes métier + {len(AFFECTED)} colonnes de contrôle')
            c.set('value',v)
    cells['subtitle'].set('value',f'{35+len(REFS)} tables · 389 colonnes métier · 77 liens initiaux + {len(relationships)} liens de référentiels · Une table = un bloc de texte.')
    cells['note0'].set('value','Commencez par les 37 liens métier affichés. Les autres liens sont accessibles dans Vue &gt; Calques.')
    cells['note3'].set('value','PK = clé primaire · FK = clé étrangère · [REF] = FK vers une liste versionnée · UK* = clé unique de DEFINITION.')
    cells['note5'].set('value','Neuf domaines métier à gauche; les référentiels CANAFE à droite. Les pages par thème expliquent les liens de codes.')
    return relationships

def documentation(stats,relationships):
    additions=[{'table':n,'column':'schema_sha256','type':'Texte (SHA-256, 64 caractères)','reason':'Figer la version de la liste et imposer la même version que le rapport.','origin':'INTERNE','nullable':'Non au gel; même valeur que le rapport parent.'} for n in AFFECTED if n!='STR_REPORT']
    additions.append({'table':'STR_IDENTIFICATION','column':'identification_family','type':'Texte : PERSON ou ENTITY','reason':'Distinguer les deux significations possibles du même code de document. Dérivé du type de la définition propriétaire.','origin':'INTERNE','nullable':'Non au gel; requis pour contrôler identifier_type_code lorsqu’il est présent.'})
    enriched=copy.deepcopy(MODEL)
    for a in additions:
        t=next(t for t in enriched['tables'] if t['name']==a['table']);t['columns'][a['column']]={**a,'rule':a['nullable'],'mapping_ids':[]}
    ref_tables=[]
    purposes={
      'schema_sha256':'Conserver la copie exacte du Swagger. Clé de version; n’est jamais envoyée à CANAFE.',
      'code':'Conserver exactement la valeur et le type JSON attendus par la CANAFE.',
      'identification_family':'Séparer les documents PERSON et ENTITY. Ce discriminant interne évite de confondre deux codes identiques.',
      'libelle_fr':'Lire la signification française publiée; vide si la source ne la fournit pas.',
      'libelle_en':'Conserver le libellé anglais publié pour rapprochement avec la source.',
      'source_pointer':'Retrouver l’enum qui contient ce code dans le Swagger archivé.',
      'libelle_source_pointer':'Retrouver la description qui donne le libellé, parfois distincte du discriminant inline.',
    }
    for name,ref in REFS.items():
        pk=['schema_sha256']+(['identification_family'] if name=='REF_TYPE_IDENTIFICATION' else [])+['code']
        ref_tables.append({'name':name,'domain':'Référentiels CANAFE','label':ref['label'],'pk':pk,'columns':{c:{'type':ref['type'] if c=='code' else 'Texte','reason':purposes[c],'nullable':c=='libelle_fr'} for c in cols(name)}})
    schema_purpose={
      'schema_sha256':'Identifiant immuable calculé sur le fichier Swagger archivé.',
      'openapi_version':'Version du format OpenAPI (3.0.0 dans cette copie).',
      'api_version':'Version déclarée par info.version. Elle ne remplace pas l’empreinte du fichier.',
      'archived_on':'Date d’archivage dans le projet, pas une date d’entrée en vigueur réglementaire.',
      'source_url':'Adresse officielle d’où provient le fichier.',
      'archive_path':'Emplacement de la copie conservée pour pouvoir la relire.'}
    ref_tables.append({'name':'REF_SCHEMA_VERSION','domain':'Référentiels CANAFE','label':'La copie du Swagger','pk':['schema_sha256'],'columns':{c:{'type':'Date' if c=='archived_on' else 'Texte','reason':schema_purpose[c],'nullable':False} for c in SCHEMA_COLS}})
    enriched['reference_tables']=ref_tables;enriched['reference_relationships']=relationships;enriched['reference_bindings']=BINDINGS
    enriched['architecture']=f'34 tables métier + {len(REFS)} référentiels de codes + 1 version du Swagger'
    enriched['additional_unique_keys']=[{'table':'STR_REPORT','columns':['str_report_id','schema_sha256']}]
    dump('model/model-with-references.json',enriched)
    schema_version={'schema_sha256':SHA,'openapi_version':SPEC['openapi'],'api_version':SPEC['info']['version'],'archived_on':'2026-09-22','source_url':'https://www148.fintrac-canafe.canada.ca/reporting-ingest/api-doc-files/swaggerExternal.yaml','archive_path':'source/swaggerExternal.yaml'}
    dump('model/reference-catalog.json',{'schema_version':schema_version,'references':REFS,'bindings':BINDINGS,'coverage':COVERAGE})
    rows=[]
    for name,ref in REFS.items():
        for r in ref['rows']:rows.append({'reference':name,**r})
    csv_out('traceability/reference-values.csv',rows,['reference','schema_sha256','identification_family','code','libelle_fr','libelle_en','source_pointer','libelle_source_pointer'])
    csv_out('traceability/reference-coverage.csv',COVERAGE,['mapping_id','table','column','source_pointer','traitement','reference'])
    fields=[]
    for b in BINDINGS:
        for mid,allowed in b['allowed_by_mapping'].items():
            f=next(f for f in MODEL['mappings'] if f['id']==mid)
            fields.append({'table':b['table'],'column':b['column'],'reference':b['reference'],'mapping_id':mid,'json_path':f['json_path'],'variant':f['variant'],'allowed_values':json.dumps(allowed,ensure_ascii=False),'source_pointer':f['resolved_pointer']})
    csv_out('traceability/reference-fields.csv',fields,['table','column','reference','mapping_id','json_path','variant','allowed_values','source_pointer'])
    md=['# DOD avec référentiels CANAFE','','Ce nouveau modèle complète les 34 tables métier. Les fichiers draw.io précédents restent inchangés. Les référentiels sont un ajout de conception interne : CANAFE fournit les codes et les règles, pas ces tables relationnelles.','',f'**34 tables métier + {len(REFS)} tables de codes + 1 table de version = {35+len(REFS)} tables.** Les 365 colonnes initiales sont conservées; cette édition ajoute {len(additions)} colonnes internes de contrôle aux tables métier. Aucun script de création de tables n’est fourni.','','## À quoi servent ces listes ?','','Un compte contient par exemple `type_code = 1`. La liste explique que 1 signifie « Personnel ». Le code transmis ne change pas; nous ajoutons sa signification et la preuve de sa provenance.','','![Comprendre les référentiels](../diagrams/images/referentiels-01-comprendre.png)','','## Parcours de lecture du draw.io','','| Page | Contenu |','|---|---|']
    for i,s in enumerate(stats,1):md.append(f"| {i} | {s['name']} |")
    md += [f'| {len(stats)+1} | Modèle complet — toutes les tables et colonnes |','','Les pages par thème montrent des extraits; une table répétée reste la même table. La dernière page rassemble les 365 colonnes initiales, les ajouts et tous les référentiels. Les liens métier existants restent disponibles. Les liens de codes et de versions sont dans deux nouveaux calques masqués au départ : **Vue > Calques**. Cette séparation garde les traits lisibles pendant une présentation.','','## Quelles clés utilise-t-on ?','','Chaque table de codes a pour clé primaire `(schema_sha256, code)`. Le code conserve son type d’origine : entier ou texte. Un code de devise et un code de type de compte ne vont pas dans la même table.','','La table métier référence cette clé avec `(schema_sha256, champ_code)`. `schema_sha256` est une FK de `STR_REPORT` vers `REF_SCHEMA_VERSION`. Les tables métier enrichies la portent également. Leur FK `(str_report_id, schema_sha256)` vers le couple unique du rapport impose la même copie du Swagger. Ces colonnes sont internes : elles ne figurent jamais dans le JSON transmis.','','Les listes sont immuables pour une empreinte donnée. Une nouvelle copie du Swagger crée un nouveau jeu de valeurs; les anciennes lignes sont conservées. `archived_on` est la date d’archivage, **pas** une date d’entrée en vigueur inventée.','','Les brouillons peuvent être incomplets. Au gel, la version de schéma est renseignée partout où elle est requise. Une colonne de code facultative reste facultative; l’ajout d’un référentiel ne la rend pas obligatoire. Pour un code non nul, les autres composants de sa FK doivent être présents : ne pas laisser une clé composite partiellement nulle contourner la validation.','','### Le cas des pièces d’identité','','Le code 1 signifie « Certificat de naissance » pour une personne et « Acte d’association » pour une entité. Une fusion sur le code seul serait fausse. `REF_TYPE_IDENTIFICATION` utilise donc `(schema_sha256, identification_family, code)`. La famille interne vaut `PERSON` ou `ENTITY`; elle se déduit du type de `STR_DEFINITION` propriétaire. La règle de cohérence avec cette définition doit être contrôlée séparément.','','## Les nouvelles colonnes dans les tables métier','','| Table | Colonne | Pourquoi |','|---|---|---|']
    for a in additions:md.append(f"| `{a['table']}` | `{a['column']}` | {a['reason']} |")
    md+=['','## Dictionnaire des référentiels','','Toutes les tables de codes utilisent les colonnes ci-dessous. `identification_family` n’existe que dans `REF_TYPE_IDENTIFICATION`. Les colonnes de métadonnées ne sont pas transmises à CANAFE.','','| Colonne | Clé / type | Pourquoi |','|---|---|---|']
    for c,why in purposes.items():md.append(f"| `{c}` | {'PK + FK, texte' if c=='schema_sha256' else 'PK, type JSON du domaine' if c=='code' else 'PK, texte (identification uniquement)' if c=='identification_family' else 'Texte'} | {why} |")
    md+=['','### REF_SCHEMA_VERSION','','| Colonne | Pourquoi |','|---|---|']
    for c,why in schema_purpose.items():md.append(f'| `{c}` | {why} |')
    md+=['','## Ne pas transformer toutes les contraintes en listes','','- **Provinces et États** : `ProvinceStateCode` contient des listes, mais aussi une branche de texte de deux caractères. Une FK fermée sur les trois listes exclurait des valeurs décrites par cette branche. Nous ne l’imposons pas. Le chevauchement du `oneOf` reste une anomalie à confirmer, déjà recensée dans [REGLES.md](REGLES.md).','- **Réponses et archives** : les codes de retour et les contenus bruts ne sont pas bloqués par une FK de liste. Un code nouveau ou inattendu doit rester archivable. Les enums observées figurent dans le fichier de couverture.','- **Formats** : longueurs, dates, montants et motifs restent dans le dictionnaire et les contraintes du Swagger.','- **Statuts internes** : `BROUILLON`, `PRET`, etc. restent des valeurs de fonctionnement interne. Ce ne sont pas des codes CANAFE.','- **Règles conditionnelles** : existence dans la liste, présence obligatoire et validité selon le rôle sont trois contrôles différents. Cette livraison ne prétend pas convertir toutes les règles de validation officielles en tables.','','## Traçabilité et listes complètes','',f'Copie archivée : 2026-09-22. Empreinte SHA-256 : `{SHA}`.','', '- [Swagger archivé](../source/swaggerExternal.yaml) · [Swagger officiel](https://www148.fintrac-canafe.canada.ca/swagger) · [Documentation et règles de validation officielles](https://fintrac-canafe.canada.ca/reporting-declaration/info/api/api-fra).','- [Toutes les valeurs, les libellés et leur provenance — CSV](../traceability/reference-values.csv).','- [Chaque champ vers son référentiel, sa variante et les valeurs permises — CSV](../traceability/reference-fields.csv).','- [Traitement de chaque occurrence enum du modèle — CSV](../traceability/reference-coverage.csv).','- [Modèle enrichi lisible par un outil — JSON](../model/model-with-references.json).','- [Dictionnaire des 365 colonnes existantes](DICTIONNAIRE.md).','','Les libellés sont extraits des descriptions publiées, sans corriger silencieusement leurs formulations ou leurs fautes. Un champ `source_pointer` indique où se trouve le code; `libelle_source_pointer` indique où son libellé est publié. Les titres des pages et les notes sont des explications métier rédigées pour ce projet. Les listes CANAFE sont conservées telles quelles, même si elles diffèrent de référentiels ISO récents.']
    for name,ref in REFS.items():
        md+=['','## '+name,'',ref['label']+'. '+constraint_note(name),'',f"**{len(ref['rows'])} valeurs.** Type JSON du code : `{ref['type']}`.",'','Champs concernés : '+', '.join('`'+b['table']+'.'+b['column']+'`' for b in BINDINGS if b['reference']==name)+'.','','| Famille | Code | Libellé français publié | Libellé anglais publié |','|---|---|---|---|']
        for row in ref['rows']:
            md.append('| '+ ' | '.join(str(row[k]).replace('|','\\|').replace('\n',' ') for k in ['identification_family','code','libelle_fr','libelle_en'])+' |')
        md+=['','Source(s) : '+', '.join('`'+p+'`' for p in ref['pointers'])+'.']
    write('docs/REFERENTIELS_CANAFE.md','\n'.join(md)+'\n')
    return additions

def main():
    protected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'diagrams').glob('*.drawio') if p!=TARGET}
    doc=ET.Element('mxfile',host='app.diagrams.net',agent='projetdod',version='26.0.0',type='device')
    stats=[intro(doc),version_page(doc),*focus_pages(doc),*catalog_pages(doc)]
    rels=full_page(doc);additions=documentation(stats,rels)
    ET.indent(doc);ET.ElementTree(doc).write(TARGET,encoding='utf-8',xml_declaration=False)
    # Contrôles structurels et de couverture; le rendu est vérifié séparément.
    for page in doc:
        cells=page.findall('.//mxCell');ids={c.get('id') for c in cells}
        assert len(ids)==len(cells),page.get('name')
        for c in cells:
            if c.get('edge')=='1':assert c.get('source') in ids and c.get('target') in ids
    full={c.get('id'):c for c in doc[-1].findall('.//mxCell')}
    for t in MODEL['tables']:
        text=html.unescape(full[t['name']].get('value',''))
        for col in t['columns']:assert col in text,(t['name'],col)
    for a in additions:assert a['column'] in full[a['table']].get('value')
    for n in REFS:assert n in full
    for name,ref in REFS.items():
        keys=set()
        for row in ref['rows']:
            key=(row['schema_sha256'],row['identification_family'],row['code'])
            assert key not in keys,(name,key)
            keys.add(key)
            schema=node(row['source_pointer'])
            assert row['code'] in schema['enum'],(name,row)
            assert type(row['code']) is (str if ref['type']=='string' else int)
    for b in BINDINGS:
        for mid,allowed in b['allowed_by_mapping'].items():
            f=next(f for f in MODEL['mappings'] if f['id']==mid)
            family=('PERSON' if '/personIdentification' in f['resolved_pointer'] else 'ENTITY') if b['reference']=='REF_TYPE_IDENTIFICATION' else ''
            keys={r['code'] for r in REFS[b['reference']]['rows'] if r['identification_family']==family}
            assert set(allowed)<=keys,(b,mid)
    assert protected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'diagrams').glob('*.drawio') if p!=TARGET}
    report={'file':TARGET.name,'pages':len(doc),'business_tables':34,'reference_tables':len(REFS),'schema_tables':1,'total_tables':35+len(REFS),'original_columns':365,'added_business_columns':len(additions),'field_reference_links':len(BINDINGS),'enum_occurrences_classified':len(COVERAGE),'catalog_values':sum(len(r['rows']) for r in REFS.values()),'old_drawio_sha256':protected,'all_original_columns_preserved':True,'all_edges_have_endpoints':True,'pages_without_overlap':stats,'source_sha256':SHA}
    dump('quality/referentiels.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['pages_without_overlap','old_drawio_sha256']},ensure_ascii=True,indent=2))

if __name__=='__main__':main()
