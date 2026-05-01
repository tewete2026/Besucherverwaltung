with t1 as (select a.BesucherID, count(b.id) as anzahl
                from tBesuche a
                join tVeranst b on b.id=a.VeranstID
                join tBesucher c on c.id=a.BesucherID
                group by a.BesucherID),
    t2 as (select a.BesucherID, IFNULL(max(b.Datum),'0000-00-00 00:00:00') as Letztes_Datum
                from tBesuche a
                join tVeranst b on b.id=a.VeranstID
                join tBesucher c on c.id=a.BesucherID
                group by a.BesucherID)
    select t3.KundenNr, t3.Nachname, IF(t3.Vorname=' ','--',t3.Vorname) as Vorname, t1.anzahl as Anzahl_Besuche, DATE_FORMAT(DATE(t2.Letztes_Datum),'%d.%m.%Y') as Letzter_Besuch, IFNULL(t3.Telefon,'--') as Telefon, IFNULL(t3.EMail,'--') as EMail
        from t1
        join t2 on t2.BesucherID=t1.BesucherID
        join tBesucher t3 on t3.id=t1.BesucherID
        order by t3.Nachname,t3.Vorname,t2.Letztes_Datum;
