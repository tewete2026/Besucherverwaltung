with t1 as (select a.id as Nr,a.Typ,a.Thema as ThemeNr,IFNULL(b.Bezeichnung,'--') as Bezeichnung,IFNULL(c.Thema,'--') as Thema,YEAR(a.Datum) as year,MONTH(a.Datum) as month,DAY(a.Datum) as day,a.Spenden
        from tVeranst a
        left join tVeranstTyp b on b.id=a.Typ
        left join tThemen c on c.id=a.Thema)
    select Bezeichnung,Thema,year as Jahr,month as Monat,count(Nr) as Anzahl_Veranst,FORMAT(SUM(Spenden),2,'de_DE') as Spenden 
        from t1 
        group by Typ,ThemeNr,year,month 
        order by Bezeichnung,Thema,year desc,month desc;
