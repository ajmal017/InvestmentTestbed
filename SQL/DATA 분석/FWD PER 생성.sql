
with t_earnings as (
select a.pid as pid
     , a.date as date
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
	  , a.eps_fore / b.close as fwd_per
	  , a.eps_fore / b.close - d.close/100 as fed_model
  from t_earnings a
     , stock_price b
	  , stock_master c
	  , index_price d
	  , index_master e
 where a.pid = b.pid
   and a.pid = c.pid
   and b.date = '2020-05-27'
   and a.date > b.date
   and a.p_date <= b.date
	and e.nm_us = 'US 10Y Rate'
	and e.cd = d.idx_cd
	and b.date = d.date
	and a.eps_fore / b.close - d.close/100 > 0
 order by a.eps_fore / b.close - d.close/100 desc
	