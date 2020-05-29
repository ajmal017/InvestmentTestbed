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

-- 테이블 investing.com.index_master 구조 내보내기
CREATE TABLE IF NOT EXISTS `index_master` (
  `cd` varchar(16) NOT NULL,
  `curr_id` int(8) NOT NULL DEFAULT 0,
  `type` char(1) NOT NULL DEFAULT 'N',
  `nm_us` varchar(64) NOT NULL,
  `nm_kr` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`curr_id`,`cd`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
-- 테이블 investing.com.index_price 구조 내보내기
CREATE TABLE IF NOT EXISTS `index_price` (
  `idx_cd` varchar(8) NOT NULL,
  `date` varchar(10) NOT NULL,
  `close` float NOT NULL,
  `open` float DEFAULT NULL,
  `high` float DEFAULT NULL,
  `low` float DEFAULT NULL,
  `vol` float DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`idx_cd`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 내보낼 데이터가 선택되어 있지 않습니다.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
