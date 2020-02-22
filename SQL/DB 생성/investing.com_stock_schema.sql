CREATE DATABASE  IF NOT EXISTS `investing.com` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `investing.com`;
-- MySQL dump 10.13  Distrib 8.0.12, for macos10.13 (x86_64)
--
-- Host: localhost    Database: investing.com
-- ------------------------------------------------------
-- Server version	8.0.12

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `economic_events`
--

DROP TABLE IF EXISTS `economic_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `economic_events` (
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `economic_events_results`
--

DROP TABLE IF EXISTS `economic_events_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `economic_events_results` (
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `economic_events_schedule`
--

DROP TABLE IF EXISTS `economic_events_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `economic_events_schedule` (
  `event_cd` int(4) unsigned NOT NULL,
  `release_date` char(10) NOT NULL,
  `release_time` char(5) NOT NULL,
  `statistics_time` int(2) DEFAULT NULL,
  `bold_value` float NOT NULL,
  `fore_value` float DEFAULT NULL,
  `pre_release_yn` int(1) unsigned zerofill DEFAULT '0',
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`event_cd`,`release_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `index_master`
--

DROP TABLE IF EXISTS `index_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `index_master` (
  `cd` varchar(16) NOT NULL,
  `curr_id` int(8) NOT NULL DEFAULT '0',
  `type` char(1) NOT NULL DEFAULT 'N',
  `nm_us` varchar(64) NOT NULL,
  `nm_kr` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`curr_id`,`cd`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `index_price`
--

DROP TABLE IF EXISTS `index_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `index_price` (
  `idx_cd` varchar(8) NOT NULL,
  `date` varchar(10) NOT NULL,
  `close` float NOT NULL,
  `open` float NOT NULL,
  `high` float NOT NULL,
  `low` float NOT NULL,
  `vol` float DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`idx_cd`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_dividends`
--

DROP TABLE IF EXISTS `stock_dividends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `stock_dividends` (
  `pid` varchar(16) NOT NULL,
  `ex_date` char(10) NOT NULL,
  `payment_date` char(10) DEFAULT NULL,
  `dividend` decimal(16,4) DEFAULT NULL,
  `period` varchar(32) DEFAULT NULL,
  `yield` decimal(16,4) DEFAULT NULL,
  PRIMARY KEY (`pid`,`ex_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_earnings`
--

DROP TABLE IF EXISTS `stock_earnings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `stock_earnings` (
  `pid` varchar(16) NOT NULL,
  `date` varchar(10) NOT NULL,
  `period_end` varchar(10) DEFAULT NULL,
  `eps_bold` decimal(16,4) DEFAULT NULL,
  `eps_fore` decimal(16,4) DEFAULT NULL,
  `revenue_bold` decimal(32,0) DEFAULT NULL,
  `revenue_fore` decimal(32,0) DEFAULT NULL,
  PRIMARY KEY (`pid`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_financial`
--

DROP TABLE IF EXISTS `stock_financial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `stock_financial` (
  `pid` varchar(16) NOT NULL,
  `date` varchar(10) NOT NULL,
  `term_type` varchar(1) NOT NULL,
  `period` int(8) NOT NULL,
  `total_revenue` decimal(16,4) DEFAULT NULL COMMENT 'Income Statement',
  `gross_profit` decimal(16,4) DEFAULT NULL COMMENT 'Income Statement',
  `operating_income` decimal(16,4) DEFAULT NULL COMMENT 'Income Statement',
  `net_income` decimal(16,4) DEFAULT NULL COMMENT 'Income Statement',
  `total_assets` decimal(16,4) DEFAULT NULL COMMENT 'Balance Sheet',
  `total_liabilities` decimal(16,4) DEFAULT NULL COMMENT 'Balance Sheet',
  `total_equity` decimal(16,4) DEFAULT NULL COMMENT 'Balance Sheet',
  `cash_from_operating_activities` decimal(16,4) DEFAULT NULL COMMENT 'Cash Flow Statement',
  `cash_from_investing_activities` decimal(16,4) DEFAULT NULL COMMENT 'Cash Flow Statement',
  `cash_from_financing_activities` decimal(16,4) DEFAULT NULL COMMENT 'Cash Flow Statement',
  `net_change_in_cash` decimal(16,4) DEFAULT NULL COMMENT 'Cash Flow Statement',
  PRIMARY KEY (`pid`,`date`,`term_type`,`period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_master`
--

DROP TABLE IF EXISTS `stock_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `stock_master` (
  `pid` varchar(16) NOT NULL,
  `country` varchar(32) NOT NULL,
  `nm` varchar(64) NOT NULL,
  `industry` varchar(32) NOT NULL,
  `sector` varchar(32) NOT NULL,
  `url` varchar(128) NOT NULL,
  `profile_url` varchar(128) NOT NULL,
  `financial_url` varchar(128) NOT NULL,
  `earnings_url` varchar(128) NOT NULL,
  `dividends_url` varchar(128) NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-02-22 21:47:00
