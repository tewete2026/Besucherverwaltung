import mariadb
from datetime import datetime
from datetime import timedelta

def getTS(config):
    period = int(config["wait-for-unlock-record"])
    ts = datetime.now() + timedelta(minutes=period)
    return ts.strftime("%Y%m%d%H%M%S%f")

def getParmMap(request):
    req_data_map = {}
    req_data = request.get_data(as_text=True)
    for parms in req_data.split("&"):
        key, value = parms.split("=")
        req_data_map.update({key:value})
    return req_data_map
    
def setVisiterWL(cur, veranst_list=[], force=False):
    rc_code = "OK"
    try:
        row_count = 0
        for VeranstID in veranst_list:
            if not isinstance(VeranstID, tuple):
                VeranstID = (VeranstID,)
            if VeranstID[0] is None:
                continue
            cur.execute("SELECT a.id,IFNULL(b.MaxBesucher,-1) as MaxBes FROM tVeranst a left join tOrte b on b.id=a.Ort WHERE a.id=?", VeranstID)
            veranst = cur.fetchone()
            if veranst is None:
                continue
            max_Bes = veranst["MaxBes"]
            if max_Bes != -1:
                cur.execute("select id,VeranstID,IF(BesucherWL=true,true,false) as BesucherWL from tBesuche where VeranstID=? order by id", VeranstID)
                pos = 0
                result_list = []
                while True:
                    row = cur.next()
                    if row is None: break
                    pos += 1
                    wl = False
                    if pos > max_Bes:
                        wl = True
                    print("setVisiterWL", row, wl)
                    if wl != row["BesucherWL"] or force:
                        row["BesucherWL"] = wl
                        result_list.append(row)
                if len(result_list) > 0:
                    for row in result_list:
                        if not force:
                            cur.execute("insert into tBesucheLOG(Action,BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL) \
                                        select 'change-wl-by-setvisiterwl',BesucherID,VeranstID,ThemenID,GeraeteID,Spende,TagInt,Monat,Jahr,EMail,BesucherWL from tBesuche where id=?", (row["id"],))
                        cur.execute("UPDATE tBesuche set BesucherWL=? where id=?", (row["BesucherWL"], row["id"]))
                        row_count += cur.rowcount
        rc_code += ", Anzahl Updates=" + str(row_count)
    except mariadb.Error as err:
        rc_code = err.msg
    
    return rc_code
