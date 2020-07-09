
SELECT a.event_nm, a.event_cd, e.nm_us AS index_nm, a.index_cd
     , a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt AS cnt
     , FORMAT((a.pos_cnt+b.neg_cnt)/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS pos_hit
	  , FORMAT(c.w_cnt/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS neg1_hit
	  , FORMAT(d.w_cnt/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS neg2_hit
	  , FORMAT((a.pos_ratio*a.pos_cnt - b.neg_ratio*b.neg_cnt)/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS pos_ratio
	  , FORMAT(c.w_ratio*c.w_cnt/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS neg1_ratio
	  , FORMAT(d.w_ratio*d.w_cnt/(a.pos_cnt+b.neg_cnt+c.w_cnt+d.w_cnt),4) AS neg2_ratio
  FROM
  (SELECT event_nm, event_cd, index_cd, COUNT(*) AS pos_cnt, AVG(index_value_ratio) AS pos_ratio
     FROM economic_events_results
    WHERE event_value_diff > 0 AND index_value_ratio > 0
    GROUP BY event_nm, event_cd, index_cd) a
, (SELECT event_cd, index_cd, COUNT(*) AS neg_cnt, AVG(index_value_ratio) AS neg_ratio
     FROM economic_events_results
    WHERE event_value_diff < 0 AND index_value_ratio < 0
    GROUP BY event_cd, index_cd) b
, (SELECT event_cd, index_cd, COUNT(*) AS w_cnt, AVG(index_value_ratio) AS w_ratio
     FROM economic_events_results
    WHERE event_value_diff > 0 AND index_value_ratio < 0
    GROUP BY event_cd, index_cd) c
, (SELECT event_cd, index_cd, COUNT(*) AS w_cnt, AVG(index_value_ratio) AS w_ratio
     FROM economic_events_results
    WHERE event_value_diff < 0 AND index_value_ratio > 0
    GROUP BY event_cd, index_cd) d
, index_master e
 WHERE a.event_cd = b.event_cd
   AND a.index_cd = b.index_cd
   AND a.event_cd = c.event_cd
   AND a.index_cd = c.index_cd  
   AND a.event_cd = d.event_cd
   AND a.index_cd = d.index_cd  
   AND a.index_cd = e.cd
--   AND a.index_cd = 'KOSPI2'
  