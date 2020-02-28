SELECT c.nm, c.country, c.industry, c.sector, c.pid
     , ROUND((a.close/b.close-1)/@term*100,2) AS profit
     , round(d.avg_yield*100,2) AS avg_yield
     , c.url
  FROM stock_price a, stock_price b, stock_master c
     , (SELECT pid, AVG(yield) AS avg_yield FROM stock_dividends GROUP BY pid) d
     , (SELECT @today:='2020-02-24', @term:=3 FROM DUAL) e
 WHERE a.pid = b.pid
   AND a.pid = c.pid
   AND a.pid = d.pid
   AND a.date = @today
   AND b.date = DATE_FORMAT(DATE_ADD(STR_TO_DATE(@today, '%Y-%m-%d'), INTERVAL -365*@term DAY), '%Y-%m-%d')
   AND d.avg_yield*100 > 4
 ORDER BY a.close/b.close DESC
 