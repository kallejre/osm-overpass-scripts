import requests
import concurrent.futures
from multiprocessing.pool import ThreadPool
import time,datetime, csv, random
op_template='''
[out:csv(cnt1,cnt2;false;",")]#DATE[timeout:3600];
area(id:#AREA);
wr[#TAG1](area)->.t1;
wr[#TAG2](area)->.t2;
make stat
  cnt1=t1.count(ways)+t1.count(relations),
  cnt2=t2.count(ways)+t2.count(relations);
out;'''
url='http://127.0.0.1/api/interpreter'
s=requests.Session()
def log(*args):
    msg=f"{datetime.datetime.now().time().isoformat()[:8]} "+' '.join(list(map(str, args)))
    print(msg)
    try:
        with open('log.txt', 'a', encoding='utf8') as f:
            print(msg, file=f)
    except Exception:
        log("Error logging previous message")
def get_query(rel_id,t1,t2,date=None):
    if date:
        date=date.strftime("[date:\"%FT%H:00:00Z\"]")
    else:date=''
    # Clean up tags:
    t1='"'+t1.strip('"').replace('"=','=').replace('="','=').replace('=','"="')+'"'
    t2='"'+t2.strip('"').replace('"=','=').replace('="','=').replace('=','"="')+'"'
    return op_template.replace('#AREA',str(int(rel_id)+3600000000)).replace('#TAG1',t1).replace('#TAG2',t2).replace('#DATE',date)
def run_query(query, area_name="", date=""):
    strt=time.time()
    log(f"Starting for {area_name} on {date}.")
    resp=s.post(url,data=query, timeout=3630)
    if resp.status_code>=400:
        msg=resp.content.decode()
        print(msg[msg.find('<body')+6:msg.find('</body')].strip())
    resp.raise_for_status()
    log(f"Request for {area_name} on {date} took {round(time.time()-strt,1)}s")
    return resp.text
def check_if_already_done(filename, data_row):
    try:
        with open(filename, 'r', encoding='utf8') as f:
            t=f.read()
    except FileNotFoundError:
        return False
    return '\n'+data_row[1]+',' in t or t.startswith(data_row[1]+',')
def run_single_request(data_row,t1,t2,filename,date=None):
    # data row = [51701,CH,Switzerland]
    area_name=','.join(data_row[1:])
    rel_id=data_row[0]
    #print('Worker started for '+' '.join(list(map(str,data_row))))
    try:
        q=get_query(rel_id,t1,t2,date)
    except requests.HTTPError as err:
        log(f"ERROR: {err} with args {t1}, {t2}, {date.strftime('%F')}, {area_name}")
        return
    if check_if_already_done(filename, data_row):
        #print(f"{datetime.datetime.now().time().isoformat()[:8]} Request for {area_name} was already completed.")
        return
    txt=run_query(q,area_name, str(date)[:10]).strip().split(',')
    # Respone has newline at end
    with open(filename,mode='a',buffering=256, newline='', encoding='utf8') as f:
        writer=csv.writer(f)
        writer.writerow(data_row[1:]+txt)
def prepare_inputs(tag1, tag2, datafile, date_start, date_end, date_step, fname_template):
    """Given tags and date range, generte requests to be processed.

    Parameters:
    datafile (str): Name of a file that contains output of all_country_names_ids
    date_start (datetime.datetime): Start of date range
    date_end (datetime.datetime): End of date range
    date_step (datetime.timedelta): Step between two dates
    fname_template (str): Output filename for CSV. MUST contain phrase #DATE, which will be replaced with actual iso date.

    Returns:
    list:List suitable to be handed to run_single_request as argument
    
    """
    # Quick basic tests to verify argument types
    assert '#DATE' in fname_template
    assert date_start-date_step < date_end
    date_start=datetime.datetime.combine(date_start.date(), datetime.datetime.min.time())
    c=0
    total=(date_end-date_start).days//date_step.days+1
    while date_start < date_end:
        c+=1
        fname = fname_template.replace("#DATE",date_start.strftime("%F"))
        log(f"Date {c} of {total}")
        def generator_day():
            with open(datafile, encoding='utf8') as f:
                file=csv.reader(f)
                for row in file:
                    yield (row, tag1,tag2,fname, date_start)
        yield generator_day
        date_start+=date_step

def prepare_inputs_2(tag1, tag2, datafile, date_start, date_end, date_step, fname_template):
    """
    Alternative generator generator iterates over countries
    instead of dates to give more uniform time consumption.
    """
    # Quick basic tests to verify argument types
    assert '#DATE' in fname_template
    assert date_start-date_step < date_end
    with open(datafile, encoding='utf8') as f:
        file=csv.reader(f)
        for row in file:
            log(f"Processing {row[2]}")
            def generator_country():
                date_strt=datetime.datetime.combine(date_start.date(), datetime.datetime.min.time())
                while date_strt < date_end:
                    fname = fname_template.replace("#DATE",date_strt.strftime("%F"))
                    yield (row, tag1,tag2,fname, date_strt)
                    date_strt+=date_step
            yield generator_country

def rsr_wrap(args):
    #print('Started for '+str(args))
    time.sleep(round(random.random()/3,2))
    try:
        run_single_request(*args)
    except Exception as err:print(err)

def perform_web_requests(inputs_generator, pool_size):
    pool=ThreadPool(pool_size)
    pool.imap(rsr_wrap, inputs_generator())
    log(f"Waiting for requests to complete.")
    pool.close()
    pool.join()
log("Process started")
inputs=prepare_inputs_2('waterway=riverbank', 'water=river',
               'sample list of countries.txt',
               datetime.datetime(2020,12,1),
               datetime.datetime(2021,12,16),
               datetime.timedelta(7),
               r'history\tags-#DATE.csv')
for days_requests in inputs:
    perform_web_requests(days_requests, 3)
    # Ideally it should wait to complete with day before moving on.
log("Process finished successfully")
#rsr_wrap(list(inputs)[0])
