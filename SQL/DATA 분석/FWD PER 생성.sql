
with t_earnings as (
select a.pid as pid
     , a.date as n_date
     , (CASE @p_pid WHEN a.pid THEN @p_date ELSE @p_date:='' END) as p_date
     , a.eps_fore as eps_fore
     , a.eps_bold as eps_bold
     , a.revenue_fore as revenue_fore
     , a.revenue_bold as revenue_bold
     , (@p_pid:=a.pid)
	  , (@p_date:=a.date)
from stock_earnings a, (select @p_pid:='', @p_date:='' from dual) b
-- where a.pid = '100160'
)
select a.pid
     , c.nm
     , c.market
	  , c.industry
     , c.sector
--   , a.p_date
--	  , a.n_date
	  , b.date
	  , b.close
	  , a.eps_fore
	  , a.eps_fore / b.close
  from t_earnings a, stock_price b, stock_master c
 where a.pid = b.pid
   and a.pid = c.pid
   and a.n_date > b.date
   and a.p_date <= b.date