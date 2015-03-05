create database if not exists CAIPIAO;
use CAIPIAO;

drop table if exists haoma;
create table haoma
(
    item_date char(8) not null,
    period char(3) not null,
    date_period char(11) not null,
    -- lottery_number char(5) not null,
    abcde char(5) not null,
    a char(1) not null,
    b char(1) not null,
    c char(1) not null,
    d char(1) not null,
    e char(1) not null,
    ab char(2),
    ac char(2),
    ad char(2),
    ae char(2),
    bc char(2),
    bd char(2),
    be char(2),
    cd char(2),
    ce char(2),
    de char(2),
    rsv1 int,
    UNIQUE(date_period),
    CONSTRAINT period_num PRIMARY KEY(item_date, period)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

drop table if exists prefer_number;
create table prefer_number
(
    item_date char(8) not null,
    period char(3) not null,
    date_period char(11) not null,
    created_time char(20) not null,
    updated_time char(20) not null,
    prefer_type varchar(8),
    lottery_number char(5) default 'abcde',
    stat char(4) default 'WAIT',
    num_count tinyint,
    dans varchar(512),
    UNIQUE(date_period),
    CONSTRAINT period_dan PRIMARY KEY(item_date, period, prefer_type)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
