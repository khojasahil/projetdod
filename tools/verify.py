"""Contrôles indépendants de couverture et exemples; sans réseau ni base de données."""
import copy, hashlib, json, re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'source/openapi.json').read_text(encoding='utf-8'))
MODEL=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
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

def main():
    roots={'STRReport':'$','SubmitReportResponse':'SubmitReportResponse$','Validations':'Validations$','ErrorWithValidation':'ErrorWithValidation$','DeleteReport':'DeleteReport$'}
    expected=set()
    for s,p in roots.items():expected.update(leaves(SCHEMAS[s],'#/components/schemas/'+s,p))
    actual={(m['json_path'],m['resolved_pointer'],variant_names(m['variant'])) for m in MODEL['mappings'] if m['kind']=='champ'}
    assert expected==actual,{'missing':sorted(expected-actual),'extra':sorted(actual-expected)}
    tables={t['name']:t for t in MODEL['tables']}
    for m in MODEL['mappings']:
        assert m['table'] in tables and m['column'] in tables[m['table']]['columns']
        assert m['source_pointer'] in MARKS and m['resolved_pointer'] in MARKS
    for t in tables.values():
        for c in t['columns'].values():
            paths={MODEL['mappings'][i]['json_path'] for i in c['mappings']}
            assert len(paths)<=1,('collision de propriétés',t['name'],c['name'],paths)
        if t['scope']=='version' and t['name']!='STR_VERSION':assert 'version_id' in t['columns'],t['name']
    for r in MODEL['relationships']:
        assert r['parent'] in tables and r['child'] in tables
        for c in r['fk'].split(', '):assert c in tables[r['child']]['columns'],r
        for c in r['parent_key'].split(', '):assert c in tables[r['parent']]['columns'],r
    for n in ('STR_PERSON_DETAILS','STR_ENTITY_DETAILS','STR_PERSON_EMPLOYER','STR_ENTITY_OWNERSHIP'):
        assert 'address_type_code' in tables[n]['columns'] and 'address__type_code' in tables[n]['columns']
    xml=ET.parse(ROOT/'diagrams/CANAFE_DOD.drawio');seen_tables=set();pages=xml.findall('diagram')
    for page in pages:
        cs=page.findall('.//mxCell');ids=[c.get('id') for c in cs]
        assert len(ids)==len(set(ids))
        seen_tables.update(set(ids)&tables.keys())
        for c in cs:
            if c.get('edge')=='1':assert c.get('source') in ids and c.get('target') in ids
            if c.get('vertex')=='1':
                g=c.find('mxGeometry');assert float(g.get('width'))>0 and float(g.get('height'))>0
    assert seen_tables==set(tables)
    v1=fixture();assert not errors(v1,SCHEMAS['STRReport']),errors(v1,SCHEMAS['STRReport']);assert not business_refs(v1)
    v2=copy.deepcopy(v1);v2['reportDetails']['submitTypeCode']=2;v2['detailsOfSuspicion']['descriptionOfSuspiciousActivity']+=' Correction fictive v2 : détail complémentaire documenté.'
    assert not errors(v2,SCHEMAS['STRReport']);assert v1['reportDetails']['submitTypeCode']==1
    dump('examples/str-v1.json',v1);dump('examples/str-v2.json',v2)
    tests=[]
    def reject(name,change,checker):
        value=copy.deepcopy(v1);change(value);assert checker(value),name;tests.append(name)
    reject('Montant à une seule décimale',lambda x:x['transactions'][0]['startingActions'][0]['details'].update(amount='10.0'),lambda x:errors(x,SCHEMAS['STRReport']))
    reject('Définitions requises absentes',lambda x:x.pop('definitions'),lambda x:errors(x,SCHEMAS['STRReport']))
    reject('Opérations requises sans élément',lambda x:x.update(transactions=[]),lambda x:errors(x,SCHEMAS['STRReport']))
    reject('Liste conductors absente',lambda x:x['transactions'][0]['startingActions'][0].pop('conductors'),lambda x:errors(x,SCHEMAS['STRReport']))
    reject('Référence inconnue',lambda x:x['transactions'][0]['startingActions'][0]['conductors'][0].update(refId='INCONNU'),business_refs)
    reject('Référence de type incompatible',lambda x:x['transactions'][0]['startingActions'][0]['conductors'][0].update(refId='NOM-P1'),business_refs)
    reject('RefId dupliqué',lambda x:x['definitions'][1].update(refId='NOM-P1'),business_refs)
    reject('Adresse libre sans texte requis',lambda x:x['definitions'][2]['address'].pop('unstructured'),lambda x:errors(x,SCHEMAS['STRReport']))
    reject('Champ supplémentaire à la racine',lambda x:x.update(internalId=1),lambda x:errors(x,SCHEMAS['STRReport']))
    optional=copy.deepcopy(v1);optional.pop('actionTaken');assert not errors(optional,SCHEMAS['STRReport'])
    optional['actionTaken']={};assert not errors(optional,SCHEMAS['STRReport'])
    submit={'code':200,'message':{'en':'FICTITIOUS EXAMPLE','fr':'EXEMPLE FICTIF'},'payload':{'externalReportUuid':'DEMO-EXTERNAL-ID-NOT-A-REAL-REPORT','reportingEntityReportReference':'DEMO-DOD-001','submitDateTime':'2026-09-22T14:00:00.000Z','validationMessages':[]}}
    assert not errors(submit,SCHEMAS['SubmitReportResponse']);dump('examples/submit-response.json',submit)
    validation={'reportingEntityBulkReference':'DEMO-LOT-001','processedDate':'2026-09-22T14:01:00-04:00','status':{'code':2001,'en':'FICTITIOUS EXAMPLE','fr':'EXEMPLE FICTIF'},'acceptedWithWarningsCount':1,'acceptedNoWarningsCount':0,'rejectedCount':0,'totalCount':1,'acknowledgements':[{'reportingEntityReportReference':'DEMO-DOD-001','messageTypeCode':2,'validationMessages':[{'path':'/transactions/0','rule':'DEMO-NON-OFFICIELLE','error':{'code':999999,'en':'FICTITIOUS WARNING','fr':'AVERTISSEMENT FICTIF'},'type':'warning'}]}]}
    ambiguity=errors(validation,SCHEMAS['Validations']);assert len(ambiguity)==1 and '2 branches' in ambiguity[0]
    province_ambiguity=errors('QC',SCHEMAS['ProvinceStateCode'],'ProvinceStateCode');assert len(province_ambiguity)==1 and '2 branches' in province_ambiguity[0]
    ambiguity+=province_ambiguity
    dump('examples/validation-result.json',validation)
    deletion={'reportDetails':{k:v1['reportDetails'][k] for k in ('reportTypeCode','reportingEntityNumber','submittingReportingEntityNumber','reportingEntityReportReference')}}
    deletion['reportDetails'].update(submitTypeCode=5,reportSubmitReasonCode=4)
    assert not errors(deletion,SCHEMAS['DeleteReport']);dump('examples/delete-request.json',deletion)
    provenance=json.loads((ROOT/'source/provenance.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/'source/swaggerExternal.yaml').read_bytes()).hexdigest()==provenance['sha256']
    stats={'date':'2026-09-22','result':'PASS','tables':len(tables),'columns':sum(len(t['columns']) for t in tables.values()),'diagram_pages':len(pages),'named_scalar_occurrences_expected':len(expected),'named_scalar_occurrences_mapped':len(actual),'str_named_scalar_occurrences':len(set(leaves(SCHEMAS['STRReport'],'#/components/schemas/STRReport','$'))),'mapping_rows_including_presence':len(MODEL['mappings']),'missing_fields':[],'source_hash_verified':True,'all_relationship_targets_exist':True,'no_column_path_collisions':True,'all_payload_tables_scoped_to_version':True,'drawio_xml_and_connectors_verified':True,'negative_scenarios_detected':tests,'known_contract_ambiguity_confirmed':ambiguity,'limits':['Validation locale ciblée; pas un moteur complet OpenAPI.','Aucun appel ni essai d’acceptation métier CANAFE.','Couverture des propriétés nommées, pas des propriétés additionnelles non décrites.','Vérification XML et géométrie; voir séparément la vérification visuelle.','Aucune base de données créée; intégrité décrite dans le modèle logique.']}
    dump('quality/verification.json',stats);print(json.dumps(stats,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
