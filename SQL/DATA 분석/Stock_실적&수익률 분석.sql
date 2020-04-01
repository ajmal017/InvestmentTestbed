WITH tmp AS (
	SELECT a.pid AS pid
	     , a.nm AS nm
		  , a.country AS country
	     , a.industry AS industry
		  , a.sector AS sector
	     , b.date AS date
	     , ROUND(b.eps_bold/b.eps_fore,2) AS eps_performance
	     , ROUND(b.revenue_bold/b.revenue_fore,2) AS revenue_performance
	     , ROUND(c.open/e.close,2) AS pre_move
		  , ROUND(d.close/c.open-1,4)*100 AS profit
		  , SUBSTR(b.date, 1, 4) AS year
	  FROM stock_master a
	     , stock_earnings b
	     , stock_price c
		  , stock_price d
		  , stock_price e		  
	 WHERE a.pid = b.pid
	   AND b.date > '2019-01-01'
	   AND b.eps_bold/b.eps_fore IS NOT NULL
	   AND b.revenue_bold/b.revenue_fore IS NOT NULL
	   AND c.pid = b.pid
	   AND c.date = DATE_FORMAT(DATE_ADD(STR_TO_DATE(b.date, '%Y-%m-%d'), INTERVAL 1 DAY), '%Y-%m-%d')
	   AND d.pid = b.pid
	   AND d.date = DATE_FORMAT(DATE_ADD(STR_TO_DATE(b.date, '%Y-%m-%d'), INTERVAL 10 DAY), '%Y-%m-%d')
	   AND e.pid = b.pid
	   AND e.date = DATE_FORMAT(DATE_ADD(STR_TO_DATE(b.date, '%Y-%m-%d'), INTERVAL -90 DAY), '%Y-%m-%d')
	   AND d.close/c.open > 1.1
	 ORDER BY d.close/c.open DESC
)
SELECT *
  FROM tmp
