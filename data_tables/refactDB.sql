-->=1.2.50
alter table tVeranst add column `cal_uid` varchar(36) DEFAULT NULL COMMENT 'Calendar-UUID' after `Sortier`;
-->=1.2.54
insert _Config(item,value) values('add-new-calevent',1);
-->=1.2.71
EXC:mysqldumpdata_bv_no_20260501125409.sql
