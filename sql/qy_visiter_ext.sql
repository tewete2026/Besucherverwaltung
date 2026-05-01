with t1 as (select a.BesucherID,b.Typ,YEAR(b.Datum) as year,MONTH(b.Datum) as month,DAY(b.Datum) as day
        from tBesuche a
        join tVeranst b on b.id=a.VeranstID where b.Typ>2)
    select tVeranstTyp.Bezeichnung,year as Jahr,month as Monat,count(BesucherID) as Besucher from t1 
        join tVeranstTyp on tVeranstTyp.id=t1.Typ
        group by t1.Typ,year,month order by tVeranstTyp.Bezeichnung,year desc,month desc;
