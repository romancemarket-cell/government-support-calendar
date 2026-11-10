import os, json, re, urllib.parse, urllib.request, datetime, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'programs.json'
TODAY=datetime.date.today()
EXCLUDE=re.compile(r'대출|융자|보증서|금리우대')

def get_json(url, params):
    req=url+'?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read()
    try:return json.loads(raw.decode('utf-8-sig'))
    except Exception:
        import xml.etree.ElementTree as ET
        root=ET.fromstring(raw); return xml_to_dict(root)

def xml_to_dict(el):
    d={}
    for c in el:
        v=xml_to_dict(c) if list(c) else (c.text or '').strip()
        if c.tag in d:
            if not isinstance(d[c.tag],list):d[c.tag]=[d[c.tag]]
            d[c.tag].append(v)
        else:d[c.tag]=v
    return d

def find_records(obj):
    if isinstance(obj,list):
        if obj and all(isinstance(x,dict) for x in obj):return obj
        for x in obj:
            r=find_records(x)
            if r:return r
    elif isinstance(obj,dict):
        for k,v in obj.items():
            if k.lower() in ('item','items','list','resultlist','bizinfolist','supportlist'):
                if isinstance(v,list):return v
                if isinstance(v,dict):
                    r=find_records(v)
                    if r:return r
        for v in obj.values():
            r=find_records(v)
            if r:return r
    return []

def pick(d,*keys):
    low={str(k).lower():v for k,v in d.items()}
    for k in keys:
        if k.lower() in low and low[k.lower()] not in (None,''):return str(low[k.lower()]).strip()
    return ''

def date_norm(s):
    if not s:return ''
    s=str(s).strip()
    m=re.search(r'(20\d{2})[-./년 ]?(\d{1,2})[-./월 ]?(\d{1,2})',s)
    if not m:return ''
    try:return datetime.date(int(m.group(1)),int(m.group(2)),int(m.group(3))).isoformat()
    except:return ''

def normalize(d,source):
    title=pick(d,'pblancNm','pbanc_nm','title','biz_pbanc_nm','bizPbancNm','사업명','공고명','공고제목','pblanc_name')
    if not title:return None
    blob=' '.join(str(v) for v in d.values() if isinstance(v,(str,int,float)))
    if EXCLUDE.search(title+' '+blob):return None
    start=date_norm(pick(d,'reqstBeginDe','pbanc_rcpt_bgng_dt','startDate','beginDate','접수시작일','신청시작일','reqstBeginDe'))
    end=date_norm(pick(d,'reqstEndDe','pbanc_rcpt_end_dt','endDate','closeDate','접수마감일','신청마감일','reqstEndDe'))
    url=pick(d,'pblancUrl','detailUrl','url','dtl_url','biz_pbanc_url','공고URL','상세URL','link')
    if url and url.startswith('//'):url='https:'+url
    if url and url.startswith('/'):url='https://www.bizinfo.go.kr'+url
    target=pick(d,'trgetNm','aply_trgt_ctnt','target','targetName','지원대상','신청대상')
    summary=pick(d,'bsnsSumryCn','biz_supt_ctnt','summary','content','사업내용','지원내용','suptCn')
    region=pick(d,'areaNm','supt_regin','region','지역','지역명') or '전국/지역 확인 필요'
    category=pick(d,'pldirSportRealmLclasCodeNm','supt_biz_clsfc','category','분야','지원분야') or '정부지원사업'
    if not end:return None
    return {'id':pick(d,'pblancId','pbanc_sn','id','사업공고번호') or re.sub(r'\W','',title)[:60], 'title':title,'category':category,'region':region,'target':target,'summary':summary[:700],'start_date':start,'end_date':end,'url':url,'source':source}

def bizinfo():
    key=os.getenv('BIZINFO_API_KEY','').strip()
    if not key:return []
    data=get_json('https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do',{'crtfcKey':key,'dataType':'json','searchCnt':'100'})
    print("API 응답 데이터:", data) 
    return [x for x in (normalize(d,'기업마당') for d in find_records(data)) if x]

def main():
    all_items=[]; errors=[]
    try:all_items+=bizinfo()
    except Exception as e:errors.append('기업마당: '+str(e))
    # Optional public-data K-Startup API adapter is intentionally not enabled until its exact service key/schema is configured.
    # No sample or fabricated records are inserted.
    uniq={}
    for p in all_items:
        uniq[p['id']] = p
    items=sorted(uniq.values(),key=lambda x:x['end_date'])
    payload={'updated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='minutes'),'count':len(items),'items':items,'sources':['기업마당 지원사업정보 API'],'errors':errors}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"saved {len(items)} programs; errors={errors}")
    if errors: print('\n'.join(errors))
if __name__=='__main__':main()
