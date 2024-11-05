DELIMITER $$
CREATE DEFINER=`u9svdbjunzg4tgvy`@`%` PROCEDURE `prc_insert_calendario`(IN `anio_d` INT, IN `anio_h` INT)
WHILE anio_d <= anio_h DO
INSERT INTO fechas (fecha, dia, mes, anio)
with recursive cte as (
-- customize start date here
select date(concat(anio_d, '-01-01')) as calendar_date
union all
select date_add(calendar_date, interval 1 day) as calendar_date from cte 
-- customize end date here
where year(date_add(calendar_date, interval 1 day)) <= anio_d
)
select
calendar_date,
day(calendar_date),
month(calendar_date),
year(calendar_date)
from cte;
set anio_d := anio_d+1;
END WHILE$$
DELIMITER ;