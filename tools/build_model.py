"""Catalogue des 34 tables : reprend les domaines du projet-io, sans DDL."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'source/openapi.json').read_text(encoding='utf-8'))
LINES=json.loads((ROOT/'source/lines.json').read_text(encoding='utf-8'))
LABELS=json.loads((ROOT/'tools/labels.json').read_text(encoding='utf-8'))
T={};F=[];R=[];S=[];DOMAINS=[]
GROUPS=[
 ('Rapport','#2563EB','Quel dossier transmet-on ?',[
  ('REPORT','str_report_id','Le rapport','Une version de la déclaration, avec le récit du soupçon et les mesures prises.'),
  ('PPP_PROJECT','ppp_id','Les projets associés','Les projets de partenariat public-privé cités dans le rapport.'),
  ('RELATED_REPORT','related_report_id','Les rapports liés','Les références d’autres déclarations utiles pour comprendre le dossier.'),
  ('RELATED_REPORT_TXN_REF','id','Les opérations liées','Les références d’opérations à retrouver dans un rapport lié.')]),
 ('Définitions','#15803D','De qui parle-t-on ?',[
  ('DEFINITION','definition_id','Le point de référence','Le repère utilisé pour citer une personne ou une entreprise dans le rapport.'),
  ('PERSON','person_id','La personne','Les renseignements sur une personne physique, selon le niveau de détail demandé.'),
  ('ENTITY','entity_id','L’entité','Les renseignements sur une entreprise, une organisation ou une fiducie.'),
  ('EMPLOYER_INFO','employer_id','L’employeur','Les coordonnées de l’employeur lorsque la définition de personne les prévoit.')]),
 ('Identité','#B7791F','Comment la décrire et l’identifier ?',[
  ('ADDRESS','address_id','L’adresse','Une adresse structurée ou en texte libre, rattachée à son propriétaire.'),
  ('IDENTIFICATION','identification_id','Les pièces d’identité','Les documents utilisés pour identifier la personne ou l’entité.')]),
 ('Entité','#0F766E','Comment l’organisation est-elle constituée ?',[
  ('REGISTRATION_INCORPORATION','reg_inc_id','L’enregistrement','Les numéros et lieux d’enregistrement ou de constitution de l’entité.'),
  ('AUTHORIZED_PERSON','auth_id','Les personnes autorisées','Les noms des personnes autorisées à agir pour l’entité.')]),
 ('Bénéficiaires effectifs','#C24153','Qui dirige ou détient l’entité ?',[
  ('DIRECTOR','director_id','Les administrateurs','Les personnes qui administrent la société.'),
  ('SHARE_OWNER','share_owner_id','Les détenteurs d’actions','Les personnes détenant des actions, telles qu’elles sont déclarées.'),
  ('TRUSTEE','trustee_id','Les fiduciaires','Les personnes qui administrent la fiducie.'),
  ('SETTLOR','settlor_id','Les constituants','Les personnes à l’origine de la fiducie.'),
  ('TRUST_UNIT_OWNER','trust_unit_owner_id','Les détenteurs d’unités','Les personnes détenant des unités de la fiducie.'),
  ('TRUST_BENEFICIARY','trust_beneficiary_id','Les bénéficiaires de fiducie','Les personnes désignées comme bénéficiaires de la fiducie.'),
  ('OTHER_ENTITY_OWNER','other_entity_owner_id','Les autres propriétaires','Les personnes détenant une entité qui n’est ni une société ni une fiducie.')]),
 ('Transactions','#C76C12','Que s’est-il passé ?',[
  ('TRANSACTION','transaction_id','L’opération','L’opération effectuée ou tentée, sa date et les circonstances connues.'),
  ('STARTING_ACTION','starting_action_id','L’action initiale','Ce qui amorce le mouvement : nature des fonds, sens et montant.'),
  ('COMPLETING_ACTION','completing_action_id','L’action finale','Ce qui est fait des fonds à l’issue du mouvement.')]),
 ('Rôles','#7C3AED','Qui fait quoi dans l’opération ?',[
  ('CONDUCTOR','conductor_id','L’exécutant','La personne ou l’entité qui réalise l’action initiale.'),
  ('ON_BEHALF_OF','obo_id','Le tiers représenté','La personne ou l’entité pour le compte de laquelle agit l’exécutant.'),
  ('SOURCE_OF_FUNDS','source_id','La source des fonds','La personne ou l’entité désignée comme source des fonds.'),
  ('INVOLVEMENT','involvement_id','La personne impliquée','La personne ou l’entité impliquée dans l’action finale.'),
  ('BENEFICIARY','beneficiary_id','Le bénéficiaire de l’opération','La personne ou l’entité qui bénéficie de l’action finale.')]),
 ('Comptes','#059669','Par quels comptes ou adresses les fonds passent-ils ?',[
  ('ACCOUNT','account_id','Le compte','Le compte tel qu’il est décrit pour une action donnée.'),
  ('ACCOUNT_HOLDER','holder_id','Les titulaires','Les personnes ou entités titulaires de ce compte.'),
  ('VC_DATA','vc_data_id','La monnaie virtuelle','Les identifiants et adresses de monnaie virtuelle associés à une action.')]),
 ('Audit','#64748B','Qu’a-t-on envoyé et quelle réponse a-t-on reçue ?',[
  ('API_SUBMISSION','submission_id','Le suivi de l’envoi','Une tentative d’envoi ou une consultation de résultats pour une version précise.'),
  ('SUBMITTED_PAYLOAD','payload_id','Le contenu transmis','La copie exacte du document envoyé, conservée avec son empreinte.'),
  ('VALIDATION_ERROR','error_id','Les messages de validation','Les erreurs et avertissements détectés en interne ou renvoyés par CANAFE.'),
  ('AUDIT_EVENT','event_id','Le journal du dossier','La trace datée des décisions et des changements apportés au dossier.')])]

def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8',newline='\n')
def dump(path,obj):write(path,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def snake(s):return re.sub(r'(?<!^)(?=[A-Z])','_',s).lower()
def resolve(s,p):
    while '$ref' in s:
        p=s['$ref'];s=SPEC
        for k in p[2:].split('/'):s=s[int(k)] if isinstance(s,list) else s[k.replace('~1','/').replace('~0','~')]
    return s,p
def col(t,n,ty,why,rule='',origin='INTERNE'):
    if n not in T[t]['columns']:T[t]['columns'][n]={'name':n,'type':ty,'reason':why,'rule':rule,'origin':origin,'mapping_ids':[]}
    elif origin=='SWAGGER':T[t]['columns'][n]['origin']='SWAGGER'
    return T[t]['columns'][n]
def link(parent,child,fk,label,card='0..N',optional=False,show=True):
    col(child,fk,'Identifiant',label,f'FK vers {parent}.{T[parent]["pk"]}'+('; facultatif' if optional else '; requis'))
    R.append({'parent':parent,'child':child,'parent_key':T[parent]['pk'],'foreign_key':fk,'cardinality':card,'meaning':label,'optional_fk':optional,'show_in_business':show})

def init():
    for name,color,question,items in GROUPS:
        domain={'name':name,'color':color,'question':question,'tables':[]};DOMAINS.append(domain)
        for suffix,pk,label,why in items:
            n='STR_'+suffix;domain['tables'].append(n)
            T[n]={'name':n,'pk':pk,'domain':name,'color':color,'label':label,'reason':why,'columns':{},'rules':[]}
            col(n,pk,'Identifiant',f'Identifie cette ligne de {label.lower()}.','Clé primaire')
    for n in T:
        if n!='STR_REPORT':link('STR_REPORT',n,'str_report_id','Appartient à cette version de rapport.',show=False)
    for n in ('STR_PPP_PROJECT','STR_RELATED_REPORT','STR_DEFINITION','STR_TRANSACTION','STR_API_SUBMISSION','STR_AUDIT_EVENT'):
        next(r for r in R if r['parent']=='STR_REPORT' and r['child']==n)['show_in_business']=True
    links=[('RELATED_REPORT','RELATED_REPORT_TXN_REF','related_report_id','Précise une opération de ce rapport lié.'),
     ('DEFINITION','PERSON','definition_id','Décrit la personne citée par ce repère.','0..1'),
     ('DEFINITION','ENTITY','definition_id','Décrit l’entité citée par ce repère.','0..1'),
     ('PERSON','EMPLOYER_INFO','person_id','Décrit l’employeur de cette personne.','0..1'),
     ('DEFINITION','IDENTIFICATION','definition_id','Identifie cette personne ou cette entité.'),
     ('ENTITY','REGISTRATION_INCORPORATION','entity_id','Documente la constitution de cette entité.'),
     ('ENTITY','AUTHORIZED_PERSON','entity_id','Désigne une personne autorisée pour cette entité.'),
     ('TRANSACTION','STARTING_ACTION','transaction_id','Décrit une action au début du mouvement.'),
     ('TRANSACTION','COMPLETING_ACTION','transaction_id','Décrit une action à la fin du mouvement.'),
     ('STARTING_ACTION','CONDUCTOR','starting_action_id','Indique qui réalise cette action.'),
     ('CONDUCTOR','ON_BEHALF_OF','conductor_id','Indique pour qui agit cet exécutant.'),
     ('STARTING_ACTION','SOURCE_OF_FUNDS','starting_action_id','Indique d’où proviennent les fonds.'),
     ('COMPLETING_ACTION','INVOLVEMENT','completing_action_id','Indique qui intervient dans cette action.'),
     ('COMPLETING_ACTION','BENEFICIARY','completing_action_id','Indique qui bénéficie de cette action.'),
     ('ACCOUNT','ACCOUNT_HOLDER','account_id','Désigne un titulaire de ce compte.'),
     ('API_SUBMISSION','SUBMITTED_PAYLOAD','submission_id','Conserve le document transmis lors de cet appel.','0..1')]
    for v in links:link('STR_'+v[0],'STR_'+v[1],v[2],v[3],v[4] if len(v)>4 else '0..N')
    for suffix,_,_,_ in GROUPS[4][3]:link('STR_ENTITY','STR_'+suffix,'entity_id','Décrit la propriété ou la gouvernance de cette entité.')
    owners=['STR_PERSON','STR_ENTITY','STR_EMPLOYER_INFO','STR_DIRECTOR','STR_TRUSTEE','STR_SETTLOR','STR_TRUST_UNIT_OWNER','STR_TRUST_BENEFICIARY']
    for n in owners:link('STR_ADDRESS',n,'address_id','Adresse de cette personne ou de cette organisation.','0..1',True)
    for n in ('STR_ACCOUNT','STR_VC_DATA'):
        for p,k in [('STR_STARTING_ACTION','starting_action_id'),('STR_COMPLETING_ACTION','completing_action_id')]:link(p,n,k,'Rattache les données à cette action.','0..1' if n=='STR_ACCOUNT' else '0..N',True)
        T[n]['rules'].append('Une seule des clés starting_action_id et completing_action_id est renseignée (XOR). Le parent appartient au même str_report_id.')
    for suffix in ('CONDUCTOR','ON_BEHALF_OF','SOURCE_OF_FUNDS','INVOLVEMENT','BENEFICIARY','ACCOUNT_HOLDER'):
        n='STR_'+suffix
        T[n]['rules'].append('Référence typée : (str_report_id, type_code, ref_id) → STR_DEFINITION(str_report_id, type_code, ref_id).')
        R.append({'parent':'STR_DEFINITION','child':n,'parent_key':'str_report_id, type_code, ref_id','foreign_key':'str_report_id, type_code, ref_id','cardinality':'0..N','meaning':'Retrouve la personne ou l’entité qui tient ce rôle.','optional_fk':False,'show_in_business':False})
    link('STR_API_SUBMISSION','STR_VALIDATION_ERROR','submission_id','Message reçu dans cette tentative ou consultation.','0..N',True)
    link('STR_API_SUBMISSION','STR_API_SUBMISSION','initial_submission_id','Relie une consultation ou une reprise à l’envoi initial.','0..N',True,False)
    link('STR_REPORT','STR_REPORT','previous_report_id','Relie cette version à la précédente.','0..1',True,False)
    # Le rapport porte lui-même les versions : aucune table supplémentaire.
    internals={
      'STR_REPORT': [('report_group_id','Identifiant','Regroupe les versions d’une même déclaration.','Stable dans toute la chaîne'),('version_number','Entier','Numérote les versions pour retrouver ce qui a changé.','Unique par report_group_id; commence à 1'),('status','Texte','État de préparation interne du rapport.','BROUILLON, PRET, GELE, REMPLACE'),('created_at','Date et heure','Date de création de cette version.',''),('created_by','Texte','Personne ou service à l’origine de la version.',''),('frozen_at','Date et heure','Date à partir de laquelle les données métier ne sont plus modifiables.','Facultatif avant gel'),('schema_sha256','Texte','Identifie la copie exacte du Swagger utilisée.','Empreinte du fichier officiel archivé')],
      'STR_VC_DATA':[('data_type','Texte','Distingue identifiant de transaction, adresse émettrice et adresse réceptrice.','TXN_ID, SENDING_ADDR, RECEIVING_ADDR')],
      'STR_API_SUBMISSION':[('operation','Texte','Nature de l’appel : soumettre, corriger, supprimer ou consulter.','SUBMIT, UPDATE, DELETE, VALIDATIONS, RECONCILE'),('environment','Texte','Distingue les essais des envois de production.','TEST ou PROD'),('attempt_number','Entier','Ordonne les appels associés à la version.','Unique avec str_report_id'),('started_at','Date et heure','Début de l’appel.',''),('completed_at','Date et heure','Fin de l’appel, si connue.',''),('http_status_code','Entier','Statut réseau; ne signifie pas à lui seul que le rapport est accepté.','Facultatif si absence de réponse'),('transport_error','Texte','Explication d’un échec technique.','Facultatif'),('processing_status','Texte','État métier déduit de la réponse et des messages.','INCONNU, RECU, EN_TRAITEMENT, ACCEPTE, AVERTISSEMENT, REJETE, SUPPRIME'),('external_report_uuid','Texte','Identifiant du rapport renvoyé par CANAFE.','Facultatif; conservé comme chaîne'),('api_response_body','Texte JSON','Réponse complète, avant interprétation; conserve aussi les champs non projetés.','Immuable'),('response_sha256','Texte','Empreinte des octets de la réponse conservée.',''),('bulk_reference','Texte','Référence de lot, si le rapport a été transmis en lot.','Facultatif'),('correlation_id','Identifiant','Regroupe les lignes qui concernent le même appel de lot.','Facultatif'),('file_name','Texte','Nom du fichier transmis, utile pour rapprocher les retours.','Facultatif')],
      'STR_SUBMITTED_PAYLOAD':[('payload_json','Texte JSON','Document exact envoyé; on peut donc retrouver ce que CANAFE a reçu.','Conserver les octets UTF-8 sans les reformater'),('payload_hash_sha256','Texte','Détecte une modification du contenu archivé.','Une empreinte seule ne prouve pas la non-répudiation'),('created_at','Date et heure','Date d’archivage du document.','')],
      'STR_VALIDATION_ERROR':[('origin','Texte','Distingue un contrôle interne d’un message reçu de CANAFE.','LOCAL ou CANAFE'),('message_type','Texte','Distingue une validation de structure d’une validation métier.','SCHEMA ou METIER'),('severity','Texte','Distingue un avertissement d’un rejet.','warning, reject ou unknown; conserve la casse des valeurs API'),('ack_report_reference','Texte','Référence qui permet de rattacher le message à la bonne déclaration.','Facultatif; obligatoire pour rapprochement de lot'),('ack_ordinal','Entier','Position de l’accusé dans la réponse de lot.','Facultatif'),('detected_at','Date et heure','Date à laquelle le message est connu.','')],
      'STR_AUDIT_EVENT':[('event_type','Texte','Action consignée dans le dossier.','CREATED, EDITED, VALIDATED, FROZEN, SUBMITTED, CORRECTED'),('event_user','Texte','Auteur de l’action.',''),('event_timestamp','Date et heure','Moment de l’action.',''),('event_details','Texte','Raison ou explication de l’action, en langage courant.','')]
    }
    for t,cs in internals.items():
        for n,ty,w,r in cs:col(t,n,ty,w,r)
    # Un rang appartient à une liste, pas à une identité réelle.
    singleton={'STR_REPORT','STR_PERSON','STR_ENTITY','STR_EMPLOYER_INFO','STR_ADDRESS','STR_ACCOUNT','STR_API_SUBMISSION','STR_SUBMITTED_PAYLOAD','STR_AUDIT_EVENT'}
    for t in T:
        if t not in singleton:col(t,'ordinal','Entier','Conserve la position dans la liste JSON, même si deux valeurs sont identiques.','Commence à 0; unique dans son parent et sa liste')
    T['STR_REPORT']['rules']+=['Une ligne = une version. UNIQUE(report_group_id, version_number). previous_report_id reste dans le même groupe et pointe vers la version précédente; pas de branche ni de cycle.', 'Au gel : report_type_code = 102; au moins une transaction; objets et listes requis présents.', 'Correction : même reporting_entity_number et re_report_reference. Une nouvelle déclaration subséquente a un nouveau groupe.', 'Les données d’une version gelée et de ses enfants ne sont jamais écrasées.']
    T['STR_DEFINITION']['rules']+=['UNIQUE(str_report_id, ref_id) et UNIQUE(str_report_id, type_code, ref_id).', 'Exactement une ligne PERSON si type_code ∈ {1,3,5}, ou une ligne ENTITY si type_code ∈ {2,4,6}.']
    for t in ('STR_PERSON','STR_ENTITY'):T[t]['rules'].append('UNIQUE(definition_id). Les champs autorisés dépendent du type_code de la définition; voir les variantes de la traçabilité.')
    T['STR_EMPLOYER_INFO']['rules'].append('UNIQUE(person_id). Possible uniquement pour une personne de type 5; une ligne vide conserve employerInformation: {}.')
    T['STR_ADDRESS']['rules'].append('Une adresse appartient à un seul propriétaire de la même version. Ce contrôle entre tables est à implanter; ce n’est pas une clé étrangère polymorphe.')
    T['STR_IDENTIFICATION']['rules'].append('La définition propriétaire est de type 3, 4, 5 ou 6. Le domaine du document dépend de personne ou entité.')
    T['STR_ACCOUNT']['rules'].append('Une action a au plus un compte : unicité de chaque clé d’action lorsqu’elle est renseignée.')
    T['STR_VC_DATA']['rules'].append('Rang unique par action ET data_type; chaque catégorie reconstitue sa propre liste, vide si aucune ligne.')
    T['STR_VALIDATION_ERROR']['rules'].append('Pour CANAFE, submission_id est requis et correspond au même str_report_id. Le terme ERROR du nom historique englobe aussi les avertissements.')
    for t in T:
        if t!='STR_REPORT':T[t]['rules'].append('Toute référence à un parent ou à une définition est vérifiée dans le même str_report_id; clé composite (str_report_id, clé_du_parent).')

BO={'directorsOfCorporation':'DIRECTOR','personsOwningSharesOfCorporation':'SHARE_OWNER','trusteesOfTrust':'TRUSTEE','settlorsOfTrust':'SETTLOR','personsOwningUnitsOfTrust':'TRUST_UNIT_OWNER','beneficiariesOfTrust':'TRUST_BENEFICIARY','personsOwningEntityNotCorporationOrTrust':'OTHER_ENTITY_OWNER'}
DEF_TYPES={'PersonName':1,'EntityName':2,'PersonDetails':3,'EntityDetails':4,'personAndEmployerDetails':5,'entityAndBeneficialOwnershipDetails':6}
ALIASES={'reportingEntityReportReference':'re_report_reference','reportingEntityContactId':'re_contact_id','submittingReportingEntityNumber':'submitting_re_number','descriptionOfSuspiciousActivity':'suspicious_activity_desc','politicallyExposedPersonIncludedIndicator':'pep_included_indicator','reportingEntityLocationId':'re_location_id','attemptedTransactionIndicator':'attempted_indicator','reportingEntityTransactionReference':'re_txn_reference','fundAssetVirtualCurrencyTypeCode':'fund_type_code','fundAssetVirtualCurrencyTypeOther':'fund_type_other','virtualCurrencyTypeCode':'vc_type_code','virtualCurrencyTypeOther':'vc_type_other','referenceNumberOtherRelatedNumber':'ref_number_other','accountStatusAtTimeOfTransaction':'account_status_code','howFundsOrVirtualCurrencyObtained':'how_funds_obtained','sourcesOfFundsOrVirtualCurrencyIndicator':'source_funds_indicator','valueInCanadianDollars':'value_in_cad','typeOfDeviceCode':'device_type_code','typeOfDeviceOther':'device_type_other','deviceIdentifierNumber':'device_id_number','internetProtocolAddress':'ip_address','dateTimeOfOnlineSession':'online_session_datetime','relationshipOfConductorCode':'relationship_code','relationshipOfConductorOther':'relationship_other','financialInstitutionNumber':'fi_number','jurisdictionOfIssueCountryCode':'jurisdiction_country_code','jurisdictionOfIssueProvinceStateCode':'jurisdiction_province_state_code','jurisdictionOfIssueProvinceStateName':'jurisdiction_province_state_name'}

def route(path,branches):
    field=path.split('.')[-1].replace('[]','');name=ALIASES.get(field,snake(field));condition=''
    if not path.startswith('$.'):
        if 'validationMessages[]' in path:
            names={'path':'instance_path','instancePath':'instance_path','schemaPath':'schema_path','keyword':'keyword','rule':'rule_id','code':'error_code','type':'severity','en':'message_en','fr':'message_fr'}
            return 'STR_VALIDATION_ERROR',names.get(field,name),'Message enfant de la réponse','colonne'
        if path.startswith('SubmitReportResponse$') and field=='externalReportUuid':return 'STR_API_SUBMISSION','external_report_uuid','','colonne'
        return ('STR_SUBMITTED_PAYLOAD','payload_json','Document DeleteReport conservé intégralement','JSON archivé') if path.startswith('DeleteReport$') else ('STR_API_SUBMISSION','api_response_body','Réponse conservée intégralement; chemin interne au JSON','JSON archivé')
    if path.startswith('$.reportDetails') or path.startswith('$.detailsOfSuspicion') or path.startswith('$.actionTaken'):
        if 'publicPrivatePartnershipProjectNameCodes' in path:return 'STR_PPP_PROJECT','project_name_code','','colonne'
        return 'STR_REPORT',('action_taken_desc' if field=='description' else name),'','colonne'
    if path.startswith('$.relatedReports'):
        return ('STR_RELATED_REPORT_TXN_REF','txn_reference','','colonne') if 'reportingEntityTransactionReferences' in path else ('STR_RELATED_REPORT',name,'','colonne')
    if path.startswith('$.definitions'):
        typ=next((DEF_TYPES[b] for b in branches if b in DEF_TYPES),None)
        base='STR_PERSON' if typ in (1,3,5) else 'STR_ENTITY'
        condition=f'typeCode de définition = {typ}'
        if field in ('typeCode','refId') and path.count('.')==2:return 'STR_DEFINITION',name,condition,'colonne'
        owner=next(('STR_'+v for k,v in BO.items() if k+'[]' in path),base)
        if '.employerInformation' in path:owner='STR_EMPLOYER_INFO'
        if '.address.' in path:return 'STR_ADDRESS',name,condition+'; propriétaire '+owner,'colonne'
        if '.identifications[]' in path:return 'STR_IDENTIFICATION',name,condition,'colonne'
        if '.authorizedPersons[]' in path:return 'STR_AUTHORIZED_PERSON',name,condition,'colonne'
        if '.registrationsIncorporations[]' in path:return 'STR_REGISTRATION_INCORPORATION',name,condition,'colonne'
        return owner,name,condition,'colonne'
    if path.startswith('$.transactions'):
        start='.startingActions[]' in path;end='.completingActions[]' in path
        action='STR_STARTING_ACTION' if start else 'STR_COMPLETING_ACTION'
        if not(start or end):return 'STR_TRANSACTION',name,'','colonne'
        cond='action initiale' if start else 'action finale'
        if '.account.holders[]' in path:return 'STR_ACCOUNT_HOLDER',name,cond,'colonne'
        if '.account.' in path:return 'STR_ACCOUNT',name,cond,'colonne'
        for fld,kind in [('virtualCurrencyTransactionIds','TXN_ID'),('sendingVirtualCurrencyAddresses','SENDING_ADDR'),('receivingVirtualCurrencyAddresses','RECEIVING_ADDR')]:
            if fld in path:return 'STR_VC_DATA','value',cond+'; data_type='+kind,'colonne'
        for role,name_role in [('onBehalfOfs','ON_BEHALF_OF'),('conductors','CONDUCTOR'),('sourcesOfFundsOrVirtualCurrency','SOURCE_OF_FUNDS'),('involvements','INVOLVEMENT'),('beneficiaries','BENEFICIARY')]:
            if '.'+role+'[]' in path:return 'STR_'+name_role,name,cond,'colonne'
        return action,name,cond,'colonne'
    raise ValueError(path)

def walk(s,p,path,branches=(),required=False,usage=None):
    orig=p;s,p=resolve(s,p)
    if 'oneOf' in s:
        for i,x in enumerate(s['oneOf']):
            label=x['$ref'].split('/')[-1] if '$ref' in x else p.split('/')[-1]+'/oneOf/'+str(i)
            scalar=resolve(x,p+'/oneOf/'+str(i))[0].get('type') not in ('object','array',None)
            walk(x,p+'/oneOf/'+str(i),path,branches+(label,),required,orig if scalar else None)
    elif s.get('type') in ('object','array'):
        S.append({'json_path':path,'source_pointer':p,'source_line':LINES[p],'type':s['type'],'required_in_parent':required,'minItems':s.get('minItems'),'variant':'; '.join(branches),'additionalProperties':s.get('additionalProperties','non précisé')})
        if s['type']=='object':
            for k,v in s.get('properties',{}).items():walk(v,p+'/properties/'+k,path+'.'+k,branches,k in s.get('required',[]))
        else:walk(s['items'],p+'/items',path+'[]',branches,True)
    else:
        t,n,condition,storage=route(path,branches)
        ty={'integer':'Entier','number':'Nombre exact','boolean':'Oui / non','string':'Texte'}.get(s.get('type'),'Texte')
        if 'maxLength' in s:ty+=' ('+str(s['maxLength'])+')'
        key=path.split('.')[-1].replace('[]','')
        why=LABELS[key]+'.'
        if t=='STR_PERSON' and key=='refId':raise AssertionError('refId doit rester dans DEFINITION')
        if storage=='colonne':col(t,n,ty,why,origin='SWAGGER')
        fid=f'F{len(F)+1:04}'
        m={'id':fid,'table':t,'column':n,'json_path':path,'source_pointer':usage or orig,'resolved_pointer':p,'source_line':LINES[usage or orig],'resolved_line':LINES[p],'required_in_parent':required,'variant':'; '.join(branches),'condition':condition,'storage':storage,'constraints':{k:s[k] for k in ('type','format','enum','pattern','minLength','maxLength','minimum','maximum','nullable') if k in s}}
        F.append(m);T[t]['columns'][n]['mapping_ids'].append(fid)

def extras():
    # La présence d’un objet est matérialisée par une ligne enfant quand elle existe.
    for t,n,path,why in [
      ('STR_REPORT','action_taken_present','$.actionTaken','Distingue des mesures non renseignées d’un objet actionTaken présent mais vide.'),
      ('STR_SOURCE_OF_FUNDS','details_present','$.transactions[].startingActions[].sourcesOfFundsOrVirtualCurrency[].details','Distingue des détails absents d’un objet details vide.'),
      ('STR_ON_BEHALF_OF','details_present','$.transactions[].startingActions[].conductors[].onBehalfOfs[].details','Distingue des détails absents d’un objet details vide.'),
      ('STR_INVOLVEMENT','details_present','$.transactions[].completingActions[].involvements[].details','Distingue des détails absents d’un objet details vide.'),
      ('STR_BENEFICIARY','details_present','$.transactions[].completingActions[].beneficiaries[].details','Distingue des détails absents d’un objet details vide.')]:
        col(t,n,'Oui / non',why,'Interne; jamais envoyé dans le JSON')
    for t in T.values():
        for c in t['columns'].values():
            ms=[m for m in F if m['id'] in c['mapping_ids'] and m['storage']=='colonne']
            if ms:
                c['required']='Selon le contexte' if any(m['required_in_parent'] for m in ms) else 'Facultatif dans le Swagger'
                if all(m['constraints'].get('type')=='string' for m in ms):c['type']='Texte'+(' ('+str(max(m['constraints'].get('maxLength',0) for m in ms))+')' if all('maxLength' in m['constraints'] for m in ms) else '')
            else:c['required']='Voir règle interne'

def markdown():
    rel=['# Registre des relations','',
      'Ce registre permet de reproduire tous les liens. Il se lit du parent vers l’enfant. Les liens vers STR_REPORT rattachent chaque ligne à une version; les autres clés sont aussi contrôlées dans cette même version.', '',
      'Une cardinalité de 0..N décrit le nombre de lignes enfants possibles par parent. Elle ne signifie pas que la clé portée par un enfant est facultative. Les obligations avant gel et les contraintes exclusives figurent dans [REGLES.md](REGLES.md). Les références composites vers DEFINITION utilisent les trois colonnes indiquées.', '',
      '| Parent | Clé parent | Enfant | Clé portée par l’enfant | Enfants par parent | Clé facultative | Explication |',
      '|---|---|---|---|---|---|---|']
    for r in R:rel.append('| '+' | '.join([r['parent'],r['parent_key'],r['child'],r['foreign_key'],r['cardinality'],'Oui' if r['optional_fk'] else 'Non',r['meaning']])+' |')
    rel+=['','Pour ADDRESS, la cardinalité 0..1 s’applique dans chaque table propriétaire. Une règle supplémentaire impose un seul propriétaire au total. Pour les versions, previous_report_id est absent sur la première version. Pour ACCOUNT et VC_DATA, une seule des deux clés d’action est renseignée.','']
    write('docs/RELATIONS.md','\n'.join(rel))
    out=['# Dictionnaire des 34 tables','', 'Ce document sert à construire le modèle. Pour le présenter à des collègues, commencer par le [guide métier](GUIDE_METIER.md).','',
      'Les neuf domaines et les noms de tables reprennent le projet précédent. Une ligne de `STR_REPORT` représente une version; tous ses enfants portent le même `str_report_id`. Les règles de saisie et les obligations au moment d’envoyer sont distinguées dans [REGLES.md](REGLES.md).','',
      'Les identifiants, rangs et indicateurs de présence sont internes. Les types sont logiques, sans choix de SGBD. « Facultatif dans le Swagger » ne dispense pas de vérifier une obligation métier conditionnelle. Les champs propres à un type de définition ne sont ni saisis ni transmis pour les autres types.','',
      'Les références `Fxxxx` renvoient aux lignes de [fields.csv](../traceability/fields.csv), qui donnent le chemin JSON complet, la variante, le JSON Pointer, les lignes du YAML et les contraintes exactes. Les réponses API sont archivées intégralement; seuls les messages et l’identifiant externe sont également projetés en colonnes.','']
    for domain in DOMAINS:
        out +=['## '+domain['name'],'',domain['question'],'']
        for n in domain['tables']:
            t=T[n];out +=['### '+n+' — '+t['label'],'',t['reason'],'']
            out+=['| Colonne | Type | À quoi elle sert | Origine / obligation | Trace |','|---|---|---|---|---|']
            for c in t['columns'].values():
                source=c['origin']+' · '+c['required'];why=c['reason']+(' '+c['rule'] if c['rule'] else '')
                ms=[m for m in F if m['id'] in c['mapping_ids']]
                # Regrouper les nombreux usages du même champ d’adresse.
                refs=', '.join(c['mapping_ids']) or 'Interne'
                if ms:
                    paths=list(dict.fromkeys(m['json_path'] for m in ms))
                    refs+=' — `'+paths[0]+'`'+(f' (+ {len(paths)-1} autres usages)' if len(paths)>1 else '')
                out.append('| '+' | '.join(str(x).replace('|','\\|') for x in [c['name'],c['type'],why,source,refs])+' |')
            if t['rules']:out+=['','À respecter :','']+['- '+x for x in t['rules']]
            out.append('')
    write('docs/DICTIONNAIRE.md','\n'.join(out).rstrip()+'\n')
    enum={}
    for m in F:
        if 'enum' in m['constraints']:
            s,p=resolve({'$ref':m['resolved_pointer']},m['resolved_pointer']);enum[p]={'values':s['enum'],'description':s.get('description',''),'line':LINES[p]}
    dump('model/code-domains.json',enum)
    parts=['# Domaines de codes','', 'Les domaines sont ceux de la copie Swagger archivée. Ils ne constituent pas des tables supplémentaires.','']
    for p,e in enum.items():parts +=['## '+p,'',f"[Source, ligne {e['line']}](../source/swaggerExternal.yaml#L{e['line']})",'', '`'+json.dumps(e['values'],ensure_ascii=False)+'`','',e['description'],'']
    write('docs/DOMAINES_CODES.md','\n'.join(x.rstrip() for x in '\n'.join(parts).splitlines()).rstrip()+'\n')

def generate():
    init()
    for schema,path in [('STRReport','$'),('SubmitReportResponse','SubmitReportResponse$'),('Validations','Validations$'),('ErrorWithValidation','ErrorWithValidation$'),('DeleteReport','DeleteReport$')]:walk(SPEC['components']['schemas'][schema],'#/components/schemas/'+schema,path)
    extras();markdown()
    obj={'architecture':'projet-io / 34 tables / 9 domaines','domains':DOMAINS,'tables':list(T.values()),'relationships':R,'mappings':F,'structures':S}
    dump('model/model.json',obj)
    for file,rows in [('fields.csv',F),('structures.csv',S),('relationships.csv',R)]:
        p=ROOT/'traceability'/file;p.parent.mkdir(exist_ok=True)
        with p.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
            for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    return obj

if __name__=='__main__':
    obj=generate();print(json.dumps({'tables':len(T),'columns':sum(len(t['columns']) for t in T.values()),'mappings':len(F)}))
