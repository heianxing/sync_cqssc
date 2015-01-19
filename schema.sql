create database if not exists HAOMA;
use HAOMA;

drop table if exists haoma;
create table haoma
(
    item_date char(8) not null,
    period char(3) not null,
    date_period char(11) not null,
    lottery_number char(5) not null,
    a char(1) not null,
    b char(1) not null,
    c char(1) not null,
    d char(1) not null,
    e char(1) not null,
    rsv1 int,
    UNIQUE(date_period),
    CONSTRAINT period_num PRIMARY KEY(item_date, period)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
