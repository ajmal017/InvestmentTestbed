-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        10.4.6-MariaDB - mariadb.org binary distribution
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  9.5.0.5196
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
  `cd` varchar(8) NOT NULL,
  `nm_us` varchar(64) NOT NULL,
  `nm_kr` varchar(128) DEFAULT NULL,
  `curr_id` int(8) NOT NULL,
  `type` char(1) DEFAULT NULL,
  PRIMARY KEY (`cd`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 테이블 데이터 investing.com.index_master:~11 rows (대략적) 내보내기
/*!40000 ALTER TABLE `index_master` DISABLE KEYS */;
INSERT INTO `index_master` (`cd`, `nm_us`, `nm_kr`, `curr_id`, `type`) VALUES
	('CL', 'Crude Oil WTI Futures', NULL, 8849, 'F'),
	('DJI', 'Dow Jones Industrial Average', NULL, 169, 'I'),
	('GC', 'Gold Futures', NULL, 8830, 'F'),
	('HG', 'Copper Futures', NULL, 8831, 'F'),
	('KQ150', 'KOSDAQ 150', NULL, 980241, 'I'),
	('KS200', 'KOSPI 200', NULL, 37427, 'I'),
	('NDX', 'Nasdaq 100', NULL, 20, 'I'),
	('NG', 'Natural Gas Futures', NULL, 8862, 'F'),
	('SI', 'Silver Futures', NULL, 8836, 'F'),
	('SPX', 'S&P 500', NULL, 166, 'I'),
	('STOXX50E', 'Euro Stoxx 50', NULL, 175, 'I');
/*!40000 ALTER TABLE `index_master` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
