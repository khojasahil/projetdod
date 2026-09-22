"""Vérifie la couverture source, les relations, les exemples et la géométrie."""
from example_checks import *
from PIL import Image

MODEL=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))

def main():
    expected=set()
    for s,p in {'STRReport':'$','SubmitReportResponse':'SubmitReportResponse$','Validations':'Validations$','ErrorWithValidation':'ErrorWithValidation$','DeleteReport':'DeleteReport$'}.items():
        expected.update(leaves(SCHEMAS[s],'#/components/schemas/'+s,p))
    actual={(m['json_path'],m['resolved_pointer'],variant_names(m['variant'])) for m in MODEL['mappings']}
    assert expected==actual,{'missing':sorted(expected-actual),'extra':sorted(actual-expected)}
    tables={t['name']:t for t in MODEL['tables']}
    assert len(tables)==34
    assert [len(d['tables']) for d in MODEL['domains']]==[4,4,2,2,7,3,5,3,4]
    assert set(tables)=={t for d in MODEL['domains'] for t in d['tables']}
    for m in MODEL['mappings']:
        assert m['column'] in tables[m['table']]['columns']
        assert MARKS[m['source_pointer']]==m['source_line']
        assert MARKS[m['resolved_pointer']]==m['resolved_line']
        assert m['id'] in tables[m['table']]['columns'][m['column']]['mapping_ids']
    for t in tables.values():
        assert t['pk'] in t['columns'] and 'str_report_id' in t['columns']
        for c in t['columns'].values():assert c['reason'] and c['type']
    for r in MODEL['relationships']:
        for c in r['foreign_key'].split(', '):assert c in tables[r['child']]['columns'],r
        for c in r['parent_key'].split(', '):assert c in tables[r['parent']]['columns'],r
    def mapped(path,table,column):
        ms=[m for m in MODEL['mappings'] if m['json_path']==path]
        assert ms and all(m['table']==table and m['column']==column for m in ms),(path,ms)
    mapped('$.definitions[].address.typeCode','STR_ADDRESS','type_code')
    mapped('$.transactions[].startingActions[].details.account.number','STR_ACCOUNT','number')
    mapped('$.transactions[].completingActions[].details.account.number','STR_ACCOUNT','number')
    mapped('$.transactions[].startingActions[].conductors[].onBehalfOfs[].refId','STR_ON_BEHALF_OF','ref_id')
    for t in ('STR_PERSON','STR_ENTITY'):assert 'address_type_code' in tables[t]['columns'] and 'address_id' in tables[t]['columns']
    for t in ('STR_ACCOUNT','STR_VC_DATA'):assert any('XOR' in r for r in tables[t]['rules'])
    for t in tables.values():
        for c in t['columns'].values():
            ms=[m for m in MODEL['mappings'] if m['id'] in c['mapping_ids'] and m['storage']=='colonne']
            if ms and t['name'] not in ('STR_VC_DATA','STR_VALIDATION_ERROR'):
                names={m['json_path'].split('.')[-1] for m in ms}
                assert len(names)<=1,('collision de propriétés',t['name'],c['name'],names)
    page_counts={}
    for filename,count in [('CANAFE_DOD.drawio',9),('CANAFE_DOD_DETAIL.drawio',34)]:
        pages=ET.parse(ROOT/'diagrams'/filename).findall('diagram');assert len(pages)==count
        seen=set();page_counts[filename]=len(pages)
        for page in pages:
            graph=page.find('mxGraphModel');pw=float(graph.get('pageWidth'));ph=float(graph.get('pageHeight'))
            cells=page.findall('.//mxCell');ids=[c.get('id') for c in cells];assert len(ids)==len(set(ids))
            seen.update(set(ids)&set(tables))
            for c in cells:
                if c.get('edge')=='1':assert c.get('source') in ids and c.get('target') in ids
                if c.get('vertex')=='1':
                    g=c.find('mxGeometry');x,y,w,h=[float(g.get(k)) for k in ('x','y','width','height')]
                    assert x>=0 and y>=0 and w>0 and h>0 and x+w<=pw+1 and y+h<=ph+1,(filename,page.get('name'),c.get('id'),x,y,w,h,pw,ph)
        assert seen==set(tables)
    scenes=json.loads((ROOT/'model/presentation.json').read_text(encoding='utf-8'));assert len(scenes)==9
    for scene in scenes:
        im=Image.open(ROOT/'diagrams/images'/(scene['slug']+'.png'));assert im.size==(scene['width']*2,scene['height']*2)
        rects={x['id']:x for x in scene['items'] if x['kind']=='rect'}
        for i in scene['items']:
            if i['kind']!='text':continue
            owner=next((n for n in scene['tables'] if i['id'].startswith(n+'-')),None)
            if owner:
                box=rects[owner]
                assert i['x']>=box['x'] and i['x']+i['w']<=box['x']+box['w']+1
                assert i['y']+i['h']<=box['y']+box['h']+1,(scene['slug'],i['id'])
    v1=fixture();assert not errors(v1,SCHEMAS['STRReport']),errors(v1,SCHEMAS['STRReport']);assert not business_refs(v1)
    v2=copy.deepcopy(v1);v2['reportDetails']['submitTypeCode']=2;v2['detailsOfSuspicion']['descriptionOfSuspiciousActivity']+=' Correction fictive v2 : détail complémentaire documenté.'
    assert not errors(v2,SCHEMAS['STRReport']);assert v1['reportDetails']['submitTypeCode']==1
    dump('examples/str-v1.json',v1);dump('examples/str-v2.json',v2)
    negative=[]
    def reject(name,change,checker):
        value=copy.deepcopy(v1);change(value);assert checker(value),name;negative.append(name)
    reject('Montant à une décimale',lambda x:x['transactions'][0]['startingActions'][0]['details'].update(amount='10.0'),lambda x:errors(x,SCHEMAS['STRReport']))
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
    submit=json.loads((ROOT/'examples/submit-response.json').read_text(encoding='utf-8'));assert not errors(submit,SCHEMAS['SubmitReportResponse'])
    deletion=json.loads((ROOT/'examples/delete-request.json').read_text(encoding='utf-8'));assert not errors(deletion,SCHEMAS['DeleteReport'])
    validation=json.loads((ROOT/'examples/validation-result.json').read_text(encoding='utf-8'))
    ambiguity=errors(validation,SCHEMAS['Validations']);assert len(ambiguity)==1 and '2 branches' in ambiguity[0]
    province=errors('QC',SCHEMAS['ProvinceStateCode']);assert len(province)==1 and '2 branches' in province[0]
    story={'notice':'Extrait fictif de lignes, colonnes non pertinentes omises; pas un jeu à charger directement.',
       'STR_REPORT':[{'str_report_id':'R-V1','report_group_id':'DOSSIER-A','version_number':1,'previous_report_id':None},{'str_report_id':'R-V2','report_group_id':'DOSSIER-A','version_number':2,'previous_report_id':'R-V1'}],
       'STR_API_SUBMISSION':[{'submission_id':'ENVOI-1','str_report_id':'R-V1','attempt_number':1,'operation':'SUBMIT','initial_submission_id':None},
          {'submission_id':'CONSULTATION-1','str_report_id':'R-V1','attempt_number':2,'operation':'VALIDATIONS','initial_submission_id':'ENVOI-1'},
          {'submission_id':'ENVOI-2','str_report_id':'R-V2','attempt_number':1,'operation':'UPDATE','initial_submission_id':None}]}
    reports={r['str_report_id']:r for r in story['STR_REPORT']};calls={r['submission_id']:r for r in story['STR_API_SUBMISSION']}
    for r in reports.values():
        if r['previous_report_id']:
            prev=reports[r['previous_report_id']];assert prev['report_group_id']==r['report_group_id'] and prev['version_number']==r['version_number']-1
    for r in calls.values():
        assert r['str_report_id'] in reports
        if r['initial_submission_id']:assert calls[r['initial_submission_id']]['str_report_id']==r['str_report_id']
    dump('examples/parcours-metier.json',story)
    prov=json.loads((ROOT/'source/provenance.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/'source/swaggerExternal.yaml').read_bytes()).hexdigest()==prov['sha256']
    for p in [ROOT/'README.md',*list((ROOT/'docs').glob('*.md'))]:
        for dest in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' in dest or dest.startswith('#'):continue
            assert (p.parent/dest.split('#')[0]).exists(),(p,dest)
    stats={'date':'2026-09-22','result':'PASS','tables':len(tables),'domains':9,'columns':sum(len(t['columns']) for t in tables.values()),'diagram_pages':page_counts,'named_scalar_occurrences_expected':len(expected),'named_scalar_occurrences_mapped':len(actual),'str_named_scalar_occurrences':len(set(leaves(SCHEMAS['STRReport'],'#/components/schemas/STRReport','$'))),'missing_fields':[],'source_hash_verified':True,'all_relationship_targets_exist':True,'all_children_scoped_to_report_version':True,'drawio_xml_geometry_and_connectors_verified':True,'negative_scenarios_detected':negative,'known_contract_ambiguities_confirmed':ambiguity+province,'limits':['Validation locale ciblée, pas un moteur OpenAPI complet.','Aucun essai d’acceptation CANAFE.','Couverture des propriétés nommées et des archives, pas des propriétés additionnelles indéfinies.','Aucune base créée; contraintes logiques à implanter.','La vérification de mise en page ne remplace pas la relecture visuelle.']}
    dump('quality/verification.json',stats);print(json.dumps(stats,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
