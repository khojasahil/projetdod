"""Contrôles indépendants de couverture et exemples; sans réseau ni base de données."""
import copy, hashlib, json, re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'source/openapi.json').read_text(encoding='utf-8'))

MARKS=json.loads((ROOT/'source/lines.json').read_text(encoding='utf-8'))
SCHEMAS=SPEC['components']['schemas']

def dump(path,data):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(s,p=''):
    while '$ref' in s:
        p=s['$ref'];s=SPEC
        for token in p[2:].split('/'):s=s[token.replace('~1','/').replace('~0','~')]
    return s,p

def leaves(s,p,path,branches=()):
    """Parcourt le contrat sans utiliser le générateur ni son catalogue de noms."""
    s,p=resolve(s,p)
    if 'oneOf' in s:
        for i,x in enumerate(s['oneOf']):
            name=x['$ref'].split('/')[-1] if '$ref' in x else p.split('/')[-1]+'/oneOf/'+str(i)
            yield from leaves(x,p+'/oneOf/'+str(i),path,branches+(name,))
    elif s.get('type')=='object':
        for k,v in s.get('properties',{}).items():yield from leaves(v,p+'/properties/'+k,path+'.'+k,branches)
    elif s.get('type')=='array':yield from leaves(s['items'],p+'/items',path+'[]',branches)
    else:yield path,p,branches

def variant_names(text):
    names=[]
    for part in text.split(';'):
        part=part.strip()
        if not part:continue
        m=re.fullmatch(r'typeCode=\d+ \(([^)]+)\)',part)
        names.append(m.group(1) if m else part)
    return tuple(names)

def errors(v,s,path='$'):
    """Validateur ciblé des mots-clés utilisés par les fixtures, pas un moteur OAS complet."""
    s,_=resolve(s)
    if 'oneOf' in s:
        matches=sum(not errors(v,x,path) for x in s['oneOf'])
        return [] if matches==1 else [f'{path}: oneOf correspond à {matches} branches']
    tp=s.get('type')
    types={'object':lambda x:isinstance(x,dict),'array':lambda x:isinstance(x,list),'string':lambda x:isinstance(x,str),'integer':lambda x:type(x)==int,'number':lambda x:type(x) in (int,float),'boolean':lambda x:type(x)==bool}
    if tp in types and not types[tp](v):return [f'{path}: type {tp} attendu']
    out=[]
    if 'enum' in s and v not in s['enum']:out.append(f'{path}: valeur hors enum')
    if isinstance(v,str):
        if 'pattern' in s and not re.search(s['pattern'],v):out.append(f'{path}: motif invalide')
        if len(v)<s.get('minLength',0) or len(v)>s.get('maxLength',10**9):out.append(f'{path}: longueur invalide')
    if isinstance(v,list):
        if len(v)<s.get('minItems',0) or len(v)>s.get('maxItems',10**9):out.append(f'{path}: cardinalité invalide')
        for i,x in enumerate(v):out+=errors(x,s.get('items',{}),f'{path}[{i}]')
    if isinstance(v,dict):
        for k in s.get('required',[]):
            if k not in v:out.append(f'{path}.{k}: propriété requise absente')
        for k,x in v.items():
            if k in s.get('properties',{}):out+=errors(x,s['properties'][k],path+'.'+k)
            elif s.get('additionalProperties') is False:out.append(f'{path}.{k}: propriété supplémentaire interdite')
    return out

def fixture():
    structured={'typeCode':1,'buildingNumber':'100','streetAddress':'Rue Exemple','city':'Montréal','provinceStateName':'Québec','postalZipCode':'H0H0H0','countryCode':'CA'}
    free={'typeCode':2,'countryCode':'CA','unstructured':'Adresse fictive pour démonstration uniquement'}
    defs=[
      {'typeCode':1,'refId':'NOM-P1','givenName':'Camille','surname':'Exemple'},
      {'typeCode':2,'refId':'NOM-E2','nameOfEntity':'Société Exemple Fictive'},
      {'typeCode':3,'refId':'BEN-P3','givenName':'Alex','surname':'Fictif','addressTypeCode':2,'address':free,'identifications':[]},
      {'typeCode':4,'refId':'BEN-E4','nameOfEntity':'Bénéficiaire Fictif Inc','identifications':[],'registrationsIncorporations':[],'authorizedPersons':[]},
      {'typeCode':5,'refId':'EXEC-P5','givenName':'Camille','surname':'Exemple','addressTypeCode':1,'address':structured,'identifications':[],'employerInformation':{'name':'Employeur Fictif','addressTypeCode':2,'address':free}},
      {'typeCode':6,'refId':'TIERS-E6','nameOfEntity':'Tiers Fictif Inc','structureTypeCode':1,'identifications':[],'authorizedPersons':[],'registrationsIncorporations':[], 'directorsOfCorporation':[{'givenName':'Claude','surname':'Exemple','addressTypeCode':1,'address':structured}], 'personsOwningSharesOfCorporation':[{'givenName':'Claude','surname':'Exemple'}], 'trusteesOfTrust':[],'settlorsOfTrust':[],'personsOwningUnitsOfTrust':[],'beneficiariesOfTrust':[],'personsOwningEntityNotCorporationOrTrust':[]}
    ]
    vc={'virtualCurrencyTransactionIds':[],'sendingVirtualCurrencyAddresses':[],'receivingVirtualCurrencyAddresses':[]}
    report={'reportDetails':{'reportTypeCode':102,'submitTypeCode':1,'activitySectorCode':2,'reportingEntityNumber':1234567,'submittingReportingEntityNumber':1234567,'reportingEntityReportReference':'DEMO-DOD-001','reportingEntityContactId':1001},
      'detailsOfSuspicion':{'descriptionOfSuspiciousActivity':'EXEMPLE FICTIF. Texte destiné uniquement à illustrer le stockage du récit et sa correction. Aucun dossier réel.','suspicionTypeCode':1,'publicPrivatePartnershipProjectNameCodes':[],'politicallyExposedPersonIncludedIndicator':False},
      'relatedReports':[],'actionTaken':{'description':'EXEMPLE FICTIF : examen interne documenté.'},'definitions':defs,
      'transactions':[{'reportingEntityLocationId':'DEMO-001','suspiciousTransactionDetails':{'attemptedTransactionIndicator':False,'dateOfTransaction':'2026-09-20','timeOfTransaction':'10:30:00-04:00','methodCode':1,'reportingEntityTransactionReference':'DEMO-TXN-001','purpose':'Démonstration fictive'},
        'startingActions':[{'details':{**vc,'direction':1,'fundAssetVirtualCurrencyTypeCode':2,'amount':'1250.00','currencyCode':'CAD','account':{'financialInstitutionNumber':'000','branchNumber':'00000','number':'DEMO-COMPTE-001','typeCode':1,'holders':[{'typeCode':1,'refId':'NOM-P1'}]},'conductorIndicator':True,'sourcesOfFundsOrVirtualCurrencyIndicator':True},'sourcesOfFundsOrVirtualCurrency':[{'typeCode':2,'refId':'NOM-E2'}],'conductors':[{'typeCode':5,'refId':'EXEC-P5','details':{'clientNumber':'DEMO-CLIENT','onBehalfOfIndicator':True},'onBehalfOfs':[{'typeCode':6,'refId':'TIERS-E6','details':{'relationshipOfConductorCode':1}}]}]}],
        'completingActions':[{'details':{**vc,'dispositionCode':1,'amount':'1250.00','currencyCode':'CAD','beneficiaryIndicator':True},'involvements':[],'beneficiaries':[{'typeCode':3,'refId':'BEN-P3'},{'typeCode':4,'refId':'BEN-E4'}]}]}]}
    return report

def business_refs(report):
    definitions=report['definitions'];by_id={x['refId']:x for x in definitions};out=[]
    if len(by_id)!=len(definitions):out.append('refId dupliqué dans la version')
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k in ('sourcesOfFundsOrVirtualCurrency','involvements','holders','beneficiaries','conductors','onBehalfOfs'):
                    domain={'sourcesOfFundsOrVirtualCurrency':(1,2),'involvements':(1,2),'holders':(1,2),'beneficiaries':(3,4),'conductors':(5,6),'onBehalfOfs':(5,6)}[k]
                    for role in v:
                        target=by_id.get(role['refId'])
                        if target is None or target['typeCode']!=role['typeCode'] or role['typeCode'] not in domain:out.append('référence incompatible : '+role['refId'])
                walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    walk(report['transactions']);return out
