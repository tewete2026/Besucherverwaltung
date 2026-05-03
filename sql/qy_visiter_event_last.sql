with t1 as (select a.BesucherID, count(b.id) as anzahl
                from tBesuche a
                left join tVeranst b on b.id=a.VeranstID
                left join tBesucher c on c.id=a.BesucherID
                group by a.BesucherID),
    t2 as (select a.BesucherID, max(b.Datum) as Letztes_Datum
                from tBesuche a
                left join tVeranst b on b.id=a.VeranstID
                left join tBesucher c on c.id=a.BesucherID
                group by a.BesucherID)
    select t3.id,IFNULL(t3.KundenNr,'--') as KundenNr, IFNULL(t3.Nachname,'--') as Nachname, IFNULL(IF(t3.Vorname=' ','--',t3.Vorname),'--') as Vorname, IFNULL(t1.anzahl,'--') as Anzahl_Besuche, IFNULL(DATE_FORMAT(DATE(t3.AufnDatum),'%d.%m.%Y'),'--') as Aufnahme_Datum, IFNULL(DATE_FORMAT(DATE(t2.Letztes_Datum),'%d.%m.%Y'),'--') as Letzter_Besuch, IFNULL(t3.Telefon,'--') as Telefon, IFNULL(t3.EMail,'--') as EMail
        from tBesucher t3
        left join t1 on t3.id=t1.BesucherID
        left join t2 on t2.BesucherID=t1.BesucherID
        order by t3.Nachname,t3.Vorname,t2.Letztes_Datum;
