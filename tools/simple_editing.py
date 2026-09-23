"""Copie draw.io avec une forme et un texte multiligne par table.

Ne réécrit jamais le fichier original. Les identifiants des tables sont
conservés pour que les connecteurs continuent à suivre la table déplacée.
"""
import hashlib,html,json,re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'diagrams/CANAFE_DOD.drawio'
TARGET=ROOT/'diagrams/CANAFE_DOD_EDITION_SIMPLE.drawio'

def esc(s):return html.escape(s)
def paragraph(text,size,color,bold=False,line=None,after=0):
    return f'<div style="font-size:{size}px;color:{color};font-weight:{"bold" if bold else "normal"};line-height:{line or size+7}px;margin:0 0 {after}px 0;">{esc(text)}</div>'
def multiline(items,size,line):
    values=[]
    for i in items:
        value=esc(i['value'].replace('\n',' '))
        values.append('<b>'+value+'</b>' if i['bold'] else value)
    return f'<div style="font-size:{size}px;line-height:{line}px;">'+ '<br>'.join(values)+'</div>'

def main():
    before=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    scenes=json.loads((ROOT/'model/presentation.json').read_text(encoding='utf-8'))
    model=json.loads((ROOT/'model/model.json').read_text(encoding='utf-8'))
    tables={t['name']:t for t in model['tables']}
    doc=ET.parse(SOURCE);pages=doc.findall('diagram');stats=[]
    for page,scene in zip(pages,scenes):
        root=page.find('mxGraphModel/root');cells={c.get('id'):c for c in root.findall('mxCell')}
        items={i['id']:i for i in scene['items']}
        remove={'background'}
        def attach(id,value,color=None):
            cell=cells[id]
            old=cell.get('style','')
            # Le texte est la valeur de la forme, pas une série de cellules.
            cell.set('value',value)
            cell.set('style',old+'html=1;whiteSpace=wrap;overflow=visible;align=left;verticalAlign=top;spacing=0;spacingTop=17;spacingLeft=22;spacingRight=18;spacingBottom=15;fontFamily=Arial;fontSize=17;fontColor=#24364B;'+(f'strokeColor={color};strokeWidth=2;' if color else ''))
        for name in scene['tables']:
            t=tables[name]
            fields=sorted([i for k,i in items.items() if re.fullmatch(re.escape(name)+r'-field\d+',k)],key=lambda i:int(i['id'].split('-field')[-1]))
            detail=scene['slug']=='10-modele-complet'
            label=paragraph(t['label'],23,'#142B46',True,30,7)
            label+=paragraph(name,16 if detail else 14,t['color'],True,23 if detail else 21,18)
            label+=multiline(fields,17,30 if detail else 39)
            refs=sorted([i for k,i in items.items() if re.fullmatch(re.escape(name)+r'-ref\d+',k)],key=lambda i:i['y'])
            if refs:
                label+='<div style="height:12px;"></div>'
                label+=paragraph('Références · lignes de cette table par parent',16,t['color'],True,23,14)
                label+='<div style="color:#5E7185;">'+multiline(refs,16,32)+'</div>'
            attach(name,label,t['color'])
            remove.update(k for k in items if k.startswith(name+'-'))
        # Une note = un rectangle avec un titre et un paragraphe éditables.
        for id,item in items.items():
            if item['kind']!='rect' or id+'-t' not in items or id+'-b' not in items:continue
            title=items[id+'-t'];body=items[id+'-b']
            label=paragraph(title['value'].replace('\n',' '),21,'#142B46',True,28,8)
            label+=paragraph(body['value'].replace('\n',' '),18,'#24364B',False,25)
            attach(id,label);remove.update([id+'-t',id+'-b'])
        # La carte des domaines est également composée de neuf blocs simples.
        if scene['slug']=='01-domaines':
            for j,domain in enumerate(model['domains']):
                label=paragraph(domain['name']+' · '+str(len(domain['tables']))+' tables',24,domain['color'],True,31,7)
                label+=paragraph(domain['question'],17,'#142B46',False,24,21)
                label+='<div style="font-size:14px;line-height:21px;">'+'<br>'.join(esc(n.removeprefix('STR_')) for n in domain['tables'])+'</div>'
                attach('domain'+str(j),label,domain['color'])
                remove.update(''+prefix+str(j) for prefix in ('stripe','domtitle','question','names'))
        for j,edge in enumerate(scene['edges']):
            if not edge['label']:continue
            bg=cells['edge-label-bg'+str(j)]
            bg.set('value',esc(edge['label']))
            bg.set('style',bg.get('style')+'html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize=14;fontColor=#5E7185;spacing=2;')
            remove.add('edge-label'+str(j))
        for id in remove:
            if id in cells:root.remove(cells[id])
        current={c.get('id'):c for c in root.findall('mxCell')}
        assert len(current)==len(root.findall('mxCell'))
        for name in scene['tables']:
            assert name in current
            assert not any(k.startswith(name+'-') for k in current),(scene['slug'],name)
        for c in current.values():
            if c.get('edge')=='1':assert c.get('source') in current and c.get('target') in current
        stats.append({'page':page.get('name'),'table_blocks':len(scene['tables']),'objects_before':len(cells)-2,'objects_after':len(current)-2})
    assert len(pages)==10 and len(scenes)==10
    # La dernière page contient les 365 colonnes et les 77 références.
    full={c.get('id'):c for c in pages[-1].findall('.//mxCell')}
    for n,t in tables.items():
        value=html.unescape(full[n].get('value'))
        for c in t['columns']:assert c+' :' in value,(n,c)
    for r in model['relationships']:
        value=html.unescape(full[r['child']].get('value'))
        assert r['foreign_key']+' → '+r['parent'].removeprefix('STR_')+'.'+r['parent_key']+' | '+r['cardinality'] in value
    from relational_page import add_page
    relational_stats=add_page(doc)
    ET.indent(doc);doc.write(TARGET,encoding='utf-8',xml_declaration=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==before
    results={'original_unchanged':True,'original_sha256':before,'file':TARGET.name,'pages':stats,'relational_page':relational_stats,'total_pages':11,'all_365_columns_and_77_references_preserved':True,'one_editable_shape_per_table':True,'connectors_preserved':True}
    (ROOT/'quality/edition-simple.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
