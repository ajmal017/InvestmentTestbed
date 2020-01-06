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
  `cd` varchar(16) NOT NULL,
  `curr_id` int(8) NOT NULL DEFAULT 0,
  `type` char(1) NOT NULL DEFAULT 'N',
  `nm_us` varchar(64) NOT NULL,
  `nm_kr` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`curr_id`,`cd`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 테이블 데이터 investing.com.index_master:~30 rows (대략적) 내보내기
DELETE FROM `index_master`;
/*!40000 ALTER TABLE `index_master` DISABLE KEYS */;
INSERT INTO `index_master` (`cd`, `curr_id`, `type`, `nm_us`, `nm_kr`) VALUES
	('NDX', 20, 'I', 'NASDAQ 100', NULL),
	('SPX', 166, 'I', 'S&P 500', NULL),
	('INDU', 169, 'I', 'Dow Jones 30', NULL),
	('RTY', 170, 'I', 'Russell 2000', NULL),
	('AS51', 171, 'I', 'S&P/ASX 200', NULL),
	('DAX', 172, 'I', 'DAX', NULL),
	('SX5E', 175, 'I', 'Euro Stoxx 50', NULL),
	('NKY', 178, 'I', 'Nikkei 225', NULL),
	('HSI', 179, 'I', 'Hang Seng', NULL),
	('DX', 8827, 'F', 'Dollar Index', NULL),
	('GC', 8830, 'F', 'Gold Futures', NULL),
	('HG', 8831, 'F', 'Copper Futures', NULL),
	('SI', 8836, 'F', 'Silver Futures', NULL),
	('CL', 8849, 'F', 'Crude Oil WTI Futures', NULL),
	('NG', 8862, 'F', 'Natural Gas Futures', NULL),
	('RTSI$', 13665, 'I', 'RTSI', NULL),
	('CCMP', 14958, 'I', 'NASDAQ', NULL),
	('IBOV', 17920, 'I', 'Bovespa', NULL),
	('A50', 28930, 'I', 'A50', NULL),
	('KOSPI', 37426, 'I', 'KOSPI', NULL),
	('KOSPI2', 37427, 'I', 'KOSPI 200', NULL),
	('KOSDAQ', 38016, 'I', 'KOSDAQ', NULL),
	('TWSE', 38017, 'I', 'Weighted', NULL),
	('SENSEX', 39929, 'I', 'Sensex 30', NULL),
	('SHCOMP', 40820, 'I', 'Shanghai', NULL),
	('VIX', 44336, 'I', 'S&P 500 VIX', NULL),
	('SHSZ300', 940801, 'I', 'CSI 300', NULL),
	('SZSE', 942630, 'I', 'SZSE', NULL),
	('KOSDQ150', 980241, 'I', 'KOSDAQ 150', NULL),
	('HNX30', 995072, 'I', 'HNX 30', NULL);
/*!40000 ALTER TABLE `index_master` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
