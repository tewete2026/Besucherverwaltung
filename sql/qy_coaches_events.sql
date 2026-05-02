select IFNULL(b.id,'--') as Nr,IFNULL(c.Bezeichnung,'--') as Bezeichnung,IFNULL(YEAR(b.Datum),0) as Jahr,IFNULL(MONTH(b.Datum),0) as Monat,IFNULL(DAY(b.Datum),0) as Tag,IFNULL(b.Von,'--') as Von,IFNULL(b.Bis,'--') as Bis,IFNULL(b.Dauer,'--') as Dauer,IFNULL(e.Vorname,'--') as Vorname,IFNULL(e.Nachname,'--') as Nachname,IFNULL(e.Telefon,'--') as Telefon,IFNULL(e.Mobil,'--') as Mobil,IFNULL(e.EMail,'--') as EMail,IF(e.Aktiv=1,1,0) as Aktiv
    from tBeraterVer a
    left join tVeranst b     on b.id=a.VeranstID
    left join tVeranstTyp c  on c.id=b.Typ
    left join tBerater e     on e.id=a.BeraterID
    order by c.Bezeichnung,Jahr desc,Monat desc,Tag desc,e.Nachname,e.Vorname;
