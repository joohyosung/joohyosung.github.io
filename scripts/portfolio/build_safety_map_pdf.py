"""Build the safety-map case study with the shared portfolio layout.

The original presentation is preserved in project_template/originals/.
Additional ownership facts (DB design, Node.js and Nginx setup) were supplied
by the portfolio owner. UI images and performance values come from the source.
"""
from build_pdfs import Deck,C,T,OUT,ROOT,H,INK,MUTED,ACCENT,MINT,TINT,WHITE,LINE
from pypdf import PdfReader
from PIL import Image
from reportlab.lib.utils import ImageReader

class SafetyDeck(Deck):
    def source_image(self,page,index=0):
        reader=PdfReader(OUT/'originals'/self.filename)
        return list(reader.pages[page-1].images)[index].image.convert('RGB')
    def place_image(self,im,x,y,w,h):
        im=im.copy();im.thumbnail((int(w),int(h)))
        self.c.drawImage(ImageReader(im),x+(w-im.width)/2,H-y-(h+im.height)/2,width=im.width,height=im.height)
    def screen(self,data):
        self.rect(56,211,550,310,TINT)
        self.place_image(self.source_image(data['page'],data.get('index',0)),70,225,522,282)
        height=self.text(data['heading'],634,222,270,19,INK,True,leading=28)
        self.text(data['body'],634,222+height+20,270,11,MUTED)
        self.text(f"원본 발표자료 p.{data['page']} / 실제 구현 화면",634,492,270,8,MUTED)
    def screen_pair(self,data):
        for i,(label,page,index,caption) in enumerate(data['items']):
            x=56+i*434
            self.rect(x,211,414,306,TINT)
            self.text(label,x+20,228,374,13,INK,True)
            self.place_image(self.source_image(page,index),x+16,267,382,205)
            self.text(caption,x+20,485,374,9,MUTED)
    def operating_structure(self,data):
        # Embed the full-resolution image so the small labels stay sharp on zoom.
        image=Image.open(ROOT/'assets/safety-map-operating-structure.png').convert('RGB')
        scale=min(848/image.width,363/image.height)
        width,height=image.width*scale,image.height*scale
        x=56+(848-width)/2
        y=182+(363-height)/2
        self.c.drawImage(ImageReader(image),x,H-y-height,width=width,height=height)
    def data_model(self,data):
        nodes=[('users','사용자',[('id','사용자 식별자'),('email','이메일'),('nickname','닉네임'),('role','사용자 권한'),('password_hash','비밀번호 해시')]),('notes','주민 안심노트',[('id','노트 식별자'),('title · content','제목과 관찰 내용'),('status','검토·공개 상태'),('observed_date','관찰일'),('author_id','작성자 외래 키')])]
        for x,(name,label,fields) in zip([56,544],nodes):
            self.rect(x,211,360,286,TINT,LINE)
            self.text(name,x+22,229,316,21,INK,True)
            self.text(label,x+22,267,316,10,ACCENT)
            for j,(field,meaning) in enumerate(fields):
                y=302+j*34
                self.text(field,x+22,y,160,10,INK,True)
                self.text(meaning,x+188,y,150,10,MUTED)
        self.line(416,350,544,350,ACCENT)
        self.line(536,345,544,350,ACCENT);self.line(536,355,544,350,ACCENT)
        self.text('1 : N',449,319,66,14,ACCENT,True)
        self.text('author_id',445,365,86,9,MUTED)
        self.text('users.id와 notes.author_id로 작성자를 연결합니다. 권한과 노트 상태를 포함한 DB 설계를 직접 담당했습니다.',56,513,848,9,MUTED)
    def performance(self,data):
        specs=[(56,'WMS 요청 수',95,4,100,'95건','4건','요청 95건 → 4건 / 약 96% 감소'),(490,'첫 로딩 시간',4.97,2.21,5,'4.97초','2.21초','첫 화면 로딩에 소요된 시간 비교')]
        for x,title,before,after,maximum,v1,v2,caption in specs:
            self.rect(x,211,414,260,TINT)
            self.text(title,x+22,230,370,15,INK,True)
            for y,label,value,formatted,color in [(286,'개선 전',before,v1,'#9cacc4'),(351,'개선 후',after,v2,ACCENT)]:
                self.text(label,x+22,y-7,60,10,MUTED)
                self.rect(x+92,y,215,16,'#dce5f2',r=3)
                self.rect(x+92,y,max(3,215*value/maximum),16,color,r=3)
                self.text(formatted,x+321,y-9,73,13,INK,True)
            self.text(caption,x+22,422,370,10,MUTED)
        self.text('개선 방식: 1024px 묶음 타일, 확대 시 이미지 재사용, 지도 레벨 8 이상에서 WMS 요청 중단.',56,490,848,10,MUTED)
        self.text('발표자료에 제시된 측정 사례입니다. 요청 수와 시간은 각각의 단위·척도로 표시했으며 팀 성과로 소개합니다.',56,516,848,9,MUTED)

def make_safety_deck():
    d=SafetyDeck('neighborhood-safety-map.pdf','BACKEND / DATABASE / INFRASTRUCTURE','우리동네 안심지도','공공 생활안전 정보와 주민 관찰을 함께 살펴보는 지도 서비스.<br/>지역 비교와 관리자 기능에서 DB 설계·서버 구축·배포까지 연결했습니다.','두 지역 비교 · 관리자 기능 · DB 설계 · Node.js·Nginx 구축 · 배포·CI/CD','임형석 · 주효성 · 유정현',['같은 기준의 지역 비교','DB·서버 기반 구축','검토와 배포 자동화'])
    d.add('01 / CONTEXT & OWNERSHIP','생활안전 정보를 같은 기준으로 비교하기','동일 반경·축척의 지역 비교와 주민 안심노트를 하나의 지도에서 제공합니다.','table',T(['팀원','담당 기능과 역할'],[['임형석','메인 지도 · 회원가입/로그인 · 공통 레이아웃 · 디자인'],['주효성','두 지역 비교 · 관리자 기능 · DB 설계 · Node.js·Nginx 구축 · 배포·CI/CD'],['유정현','안심노트 작성·열람 · 이용 안내 · 노트 API · 공용 위치 처리']],weights=[1,4],rowheight=64,note='팀 우리 동네 지킴이 / 공공정보의 범위와 최근 현장정보의 한계를 주민 관찰로 함께 살펴보는 방향으로 기획했습니다.'))
    d.add('02 / OPERATING STRUCTURE','협업에서 운영까지, 전체 구조 한눈에','팀 도구 · GitHub · CI/CD · EC2 · 브라우저 · 사용자와 DB의 연결 관계를 함께 살펴봅니다.','operating_structure',{})
    d.add('02 / SYSTEM ARCHITECTURE','브라우저에서 서버와 DB까지 연결하기','React 화면과 지도 SDK, 서버의 외부 WMS 연동, MySQL을 연결한 운영 구조입니다.','flow',C(('브라우저 · 지도','React와 Kakao Maps JS에서 지도 탐색·두 지역 비교·안심노트를 제공합니다.'),('Nginx · Node.js','AWS EC2 환경의 Nginx와 Node.js·Express 서버를 구축했습니다. 생활안전지도 WMS는 Express 안에서 호출합니다.'),('MySQL · 데이터','사용자와 노트 데이터를 저장합니다. DB 설계와 서버 구축을 본인이 담당했습니다.'),note='React 화면 전체와 노트 API는 팀 역할표에 따라 나누어 개발했습니다. 아래 구조는 발표자료의 기술·연결 관계를 재구성한 개념도입니다.'))
    d.add('03 / DATABASE DESIGN','작성자와 안심노트를 1:N 관계로 설계','사용자 권한과 노트의 검토·공개 상태를 데이터 구조에 포함했습니다.','data_model',{})
    d.add('04 / DELIVERY PIPELINE','검사와 빌드를 거쳐 EC2에 전달하는 흐름','작업 브랜치와 PR 리뷰, GitHub Actions를 통한 CI/CD 구성을 소개합니다.','flow',C(('브랜치 · PR 리뷰','작업 브랜치에서 main 대상 PR을 만들고 리뷰를 반영한 뒤 병합합니다.'),('GitHub Actions','코드 검사, API·계산식 테스트, 배포 스크립트와 React 빌드를 수행합니다. CD에서는 빌드·패키징 및 Artifact 보관을 진행합니다.'),('EC2 배포','SSH/SCP로 결과물을 전달합니다. Node.js·Nginx 서버 기반과 배포·CI/CD 구성을 담당했습니다.'),note='원본 발표자료의 협업·운영 흐름을 기준으로 정리했습니다. 별도의 트래픽·가용성 수치는 제시하지 않습니다.'))
    d.add('05 / AREA COMPARISON','반경과 축척을 맞춰 두 지역을 비교하기','본인 담당 기능인 A/B 두 지역 비교의 실제 화면입니다.','screen',dict(page=7,heading='비교 기준을<br/>화면에서 통일',body='A/B 지점을 선택하고 같은 반경과 축척으로 살펴봅니다.<br/><br/>주소·장소 검색과 지도 위치를 연결해 지역별 정보를 비교할 수 있도록 구성했습니다.<br/><br/>화면의 유형별 점수와 수치는 가상 집계 기반 예시입니다. 실제 지역의 안전도를 나타내는 통계와 구분합니다.'))
    d.add('06 / ADMINISTRATION','검토 상태에 따라 공개 범위를 구분하기','본인이 담당한 관리자 기능과 안심노트의 검토·공개 상태를 정리했습니다.','table',T(['상태','의미와 공개 처리'],[['PENDING','안심노트 등록 후 검토 대기'],['APPROVED','승인된 노트 / 공개 목록과 공개 상세에서 제공'],['REJECTED','검토 후 거절된 노트'],['HIDDEN','숨김 처리된 노트']],weights=[1.5,4],rowheight=52,note='노트 작성·열람과 노트 API는 유정현 담당입니다. 관리자 기능 및 서버 기반은 본인 담당 범위로 구분했습니다.'))
    d.add('07 / TEAM USER EXPERIENCE','지도에서 관찰을 남기고 함께 살펴보기','주민 관찰을 위치와 연결한 팀의 안심노트 기능입니다.','screen_pair',dict(items=[('작성 / 관찰 내용과 위치 지정',8,0,'검색·지도 클릭으로 위치를 반영하고 PENDING으로 저장'),('열람 / 목록에서 상세 정보로',9,0,'동일 좌표의 노트를 묶어 현재 지도에서 목록·상세 열람')]))
    d.add('08 / PERFORMANCE','WMS 요청 구조를 바꾸어 로딩 개선','256px 타일별 호출과 순차 처리, 브라우저 캐시 제한으로 발생한 지연을 개선한 팀 사례입니다.','performance',{})
    d.add('09 / TROUBLESHOOTING','실제 데이터와 이벤트 흐름으로 원인 찾기','WMS 색상 처리와 마커 클릭 전파 문제를 해결한 팀의 사례입니다.','cards',C(('PIXEL CLASSIFICATION','실제 RGBA 값으로 분류 보완','문제: 대표 범례 색상과 원본 WMS 이미지의 실제 색상이 달라 미분류 픽셀이 발생했습니다.<br/><br/>개선: 실제 이미지에서 추출한 색상에 등급을 지정하고 유사 색상 판별 기준을 보완했습니다. 인접 등급의 오분류 방지와 미표시·미분류 구분에 중점을 뒀습니다.'),('MAP INTERACTION','마커 클릭이 지도에 전달되지 않게','문제: 안심노트 마커를 클릭할 때 지도 클릭으로도 전달되어 A 지점이 함께 이동했습니다.<br/><br/>개선: 마커의 clickable 옵션을 켜서 클릭 이벤트가 아래 지도로 전달되지 않도록 처리했습니다.'),note='개별 트러블슈팅 사례는 팀 발표자료의 결과입니다. 역할표에 없는 항목을 개인 단독 성과로 확대하지 않았습니다.'))
    d.add('10 / REVIEW & NEXT STEPS','AI의 제안을 실제 코드와 대조하며 검토하기','AI 도구 활용과 사람의 검토를 연결한 협업 방식, 이후 개선 방향을 담았습니다.','cards',C(('AI-ASSISTED REVIEW','리뷰를 검증과 수정으로 연결','Claude·ChatGPT로 PR 생성·등록을 지원하고 CodeRabbit으로 변경 코드를 리뷰했습니다.<br/><br/>리뷰 제안은 실제 코드 대조 → 반영 필요성 판단 → 승인 → 수정·검증의 흐름으로 다뤘습니다.'),('NEXT ITERATION','서비스 경험과 운영 기능 보완','향후 개선안:<br/>1. 안심노트 등록에 따른 칭호 부여<br/>2. 계산식의 절대적·직관적 기준치 적용<br/>3. 관리자 기능에 사용자 제재 추가<br/><br/>위 항목은 완료 기능이 아닌 개선 방향입니다.'),note='팀 회고: API의 실제 응답 데이터 확인, 초반 설계와 사람의 검수 중요성, AI 도구와 협업하며 개발한 경험을 남겼습니다.'))
    d.pages=[(f"{i:02d} / "+entry[0].split(' / ',1)[1],*entry[1:]) for i,entry in enumerate(d.pages,1)]
    return d

if __name__=='__main__':
    make_safety_deck().build()
