SELECT 
    COUNT(*) AS cnt,
    b.nm AS nm,
    b.country AS country,
    b.industry AS industry,
    a.pid AS pid,
    a.period AS period,
    AVG(a.yield) * 100 AS yield,
    ROUND(STD(a.yield), 2) * 100 AS std,
    MAX(a.ex_date) AS last_dt,
    b.url AS url
FROM
    stock_dividends a,
    stock_master b
WHERE
    a.pid = b.pid AND b.country = 'US'
        AND a.period = 'Quarterly'
        AND a.yield > 0.03
GROUP BY a.pid , a.period , b.nm , b.country , b.url , b.industry
ORDER BY AVG(a.yield) DESC , STD(a.yield)