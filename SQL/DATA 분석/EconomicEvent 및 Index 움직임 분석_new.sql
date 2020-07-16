WITH first_template AS (
WITH base AS (SELECT a.nm_us AS index_nm, a.cd AS index_cd, b.nm_us AS event_nm, b.cd AS event_cd, a.type AS index_type, MIN(c.event_date) AS start_dt, MAX(c.event_date) AS end_dt
				    FROM index_master a, economic_events b, economic_events_results c
				   WHERE a.cd = c.index_cd
				     AND b.cd = c.event_cd
				   GROUP BY a.nm_us, a.cd, b.nm_us, b.cd, a.type),
     u_b_r AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff > 0
			  AND value_diff > 0
			  AND direction = 1
			GROUP BY event_cd, index_cd, direction),
     u_s_r AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff > 0
			  AND value_diff < 0
			  AND direction = -1
			GROUP BY event_cd, index_cd, direction),
     d_b_r AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff < 0
			  AND value_diff > 0
			  AND direction = -1
			GROUP BY event_cd, index_cd, direction),
     d_s_r AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff < 0
			  AND value_diff < 0
			  AND direction = 1
			GROUP BY event_cd, index_cd, direction),
     u_b_w AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff > 0
			  AND value_diff < 0
			  AND direction = 1
			GROUP BY event_cd, index_cd, direction),
     u_s_w AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff > 0
			  AND value_diff > 0
			  AND direction = -1
			GROUP BY event_cd, index_cd, direction),
     d_b_w AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff < 0
			  AND value_diff < 0
			  AND direction = -1
			GROUP BY event_cd, index_cd, direction),
     d_s_w AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, -1*SUM(value_diff/in_value) AS profit
			 FROM economic_events_results
			WHERE event_diff < 0
			  AND value_diff > 0
			  AND direction = 1
			GROUP BY event_cd, index_cd, direction)			
SELECT base.index_nm AS index_nm
     , base.event_nm AS event_nm
	 , base.index_cd AS index_cd
     , base.event_cd AS event_cd
     , base.index_type AS index_type
     , base.start_dt AS start_dt
     , base.end_dt AS end_dt     
	 , IFNULL(u_b_r.cnt, 0) AS u_b_r_cnt
     , IFNULL(u_s_r.cnt, 0) AS u_s_r_cnt
     , IFNULL(d_b_r.cnt, 0) AS d_b_r_cnt
     , IFNULL(d_s_r.cnt, 0) AS d_s_r_cnt
	 , IFNULL(u_b_w.cnt, 0) AS u_b_w_cnt
     , IFNULL(u_s_w.cnt, 0) AS u_s_w_cnt
     , IFNULL(d_b_w.cnt, 0) AS d_b_w_cnt
     , IFNULL(d_s_w.cnt, 0) AS d_s_w_cnt
     , IFNULL(u_b_r.profit, 0) AS u_b_r_profit
     , IFNULL(u_s_r.profit, 0) AS u_s_r_profit
     , IFNULL(d_b_r.profit, 0) AS d_b_r_profit
     , IFNULL(d_s_r.profit, 0) AS d_s_r_profit
     , IFNULL(u_b_w.profit, 0) AS u_b_w_profit
     , IFNULL(u_s_w.profit, 0) AS u_s_w_profit
     , IFNULL(d_b_w.profit, 0) AS d_b_w_profit
     , IFNULL(d_s_w.profit, 0) AS d_s_w_profit
  FROM base
  LEFT JOIN u_b_r
    ON base.index_cd = u_b_r.index_cd
   AND base.event_cd = u_b_r.event_cd
  LEFT JOIN u_s_r
    ON base.index_cd = u_s_r.index_cd
   AND base.event_cd = u_s_r.event_cd
  LEFT JOIN d_b_r
    ON base.index_cd = d_b_r.index_cd
   AND base.event_cd = d_b_r.event_cd
  LEFT JOIN d_s_r
    ON base.index_cd = d_s_r.index_cd
   AND base.event_cd = d_s_r.event_cd  
  LEFT JOIN u_b_w
    ON base.index_cd = u_b_w.index_cd
   AND base.event_cd = u_b_w.event_cd
  LEFT JOIN u_s_w
    ON base.index_cd = u_s_w.index_cd
   AND base.event_cd = u_s_w.event_cd
  LEFT JOIN d_b_w
    ON base.index_cd = d_b_w.index_cd
   AND base.event_cd = d_b_w.event_cd
  LEFT JOIN d_s_w
    ON base.index_cd = d_s_w.index_cd
   AND base.event_cd = d_s_w.event_cd     
)
SELECT index_nm, event_nm, index_cd, event_cd, start_dt, end_dt
	 , u_b_r_cnt, u_s_r_cnt, d_b_r_cnt, d_s_r_cnt, u_b_w_cnt, u_s_w_cnt, d_b_w_cnt, d_s_w_cnt
     , u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt AS tot_cnt
     , FORMAT((u_b_r_cnt+d_b_r_cnt+u_b_w_cnt+d_b_w_cnt)/(u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt),4) AS long_ratio
 	 , FORMAT((u_s_r_cnt+d_s_r_cnt+u_s_w_cnt+d_s_w_cnt)/(u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt),4) AS short_ratio
     , FORMAT((u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt)/(u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt),4) AS right_ratio
 	 , FORMAT((u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt)/(u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt),4) AS wrong_ratio
 	 , FORMAT(u_b_r_profit+d_b_r_profit+u_b_w_profit+d_b_w_profit,4) AS long_profit
 	 , FORMAT(u_s_r_profit+d_s_r_profit+u_s_w_profit+d_s_w_profit,4) AS short_profit
 	 , FORMAT(u_b_r_profit+d_b_r_profit+u_s_r_profit+d_s_r_profit,4) AS right_profit
 	 , FORMAT(u_b_w_profit+d_b_w_profit+u_s_w_profit+d_s_w_profit,4) AS wrong_profit
-- 	 , FORMAT(u_b_r_cnt*u_b_r_profit+d_b_r_cnt*d_b_r_profit+u_b_w_cnt*u_b_w_profit+d_b_w_cnt*d_b_w_profit,4) AS long_profit
-- 	 , FORMAT(u_s_r_cnt*u_s_r_profit+d_s_r_cnt*d_s_r_profit+u_s_w_cnt*u_s_w_profit+d_s_w_cnt*d_s_w_profit,4) AS short_profit
-- 	 , FORMAT(u_b_r_cnt*u_b_r_profit+d_b_r_cnt*d_b_r_profit+u_s_r_cnt*u_s_r_profit+d_s_r_cnt*d_s_r_profit,4) AS right_profit
-- 	 , FORMAT(u_b_w_cnt*u_b_w_profit+d_b_w_cnt*d_b_w_profit+u_s_w_cnt*u_s_w_profit+d_s_w_cnt*d_s_w_profit,4) AS wrong_profit
 	 
  FROM first_template
 WHERE 1=1
   AND u_b_r_cnt+u_s_r_cnt+d_b_r_cnt+d_s_r_cnt+u_b_w_cnt+u_s_w_cnt+d_b_w_cnt+d_s_w_cnt >= 10
   AND index_type = 'I'
   AND index_cd NOT IN ('VIX', 'SZ5E', 'DAX', 'RTSI$', 'AS51', 'SENSEX', 'IBOV', 'TWSE', 'HNX30')
