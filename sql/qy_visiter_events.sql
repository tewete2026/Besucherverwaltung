select b.id as Nr,c.Bezeichnung,YEAR(b.Datum) as Jahr,MONTH(b.Datum) as Monat,DAY(b.Datum) as Tag,b.Von,b.Bis,b.Dauer,b.Spenden,e.Nachname,e.Vorname,IF(e.Newsletter=1,1,0) as Newsl,DATE_FORMAT(DATE(e.AufnDatum),'%d.%m.%Y') as AufnDatum,DATE_FORMAT(DATE(e.LetztDatum),'%d.%m.%Y') as LetztBesuch,IFNULL(e.Telefon,'--') as Telefon,IFNULL(e.EMail,'--') as EMail,IF(e.Aktiv=1,1,0) as Aktiv
    from tBesuche a
    join tVeranst b     on b.id=a.VeranstID
    join tVeranstTyp c  on c.id=b.Typ
    join tBesucher e    on e.id=a.BesucherID
    order by c.Bezeichnung,Jahr desc,Monat desc,Tag desc,e.Nachname,e.Vorname;       