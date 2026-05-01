with t1 as (select a.BesucherID,b.Thema
        from tBesuche a
        join tVeranst b on b.id=a.VeranstID where b.Typ=2),
    t2 as (select count(t1.BesucherID) anzahl,t1.Thema from t1 
        group by t1.Thema)
    select t2.anzahl as Anzahl,tThemen.Thema from t2
        join tThemen on tThemen.id=t2.Thema
        order by tThemen.Thema;
