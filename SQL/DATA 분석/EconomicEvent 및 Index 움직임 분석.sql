WITH first_template AS (
WITH base AS (SELECT a.nm_us AS index_nm, a.cd AS index_cd, b.nm_us AS event_nm, b.cd AS event_cd
				FROM index_master a, economic_events b),
     r_p AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, AVG(value_diff/in_value)*AVG(direction) AS ratio
			 FROM economic_events_results
			WHERE event_diff > 0 AND value_diff > 0
			GROUP BY event_cd, index_cd),
     r_m AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, AVG(value_diff/in_value)*AVG(direction) AS ratio
			 FROM economic_events_results
			WHERE event_diff < 0 AND value_diff < 0
			GROUP BY event_cd, index_cd),
     w_p AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, AVG(value_diff/in_value)*AVG(direction) AS ratio
			 FROM economic_events_results
			WHERE event_diff > 0 AND value_diff < 0
			GROUP BY event_cd, index_cd),
	 w_m AS (SELECT event_cd, index_cd, COUNT(*) AS cnt, AVG(value_diff/in_value)*AVG(direction) AS ratio
			 FROM economic_events_results
			WHERE event_diff < 0 AND value_diff > 0
			GROUP BY event_cd, index_cd)
SELECT base.index_nm AS index_nm
     , base.event_nm AS event_nm
	 , base.index_cd AS index_cd
     , base.event_cd AS event_cd
	 , IFNULL(r_p.cnt, 0) AS r_p_cnt
     , IFNULL(r_m.cnt, 0) AS r_m_cnt
     , IFNULL(w_p.cnt, 0) AS w_p_cnt
     , IFNULL(w_m.cnt, 0) AS w_m_cnt
     , IFNULL(r_p.ratio, 0) AS r_p_ratio
     , IFNULL(r_m.ratio, 0) AS r_m_ratio
     , IFNULL(w_p.ratio, 0) AS w_p_ratio
     , IFNULL(w_m.ratio, 0) AS w_m_ratio
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
SELECT index_nm, event_nm, index_cd, event_cd
	 , r_p_cnt, r_m_cnt, w_p_cnt, w_m_cnt
     , r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt AS tot_cnt
     , FORMAT((r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS pos_hit
 	 , FORMAT((w_p_cnt+w_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS neg_hit
 	 , FORMAT((r_p_cnt*r_p_ratio+r_m_cnt*r_m_ratio)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS pos_ratio
 	 , FORMAT((w_p_cnt*w_p_ratio+w_m_cnt*w_m_ratio)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt),4) AS neg_ratio
  FROM first_template
 WHERE ((r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt) > 0.65
    OR (w_p_cnt+w_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt) > 0.65)
   AND r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt >= 10
 ORDER BY (r_p_cnt+r_m_cnt)/(r_p_cnt+r_m_cnt+w_p_cnt+w_m_cnt) DESC