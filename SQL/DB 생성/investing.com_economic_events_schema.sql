-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        10.3.9-MariaDB - mariadb.org binary distribution
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- investing.com 데이터베이스 구조 내보내기
CREATE DATABASE IF NOT EXISTS `investing.com` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `investing.com`;

-- 테이블 investing.com.economic_events 구조 내보내기
CREATE TABLE IF NOT EXISTS `economic_events` (
  `cd` int(4) unsigned NOT NULL,
  `nm_us` varchar(128) DEFAULT NULL,
  `nm_kr` varchar(256) DEFAULT NULL,
  `link` varchar(256) DEFAULT NULL,
  `ctry` varchar(16) DEFAULT NULL,
  `period` char(1) DEFAULT NULL,
  `imp_us` int(1) DEFAULT NULL,
  `imp_kr` int(1) DEFAULT NULL,
  `type` varchar(8) DEFAULT NULL,
  `unit` char(1) DEFAULT NULL,
  PRIMARY KEY (`cd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 investing.com.economic_events_results 구조 내보내기
CREATE TABLE IF NOT EXISTS `economic_events_results` (
  `event_cd` int(4) NOT NULL,
  `event_nm` varchar(128) DEFAULT NULL,
  `index_cd` varchar(8) NOT NULL,
  `event_date` char(10) NOT NULL,
  `position_in_date` char(10) DEFAULT NULL,
  `position_out_date` char(10) DEFAULT NULL,
  `position_in_value` float DEFAULT NULL,
  `position_out_value` float DEFAULT NULL,
  `event_value_diff` float DEFAULT NULL,
  `index_value_ratio` float DEFAULT NULL,
  PRIMARY KEY (`event_cd`,`index_cd`,`event_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 investing.com.economic_events_schedule 구조 내보내기
CREATE TABLE IF NOT EXISTS `economic_events_schedule` (
  `event_cd` int(4) unsigned NOT NULL,
  `release_date` char(10) NOT NULL,
  `release_time` char(5) NOT NULL,
  `statistics_time` int(2) DEFAULT NULL,
  `bold_value` float NOT NULL,
  `fore_value` float DEFAULT NULL,
  `pre_release_yn` int(1) unsigned zerofill DEFAULT 0,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`event_cd`,`release_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
