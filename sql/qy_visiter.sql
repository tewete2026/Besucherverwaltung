with t1 as (select a.BesucherID,YEAR(b.Datum) as year,MONTH(b.Datum) as month,DAY(b.Datum) as day,b.Spenden
        from tBesuche a
        join tVeranst b on b.id=a.VeranstID)
    select year as Jahr,month as Monat,count(BesucherID) as Besucher,FORMAT(SUM(Spenden),2,'de_DE') as Spenden from t1 group by year,month order by year desc,month desc;
