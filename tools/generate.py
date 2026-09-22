"""Génère documentation et draw.io; aucun DDL et aucun appel à la CANAFE."""
import csv, hashlib, html, json, re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'source/openapi.json').read_text(encoding='utf-8'))
LINES=json.loads((ROOT/'source/lines.json').read_text(encoding='utf-8'))
TABLES={}; MAPPINGS=[]; STRUCTURES=[]; RELATIONS=[]; ENUMS={}

def snake(s):
    return re.sub(r'(?<!^)(?=[A-Z])','_',s).lower()
def resolve(s,p):
    while '$ref' in s:
        p=s['$ref']; s=SPEC
        for k in p[2:].split('/'): s=s[k.replace('~1','/').replace('~0','~')]
    return s,p
def ptr(p,k): return p+'/'+str(k).replace('~','~0').replace('/','~1')
def write(p,s):
    path=ROOT/p; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(s,encoding='utf-8')
def jsonwrite(p,x): write(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def cell(x): return str(x).replace('|','\\|').replace('\n','<br>')

LABELS={
 'reportTypeCode':'Type de déclaration : DOD, code 102 dans ce projet',
 'submitTypeCode':'Nature de la demande : création, mise à jour ou suppression',
 'activitySectorCode':'Secteur d’activité de l’entité déclarante',
 'reportingEntityNumber':'Numéro de l’entité responsable de la déclaration',
 'submittingReportingEntityNumber':'Numéro de l’entité qui transmet la déclaration',
 'reportingEntityReportReference':'Référence de déclaration attribuée par l’entité déclarante',
 'reportingEntityContactId':'Identifiant du contact de l’entité déclarante',
 'ministerialDirectiveCode':'Directive ministérielle associée',
 'descriptionOfSuspiciousActivity':'Récit des faits, du contexte et des soupçons',
 'suspicionTypeCode':'Catégorie du soupçon déclaré',
 'politicallyExposedPersonIncludedIndicator':'Présence déclarée d’une personne politiquement vulnérable',
 'publicPrivatePartnershipProjectNameCodes':'Projet de partenariat public-privé associé',
 'reportingEntityTransactionReferences':'Référence d’une opération dans une déclaration connexe',
 'description':'Description des mesures prises',
 'reportingEntityLocationId':'Établissement de l’entité déclarante concerné',
 'attemptedTransactionIndicator':'Distinction entre opération tentée et opération effectuée',
 'reasonNotCompleted':'Raison pour laquelle l’opération n’a pas été achevée',
 'dateOfTransaction':'Date locale de l’opération', 'timeOfTransaction':'Heure de l’opération avec décalage UTC',
 'dateOfPosting':'Date de comptabilisation', 'timeOfPosting':'Heure de comptabilisation avec décalage UTC',
 'methodCode':'Mode de réalisation de l’opération', 'methodOther':'Précision du mode autre',
 'reportingEntityTransactionReference':'Référence de l’opération attribuée par l’entité déclarante',
 'purpose':'Objet de l’opération', 'direction':'Sens du flux de l’action initiale',
 'fundAssetVirtualCurrencyTypeCode':'Nature des fonds, actifs ou monnaies virtuelles',
 'fundAssetVirtualCurrencyTypeOther':'Précision de la nature autre des fonds ou actifs',
 'amount':'Montant déclaré, conservé dans sa représentation textuelle exacte',
 'currencyCode':'Devise des fonds', 'virtualCurrencyTypeCode':'Type de monnaie virtuelle',
 'virtualCurrencyTypeOther':'Précision de la monnaie virtuelle autre',
 'exchangeRate':'Taux de change déclaré, conservé sans arrondi',
 'valueInCanadianDollars':'Contre-valeur déclarée en dollars canadiens',
 'virtualCurrencyTransactionIds':'Identifiant d’opération sur le réseau de monnaie virtuelle',
 'sendingVirtualCurrencyAddresses':'Adresse de monnaie virtuelle émettrice',
 'receivingVirtualCurrencyAddresses':'Adresse de monnaie virtuelle réceptrice',
 'referenceNumber':'Numéro de référence de l’action',
 'referenceNumberOtherRelatedNumber':'Autre numéro associé à la référence',
 'accountStatusAtTimeOfTransaction':'État du compte au moment de cette action',
 'howFundsOrVirtualCurrencyObtained':'Origine décrite des fonds ou monnaies virtuelles',
 'sourcesOfFundsOrVirtualCurrencyIndicator':'Indicateur de présence d’une source de fonds',
 'conductorIndicator':'Indicateur de présence d’un exécutant',
 'involvementIndicator':'Indicateur de présence d’une personne ou entité impliquée',
 'beneficiaryIndicator':'Indicateur de présence d’un bénéficiaire de l’action finale',
 'onBehalfOfIndicator':'Indicateur d’exécution pour le compte d’un tiers',
 'typeCode':'Discriminant de la structure ou du rôle dans ce contexte',
 'refId':'Référence locale à une définition de la même version de déclaration',
 'accountNumber':'Numéro de compte associé au rôle', 'policyNumber':'Numéro de police associé au rôle',
 'identifyingNumber':'Autre numéro identifiant la participation au flux',
 'clientNumber':'Numéro de client connu dans ce rôle', 'emailAddress':'Adresse courriel connue dans ce rôle',
 'url':'Adresse web connue dans ce rôle', 'typeOfDeviceCode':'Type d’appareil utilisé',
 'typeOfDeviceOther':'Précision du type d’appareil autre', 'username':'Nom d’utilisateur utilisé',
 'deviceIdentifierNumber':'Identifiant de l’appareil utilisé', 'internetProtocolAddress':'Adresse IP de la session',
 'dateTimeOfOnlineSession':'Date et heure de session avec décalage UTC',
 'relationshipOfConductorCode':'Lien entre l’exécutant et la personne ou entité représentée',
 'relationshipOfConductorOther':'Précision de la relation autre', 'dispositionCode':'Utilisation ou destination des fonds',
 'dispositionOther':'Précision de la disposition autre',
 'surname':'Nom de famille', 'givenName':'Prénom', 'otherNameInitial':'Autres noms ou initiales',
 'nameOfEntity':'Dénomination de l’entité', 'alias':'Alias de la personne',
 'telephoneNumber':'Numéro de téléphone', 'extensionNumber':'Poste téléphonique',
 'dateOfBirth':'Date de naissance', 'countryOfResidenceCode':'Pays de résidence',
 'countryOfCitizenshipCode':'Pays de citoyenneté', 'occupation':'Profession ou métier',
 'nameOfEmployer':'Nom de l’employeur déclaré dans PersonDetails', 'name':'Nom de l’employeur',
 'addressTypeCode':'Qualification de l’adresse au niveau du propriétaire',
 'unitNumber':'Numéro d’unité', 'buildingNumber':'Numéro d’immeuble', 'streetAddress':'Rue',
 'city':'Ville', 'district':'District', 'provinceStateCode':'Code de province ou État',
 'provinceStateName':'Nom de province ou État', 'subProvinceSubLocality':'Subdivision ou localité',
 'postalZipCode':'Code postal', 'countryCode':'Pays de l’adresse', 'unstructured':'Adresse en texte libre',
 'identifierTypeCode':'Type de document d’identification', 'identifierTypeOther':'Précision du document autre',
 'number':'Numéro déclaré dans le contexte de cette table',
 'jurisdictionOfIssueCountryCode':'Pays de délivrance ou d’enregistrement',
 'jurisdictionOfIssueProvinceStateCode':'Province ou État de délivrance ou d’enregistrement',
 'jurisdictionOfIssueProvinceStateName':'Nom de juridiction non codifiée',
 'natureOfPrincipalBusiness':'Nature de l’activité principale de l’entité',
 'registrationIncorporationIndicator':'Indicateur d’enregistrement ou de constitution',
 'structureTypeCode':'Structure juridique de l’entité', 'structureTypeOther':'Précision de la structure autre',
 'financialInstitutionNumber':'Numéro de l’institution financière du compte', 'branchNumber':'Numéro de succursale',
 'typeOther':'Précision du type de compte autre', 'dateOpened':'Date d’ouverture du compte',
 'dateClosed':'Date de fermeture du compte', 'externalReportUuid':'Identifiant externe renvoyé par CANAFE, traité comme texte',
 'submitDateTime':'Horodatage de soumission renvoyé par CANAFE',
 'code':'Code numérique du résultat dans ce contexte', 'en':'Libellé ou message en anglais', 'fr':'Libellé ou message en français',
 'path':'Chemin du champ signalé par la validation métier', 'rule':'Identifiant de règle de validation',
 'type':'Sévérité de validation : rejet ou avertissement', 'instancePath':'Chemin du champ dans le document validé',
 'schemaPath':'Chemin dans le schéma utilisé par le validateur', 'keyword':'Mot-clé de validation concerné',
 'reportingEntityBulkReference':'Référence du lot attribuée par l’entité déclarante',
 'processedDate':'Horodatage de traitement renvoyé par CANAFE',
 'acceptedWithWarningsCount':'Nombre de déclarations acceptées avec avertissements',
 'acceptedNoWarningsCount':'Nombre de déclarations acceptées sans avertissement',
 'rejectedCount':'Nombre de déclarations rejetées', 'totalCount':'Nombre total de déclarations traitées',
 'messageTypeCode':'Distinction entre validation de schéma et validation métier',
 'reportSubmitReasonCode':'Motif de suppression : duplicata ou soumission par erreur'
}

def col(t,n,typ,why,origin='TECHNIQUE',constraint='',nullable=False):
    if n not in TABLES[t]['columns']:
        TABLES[t]['columns'][n]={'name':n,'type':typ,'reason':why,'origin':origin,'constraint':constraint,'nullable':nullable,'mappings':[]}
    return TABLES[t]['columns'][n]
def table(n,domain,why,parent=None,array=False,scope='version',subtype=False):
    if n in TABLES: return n
    TABLES[n]={'name':n,'domain':domain,'reason':why,'columns':{},'parent':parent,'array':array,'scope':scope,'constraints':[]}
    if subtype:
        col(n,'id','IDENTIFIANT','Identité partagée avec la définition parente.',constraint='PK; FK STR_DEFINITION.id')
    else: col(n,'id','IDENTIFIANT','Identifiant interne stable de cette occurrence.',constraint='PK')
    if scope=='version' and n!='STR_VERSION':
        col(n,'version_id','IDENTIFIANT','Isole les données dans une version et empêche les références entre versions.',constraint='FK STR_VERSION.id')
        TABLES[n]['constraints'].append('UNIQUE(version_id, id) pour les références composites.')
    if parent:
        fk='id' if subtype else 'parent_id'
        if not subtype: col(n,fk,'IDENTIFIANT',f'Rattache cette occurrence à {parent}.',constraint=f'FK {parent}.id')
        RELATIONS.append({'parent':parent,'child':n,'fk':fk,'parent_key':'id','cardinality':'1 → 0..N' if array else '1 → 0..1','kind':'composition','same_version':scope=='version'})
        if array:
            col(n,'ordinal','ENTIER','Préserve l’ordre JSON et distingue des valeurs répétées.',constraint='>= 0; UNIQUE(parent_id, ordinal)')
        else: TABLES[n]['constraints'].append(f'UNIQUE({fk}); une occurrence au plus par parent.')
    return n

def addmap(t,n,path,p,resolved,s,required,variant='',kind='champ'):
    m={'table':t,'column':n,'json_path':path,'source_pointer':p,'resolved_pointer':resolved,'source_line':LINES.get(p,LINES.get(resolved)), 'resolved_line':LINES.get(resolved),'required_in_parent':required,'variant':variant,'kind':kind,'constraints':{k:s[k] for k in ('type','format','enum','pattern','minLength','maxLength','minimum','maximum','nullable','minItems','maxItems') if k in s}}
    MAPPINGS.append(m)
    if n: TABLES[t]['columns'][n]['mappings'].append(len(MAPPINGS)-1)
    if 'enum' in s: ENUMS[resolved]={'pointer':resolved,'line':LINES.get(resolved),'values':s['enum'],'description':s.get('description','')}

def typ(s):
    return {'integer':'ENTIER','number':'NOMBRE EXACT','boolean':'BOOLÉEN','string':f"TEXTE({s['maxLength']})" if 'maxLength' in s else 'TEXTE','object':'OBJET JSON'}.get(s.get('type'),'TEXTE')
def scalar(t,n,field,path,p,s,required,variant='',resolved_pointer=None):
    s,r=resolve(s,p)
    if resolved_pointer:r=resolved_pointer
    why=LABELS.get(field)
    if why is None: raise ValueError('Libellé manquant: '+field)
    why+='; conserve cette information au niveau de '+t+'.'
    if field in ('amount','exchangeRate','valueInCanadianDollars'): why+=' Évite de modifier la précision ou les zéros du texte JSON.'
    c=col(t,n,typ(s),why,'SWAGGER',nullable=not required or bool(variant))
    if c['type']!=typ(s): c['type']='TEXTE' if c['type'].startswith('TEXTE') and typ(s).startswith('TEXTE') else 'VARIANT JSON SCALAIRE'
    addmap(t,n,path,p,r,s,required,variant)

ARRAY_NAMES={
 'publicPrivatePartnershipProjectNameCodes':'STR_PPP_PROJECT', 'relatedReports':'STR_RELATED_REPORT',
 'reportingEntityTransactionReferences':'STR_RELATED_TRANSACTION', 'transactions':'STR_TRANSACTION',
 'startingActions':'STR_STARTING_ACTION','completingActions':'STR_COMPLETING_ACTION',
 'sourcesOfFundsOrVirtualCurrency':'STR_SOURCE_OF_FUNDS','conductors':'STR_CONDUCTOR',
 'onBehalfOfs':'STR_ON_BEHALF_OF','involvements':'STR_INVOLVEMENT','beneficiaries':'STR_BENEFICIARY',
 'directorsOfCorporation':'STR_DIRECTOR','personsOwningSharesOfCorporation':'STR_SHARE_OWNER',
 'trusteesOfTrust':'STR_TRUSTEE','settlorsOfTrust':'STR_SETTLOR','personsOwningUnitsOfTrust':'STR_TRUST_UNIT_OWNER',
 'beneficiariesOfTrust':'STR_TRUST_BENEFICIARY','personsOwningEntityNotCorporationOrTrust':'STR_OTHER_ENTITY_OWNER',
}
ARRAY_SUFFIX={'identifications':'IDENTIFICATION','authorizedPersons':'AUTHORIZED_PERSON','registrationsIncorporations':'REGISTRATION','holders':'HOLDER','virtualCurrencyTransactionIds':'VC_TRANSACTION','sendingVirtualCurrencyAddresses':'VC_SENDER','receivingVirtualCurrencyAddresses':'VC_RECEIVER','validationMessages':'MESSAGE','acknowledgements':'ACK'}
DEFS={'PersonName':'STR_PERSON_NAME','EntityName':'STR_ENTITY_NAME','PersonDetails':'STR_PERSON_DETAILS','EntityDetails':'STR_ENTITY_DETAILS','personAndEmployerDetails':'STR_PERSON_EMPLOYER','entityAndBeneficialOwnershipDetails':'STR_ENTITY_OWNERSHIP'}

def structure(t,path,p,s,required,kind,storage):
    STRUCTURES.append({'table':t,'json_path':path,'source_pointer':p,'line':LINES.get(p),'kind':kind,'required_in_parent':required,'minItems':s.get('minItems'),'additionalProperties':s.get('additionalProperties','non précisé'),'storage':storage})

def props(t,s,p,path,prefix='',variant='',skip=()):
    s,p=resolve(s,p)
    for field,v in s.get('properties',{}).items():
        if field in skip: continue
        pp=ptr(ptr(p,'properties'),field); sp=path+'.'+field; n=prefix+snake(field)
        required=field in s.get('required',[]); z,r=resolve(v,pp)
        if 'oneOf' in z and all(resolve(b,r+'/oneOf/'+str(i))[0].get('type') not in ('object','array',None) for i,b in enumerate(z['oneOf'])):
            for i,b in enumerate(z['oneOf']):
                bs,bp=resolve(b,r+'/oneOf/'+str(i))
                scalar(t,n,field,sp,pp,bs,required,variant+'; '+r.split('/')[-1]+'/oneOf/'+str(i),resolved_pointer=bp)
            continue
        if field=='definitions' and t=='STR_VERSION':
            structure(t,sp,pp,z,required,'array','STR_DEFINITION')
            dn=table('STR_DEFINITION','Définitions','Catalogue des six variantes, local à la version.',t,True)
            TABLES[dn]['constraints']+=['UNIQUE(version_id, ref_id).','UNIQUE(version_id, type_code, ref_id).','Exactement un sous-type correspondant à type_code, de 1 à 6.']
            for i,b in enumerate(z['items']['oneOf']):
                ds,dp=resolve(b,pp+'/items/oneOf/'+str(i)); schema=dp.split('/')[-1]
                vt=f"typeCode={ds['properties']['typeCode']['enum'][0]} ({schema})"
                for f in ('typeCode','refId'): scalar(dn,snake(f),f,sp+'[].'+f,dp+'/properties/'+f,ds['properties'][f],True,vt)
                sub=table(DEFS[schema],'Définitions',f'Données propres à la variante {schema}; interdit les attributs d’un autre sous-type.',dn,False,subtype=True)
                props(sub,ds,dp,sp+'[]',variant=vt,skip=('typeCode','refId'))
            continue
        if z.get('type')=='array':
            an=ARRAY_NAMES.get(field) or t+'_'+ARRAY_SUFFIX[field]
            domain=TABLES[t]['domain']
            if field=='transactions': domain='Opérations'
            if field in ('startingActions','completingActions'): domain='Actions'
            if field in ('sourcesOfFundsOrVirtualCurrency','conductors','onBehalfOfs','involvements','beneficiaries'): domain='Rôles'
            if field in ('directorsOfCorporation','personsOwningSharesOfCorporation','trusteesOfTrust','settlorsOfTrust','personsOwningUnitsOfTrust','beneficiariesOfTrust','personsOwningEntityNotCorporationOrTrust'): domain='Propriété effective'
            table(an,domain,f'Une ligne par élément de {sp}; préserve multiplicité et ordre.',t,True,scope=TABLES[t]['scope'])
            structure(t,sp,pp,z,required,'array',an)
            if not required:
                col(t,n+'_present','BOOLÉEN',f'Distingue {sp} absent d’une liste présente mais vide.',constraint='false = absent; true = [] ou éléments')
                addmap(t,n+'_present',sp,pp,r,z,required,variant,'présence technique')
            item,ip=resolve(z['items'],r+'/items')
            if item.get('type')=='object' or 'oneOf' in item:
                obj(an,item,ip,sp+'[]',variant=variant)
            else: scalar(an,'value',field,sp+'[]',r+'/items',z['items'],True,variant)
        elif z.get('type')=='object' or 'oneOf' in z:
            if field=='account' and t in ('STR_STARTING_ACTION','STR_COMPLETING_ACTION'):
                an=t+'_ACCOUNT'; table(an,'Comptes','Photographie du compte dans cette action; aucun partage implicite entre opérations.',t,scope='version')
                structure(t,sp,pp,z,required,'object',an); obj(an,z,r,sp,variant=variant)
            else:
                structure(t,sp,pp,z,required,'object','Colonnes '+n+'_* de '+t)
                if not required:
                    col(t,n+'_present','BOOLÉEN',f'Distingue {sp} absent de l’objet vide {{}}.',constraint='false ⇒ aucune valeur enfant; true ⇒ objet émis')
                    addmap(t,n+'_present',sp,pp,r,z,required,variant,'présence technique')
                obj(t,z,r,sp,n+'__',variant)
        else: scalar(t,n,field,sp,pp,v,required,variant)

def obj(t,s,p,path,prefix='',variant=''):
    s,p=resolve(s,p)
    if 'oneOf' in s:
        for i,v in enumerate(s['oneOf']):
            v,r=resolve(v,p+'/oneOf/'+str(i)); vv=r.split('/')[-1]
            props(t,v,r,path,prefix,variant+'; '+vv if variant else vv)
    elif s.get('properties'): props(t,s,p,path,prefix,variant)
    else:
        # params est un objet vide additionalProperties:false, sa présence suffit.
        structure(t,path,p,s,False,'empty object','Objet vide {}; présence dans le parent')

def technical():
    table('STR_REPORT','Cycle de vie','Identité interne durable de la déclaration, commune à toutes ses versions.',scope='internal')
    col('STR_REPORT','created_at','HORODATAGE UTC','Date de création de l’identité interne.')
    col('STR_REPORT','created_by','TEXTE','Auteur de la création, pour la responsabilité interne.')
    table('STR_SCHEMA_RELEASE','Référentiels','Identifie exactement le contrat utilisé pour produire et valider une version.',scope='internal')
    for n,tp,w in [('source_url','TEXTE','URL officielle du contrat.'),('retrieved_at','HORODATAGE UTC','Date de récupération de cette copie.'),('sha256','TEXTE(64)','Empreinte du fichier source; distingue deux contrats affichant la même version.'),('info_version','TEXTE','Version affichée dans info.version du contrat.'),('archive_path','TEXTE','Emplacement de la copie immuable du contrat.')]: col('STR_SCHEMA_RELEASE',n,tp,w)
    TABLES['STR_SCHEMA_RELEASE']['constraints'].append('UNIQUE(sha256).')
    table('STR_VERSION','Rapport','Photographie complète des données DOD; une modification après gel crée une nouvelle version.',scope='internal')
    for n,tp,w,con in [('report_id','IDENTIFIANT','Rattache la version à sa déclaration durable.','FK STR_REPORT.id'),('version_number','ENTIER','Ordonne les révisions internes, indépendamment de submitTypeCode.','>= 1; UNIQUE(report_id, version_number)'),('previous_version_id','IDENTIFIANT','Relie explicitement la révision à la précédente.','FK STR_VERSION.id; même report_id; numéro inférieur'),('schema_release_id','IDENTIFIANT','Fixe la copie du Swagger utilisée.','FK STR_SCHEMA_RELEASE.id'),('created_at','HORODATAGE UTC','Date de création de cette version.',''),('created_by','TEXTE','Auteur de cette version.',''),('frozen_at','HORODATAGE UTC','Date du gel des données avant soumission.','Après gel : données immuables'),('workflow_status','TEXTE','État interne : DRAFT, READY, FROZEN, SUPERSEDED; distinct de l’acceptation CANAFE.','Enum interne')]: col('STR_VERSION',n,tp,w,constraint=con,nullable=n in ('previous_version_id','frozen_at'))
    for parent,child,fk in [('STR_REPORT','STR_VERSION','report_id'),('STR_SCHEMA_RELEASE','STR_VERSION','schema_release_id'),('STR_VERSION','STR_VERSION','previous_version_id')]: RELATIONS.append({'parent':parent,'child':child,'fk':fk,'parent_key':'id','cardinality':'1 → 0..N','kind':'historique','same_version':False})
    table('STR_DISPATCH','Soumissions','Enveloppe logique individuelle ou lot DOD; plusieurs tentatives peuvent transmettre la même enveloppe.',scope='internal')
    for n,tp,w,con in [('environment','TEXTE','Distingue les envois de test et de production.','Valeurs internes TEST, PROD'),('mode','TEXTE','Distingue envoi individuel et lot.','SINGLE, BULK'),('created_at','HORODATAGE UTC','Date de préparation de l’enveloppe.',''),('bulk_reference','TEXTE','Référence de lot utilisée pour le rapprochement des validations.','Voir Validations.reportingEntityBulkReference'),('file_name','TEXTE','Nom du fichier transmis et utilisé pour consulter les validations.','Voir GET /api/v1/bulkSubmission et /reports/validations')]: col('STR_DISPATCH',n,tp,w,constraint=con,nullable=n in ('bulk_reference','file_name'))
    table('STR_DISPATCH_ITEM','Soumissions','Associe une version gelée à un envoi; permet un résultat distinct pour chaque déclaration d’un lot.','STR_DISPATCH',True,scope='internal')
    col('STR_DISPATCH_ITEM','version_id','IDENTIFIANT','Version exacte transmise ou visée par la suppression.',constraint='FK STR_VERSION.id; version gelée')
    col('STR_DISPATCH_ITEM','operation','TEXTE','Action API demandée; reste distincte de la révision interne.',constraint='CREATE, UPDATE, DELETE')
    TABLES['STR_DISPATCH_ITEM']['constraints'].append('Pas de doublon de référence de déclaration dans un même lot. Mode SINGLE : exactement un élément.')
    RELATIONS.append({'parent':'STR_VERSION','child':'STR_DISPATCH_ITEM','fk':'version_id','parent_key':'id','cardinality':'1 → 0..N','kind':'soumission','same_version':False})
    table('STR_ARTIFACT','Soumissions','Archive immuable des octets du document envoyé ou reçu; permet une restitution exacte et la comparaison des empreintes.',scope='internal')
    for n,tp,w in [('content','OCTETS','Contenu exact de la charge utile; JSON UTF-8 pour les documents déclaratifs.'),('sha256','TEXTE(64)','Empreinte calculée sur les octets, sans reformater le JSON.'),('media_type','TEXTE','Type du document archivé.'),('created_at','HORODATAGE UTC','Date de capture du document.')]:col('STR_ARTIFACT',n,tp,w)
    table('STR_API_EXCHANGE','Soumissions','Un appel réseau réel, y compris nouvelle tentative et consultation de validations.','STR_DISPATCH',True,scope='internal')
    for n,tp,w,con in [('purpose','TEXTE','Distingue SUBMIT, UPDATE, DELETE, GET_BULK_URL, UPLOAD_BULK, POLL_VALIDATIONS, RECONCILE.','Enum interne'),('http_method','TEXTE','Méthode HTTP utilisée.',''),('endpoint_path','TEXTE','Chemin appelé, sans jeton SAS ni secret.',''),('started_at','HORODATAGE UTC','Début de l’appel.',''),('completed_at','HORODATAGE UTC','Fin de l’appel, si connue.',''),('http_status','ENTIER','Statut transport; peut rester absent après un délai dépassé.',''),('transport_error','TEXTE','Diagnostic technique en cas d’échec réseau.',''),('request_artifact_id','IDENTIFIANT','Document exact transmis, commun aux reprises identiques.','FK STR_ARTIFACT.id'),('response_artifact_id','IDENTIFIANT','Réponse exacte reçue, avant toute interprétation.','FK STR_ARTIFACT.id')]:col('STR_API_EXCHANGE',n,tp,w,constraint=con,nullable=n in ('completed_at','http_status','transport_error','request_artifact_id','response_artifact_id'))
    for fk in ('request_artifact_id','response_artifact_id'): RELATIONS.append({'parent':'STR_ARTIFACT','child':'STR_API_EXCHANGE','fk':fk,'parent_key':'id','cardinality':'1 → 0..N','kind':'archive','same_version':False})
    table('STR_ACK_LINK','Soumissions','Rapprochement explicite entre un accusé de validation et l’élément d’envoi concerné.',scope='internal')
    col('STR_ACK_LINK','ack_id','IDENTIFIANT','Accusé reçu à rapprocher.',constraint='FK STR_VALIDATION_RESULT_ACK.id; UNIQUE')
    col('STR_ACK_LINK','dispatch_item_id','IDENTIFIANT','Élément identifié dans le même envoi par sa référence de déclaration.',constraint='FK STR_DISPATCH_ITEM.id')
    col('STR_ACK_LINK','linked_at','HORODATAGE UTC','Horodatage du rapprochement.')
    for parent,fk in [('STR_VALIDATION_RESULT_ACK','ack_id'),('STR_DISPATCH_ITEM','dispatch_item_id')]: RELATIONS.append({'parent':parent,'child':'STR_ACK_LINK','fk':fk,'parent_key':'id','cardinality':'1 → 0..1' if fk=='ack_id' else '1 → 0..N','kind':'rapprochement','same_version':False})
    table('STR_AUDIT_EVENT','Cycle de vie','Journal append-only des décisions et modifications internes.','STR_VERSION',True,scope='internal')
    for n,tp,w in [('occurred_at','HORODATAGE UTC','Date de l’événement.'),('actor','TEXTE','Auteur ou service responsable.'),('event_type','TEXTE','Nature de l’action : création, gel, correction, rapprochement.'),('reason','TEXTE','Justification lisible de la décision.')]: col('STR_AUDIT_EVENT',n,tp,w)
    table('STR_CODE_VALUE','Référentiels','Valeurs autorisées par domaine exact du Swagger, conservées par version du contrat.','STR_SCHEMA_RELEASE',True,scope='internal')
    for n,tp,w in [('domain_pointer','TEXTE','JSON Pointer de la définition du domaine; évite de mélanger les différents typeCode.'),('code_json','SCALAIRE JSON','Valeur exacte, avec distinction entre chaîne et nombre.'),('description','TEXTE','Description officielle du domaine et des valeurs, si disponible.')]: col('STR_CODE_VALUE',n,tp,w)
    TABLES['STR_CODE_VALUE']['constraints'].append('UNIQUE(parent_id, domain_pointer, code_json).')

def build():
    technical()
    TABLES['STR_VERSION']['scope']='version'
    obj('STR_VERSION',SPEC['components']['schemas']['STRReport'],'#/components/schemas/STRReport','$')
    TABLES['STR_VERSION']['constraints']+=['report_details__report_type_code = 102 : périmètre DOD interne.', 'Au gel : reportDetails, detailsOfSuspicion, relatedReports, definitions et transactions présents; au moins une opération.', 'Pour une correction : même identité déclarative (numéro d’entité et référence) que la version précédente.']
    for n,schema,parent in [('STR_SUBMIT_RESPONSE','SubmitReportResponse','STR_API_EXCHANGE'),('STR_VALIDATION_RESULT','Validations','STR_API_EXCHANGE'),('STR_API_ERROR','ErrorWithValidation','STR_API_EXCHANGE'),('STR_DELETE_REQUEST','DeleteReport','STR_DISPATCH_ITEM')]:
        table(n,'Réponses API' if schema!='DeleteReport' else 'Soumissions',f'Projection du schéma {schema}; le document exact reste dans STR_ARTIFACT.',parent,scope='internal')
        obj(n,SPEC['components']['schemas'][schema],'#/components/schemas/'+schema,schema+'$')
    TABLES['STR_DELETE_REQUEST']['constraints']+=['report_details__report_type_code = 102; report_details__submit_type_code = 5.', 'Exiger les six champs de reportDetails avant envoi, comme règle interne : required est mal positionné dans le Swagger.', 'Identifiants de déclaration identiques à la version référencée par le parent STR_DISPATCH_ITEM.']
    TABLES['STR_VALIDATION_RESULT_ACK_MESSAGE']['constraints'].append('Variante interprétée selon message_type_code du parent : 1 = SchemaValidationMessages; 2 = ValidationMessage. Voir ambiguïté oneOf documentée.')
    for t in TABLES.values():
        if t['scope']=='version' and t['name']!='STR_DEFINITION' and 'ref_id' in t['columns']:
            t['constraints'].append('FK (version_id, type_code, ref_id) → STR_DEFINITION(version_id, type_code, ref_id). Domaine de type_code selon ce rôle. Résolution obligatoire avant gel.')
            RELATIONS.append({'parent':'STR_DEFINITION','child':t['name'],'fk':'version_id, type_code, ref_id','parent_key':'version_id, type_code, ref_id','cardinality':'1 → 0..N','kind':'référence typée','same_version':True})
        if t['parent'] and t['scope']=='version':t['constraints'].append('FK composite (version_id, parent_id), ou (version_id, id) pour un sous-type, vers (version_id, id) du parent; si parent=STR_VERSION, parent_id=version_id.')

def export():
    jsonwrite('model/model.json',{'tables':list(TABLES.values()),'relationships':RELATIONS,'mappings':MAPPINGS,'structures':STRUCTURES})
    jsonwrite('model/code-domains.json',ENUMS)
    for filename,rows in [('traceability/fields.csv',MAPPINGS),('traceability/structures.csv',STRUCTURES),('traceability/relationships.csv',RELATIONS)]:
        p=ROOT/filename;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
            for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    intro=['# Dictionnaire des tables et colonnes','',f'{len(TABLES)} tables logiques. Aucun type physique de SGBD n’est imposé.','',
    'Chaque colonne indique son utilité et son origine. `TECHNIQUE` signifie choix interne sans champ JSON à transmettre. `SWAGGER` signifie donnée explicitement décrite. Les colonnes de présence sont techniques même si elles ont un chemin de correspondance.', '',
    '**Lecture des obligations :** les marqueurs « requis » concernent la propriété dans son objet parent présent et sa variante active. Une propriété facultative est omise si inconnue; elle ne devient pas `null` dans le JSON. Les brouillons peuvent être incomplets; le gel doit satisfaire toutes les obligations structurelles et les règles applicables.', '',
    '**Adresses :** colonnes intégrées à leur propriétaire, avec `address_present` et `address__type_code` pour le discriminant situé DANS l’adresse. Le champ extérieur `addressTypeCode` devient `address_type_code` et reste distinct. Les variantes structurée et libre sont exclusives. Le double soulignement sépare les niveaux d’objet JSON.', '',
    '**Présence des objets :** les colonnes `*_present` sont obligatoires dans le modèle interne. False interdit leurs descendants; true permet `{}` si le Swagger le permet. Une collection obligatoire n’a pas besoin d’un indicateur : zéro ligne signifie `[]`.', '',
    '**Types :** TEXTE conserve la forme API; NOMBRE EXACT exclut les flottants binaires. IDENTIFIANT est une clé interne, dont le type physique sera choisi lors de l’implantation. Les montants, taux, dates et heures API restent textuels conformément au contrat.','',
    '| Table | Domaine | Rôle |','|---|---|---|']
    for t in TABLES.values():intro.append(f"| [{t['name']}](#{t['name'].lower()}) | {t['domain']} | {t['reason']} |")
    for t in TABLES.values():
        intro+=['',f"## {t['name']}",'',t['reason'],'']
        if t['constraints']:intro+=['Contraintes :']+['- '+x for x in t['constraints']]+['']
        intro+=['| Colonne | Type logique | Origine | Pourquoi cette colonne / contrainte interne | Traçabilité |','|---|---|---|---|---|']
        for c in t['columns'].values():
            refs=[]
            for ix in c['mappings']:
                m=MAPPINGS[ix];line=m['source_line'];flags=('requis' if m['required_in_parent'] else 'facultatif')+(' ; '+m['variant'] if m['variant'] else '')
                refs.append(f"`{m['json_path']}` ({flags}) ; [L{line}](../source/swaggerExternal.yaml#L{line}) ; `{m['source_pointer']}`"+ (f" → `{m['resolved_pointer']}`" if m['source_pointer']!=m['resolved_pointer'] else '')+f" ; contraintes : `{json.dumps(m['constraints'],ensure_ascii=False,separators=(',',':'))}`")
            intro.append('| '+' | '.join(cell(x) for x in [c['name'],c['type'],c['origin'],c['reason']+(' '+c['constraint'] if c['constraint'] else ''),'<br>'.join(refs) or 'Interne — non sérialisé'])+' |')
    write('docs/DICTIONNAIRE.md','\n'.join(intro)+'\n')
    enumdoc=['# Domaines de codes','', 'Chaque domaine est identifié par son JSON Pointer, et non par le seul nom `typeCode`. Les codes restent attachés à STR_SCHEMA_RELEASE. Les descriptions ci-dessous sont celles du Swagger archivé.','']
    for p,e in ENUMS.items():enumdoc +=[f'## {p}','',f"Source : [ligne {e['line']}](../source/swaggerExternal.yaml#L{e['line']}).",'',f"Valeurs : `{json.dumps(e['values'],ensure_ascii=False)}`",'',e['description'],'']
    write('docs/DOMAINES_CODES.md','\n'.join(line.rstrip() for line in '\n'.join(enumdoc).splitlines()).rstrip()+'\n')

def drawio():
    mx=ET.Element('mxfile',host='app.diagrams.net',agent='projetdod',version='24.7.17')
    pages=[]
    domains=list(dict.fromkeys(t['domain'] for t in TABLES.values()))
    pages.append(('00 — Vue d’ensemble',list(TABLES),True))
    for domain in domains:
        names=[n for n,t in TABLES.items() if t['domain']==domain]
        for start in range(0,len(names),4):pages.append((f'{domain} — {start//4+1}',names[start:start+4],False))
    for pi,(name,names,overview) in enumerate(pages):
        diag=ET.SubElement(mx,'diagram',id='page'+str(pi),name=name)
        model=ET.SubElement(diag,'mxGraphModel',dx='1800',dy='1000',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='0',pageScale='1',math='0',shadow='0')
        r=ET.SubElement(model,'root');ET.SubElement(r,'mxCell',id='0');ET.SubElement(r,'mxCell',id='1',parent='0')
        def node(i,label,x,y,w,h,style):
            c=ET.SubElement(r,'mxCell',id=i,value=label,style=style,vertex='1',parent='1'); ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        node('title',html.escape(name)+'<br><font style="font-size:12px">Flèches parent → enfant. PK : clé primaire; FK : référence. Traits violets : définition typée.<br>Voir DICTIONNAIRE.md et REGLES.md pour contraintes conditionnelles et gel.</font>',40,10,1350,90,'text;html=1;align=left;verticalAlign=middle;fontSize=22;')
        positions={};heights={}
        cols=6 if overview else 2; width=300 if overview else 650; gap=100
        row_y=150
        for start in range(0,len(names),cols):
            row=names[start:start+cols]; maxh=0
            for j,n in enumerate(row):
                t=TABLES[n]; cdata=list(t['columns'].values())
                if overview:
                    label='<b>'+n+'</b><br>'+html.escape(t['domain'])+'<br>'+str(len(cdata))+' colonnes'
                    h=90
                else:
                    rows=['<b>'+html.escape(c['name'])+'</b> : '+html.escape(c['type'])+(' [PK]' if c['name']=='id' else '')+(' [FK]' if 'FK ' in c['constraint'] else '') for c in cdata]
                    label='<b>'+n+'</b><hr><div style="text-align:left">'+'<br>'.join(rows)+'</div>'
                    h=70+len(rows)*23
                x=40+j*(width+gap);positions[n]=(x,row_y);heights[n]=h;maxh=max(maxh,h)
                node(n,label,x,row_y,width,h,'rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=12;fillColor=#e8f1fa;strokeColor=#34699a;fontSize='+('12' if overview else '14')+';')
            row_y+=maxh+160
        # Contexte externe compact : chaque parent hors page est visible, avec vraie relation.
        external=[] if overview else sorted({e['parent'] for e in RELATIONS if e['child'] in names and e['parent'] not in names})
        for j,n in enumerate(external):node(n,'<b>'+n+'</b><br>Référence — détail sur une autre page',1550,150+j*125,420,85,'rounded=1;html=1;whiteSpace=wrap;fillColor=#f5f5f5;strokeColor=#999999;fontSize=13;')
        visible=set(names)|set(external)
        for i,e in enumerate(RELATIONS):
            if e['parent'] in visible and e['child'] in names:
                if overview and e['kind']=='référence typée':continue
                label=e['cardinality'] if overview else e['cardinality']+' | '+e['fk']
                style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor='+('#9673a6' if e['kind']=='référence typée' else '#667788')+';fontSize=11;labelBackgroundColor=#ffffff;'
                c=ET.SubElement(r,'mxCell',id='edge'+str(i),value=label,style=style,edge='1',parent='1',source=e['parent'],target=e['child']);ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
    ET.indent(mx);write('diagrams/CANAFE_DOD.drawio',ET.tostring(mx,encoding='unicode')+'\n')
    return len(pages)

if __name__=='__main__':
    build();export();pages=drawio()
    print(json.dumps({'tables':len(TABLES),'columns':sum(len(t['columns']) for t in TABLES.values()),'mappings':len(MAPPINGS),'structures':len(STRUCTURES),'pages':pages}))
