with
    t1 as (select vorname,nachname,count(*) as anzahl from tBesucher group by vorname,nachname having count(*)>1),
    t2 as (select vorname,nachname,telefon,count(*) as anzahl from tBesucher group by vorname,nachname,telefon having count(*)>1),
    t3 as (select vorname,nachname,email,count(*) as anzahl from tBesucher group by vorname,nachname,email having count(*)>1),
    t4 as (select vorname,nachname,telefon,email,count(*) as anzahl from tBesucher group by vorname,nachname,telefon,email having count(*)>1)
select IFNULL(IF(t2.anzahl>1,'*',''),'-') as v_n_t,IFNULL(IF(t3.anzahl>1,'*',''),'-') as v_n_e,IFNULL(IF(t4.anzahl>1,'*',''),'--') as v_n_t_e,id,KundenNr,IFNULL(AnredeBezeichnung,'--') as Anrede,t.Nachname,t.Vorname,IFNULL(t.Telefon,'--') as Telefon,IFNULL(t.EMail,'--') as EMail,IF(Aktiv=1,1,0) as Aktiv,DATE_FORMAT(DATE(AufnDatum),'%d.%m.%Y') as AufnDatum,IFNULL(DATE_FORMAT(DATE(LetztDatum),'%d.%m.%Y'),'--') as LetztBesuch
    from tBesucher t join t1 on CONCAT(t.vorname,t.nachname)=CONCAT(t1.vorname,t1.nachname) 
    left join t2 on CONCAT(t2.vorname,t2.nachname)=CONCAT(t1.vorname,t1.nachname) 
    left join t3 on CONCAT(t3.vorname,t3.nachname)=CONCAT(t1.vorname,t1.nachname) 
    left join t4 on CONCAT(t4.vorname,t4.nachname)=CONCAT(t1.vorname,t1.nachname) 
    left join tAnrede an on an.AnredeID=t.Anrede
    order by t.nachname,t.vorname;
