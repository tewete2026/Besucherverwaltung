with t1 as (select a.id as Nr,a.Typ,IFNULL(b.Bezeichnung,'--') as Bezeichnung,YEAR(a.Datum) as year,MONTH(a.Datum) as month,DAY(a.Datum) as day,a.Spenden
        from tVeranst a
        left join tVeranstTyp b on b.id=a.Typ)
    select Bezeichnung,year as Jahr,month as Monat,count(Nr) as Anzahl_Veranst,FORMAT(SUM(Spenden),2,'de_DE') as Spenden 
        from t1 
        group by Typ,year,month 
        order by Bezeichnung,year desc,month desc;
