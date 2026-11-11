"""Subset the bundled OFL fonts for the main page. Requires fonttools."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset
ROOT=Path(__file__).resolve().parents[2]
text=''.join(path.read_text() for path in ROOT.glob('*.html'))+(ROOT/'css/style.css').read_text()
chars=set(map(ord,text))|set(range(32,127))
for weight in ['Regular','Bold']:
    font=TTFont(ROOT/'assets/fonts'/f'NotoSansKR-{weight}.ttf')
    options=subset.Options();options.layout_features=['*']
    sub=subset.Subsetter(options=options);sub.populate(unicodes=chars);sub.subset(font)
    font.save(ROOT/'assets/fonts'/f'NotoSansKR-{weight}-web.ttf')
