with t1 as (select a.BesucherID,IFNULL(YEAR(b.Datum),0) as year,IFNULL(MONTH(b.Datum),0) as month,IFNULL(DAY(b.Datum),0) as day
        from tBesuche a
        left join tVeranst b on b.id=a.VeranstID)
    select year as Jahr,month as Monat,count(BesucherID) as Besucher
        from t1 
        group by year,month 
        order by year desc,month desc;
