-->=1.2.50
alter table tVeranst add column `cal_uid` varchar(36) DEFAULT NULL COMMENT 'Calendar-UUID' after `Sortier`;
-->=1.2.54
insert _Config(item,value) values('add-new-calevent',1);
-->=1.2.71
EXC:mysqldumpdata_bv_no_20260501125409.sql
-->=1.2.80
alter table tBerater add column (`username` varchar(20) DEFAULT NULL COMMENT 'Login Benutzername', `password` varchar(50) DEFAULT NULL COMMENT 'Login Passwort');
-->=1.2.81
alter table tBerater add column (`authMods` varchar(255) DEFAULT NULL COMMENT 'Berechtigungen für Module');
alter table tBerater modify column `password` varchar(255);
alter table _Config modify column `value` varchar(255);
insert into _Config(item,value) values('used-modules','[["01",["Veranstaltungen",1]],["02",["Besucher",1]],["03",["Berater",0]],["05",["Veranstaltungsthemen",1]],["06",["Veranstaltungsarten",0]],["07",["Veranstaltungsorte",0]]]');
alter table tBerater add column (`passChange` bit(1) DEFAULT 0 COMMENT 'Soll das Passwort neu eingegeben werden=1');
