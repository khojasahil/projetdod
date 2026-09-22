"""Regénère le catalogue, la traçabilité et les vues; ne modifie pas les guides."""
from build_model import generate

if __name__=='__main__':
    m=generate()
    from render_models import main
    main()
    print(f"{len(m['tables'])} tables, {sum(len(t['columns']) for t in m['tables'])} colonnes, {len(m['mappings'])} correspondances.")
