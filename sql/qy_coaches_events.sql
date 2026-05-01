select b.id as Nr,c.Bezeichnung,YEAR(b.Datum) as Jahr,MONTH(b.Datum) as Monat,DAY(b.Datum) as Tag,b.Von,b.Bis,b.Dauer,b.Spenden,e.Vorname,e.Nachname,IFNULL(e.Telefon,'--') as Telefon,IFNULL(e.Mobil,'--') as Mobil,IFNULL(e.EMail,'--') as EMail,IF(e.Aktiv=1,1,0) as Aktiv
    from tBeraterVer a
    join tVeranst b     on b.id=a.VeranstID
    join tVeranstTyp c  on c.id=b.Typ
    join tBerater e     on e.id=a.BeraterID
    order by c.Bezeichnung,Jahr desc,Monat desc,Tag desc,e.Nachname,e.Vorname;
