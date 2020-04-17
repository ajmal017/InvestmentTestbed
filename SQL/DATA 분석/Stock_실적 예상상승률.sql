SELECT d.country AS country, d.nm AS nm, c.pid AS pid, c.date AS release_date
	  , round(c.revenue_fore) AS revenue_fore
	  , round(c.eps_fore) AS eps_fore
	  , c.p_date AS release_date_prev
     , round(c.revenue_prev) AS revenue_prev
	  , round(c.eps_prev) AS eps_prev
     , c.chg_revenue_fore*100 AS 'chg_revenue_fore(%)'
	  , c.chg_eps_fore*100 AS 'chg_eps_fore(%)'
	  , round(f.close/e.close-1, 4)*100 AS 'down(%)'
	  , round(g.close/f.close-1, 4)*100 AS 'up(%)'	  
	  , d.url
 FROM (SELECT a.pid AS pid, a.date AS date
 				, a.revenue_fore AS revenue_fore, a.eps_fore AS eps_fore
 				, @p_revenue_bold AS revenue_prev, @p_eps_bold AS eps_prev
            , (CASE @p_pid WHEN a.pid THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) num
            , (CASE @p_pid WHEN a.pid THEN @p_date ELSE @p_date:='' END) p_date
            , (CASE @p_pid WHEN a.pid THEN
            										 CASE WHEN (@p_revenue_bold > 0) THEN ROUND(a.revenue_fore/@p_revenue_bold-1, 2) 
            										      WHEN (@p_revenue_bold < 0) THEN ROUND(a.revenue_fore/@p_revenue_bold-1, 2) * -1
               									  END 
								              ELSE 0 
				   END
				  ) chg_revenue_fore
            , (CASE @p_pid WHEN a.pid THEN 
            										 CASE WHEN (@p_eps_bold > 0) THEN round(a.eps_fore/@p_eps_bold-1, 2) 
            										      WHEN (@p_eps_bold < 0) THEN ROUND(a.eps_fore/@p_eps_bold-1, 2) * -1
               									  END 
								              ELSE 0 
					END
				  ) chg_eps_fore
            , (@p_pid:=a.pid), (@p_date:=a.date)
				, (@p_revenue_bold:= a.revenue_bold), (@p_revenue_fore:= a.revenue_fore)
				, (@p_eps_bold:= a.eps_bold), (@p_eps_fore:= a.eps_fore)
         FROM stock_earnings a, (SELECT @p_pid:='', @p_date:='', @p_eps_bold:=0, @p_eps_fore:=0, @p_revenue_bold:=0, @p_revenue_fore:=0, @rownum:=0 FROM DUAL) b
        ORDER BY a.pid, a.date) c, stock_master d, stock_price e, stock_price f, stock_price g
WHERE c.pid = d.pid
  AND d.country = 'KR'
  AND c.eps_fore IS NOT NULL 
  AND c.date > '2020-04-01'
  AND c.pid = e.pid
  AND c.pid = f.pid
  AND c.pid = g.pid
  AND e.date = '2020-02-20'
  AND f.date = '2020-03-19'
  AND g.date = '2020-04-14'
ORDER BY chg_revenue_fore DESC 