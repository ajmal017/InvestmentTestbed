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

-- 테이블 investing.com.stock_dividends 구조 내보내기
CREATE TABLE IF NOT EXISTS `stock_dividends` (
  `pid` varchar(16) NOT NULL,
  `ex_date` char(10) NOT NULL,
  `payment_date` char(10) DEFAULT NULL,
  `dividend` decimal(16,4) DEFAULT NULL,
  `period` varchar(32) DEFAULT NULL,
  `yield` decimal(16,4) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`pid`,`ex_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 테이블 데이터 investing.com.stock_dividends:~0 rows (대략적) 내보내기
/*!40000 ALTER TABLE `stock_dividends` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_dividends` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
