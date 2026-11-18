"""Rebuild the portfolio PDFs from preserved sources.

Dependencies: reportlab, pypdfium2, pillow.
Usage: python scripts/portfolio/build_pdfs.py
Original decks stay under project_template/originals/. New decks retain their URLs.
"""
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'project_template'
WORK=ROOT/'work/portfolio'
WORK.mkdir(parents=True,exist_ok=True)
W,H=960,600
INK='#142846'; MUTED='#53637b'; ACCENT='#315d9f'; MINT='#c4d9f4'; PAPER='#fbfcfe'; TINT='#f0f4fa'; LINE='#d7e0ee'; WHITE='#ffffff'
FONT_DIR=WORK/'fonts'; FONT_DIR.mkdir(exist_ok=True)

def prepare_fonts():
    for name in ['Regular','Bold']:
        pdfmetrics.registerFont(TTFont('Noto'+name,str(ROOT/'assets/fonts'/f'NotoSansKR-{name}.ttf')))
prepare_fonts()
pdfmetrics.registerFontFamily('NotoRegular',normal='NotoRegular',bold='NotoBold',italic='NotoRegular',boldItalic='NotoBold')

class Deck:
    def __init__(self,filename,category,title,subtitle,role,team,steps):
        self.filename=filename; self.category=category; self.title=title; self.subtitle=subtitle; self.role=role; self.team=team; self.steps=steps
        self.pages=[]; self.commands=[]
    def add(self,eyebrow,title,lead,kind,data):
        self.pages.append((eyebrow,title,lead,kind,data));return self
    def rect(self,x,y,w,h,fill=WHITE,stroke=None,r=9):
        c=self.c;c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill));c.setLineWidth(.7)
        c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    def line(self,x,y,x2,y2,color=LINE):
        self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(.7);self.c.line(x,H-y,x2,H-y2)
    def text(self,text,x,y,w,size=12,color=INK,bold=False,leading=None):
        # Top coordinates, with every text box checked against the safe page region.
        style=ParagraphStyle('body',fontName='NotoBold' if bold else 'NotoRegular',fontSize=size,leading=leading or size*1.65,textColor=HexColor(color),wordWrap='CJK',splitLongWords=True)
        p=Paragraph(text,style);_,height=p.wrap(w,H)
        if y+height>(H-18 if y>=560 else H-55):raise ValueError(f'Text overflow {self.filename}: {text[:55]} y={y} height={height}')
        p.drawOn(self.c,x,H-y-height)
        return height
    def footer(self,n,dark=False):
        color='#acbdd6' if dark else MUTED
        self.line(56,552,904,552,'#334e73' if dark else LINE)
        self.text('JOO / AI · MACHINE LEARNING · BACKEND',56,565,600,8,color)
        self.text(f'{n:02d} / {len(self.pages)+1:02d}',848,565,56,8,color)
    def page(self,number,eyebrow,title,lead):
        self.c.setFillColor(HexColor(PAPER));self.c.rect(0,0,W,H,fill=1,stroke=0)
        self.text('JOO<span color="'+ACCENT+'">.</span>',56,25,200,20,bold=True)
        self.text(self.category,570,34,334,8,MUTED)
        self.line(56,67,904,67)
        self.text(eyebrow,56,86,848,9,ACCENT,bold=True)
        self.text(title,56,110,848,27,bold=True,leading=38)
        self.text(lead,56,159,848,11,MUTED)
        self.footer(number)
    def cover(self):
        self.c.setFillColor(HexColor(INK));self.c.rect(0,0,W,H,fill=1,stroke=0)
        self.text('JOO<span color="'+MINT+'">.</span>',56,32,300,26,WHITE,bold=True)
        self.text('PROJECT CASE STUDY',692,47,212,9,MINT)
        self.line(56,93,904,93,'#334e73')
        self.text(self.category,56,124,540,10,MINT,bold=True)
        self.text(self.title,56,162,552,39,WHITE,True,leading=55)
        self.text(self.subtitle,56,307,520,13,'#c2cee0')
        self.rect(656,132,248,272,'#1b304f','#3b5477')
        self.text('FROM QUESTION TO SOLUTION',678,154,210,8,MINT)
        for i,s in enumerate(self.steps):
            y=199+i*62
            self.text(f'0{i+1}',680,y,25,10,MINT)
            self.text(s,716,y-3,164,15,WHITE,True)
            if i<2:self.line(716,y+38,880,y+38,'#334e73')
        self.rect(56,435,848,86,'#1b304f')
        self.text('MY ROLE' if self.role else 'TEAM PROJECT',76,451,760,8,MINT,True)
        self.text(self.role or '팀 단위 문제 정의 · MVP 구현 · 서비스 개선 사례',76,470,800,12,WHITE,True)
        self.footer(1,True)
    def cards(self,data):
        items=data['items'];cols=data.get('cols',2);start=data.get('top',211);height=data.get('height',260);gap=20
        width=(848-gap*(cols-1))/cols
        for i,(label,title,body) in enumerate(items):
            x=56+(i%cols)*(width+gap);y=start+(i//cols)*(height+18)
            self.rect(x,y,width,height,TINT)
            self.text(label,x+22,y+20,width-44,9,ACCENT,True)
            ht=self.text(title,x+22,y+49,width-44,18,INK,True,leading=27)
            self.text(body,x+22,y+ht+65,width-44,11,MUTED)
        if data.get('note'):self.text(data['note'],56,502,848,9,MUTED)
    def table(self,data):
        headers=data['headers'];rows=data['rows'];weights=data.get('weights',[1]*len(headers));widths=[848*w/sum(weights) for w in weights]
        y=data.get('top',211);rh=data.get('rowheight',44);size=data.get('size',10)
        self.rect(56,y,848,36,INK,r=5)
        x=56
        for header,w in zip(headers,widths):self.text(header,x+14,y+9,w-28,9,WHITE,True);x+=w
        y+=36
        for row in rows:
            maxh=0
            # Calculate cell heights before drawing so no row overlaps another.
            for val,w in zip(row,widths):
                st=ParagraphStyle('measure',fontName='NotoRegular',fontSize=size,leading=size*1.6,wordWrap='CJK')
                ph=Paragraph(str(val),st).wrap(w-28,H)[1];maxh=max(maxh,ph)
            actual=max(rh,maxh+18)
            self.rect(56,y,848,actual,WHITE if rows.index(row)%2 else TINT,r=0)
            x=56
            for val,w in zip(row,widths):self.text(str(val),x+14,y+9,w-28,size,MUTED);x+=w
            y+=actual
        if y>525:raise ValueError(f'Table overflow {self.filename} {y}')
        if data.get('note'):self.text(data['note'],56,y+14,848,9,MUTED)
    def chart(self,data):
        # A consistent, directly labelled horizontal bar chart; values come only from source decks.
        self.rect(56,211,518,289,TINT)
        self.text(data['chart_title'],78,229,470,13,INK,True)
        rows=data['values'];maxval=data.get('maximum',100);gap=190/max(1,len(rows));y=278
        for label,value,formatted in rows:
            self.text(label,78,y,135,10,MUTED)
            self.rect(220,y+2,274,15,'#dce5f2',r=3)
            self.rect(220,y+2,max(2,274*value/maxval),15,ACCENT,r=3)
            self.text(formatted,505,y-1,56,10,INK,True)
            y+=gap
        self.text(data.get('chart_note','원문 발표자료의 수치를 기준으로 재구성했습니다.'),78,466,470,8,MUTED)
        heading_height=self.text(data['heading'],604,222,300,20,INK,True,leading=28)
        self.text(data['body'],604,max(285,222+heading_height+15),300,11,MUTED)
    def flow(self,data):
        items=data['items'];cols=len(items);gap=20;width=(848-gap*(cols-1))/cols
        for i,(title,body) in enumerate(items):
            x=56+i*(width+gap)
            self.rect(x,224,width,212,INK if i==cols-1 else TINT)
            self.text(f'0{i+1}',x+22,245,width-44,10,MINT if i==cols-1 else ACCENT,True)
            self.text(title,x+22,285,width-44,19,WHITE if i==cols-1 else INK,True)
            self.text(body,x+22,340,width-44,11,'#c2cee0' if i==cols-1 else MUTED)
        if data.get('note'):self.text(data['note'],56,466,848,10,MUTED)
    def figure(self,data):
        src=pdfium.PdfDocument(str(OUT/'originals'/self.filename));page=src[data['page']-1]
        im=page.render(scale=1.6).to_pil().convert('RGB');a,b,c,d=data['crop'];im=im.crop((int(im.width*a),int(im.height*b),int(im.width*c),int(im.height*d)))
        x,y,w,h=56,211,550,310
        self.rect(x,y,w,h,TINT)
        im.thumbnail((int(w-28),int(h-28)))
        self.c.drawImage(ImageReader(im),x+(w-im.width)/2,H-y-(h+im.height)/2,width=im.width,height=im.height)
        self.text(data['heading'],634,216,270,18,INK,True)
        self.text(data['body'],634,279,270,11,MUTED)
        self.text(f'원본 발표자료 p.{data["page"]}의 구현 화면 / 도식',634,486,270,8,MUTED)
    def erd(self,data):
        nodes=[('Profile','user_id · profile_image<br/>participations_cnt · post_cnt · comment_cnt'),('User','email · password · name · nickname<br/>birth · address'),('Event','user_id · title · content · deadline<br/>participants_cnt · location · category'),('Count','post_id · ip_address'),('Post','user_id · title · content · tag<br/>location · view_cnt · post_image'),('Participants','event_id · user_id'),('Room','name'),('Comment','post_id · user_id · parent_comment_id<br/>content · created_at'),('Message','value · date · user · room')]
        edges=[(0,1),(1,2),(1,4),(2,5),(3,4),(4,7)]
        for a,b in edges:
            ax=56+(a%3)*292;ay=213+(a//3)*108
            bx=56+(b%3)*292;by=213+(b//3)*108
            if ay==by:self.line(min(ax,bx)+264,ay+47,max(ax,bx),by+47,ACCENT)
            else:self.line(ax+132,ay+92,bx+132,by,ACCENT)
        for i,(name,fields) in enumerate(nodes):
            x=56+(i%3)*292;y=213+(i//3)*108
            self.rect(x,y,264,92,TINT,LINE)
            self.text(name,x+16,y+9,232,12,INK,True)
            self.text(fields,x+16,y+37,232,8,MUTED,leading=13)
    def comparison(self,data):
        page=PdfReader(OUT/'originals'/self.filename).pages[data['page']-1]
        images={item.name:item.image for item in page.images}
        for i,(label,name) in enumerate(data['images']):
            x=56+i*292;self.rect(x,211,264,310,TINT)
            self.text(label,x+16,224,232,10,ACCENT,True)
            im=images[name].convert('RGBA');white=Image.new('RGBA',im.size,'white');white.alpha_composite(im);im=white.convert('RGB')
            im.thumbnail((148,252));self.c.drawImage(ImageReader(im),x+(264-im.width)/2,H-258-im.height,width=im.width,height=im.height)
        self.text(data['heading'],660,224,244,20,INK,True,leading=29)
        self.text(data['body'],660,306,244,11,MUTED)
    def build(self):
        self.c=canvas.Canvas(str(OUT/self.filename),pagesize=(W,H),pageCompression=1)
        self.c.setTitle(self.title.replace('<br/>',' '));self.c.setAuthor('주효성 / JOO');self.c.setSubject(self.category+' | Portfolio case study')
        self.cover();self.c.bookmarkPage('cover');self.c.addOutlineEntry('프로젝트 개요','cover',0,False);self.c.showPage()
        for n,(eyebrow,title,lead,kind,data) in enumerate(self.pages,2):
            self.page(n,eyebrow,title,lead);self.c.bookmarkPage(f'p{n}');self.c.addOutlineEntry(title,f'p{n}',0,False)
            getattr(self,kind)(data);self.c.showPage()
        self.c.save();print(f'{self.filename}: {len(self.pages)+1} pages')

def C(*items,**kwargs):return dict(items=items,**kwargs)
def T(headers,rows,**kwargs):return dict(headers=headers,rows=rows,**kwargs)

customer=Deck('RPA_4기_프로젝트2+3.pdf','MACHINE LEARNING / CUSTOMER SEGMENTATION','자녀의 성장 주기로<br/>이해하는 고객','유아용품 구매 데이터에서 고객 세분화와<br/>맞춤형 서비스의 가능성을 탐색했습니다.','데이터 전처리 · 머신러닝 모델 생성','김성민 · 김여민 · 박종서 · 이송이 · 주효성',['고객 문제 정의','데이터 분석·모델링','맞춤형 서비스 제안'])
customer.add('01 / CONTEXT & TEAM','구매 기록에서 고객의 다음 필요를 찾기','분기별 결제 금액 감소와 낮은 재구매율을 출발점으로 삼았습니다.','table',T(['팀원','담당 역할'],[['김성민','데이터 전처리 · 머신러닝 모델 생성'],['김여민','데이터 전처리 · 발표'],['박종서','데이터 전처리 · 도메인 자료조사'],['이송이','데이터 전처리 · PPT 작성'],['주효성','데이터 전처리 · 머신러닝 모델 생성']],weights=[1,4],rowheight=42,note='원문 현황: 3회 이상 재구매율 26.7%. 출생아 수 감소와 육아용품 시장 확대라는 배경에서 고객 맞춤 서비스를 검토했습니다.'))
customer.add('02 / DATA PREPARATION','구매 시 자녀 월령을 분석의 중심에','고객 연령과 구매 시점을 함께 살펴보고, 자녀의 생애 주기를 기준으로 데이터를 정리했습니다.','flow',C(('값의 단위 점검','월령이 100보다 큰 값을 일수 오기입으로 판단해 30으로 나누어 변환했습니다.'),('결측값 처리','주 구매 고객군을 파악한 뒤 해당 고객군의 구매 시 자녀 월령 평균으로 대체했습니다.'),('생애 주기 구분','출산 전 · 출산 · 100일 후 · 영아기 · 유아기 · 아동으로 구분했습니다.'),note='원문 구분 경계: -2개월 / 3개월 / 7개월 / 12개월 / 36개월. 고객 연령은 30대, 특히 30~36세에 집중되었습니다.'))
customer.add('03 / EXPLORATORY ANALYSIS','성장 주기가 바뀌면 구매 품목도 바뀝니다','같은 고객이라도 자녀의 성장 단계에 따라 필요한 상품이 달라진다는 점에 주목했습니다.','cards',C(('100일 후','기저귀·더블하트·체험팩','해당 주기의 구매 건수 상위 품목을 파악했습니다. 다음 단계의 고객에게 필요한 정보를 제안하는 근거로 활용했습니다.'),('영아기','주기 이동에 따른 품목 변화','FMC·팬티·FC 구매 건수가 증가하고, 이전 주기에서 상위였던 일부 품목의 구매 건수는 하락했습니다.'),note='분석 결과는 관찰된 구매 패턴입니다. 고객 개인의 선호나 구매 전환 개선 효과를 검증한 결과와는 구분합니다.'))
customer.add('04 / PREDICTION MODELS','두 가지 예측 모델의 평가 결과','재구매와 등급별 구매금액 예측을 시도했습니다. 아래 명칭과 평가지표 표기는 원문 기준입니다.','table',T(['항목','재구매 예측','등급별 구매금액 예측'],[['모델','Random Forest','Decision Tree'],['데이터 분할','test_size=0.3 / random_state=50','test_size=0.3 / random_state=0'],['주요 설정','max_depth=4 / n_estimators=150','max_depth=8'],['훈련 / 테스트','0.79 / 0.79','0.92 / 0.92']],weights=[1.2,2.1,2.1],rowheight=49,note='원문은 두 결과를 ‘정확도’로 표기합니다. 구매금액 타깃 정의와 지표 산식, 사용자·시간 단위 분리 여부는 추가 확인이 필요합니다.'))
customer.add('05 / DEMAND MODEL','물품대분류 예측과 변수 중요도','원문은 Decision Tree Regressor를 활용한 ‘물품대분류별 수요 예측 모델’로 소개합니다.','chart',dict(chart_title='발표 자료의 모델 변수 중요도',values=[('구매금액',76.4,'76.4%'),('구매일',10.7,'10.7%'),('구매 시 월령',10.5,'10.5%')],heading='어떤 정보가<br/>모델에 기여했을까?',body='설정: max_depth=30,<br/>min_samples_leaf=10,<br/>random_state=100.<br/><br/>입력: 구매일·ID·구매금액·결혼유무·거주지역·연령·카드·유입경로·자녀여부·월령.<br/><br/>원문 타깃은 물품대분류입니다. 범주형 타깃에 대한 회귀 모델 적용 방식과 인코딩은 재검토할 항목입니다.',chart_note='상위 세 변수만 표시했습니다. 중요도는 인과관계나 실제 수요 증가를 뜻하지 않습니다.'))
customer.add('06 / SERVICE PROPOSAL','같은 주기와 다음 주기를 함께 안내하기','주기별 구매 건수 상위 상품을 바탕으로 고객 맞춤 메시지와 상품 링크를 제안했습니다.','table',T(['순위','100일 후 고객의 상위 상품','영아기 고객의 상위 상품'],[['1','모유실감 젖꼭지 L (2입)','모유실감 젖꼭지 LL (2입)'],['2','하기스 네이처메이드 여아 132매','맘큐 허그박스'],['3','하기스 네이처메이드 남아 132매','모유실감 젖꼭지 L (2입)'],['4','모유실감 젖꼭지 M (2입)','하기스 네이처메이드 여아 132매'],['5','하기스 맥스드라이 3단계 공용 20매','여행용티슈 카카오프렌즈 70매 × 3개']],weights=[.5,2.5,2.5],rowheight=43,size=9,note='메시지 제안: 현재 주기 고객이 많이 구매한 상품, 다음 주기에 필요한 상품, 주기별 육아 노하우를 함께 안내합니다.'))
customer.add('07 / CUSTOMER EXPERIENCE','등급과 유입 채널을 서비스 제안으로','체험팩 선호와 유입 경로 분석을 바탕으로 고객 등급 개편과 SNS 광고를 제안했습니다.','table',T(['등급','3개월 누적 결제금액','혜택'],[['예비맘','5만원 이상','적립금 1% · 1만원 상당 체험팩'],['숙련맘','7만원 이상','적립금 3% · 3만원 상당 체험팩'],['슈퍼맘','10만원 이상','적립금 5% · 5만원 상당 체험팩']],weights=[1,1.7,2.8],rowheight=62,note='체험팩은 물품대분류별 판매량 2순위였습니다. 인스타그램·네이버블로그 유입이 약 67%라는 분석을 토대로 SNS 광고 방향을 제안했습니다.'))
customer.add('08 / REFLECTION','분석을 서비스 제안으로 연결한 경험','팀의 모델링 결과와 서비스 아이디어, 실제 검증한 성과의 범위를 구분합니다.','cards',C(('MY LEARNING','전처리와 도메인 이해','구매 시 월령에 초점을 두고 고객을 세분화하며, 모델링 전에 데이터의 의미와 품질을 이해하는 과정의 중요성을 배웠습니다.'),('NEXT QUESTIONS','평가 설계와 효과 검증','사용자·시간 기준 분할과 타깃 정의를 점검하고, 제안한 메시지나 등급제가 재구매에 미치는 효과를 실험하는 것이 다음 과제입니다.'),note='팀 회고: 목적에 맞는 데이터 활용, 전처리 협업, 도메인 배경지식, 분석 방향에 맞는 모델 선택의 중요성을 정리했습니다.'))

steel=Deck('RPA_4기_프로젝트1.pdf','MACHINE LEARNING / MANUFACTURING','제조 데이터에서 찾은<br/>불량의 단서','철강 제조 조건과 불량 여부의 관계를 탐색하고<br/>분류 모델의 결과와 주요 변수를 비교했습니다.','데이터 전처리 · 시각화 · 모델링 · 발표','송지혁 · 주효성 · 맹지은 · 박용식 · 강승현',['제조 데이터 탐색','분류 모델 비교','주요 변수 해석'])
steel.add('01 / CONTEXT & TEAM','제조 조건과 불량 사이의 패턴 탐색','철강 종류, 작업 시간, 규격과 공정 변수를 중심으로 제조 데이터를 분석했습니다.','table',T(['팀원','담당 역할'],[['송지혁','데이터 전처리 · 시각화 · 데이터 모델링'],['주효성','데이터 전처리 · 시각화 · 모델링 · PPT 발표'],['맹지은','데이터 전처리 · 모델링 · PPT 작성'],['박용식','데이터 전처리 · 시각화 · 데이터 모델링'],['강승현','데이터 전처리 · 모델링']],weights=[1,4],rowheight=42,note='교육용 제조 데이터 분석 프로젝트입니다. 원문 역할표를 기준으로 팀 결과와 본인의 담당 범위를 구분했습니다.'))
steel.add('02 / EXPLORATORY ANALYSIS','양품과 불량의 분포부터 확인했습니다','클래스 분포를 먼저 살펴본 뒤 철강 종류·시간·규격별 패턴을 탐색했습니다.','chart',dict(chart_title='원문 SCALE 분포 요약',values=[('양품',67.9,'67.9%'),('불량',32.1,'32.1%')],heading='비교의 출발점은<br/>데이터의 분포',body='원문 도표는 양품 약 68%, 불량 약 32%로 요약합니다.<br/><br/>철강 종류별 생산량과 불량 건수, 시간대별 불량률, 규격과 Rolling Descaling 조건을 함께 살펴봤습니다.',chart_note='원문 원형 그래프 67.9% / 32.1%와 요약 표기의 68% / 32%를 구분했습니다.'))
steel.add('03 / EXPLORATORY FINDINGS','시간과 규격에 따른 차이를 관찰했습니다','원문에서 관찰한 패턴을 정리했습니다. 원인이나 개선 효과를 검증한 결과는 아닙니다.','cards',C(('TIME & STEEL KIND','C0와 작업 시간대','C0의 생산량과 불량 건수가 많았습니다. C0를 시간대로 나누어 보았을 때 원문은 오전의 높은 불량률을 주요 관찰로 제시했습니다.'),('SPEC & PROCESS','JS 규격과 공정 조건','수량 20개 이상인 규격 중 JS의 높은 불량률을 관찰했습니다. 규격별 Rolling Descaling 조건도 함께 비교했습니다.'),note='분석 질문: 생산량 차이와 조건별 표본 수를 고려했을 때에도 같은 패턴이 유지되는지 추가 확인이 필요합니다.'))
steel.add('04 / MODEL COMPARISON','세 가지 분류 모델을 비교했습니다','아래 값은 원문 발표자료의 훈련·테스트 정확도입니다.','table',T(['모델','훈련 정확도','테스트 정확도'],[['Random Forest','97%','95%'],['Logistic Regression','88%','88%'],['XGBoost','100%','99%']],weights=[2.5,1.5,1.5],rowheight=64,note='발표 자료에는 분할 방식과 클래스별 정밀도·재현율이 제시되지 않았습니다. 높은 정확도를 현장 적용 성능이나 불량 감소 효과로 해석하지 않습니다.'))
steel.add('05 / INTERPRETATION','예측 결과에서 공정의 단서를 찾기','모델 중요도와 EDA를 함께 검토하며 후속 분석 대상을 정리했습니다.','flow',C(('모델 중요도','XGBoost 결과에서 Rolling Temp T5와 HSB가 주요 변수로 제시되었습니다.'),('탐색 결과 연결','JS 규격과 시간대, Rolling Descaling 관련 관찰을 함께 정리했습니다.'),('후속 확인','변수의 의미와 측정 시점을 점검하고 공정 담당자의 도메인 해석과 비교할 수 있습니다.'),note='원문의 변수 중요도 순위는 1위 Rolling Temp T5, 2위 HSB입니다. 중요도는 불량 발생의 인과관계를 증명하지 않습니다.'))
steel.add('06 / REFLECTION','작은 데이터에서도 전처리가 중요했습니다','본인 회고와 팀의 관찰을 바탕으로 다음 분석에서 점검할 내용을 정리했습니다.','cards',C(('MY LEARNING','전처리의 어려움','주효성의 원문 회고는 데이터가 적어 전처리 과정이 어려웠다는 점입니다. 데이터 품질과 표본 규모를 먼저 확인하는 태도로 연결할 수 있습니다.'),('NEXT QUESTIONS','검증 가능한 평가 설계','분할 기준·표본 수·라벨 정의를 명확히 하고, 클래스별 성능과 과적합을 점검한 뒤 현장 적용 가능성을 판단해야 합니다.'),note='팀 회고에는 다양한 인사이트와 의견을 공유한 경험, 더 많은 데이터를 다뤄보고 싶다는 의견, 학습을 더 이어가겠다는 의견이 담겨 있습니다.'))

backend=Deck('RPA_4기_프로젝트5.pdf','BACKEND DEVELOPMENT / COMMUNITY','사람과 모임을 연결하는<br/>모여방','우리 동네 소모임을 위한 웹 애플리케이션.<br/>Django 기반 모델·게시판·인증 구현을 경험했습니다.','기초 모델 · 게시판 전체 · JWT Token 작성','박진원 · 신명규 · 박용식 · 송지혁 · 김경태 · 주효성',['서비스 기능 정의','모델·API 구성','게시판·인증 구현'])
backend.add('01 / TEAM & OWNERSHIP','팀 전체 기능과 나의 구현 범위','지역 커뮤니티에 필요한 여러 기능을 나누어 개발한 6인 팀 프로젝트입니다.','table',T(['팀원','원문 담당 역할'],[['박진원','JWT Token · 소셜 로그인 · 프로필 API'],['신명규','프로필 프런트 페이지'],['박용식','채팅·DM API 및 프런트 페이지'],['송지혁','이벤트 전체 · 무한 스크롤 · 주소 검색 API'],['김경태','웹 디자인 · 메인 페이지 · 내비게이션'],['주효성','기초 모델 · 게시판 전체 · JWT Token']],weights=[1,4],rowheight=38,size=10))
backend.add('02 / ARCHITECTURE','모델과 API로 서비스 기능 연결하기','Django REST Framework와 외부 DB인 AWS RDS를 사용한 팀의 서비스 구성을 정리했습니다.','flow',C(('웹 클라이언트','메인·프로필·게시판 등 사용자 화면에서 서비스 기능에 접근합니다.'),('Django REST API','모델과 API를 통해 사용자·활동·게시글 등의 데이터를 처리합니다.'),('외부 데이터베이스','원문 개발 환경에 제시된 AWS RDS를 데이터 저장소로 연결했습니다.'),note='이 그림은 원문 기술과 기능을 설명하기 위한 개념도입니다. 서버 배포 토폴로지나 운영 환경의 검증 결과를 의미하지 않습니다.'))
backend.add('03 / DATA MODEL','사용자·활동·게시글을 중심으로 한 ERD','원본 ERD의 모델과 핵심 필드를 다시 그렸습니다. 대표 관계를 연결했으며 전체 필드와 제약조건은 원본을 참고하세요.','erd',{})
backend.add('04 / API CAPABILITIES','게시판에서 커뮤니티 기능으로','본인은 게시판과 기초 모델, JWT 관련 구현을 담당했습니다. 아래는 팀 전체 API 구성입니다.','cards',C(('CORE / MY CONTRIBUTION','모델·게시판·JWT','기초 데이터 모델과 게시판 기능을 구현하고 JWT Token 작성을 담당했습니다. 구체적인 코드와 테스트 근거를 보강하면 구현 판단을 더 명확히 설명할 수 있습니다.'),('TEAM CAPABILITIES','기능별 API 연결','팀 자료에는 REST Framework, JWT, 채팅, 주소 검색, 무한 스크롤, DM 및 알림 API가 제시되어 있습니다. 각 기능은 역할표에 따라 나누어 담당했습니다.'),note='본인 기여: 기초 모델 · 게시판 · JWT. 채팅·DM·주소 검색·무한 스크롤 등은 팀원별 담당 기능입니다.'))
backend.add('05 / AUTHENTICATION','Access와 Refresh의 역할을 구분하기','원문 JWT 설명을 바탕으로 인증 흐름을 개념적으로 정리했습니다.','flow',C(('로그인','사용자를 인증하고 토큰을 활용하는 흐름을 구성합니다.'),('Access Token','로그인 이후 권한 인증에 사용하는 토큰입니다.'),('Refresh Token','Access Token 만료 시 재발급에 사용하는 토큰입니다.'),note='로그인·권한 인증·토큰 재발급의 역할을 정리한 개념도입니다. 실제 토큰 처리 정책과 구현 상세는 별도 코드 검토가 필요합니다.'))
backend.add('06 / REFLECTION','구현의 어려움을 구조 이해로 연결하기','본인 회고에는 JWT 구현의 어려움과 학습 경험이 남아 있습니다.','cards',C(('MY LEARNING','인증 기능을 다뤄본 경험','JWT에 어려움이 있었지만 많은 공부가 됐다는 원문 회고를 담았습니다. 인증 흐름을 코드와 요청·응답으로 설명하는 자료가 다음 보완점입니다.'),('TEAM LEARNING','구조·협업·완성도의 균형','팀원들은 구조 원리 이해, 협업의 중요성, 반복 오류 해결, 일상적인 웹 기능 구현의 난도를 회고했습니다. 기능 범위와 UI 완성도 사이의 균형도 과제로 남았습니다.'),note='Django 기반의 기초 모델·게시판·JWT 구현을 경험한 프로젝트입니다. 역할표와 팀 전체 결과를 함께 소개합니다.'))

silver=Deck('RPA_4기_프로젝트4.pdf','PUBLIC DATA / PROBLEM DEFINITION','노인 부양 부담 완화를 위한<br/>분석과 서비스 제안','공공 통계로 초기 가설을 점검하고<br/>의료·복지 서비스 접근성을 위한 아이디어를 제안했습니다.','데이터 전처리 · 자료조사 · PPT 제작','김성민 · 김여민 · 박종서 · 이주상 · 주효성',['문제와 가설 수립','공공 통계 검토','서비스 아이디어 제안'])
silver.add('01 / CONTEXT & TEAM','고령화라는 큰 문제를 분석 가능한 질문으로','노인의 소득·경제활동, 의료비와 복지시설을 중심으로 공공 통계를 탐색했습니다.','table',T(['팀원','원문 담당 역할'],[['김성민','데이터 전처리 · 자료조사 · PPT 제작'],['김여민','데이터 전처리 · 자료조사 · 정리 및 발표'],['이주상','초기 자료조사 · 데이터 전처리'],['박종서','데이터 전처리 · 자료조사 · 앱 이미지 제작'],['주효성','데이터 전처리 · 자료조사 · PPT 제작']],weights=[1,4],rowheight=42,note='실버라이닝 팀의 분석·서비스 기획 프로젝트입니다. 앱 이미지는 박종서 담당이며, 실제 운영 서비스나 ML 모델 구현으로 소개하지 않습니다.'))
silver.add('02 / HYPOTHESIS CHECK','초기의 가설이 모두 맞지는 않았습니다','통계와 문헌을 확인하며 해결해야 할 문제의 초점을 조정했습니다.','table',T(['초기 가설','자료에서 관찰한 내용','원문의 판단'],[['일자리 부족과 낮은 소득','전체소득·근로소득 증가, 고용률 증가와 실업률 감소','초기 가설 재검토'],['의료비 부담 증가','의료서비스 수요와 비용 부담, 만성질환 관련 부담 증가','분석 초점 유지'],['여가시설 대비 복지시설 부족','복지 수요 증가와 이용 가능한 시설의 부족','서비스 방향으로 연결']],weights=[1.5,2.7,1.2],rowheight=75,note='원문의 ‘가설 성공·실패’는 탐색적 통계 해석입니다. 통계적 가설 검정이나 인과 추정 결과를 뜻하지 않습니다.'))
silver.add('03 / EVIDENCE','소득 증가만으로 설명되지 않는 부담','경제활동 개선과 의료·복지 수요 증가를 함께 고려했습니다.','cards',C(('ECONOMIC ACTIVITY','소득·고용의 변화','통계청 경제활동인구조사와 보건복지부 노인실태조사를 활용했습니다. 노인의 소득과 고용 변화는 초기의 일자리 부족 가설을 재검토하게 했습니다.'),('HEALTH & WELFARE','의료비와 시설의 문제','건강보험·장기요양보험·노인복지시설 통계를 함께 검토했습니다. 의료비 부담과 서비스 수요, 시설 접근성에 해결 방향을 집중했습니다.'),note='서로 다른 연도·모집단의 공공자료를 연결한 탐색입니다. 각 지표의 정의와 비교 가능성은 원본 자료에서 확인해야 합니다.'))
silver.add('04 / INSIGHTS','이용자의 생활 방식까지 함께 살펴보기','의료·복지 수요에 더해 커뮤니티 선호와 거주 희망 형태를 서비스 기획의 맥락으로 고려했습니다.','flow',C(('수요 변화','고령인구 증가에 따라 의료·복지 서비스에 대한 수요가 확대될 것으로 보았습니다.'),('생활 맥락','커뮤니티 활동과 일반주택·아파트 거주 선호 등 원문이 조사한 생활 특성을 검토했습니다.'),('서비스 접근','기존 공간과 일상생활 속에서 필요한 서비스를 찾고 예약하는 방향을 제안했습니다.'),note='거주 희망 형태 자료만으로 자녀와의 동거 선호까지 단정하지 않습니다. 원문에 담긴 해석과 실제 지표의 범위를 구분했습니다.'))
silver.add('05 / SERVICE CONCEPT','필요한 돌봄과 진료를 예약하는 서비스','분석 결과에서 출발한 노인 맞춤 앱의 기능을 정리했습니다.','cards',C(('CARE AT HOME','방문요양 서비스 예약','사용자가 필요한 방문요양 서비스를 찾고 예약하는 기능을 제안했습니다. 일상에서 의료·복지 서비스를 연결하는 접근입니다.'),('MEDICAL ACCESS','병원 예약','진료가 필요한 사용자가 병원을 찾고 예약할 수 있는 기능을 제안했습니다. 기존 예약 서비스 사례를 참고했습니다.'),note='이 프로젝트의 결과물은 서비스 아이디어와 앱 화면 시안입니다. 서버 구현·실사용 검증·운영 성과는 자료에서 확인되지 않습니다.'))
silver.add('06 / PROTOTYPE','서비스의 형태를 화면으로 구체화하기','원문에 제시된 앱 시안을 보존했습니다. 앱 이미지 제작 담당자는 박종서입니다.','figure',dict(page=20,crop=[.12,.16,.39,.89],heading='방문요양과<br/>병원 예약',body='원문의 앱 화면은 서비스 아이디어를 전달하는 프로토타입입니다.<br/><br/>주효성의 담당은 자료조사·전처리·PPT 제작입니다. 화면 제작이나 실제 앱 개발을 본인의 구현 성과로 소개하지 않습니다.'))
silver.add('07 / REFLECTION','관심을 데이터 해석과 서비스 기획으로','원문에서 본인은 노인 복지의 취약 지점을 조사하고 앱 아이디어를 기획하며 데이터 해석을 배웠다고 회고했습니다.','cards',C(('MY LEARNING','자료를 연결해 문제를 이해하기','통계와 여러 자료를 조사하며 이미 진행 중인 정책과 여전히 남은 취약 지점을 함께 보았습니다. 해석을 서비스 아이디어로 연결하는 경험을 쌓았습니다.'),('TEAM LEARNING','가설을 수정할 수 있는 태도','팀은 초기 가설이 맞지 않을 수 있다는 점과 외부 자료를 연결해 해석하는 과정을 회고했습니다. 실제 이용자 인터뷰와 수요 검증이 이후의 과제입니다.'),note='공공데이터 프로젝트는 AI 모델의 성능 근거보다 문제 정의·리서치·서비스 기획 역량을 보여주는 사례로 배치했습니다.'))

todo=Deck('투두일리 최종발표_231024_153818.pdf','PRODUCT THINKING / SERVICE ITERATION','생산성 앱을 더 쉽게 찾는<br/>투두일리','문제 정의와 MVP 출시에서 출발해<br/>사용자 반응과 전환 지표로 개선을 반복했습니다.','', '정진성 · 김성훈 · 주효성',['사용자 문제 정의','MVP 출시','측정과 반복 개선'])
todo.add('01 / PROBLEM DEFINITION','나에게 맞는 생산성 앱을 찾기 어렵다','스토어·리뷰·블로그를 오가며 정보를 비교하고 다시 다운로드까지 이동해야 하는 번거로움에 주목했습니다.','cards',C(('USER PROBLEM','탐색과 비교의 분산','앱 스토어의 설명과 리뷰만으로 필요한 정보를 찾기 어려웠고, 외부 리뷰를 확인한 뒤 다시 스토어를 방문해야 했습니다.'),('SOLUTION HYPOTHESIS','탐색·비교·다운로드를 한곳에','생산성 앱을 모아 필터링하고, 동일한 형식의 상세 정보와 추천 아티클을 제공하며 다운로드 링크로 이어지는 서비스를 기획했습니다.'),note='팀 구성: 정진성 · 김성훈 · 주효성. 원문에 개인별 역할표가 없어 출시·인터뷰·개선 성과는 팀 단위로 소개합니다.'))
todo.add('02 / MVP','5일 안에 핵심 가설을 확인할 형태로','원문 기준 기획부터 최초 MVP 완성까지 9월 24~29일, 5일이 소요됐습니다.','flow',C(('최소 정보','서비스 10개, 비교 콘텐츠 카테고리, 최소한의 서비스 설명으로 시작했습니다.'),('최소 연결','별도 상세 페이지나 다운로드 링크 대신 각 서비스의 홈페이지 링크를 제공했습니다.'),('탐색 확장','이후 키워드 필터, 인기 서비스, 상세 리뷰, 추천 아티클과 다운로드 동선을 보강했습니다.'),note='원문 표기: 2023.09.29 출시 / 2023.10.21 기준 총 사용자 609명. 과거 팀 발표 시점의 집계이며 현재 이용자 수가 아닙니다.'))
todo.add('03 / MEASUREMENT','탐색과 다운로드를 두 단계로 측정','원문 KPI 표의 수치를 유지했습니다. 목표와 실측, 향후 예상값을 구분합니다.','table',T(['지표','목표','개선 전','1차 개선','2차 개선'],[['메인 → 상세 전환율','30%','29.4%','37.6%','29.2%'],['상세 → 다운로드 클릭','50%','25%','48.5%','21.44%']],weights=[2.2,.8,1,1,1],rowheight=79,note='집계 기간: 개선 전 09/29~10/04, 1차 10/05~10/12, 2차 10/13~10/19. 상세 슬라이드의 모수와 KPI 표에 불일치가 있어 수치를 임의로 재산출하지 않았습니다.'))
todo.add('04 / FIRST ITERATION','필터와 2열 노출로 탐색 동선을 바꾸기','경쟁 서비스의 UI를 분석하고 원하는 앱을 찾는 과정을 줄이는 방향으로 개선했습니다.','chart',dict(chart_title='메인 → 상세 페이지 전환율 / KPI 표 기준',values=[('개선 전',29.4,'29.4%'),('1차 개선',37.6,'37.6%')],heading='탐색의 부담을<br/>줄이는 시도',body='원하는 키워드 필터를 추가하고 서비스 노출을 2열로 변경했습니다.<br/><br/>원문은 메인→상세 전환율이 약 28% 상대 증가했다고 정리합니다.<br/><br/>동일 사용자 무작위 실험이 아니므로 UI 변경만의 인과 효과로 단정하지 않습니다.',chart_note='29.4% → 37.6%는 8.2%p 차이이며, 상대 증가율은 약 28%입니다.'))
todo.add('04 / INTERFACE EVOLUTION','찾고 비교하기 쉬운 인터페이스로','실제 서비스의 전후 화면을 함께 보며 첫 번째 개선의 의도를 설명합니다.','comparison',dict(page=7,images=[('BEFORE / 목록 중심','I8.png'),('AFTER / 키워드와 2열 노출','I7.png')],heading='탐색의 기준을<br/>화면에 드러내기',body='원하는 기능을 키워드로 좁히고, 여러 앱을 한눈에 비교할 수 있도록 노출 구조를 바꿨습니다.<br/><br/>왼쪽 이미지는 당시 서비스 화면입니다. 측정 결과는 앞 페이지의 KPI 표를 기준으로 소개합니다.'))
todo.add('05 / SECOND ITERATION','사용자의 설명과 실제 지표를 함께 보기','7명 심층 인터뷰에서 상세 정보 부족을 확인하고 설명과 다운로드 버튼을 보강했습니다.','cards',C(('CHANGE','정보와 버튼을 보강','앱 평점, 모델 설명, 장단점·대표 기능을 추가하고 다운로드 버튼을 일체화했습니다. 유입 확대를 위한 마케팅도 함께 시작했습니다.'),('OBSERVATION','전환율은 오히려 하락','상세→다운로드 클릭 전환율은 48.5%에서 21.44%로 하락했습니다. 원문은 다운로드 클릭 약 70% 하락도 표기하며, 광고 유입의 타깃과 서비스 적합성을 재검토했습니다.'),note='클릭 수·클릭 전환율·상대 증감은 서로 다른 지표입니다. 여러 변경이 동시에 이루어져 원인을 한 가지로 확정하지 않습니다.'))
todo.add('06 / NEXT EXPERIMENT','추천 콘텐츠와 타기팅을 다시 설계하기','원문 발표 시점에서 3차 개선은 진행·예정 단계였습니다. 아래 내용은 완료 성과가 아닌 계획입니다.','flow',C(('퍼널 확장','추천 콘텐츠 카테고리를 늘려 탐색과 다운로드로 이어지는 진입점을 추가합니다.'),('노출 개선','인기 Top 배지와 관심도를 높일 수 있는 콘텐츠 노출을 검토합니다.'),('타깃 재검토','앱 추천 소재와 광고 타기팅을 조정해 서비스와 맞는 유입을 확인합니다.'),note='원문 예상: 다운로드 클릭 전환율 30%, 메인→상세 전환율 38%. 결과로 확인된 수치가 아니므로 실측 지표 표에는 넣지 않았습니다.'))
todo.add('07 / MARKETING','유입이 많아도 전환이 높지는 않았습니다','1차 광고에서 CTR과 서비스 내부 전환이 반대로 움직이는 현상을 보고 타기팅을 재검토했습니다.','table',T(['날짜 (2023)','CTR','CPC'],[['10.14','0.3%','58원'],['10.15','0.9%','108원'],['10.16','0.6%','98원'],['10.17','0.8%','106원']],weights=[2,1.5,1.5],rowheight=53,note='원문은 1차 구글애즈 검색광고·유튜브 DA 이후 리타기팅과 2차 검색광고를 진행 중이라고 설명합니다. 광고별 수익이나 최종 캠페인 성과는 제시되지 않았습니다.'))
todo.add('08 / RETROSPECTIVE','다시 시도하는 힘과 측정의 중요성','팀의 Keep / Problem / Try 회고를 문제 해결 방식으로 정리했습니다.','cards',C(('KEEP','빠른 대안과 반복 시도','5번의 기획 수정과 한 번의 피보팅 과정에서도 다시 시도하는 끈기, 문제가 생겼을 때 대안을 빠르게 제시한 경험을 남겼습니다.'),('PROBLEM → TRY','리소스와 데이터를 미리 계획','업무별 시간 배분과 데이터 선정·수집·분석의 어려움을 회고했습니다. 데일리 스크럼과 수시 공유, 기획 단계부터 데이터 위치와 분석 방법을 정하는 방식을 제안했습니다.'),note='원문에 개인별 기여 분리가 없어 위 회고는 팀의 학습으로 표현했습니다. 개인의 구체적 역할은 별도 확인 후 보강할 수 있습니다.'))

if __name__=='__main__':
    import sys
    from build_safety_map_pdf import make_safety_deck
    from build_kbeauty_pdf import make_kbeauty_deck
    decks=[customer,backend,steel,silver,todo,make_safety_deck(),make_kbeauty_deck()]
    requested=set(sys.argv[1:])
    if requested:
        assert requested <= {deck.filename for deck in decks}, 'Unknown PDF filename'
    for deck in decks:
        if not requested or deck.filename in requested:deck.build()
