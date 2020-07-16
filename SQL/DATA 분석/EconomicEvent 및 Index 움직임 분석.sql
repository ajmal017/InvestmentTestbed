WITH first_template AS (
WITH base AS (SELECT a.nm_us AS index_nm, a.cd AS index_cd, b.nm_us AS event_nm, b.cd AS event_cd, a.type AS index_type
				FROM index_master a, economic_events b),
     r_p AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value)*direction AS profit, direction
			 FROM economic_events_results
			WHERE event_diff > 0 AND value_diff*direction > 0
			GROUP BY event_cd, index_cd, direction),
     r_m AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value)*direction AS profit, direction
			 FROM economic_events_results
			WHERE event_diff < 0 AND value_diff*direction < 0
			GROUP BY event_cd, index_cd, direction),
     w_p AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value)*direction AS profit, direction
			 FROM economic_events_results
			WHERE event_diff > 0 AND value_diff*direction < 0
			GROUP BY event_cd, index_cd, direction),
	 w_m AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value)*direction AS profit, direction
			 FROM economic_events_results
			WHERE event_diff < 0 AND value_diff*direction > 0
			GROUP BY event_cd, index_cd, direction)
SELECT base.index_nm AS index_nm
     , base.event_nm AS event_nm
	 , base.index_cd AS index_cd
     , base.event_cd AS event_cd
     , base.index_type AS index_type
	 , IFNULL(r_p.cnt, 0) AS r_p_cnt
     , IFNULL(r_m.cnt, 0) AS r_m_cnt
     , IFNULL(w_p.cnt, 0) AS w_p_cnt
     , IFNULL(w_m.cnt, 0) AS w_m_cnt
     , IFNULL(r_p.profit, 0) AS r_p_profit
     , IFNULL(r_m.profit, 0) AS r_m_profit
     , IFNULL(w_p.profit, 0) AS w_p_profit
     , IFNULL(w_m.profit, 0) AS w_m_profit
  FROM base
  LEFT JOIN r_p
    ON base.index_cd = r_p.index_cd
   AND base.event_cd = r_p.event_cd
  LEFT JOIN r_m
    ON base.index_cd = r_m.index_cd
   AND base.event_cd = r_m.event_cd
  LEFT JOIN w_p
    ON base.index_cd = w_p.index_cd
   AND base.event_cd = w_p.event_cd
  LEFT JOIN w_m
    ON base.index_cd = w_m.index_cd
   AND base.event_cd = w_m.event_cd  
)
SELECT index_nm, event_nm, index_cd, event_cd, index_type
	 , r_p_cnt, r_m_cnt, w_p_cnt, w_m_cnt
     , r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt AS tot_cnt
     , FORMAT((r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS pos_hit
 	 , FORMAT((w_p_cnt+w_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS neg_hit
 	 , FORMAT((r_p_cnt*r_p_profit+r_m_cnt*r_m_profit)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS pos_profit
 	 , FORMAT((w_p_cnt*w_p_profit+w_m_cnt*w_m_profit)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS neg_profit
  FROM first_template
 WHERE 1=1
--   AND (r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt) > 0.65
   AND r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt >= 10
   AND index_type = 'I'
   AND index_cd NOT IN ('VIX', 'SZ5E', 'DAX', 'RTSI$', 'AS51', 'SENSEX', 'IBOV', 'TWSE', 'HNX30')
--	('KOSDAQ', 'CCMP', 'SZSE', 'KOSPI', 'SPX')
--	AND event_cd = 1
--	AND index_cd = 'KOSPI'
 ORDER BY (r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt) DESC