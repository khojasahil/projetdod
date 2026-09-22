"""Une seule planche : toutes les tables, colonnes et références du catalogue."""

def build(Page,M,T,wrap,font):
    # Trois parcours verticaux, plutôt qu’une grille dont la hauteur serait
    # imposée partout par le domaine de sept tables.
    columns=[[0,5,7],[1,6,8],[2,3,4]]
    notes={
        0:('Le point de départ du dossier','Le rapport rassemble le récit et les références. Une correction crée une nouvelle version dans le même groupe; les faits de la version précédente restent consultables.'),
        1:('La fiche et son usage sont deux choses différentes','DEFINITION donne le repère. PERSON ou ENTITY décrit la fiche. Les rôles citent ce repère avec le type attendu. Une même personne réelle peut donc avoir plusieurs fiches déclaratives.'),
        2:('Une adresse n’est pas une pièce d’identité','L’adresse décrit où se trouve la personne ou l’organisation. L’identification décrit le document utilisé pour l’identifier. Chaque adresse garde un seul propriétaire dans cette version du rapport.'),
        3:('Être autorisé à agir ne signifie pas être propriétaire','Ces deux tables complètent la fiche de l’entité : son enregistrement d’un côté, les personnes autorisées de l’autre. Les renseignements de direction et de propriété sont rangés dans le domaine suivant.'),
        4:('Sept listes, une entité concernée','Ces renseignements appartiennent à une entité de type 6. Les noms sont décrits directement dans les listes du Swagger. Le bénéficiaire d’une fiducie n’est pas le bénéficiaire d’une opération.'),
        5:('Lire le mouvement dans les deux sens','L’opération donne le contexte. Ses actions décrivent ce qui amorce le mouvement et ce qui est fait des fonds à l’arrivée. Il peut y avoir plusieurs actions initiales et plusieurs actions finales.'),
        6:('Camille agit pour la société A','Camille est l’exécutante; A est le tiers représenté. La source des fonds, le titulaire du compte et le bénéficiaire restent des renseignements distincts. On les décrit selon les faits connus.'),
        7:('Un compte reste lié à une action précise','ACCOUNT et VC_DATA ont chacun deux clés d’action possibles. On en renseigne exactement une : initiale ou finale. Dans VC_DATA, data_type sépare les identifiants, les adresses émettrices et les adresses réceptrices.'),
        8:('Une tentative d’envoi n’est pas une nouvelle version','Le contenu transmis et la réponse restent archivés. Un nouvel essai du même contenu crée une tentative; une correction du contenu crée une version. Une réponse HTTP positive ne prouve pas, à elle seule, l’acceptation du rapport.')
    }
    W=2080;CW=950;GAP=100;X0=70;TOP=680
    layouts={};maxbottom=0
    def field_label(t,c):
        fk=any(r['child']==t['name'] and c in r['foreign_key'].split(', ') for r in M['relationships'])
        mark=' [PK]' if c==t['pk'] else (' [FK]' if fk else '')
        return c+' : '+t['columns'][c]['type']+mark
    def refs(t):
        return [(i,r) for i,r in enumerate(M['relationships']) if r['child']==t['name']]
    def ref_label(r):
        return r['foreign_key']+' → '+r['parent'].removeprefix('STR_')+'.'+r['parent_key']+' | '+r['cardinality']
    def height(t):
        return 112+len(t['columns'])*30+54+sum(len(wrap(ref_label(r),CW-48,16))*23+9 for _,r in refs(t))+24
    for col,indices in enumerate(columns):
        y=TOP
        for di in indices:
            domain=M['domains'][di];x=X0+col*(W+GAP);positions=[];cy=y+132
            for j in range(0,len(domain['tables']),2):
                pair=domain['tables'][j:j+2];rowh=max(height(T[n]) for n in pair)
                for k,n in enumerate(pair):positions.append((n,x+40+k*(CW+100),cy,height(T[n])))
                cy+=rowh+100
            note_y=cy-45;domainh=note_y+182-y
            layouts[di]=(x,y,domainh,positions,note_y)
            y+=domainh+100
        maxbottom=max(maxbottom,y)
    p=Page('10-modele-complet','Le modèle complet — domaines, tables et colonnes',
           '34 tables · 365 colonnes · 77 références documentées · Une seule page à parcourir en zoomant.',10,
           w=X0*2+W*3+GAP*2,h=maxbottom+80)
    p.note('read','Comment parcourir cette page',
           'À gauche : le rapport, les opérations et les comptes. Au centre : les fiches, les rôles et les envois. À droite : l’identité, l’entité et sa propriété. Chaque domaine garde sa couleur et ses noms de tables.',70,185,2080,185)
    p.note('keys','Les repères à connaître',
           'PK identifie une ligne. FK retrouve une ligne liée. Sous chaque table, les références indiquent la clé et la table visée. Le nombre après | se lit depuis le parent : 0..1 ou 0..N lignes de la table courante.',2250,185,2080,185)
    p.note('history','Le rapport reste le fil conducteur',
           'Chaque table porte str_report_id : tous ses renseignements appartiennent à une version précise. Les références vers les autres tables sont toujours contrôlées dans cette même version.',4430,185,2080,185)
    p.note('complete-links','Retrouver les liens sans perdre le fil',
           'Les flèches montrent les liens de structure au sein des domaines. Les 77 références, y compris les liens entre domaines et vers REPORT, sont écrites au bas des cartes. STR_ est omis dans ces références pour alléger la lecture.',70,410,3170,175)
    p.note('reading-codes','Lire les champs avec leur contexte',
           'Les types sont logiques. Les colonnes applicables dépendent du type de définition et de l’action décrite. 0..N autorise une liste vide dans le stockage; les obligations avant envoi restent celles du dictionnaire et du Swagger.',3340,410,3170,175)
    p.overview_columns={};p.overview_relations=[]
    for di in range(9):
        d=M['domains'][di];x,y,h,positions,ny=layouts[di]
        p.rect('zone-'+str(di),x,y,W,h,'#EDF2F8','#D8E2EC',16)
        p.items[-1]['backdrop']=True
        p.text('zone-title-'+str(di),f"{di+1:02}  {d['name']}  ·  {len(d['tables'])} tables",x+40,y+25,W-80,30,d['color'],True)
        p.text('zone-question-'+str(di),d['question'],x+40,y+75,W-80,19)
        for n,cx,cy,ch in positions:
            t=T[n];p.rect(n,cx,cy,CW,ch)
            p.rect(n+'-bar',cx,cy,7,ch,t['color'],t['color'],0)
            p.text(n+'-label',t['label'],cx+24,cy+18,CW-48,23,'#142B46',True)
            p.text(n+'-name',n,cx+24,cy+55,CW-48,16,t['color'],True)
            fy=cy+96
            for j,c in enumerate(t['columns']):
                p.text(n+'-field'+str(j),field_label(t,c),cx+24,fy,CW-48,17,'#24364B',c==t['pk']);fy+=30
            p.text(n+'-refs-title','Références · lignes de cette table par parent',cx+24,fy+12,CW-48,16,t['color'],True)
            fy+=49
            for ri,r in refs(t):
                dh=p.text(n+'-ref'+str(ri),ref_label(r),cx+24,fy,CW-48,16,'#5E7185')
                fy+=dh+9;p.overview_relations.append(ri)
            p.cards[n]=(cx,cy,CW,ch);p.overview_columns[n]=list(t['columns'])
        title,body=notes[di];p.note('domain-note-'+str(di),title,body,x+40,ny,W-80,150)
    # Relations locales : couloirs entre les deux colonnes ou autour des cartes.
    # Les références complètes restent dans chaque carte, y compris celles
    # entre domaines; elles sont vérifiées contre le catalogue, sans omission.
    local=[('REPORT','PPP_PROJECT'),('REPORT','RELATED_REPORT'),('RELATED_REPORT','RELATED_REPORT_TXN_REF'),
           ('DEFINITION','PERSON'),('DEFINITION','ENTITY'),('PERSON','EMPLOYER_INFO'),
           ('TRANSACTION','STARTING_ACTION'),('TRANSACTION','COMPLETING_ACTION'),
           ('CONDUCTOR','ON_BEHALF_OF'),('ACCOUNT','ACCOUNT_HOLDER'),
           ('API_SUBMISSION','SUBMITTED_PAYLOAD'),('API_SUBMISSION','VALIDATION_ERROR')]
    for a,b in local:
        an='STR_'+a;bn='STR_'+b;ax,ay,aw,ah=p.cards[an];bx,by,bw,bh=p.cards[bn]
        rel=next(r for r in M['relationships'] if r['parent']==an and r['child']==bn)
        label=rel['cardinality']
        if ax!=bx:
            start,end=('right','left') if ax<bx else ('left','right')
            mid=(min(ax,bx)+CW+max(ax,bx))/2
            p.edge(a,b,label,start=start,end=end,route=[(mid,ay+ah/2),(mid,by+bh/2)],label_at=(mid,(ay+ah/2+by+bh/2)/2))
        else:
            side='left' if a not in ('PERSON',) else 'right'
            rail=ax-20 if side=='left' else ax+aw+20
            # Le lien passe à l’extérieur des cartes, jamais dans une colonne.
            p.edge(a,b,'',start=side,end=side,route=[(rail,ay+ah/2),(rail,by+bh/2)])
    return p
