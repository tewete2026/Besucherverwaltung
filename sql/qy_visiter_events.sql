select IFNULL(b.id,'--') as Nr,IFNULL(c.Bezeichnung,'--') as Bezeichnung,IFNULL(YEAR(b.Datum),0) as Jahr,IFNULL(MONTH(b.Datum),0) as Monat,IFNULL(DAY(b.Datum),0) as Tag,IFNULL(b.Von,'--') as Von,IFNULL(b.Bis,'--') as Bis,IFNULL(b.Dauer,'--') as Dauer,IFNULL(e.Nachname,'--') as Nachname,IFNULL(e.Vorname,'--') as Vorname,IF(e.Newsletter=1,1,0) as Newsl,IFNULL(DATE_FORMAT(DATE(e.AufnDatum),'%d.%m.%Y'),'--') as AufnDatum,IFNULL(DATE_FORMAT(DATE(e.LetztDatum),'%d.%m.%Y'),'--') as LetztBesuch,IFNULL(e.Telefon,'--') as Telefon,IFNULL(e.EMail,'--') as EMail,IF(e.Aktiv=1,1,0) as Aktiv
    from tBesuche a
    left join tVeranst b     on b.id=a.VeranstID
    left join tVeranstTyp c  on c.id=b.Typ
    left join tBesucher e    on e.id=a.BesucherID
    order by c.Bezeichnung,Jahr desc,Monat desc,Tag desc,e.Nachname,e.Vorname;       