-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: vallacar_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `vallacar_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `vallacar_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `vallacar_db`;

--
-- ============================================================================
--  VALLACAR TRANSIT - CERES LINER TRACKER
--  Database : vallacar_db   (XAMPP / MariaDB)
--  Schema   : matches the current Django models and CRUD
--
--  Relationships implemented as FOREIGN KEYs:
--    auth_user (USER ACCOUNTS) 1 --- N  tblbus, tbldriver, tblconductor,
--                                       tbltrip, tblincident, tblmaintenance,
--                                       tblinfo
--    tblbus (BUS)              1 --- N  tbldriver, tblconductor, tbltrip,
--                                       tblincident, tblmaintenance
--
--  Import with phpMyAdmin or:
--    mysql -u root < vallacar_db.sql
-- ============================================================================
--

--
-- ============================================================================
-- 1. USER ACCOUNTS  (auth_user)
-- ============================================================================
--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$720000$bOj5VBWtCXUDkvqS0bEcbq$LYdO8A8VA9CspX3XllYy93oquLorg67N4qI9+oeIoxo=','2026-11-10 07:06:25.203153',1,'admin','','','admin@vallacar.local',1,1,'2026-10-15 07:26:55.224965');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 2. BUS  (tblbus)  -> user_id REFERENCES auth_user
-- ============================================================================
--
-- Table structure for table `tblbus`
--

DROP TABLE IF EXISTS `tblbus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblbus` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `bus_number` varchar(50) NOT NULL,
  `plate_number` varchar(20) NOT NULL,
  `capacity` int(10) unsigned NOT NULL CHECK (`capacity` >= 0),
  `route` varchar(255) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `current_location` varchar(255) NOT NULL,
  `last_gps_update` datetime(6) DEFAULT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `movement_status` varchar(20) NOT NULL,
  `movement_reason` varchar(255) NOT NULL,
  `qr_token` char(32) NOT NULL,
  `actual_departure` time(6) DEFAULT NULL,
  `bay` varchar(50) NOT NULL,
  `current_terminal` varchar(255) NOT NULL,
  `final_destination` varchar(255) NOT NULL,
  `final_destination_eta` time(6) DEFAULT NULL,
  `next_stop` varchar(255) NOT NULL,
  `next_stop_eta` time(6) DEFAULT NULL,
  `operator` varchar(100) NOT NULL,
  `scheduled_time` time(6) DEFAULT NULL,
  `next_terminal` varchar(255) NOT NULL,
  `next_terminal_eta` time(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bus_number` (`bus_number`),
  UNIQUE KEY `plate_number` (`plate_number`),
  UNIQUE KEY `tblbus_qr_token_25bc2915_uniq` (`qr_token`),
  KEY `tblbus_user_id_c19f51cc_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblbus_user_id_c19f51cc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbus`
--

LOCK TABLES `tblbus` WRITE;
/*!40000 ALTER TABLE `tblbus` DISABLE KEYS */;
INSERT INTO `tblbus` VALUES (1,'t76775','46745',1,'Kabankalan','active','2026-10-17 15:01:37.042480','2026-10-17 15:06:48.141446',1,'Bacolod','2026-10-17 15:06:48.141384',0.000010,0.000001,'en_route','','bd74d5d344dd4225a7ac1bd2f152f86e',NULL,'','','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(2,'101','VTI 2001',49,'Kabankalan - Candoni','active','2026-11-10 06:56:14.102840','2026-11-10 06:56:14.102851',NULL,'Kabankalan Terminal','2026-11-10 06:56:14.095776',9.991700,122.812800,'at_terminal','','4e0c26fac0b543abb5fe6fd322446115',NULL,'','Kabankalan','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(3,'102','VTI 2002',45,'Bacolod - Sipalay','active','2026-11-10 06:56:14.120829','2026-11-10 06:56:14.120840',NULL,'En route from Bacolod Terminal','2026-11-10 06:56:14.095776',10.676500,122.950900,'en_route','','6675c8412a994766bd28ab20128db3e6',NULL,'','Bacolod','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(4,'103','VTI 2003',53,'Narra - Bacolod','active','2026-11-10 06:56:14.128221','2026-11-10 06:56:14.128228',NULL,'En route from Narra','2026-11-10 06:56:14.095776',9.967000,122.617000,'en_route','','5f784b258d6144338e456dd02a6445ad',NULL,'','Narra','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(5,'104','VTI 2004',49,'Sipalay - Bacolod','active','2026-11-10 06:56:14.137846','2026-11-10 06:56:14.137854',NULL,'En route from Sipalay Terminal','2026-11-10 06:56:14.095776',9.750000,122.400000,'en_route','','56f854a403634f7fadd2870a638eb99e',NULL,'','Sipalay','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(6,'105','VTI 2005',45,'Candoni - Bacolod','active','2026-11-10 06:56:14.145425','2026-11-10 06:56:14.145434',NULL,'En route from Candoni','2026-11-10 06:56:14.095776',9.831044,122.642981,'en_route','','dde0269c72ad4ac6a220ddf0266b45b0',NULL,'','Candoni','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(7,'106','VTI 2006',53,'Hinoba-an - Kabankalan','active','2026-11-10 06:56:14.157364','2026-11-10 06:56:14.157381',NULL,'En route from Hinoba-an Terminal','2026-11-10 06:56:14.095776',9.583000,122.467000,'en_route','','f947e540abec4b4892f634749179a7c9',NULL,'','Hinoba-an','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(8,'107','VTI 2007',49,'Kabankalan - Bacolod','active','2026-11-10 06:56:14.171325','2026-11-10 06:56:14.171333',NULL,'En route from Kabankalan','2026-11-10 06:56:14.095776',9.991700,122.812800,'en_route','','b9aff0d1e14f4352a31451fa8652f237',NULL,'','Kabankalan','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(9,'108','VTI 2008',49,'San Carlos - Sipalay','active','2026-11-10 06:56:14.185258','2026-11-10 06:56:14.185270',NULL,'En route from San Carlos Terminal','2026-11-10 06:56:14.095776',10.496600,123.422400,'en_route','','e4e58ed1e1db458786ace0e8163f6254',NULL,'','San Carlos','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(10,'109','VTI 2009',45,'Victorias - Hinoba-an','active','2026-11-10 06:56:14.194521','2026-11-10 06:56:14.194531',NULL,'En route from Victorias','2026-11-10 06:56:14.095776',10.900000,123.066700,'en_route','','6fd92120aee94de998ad983a94ce3b62',NULL,'','Victorias','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL),(11,'110','VTI 2010',53,'Sagay - Kabankalan','active','2026-11-10 06:56:14.205907','2026-11-10 06:56:14.205922',NULL,'En route from Sagay Terminal','2026-11-10 06:56:14.095776',10.891700,123.415000,'en_route','','93de8fa0a6d84672b4152b19043fe9c2',NULL,'','Sagay','',NULL,'',NULL,'Ceres Liner',NULL,'',NULL);
/*!40000 ALTER TABLE `tblbus` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 3. DRIVER  (tbldriver)  -> user_id, bus_id
-- ============================================================================
--
-- Table structure for table `tbldriver`
--

DROP TABLE IF EXISTS `tbldriver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbldriver` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `license_number` varchar(50) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `address` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `license_number` (`license_number`),
  KEY `tbldriver_bus_id_5ae681af_fk_tblbus_id` (`bus_id`),
  KEY `tbldriver_user_id_d4fa85e1_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tbldriver_bus_id_5ae681af_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tbldriver_user_id_d4fa85e1_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbldriver`
--

LOCK TABLES `tbldriver` WRITE;
/*!40000 ALTER TABLE `tbldriver` DISABLE KEYS */;
INSERT INTO `tbldriver` VALUES (1,'kkk','254645','070989696','hvvh','2026-10-17 15:02:21.161294','2026-10-17 15:02:21.161325',1,1);
/*!40000 ALTER TABLE `tbldriver` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 4. CONDUCTOR  (tblconductor)  -> user_id, bus_id
-- ============================================================================
--
-- Table structure for table `tblconductor`
--

DROP TABLE IF EXISTS `tblconductor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblconductor` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `address` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  KEY `tblconductor_bus_id_f0b905e0_fk_tblbus_id` (`bus_id`),
  KEY `tblconductor_user_id_9d816d72_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblconductor_bus_id_f0b905e0_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblconductor_user_id_9d816d72_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblconductor`
--

LOCK TABLES `tblconductor` WRITE;
/*!40000 ALTER TABLE `tblconductor` DISABLE KEYS */;
INSERT INTO `tblconductor` VALUES (1,'vjhmgy','123345667','9768755','vhgvmgh','2026-10-17 15:03:01.654295','2026-10-17 15:03:01.654318',1,1);
/*!40000 ALTER TABLE `tblconductor` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 5. TRIP  (tbltrip)  -> user_id, bus_id
-- ============================================================================
--
-- Table structure for table `tbltrip`
--

DROP TABLE IF EXISTS `tbltrip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbltrip` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `origin` varchar(255) NOT NULL,
  `destination` varchar(255) NOT NULL,
  `route` varchar(255) NOT NULL,
  `scheduled_departure` datetime(6) NOT NULL,
  `scheduled_arrival` datetime(6) NOT NULL,
  `actual_departure` datetime(6) DEFAULT NULL,
  `actual_arrival` datetime(6) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `delay_minutes` int(10) unsigned NOT NULL CHECK (`delay_minutes` >= 0),
  `passenger_count` int(10) unsigned NOT NULL CHECK (`passenger_count` >= 0),
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tbltrip_bus_id_ccb195e5_fk_tblbus_id` (`bus_id`),
  KEY `tbltrip_user_id_531e7dd9_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tbltrip_bus_id_ccb195e5_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tbltrip_user_id_531e7dd9_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbltrip`
--

LOCK TABLES `tbltrip` WRITE;
/*!40000 ALTER TABLE `tbltrip` DISABLE KEYS */;
/*!40000 ALTER TABLE `tbltrip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'vallacar_db'
--
--
-- ============================================================================
-- 6. INCIDENT  (tblincident)  -> user_id, bus_id
-- ============================================================================
--
-- Table structure for table `tblincident`
--

DROP TABLE IF EXISTS `tblincident`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblincident` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `incident_type` varchar(20) NOT NULL,
  `severity` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `resolved_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tblincident_bus_id_0696e0aa_fk_tblbus_id` (`bus_id`),
  KEY `tblincident_user_id_f084d3b4_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblincident_bus_id_0696e0aa_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblincident_user_id_f084d3b4_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblincident`
--

LOCK TABLES `tblincident` WRITE;
/*!40000 ALTER TABLE `tblincident` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblincident` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 7. MAINTENANCE  (tblmaintenance)  -> user_id, bus_id
-- ============================================================================
--
-- Table structure for table `tblmaintenance`
--

DROP TABLE IF EXISTS `tblmaintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblmaintenance` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `record_type` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `inspection_date` date NOT NULL,
  `next_due_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `cost` decimal(10,2) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tblmaintenance_bus_id_b7c41b43_fk_tblbus_id` (`bus_id`),
  KEY `tblmaintenance_user_id_f84c6842_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblmaintenance_bus_id_b7c41b43_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblmaintenance_user_id_f84c6842_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblmaintenance`
--

LOCK TABLES `tblmaintenance` WRITE;
/*!40000 ALTER TABLE `tblmaintenance` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblmaintenance` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 8. INFO  (tblinfo)  -> user_id
-- ============================================================================
--
-- Table structure for table `tblinfo`
--

DROP TABLE IF EXISTS `tblinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblinfo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `age` int(10) unsigned NOT NULL CHECK (`age` >= 0),
  `address` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tblinfo_user_id_4a36749d_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblinfo_user_id_4a36749d_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblinfo`
--

LOCK TABLES `tblinfo` WRITE;
/*!40000 ALTER TABLE `tblinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblinfo` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 9. SUPPORTING APPLICATION TABLES  (routes, stops, QR taps)
-- ============================================================================
--
-- Table structure for table `tblterminal`
--

DROP TABLE IF EXISTS `tblterminal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblterminal` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `code` varchar(30) NOT NULL,
  `city` varchar(255) NOT NULL,
  `province` varchar(255) NOT NULL,
  `latitude` decimal(9,6) NOT NULL,
  `longitude` decimal(9,6) NOT NULL,
  `is_owned_terminal` tinyint(1) NOT NULL,
  `is_major_stop` tinyint(1) NOT NULL,
  `source` varchar(255) NOT NULL,
  `aliases` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblterminal`
--

LOCK TABLES `tblterminal` WRITE;
/*!40000 ALTER TABLE `tblterminal` DISABLE KEYS */;
INSERT INTO `tblterminal` VALUES (1,'Bacolod North','BCDN','Bacolod City','Negros Occidental',10.676500,122.950900,1,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Bacolod North Bus Terminal, Bacolod North','2026-11-10 06:37:28.566513','2026-11-10 06:37:28.566549'),(2,'Bacolod South','BCDS','Bacolod City','Negros Occidental',10.655000,122.955000,1,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Bacolod South Bus Terminal, Bacolod South, Bacolod, Bacolod City','2026-11-10 06:37:28.570904','2026-11-10 06:37:28.570930'),(3,'Bago','BAGO','Bago City','Negros Occidental',10.537600,122.838900,0,1,'https://byahi.ph/negros/routes/NEG-BCD-DGT','Bago City, Bago','2026-11-10 06:37:28.573021','2026-11-10 06:37:28.573044'),(4,'Binalbagan','BIN','Binalbagan','Negros Occidental',10.073900,122.866700,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Binalbagan','2026-11-10 06:37:28.574740','2026-11-10 06:37:28.574758'),(5,'Cadiz','CAD','Cadiz City','Negros Occidental',10.958600,123.132100,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Cadiz City, Cadiz','2026-11-10 06:37:28.576373','2026-11-10 06:37:28.576389'),(6,'Calatrava','CAL','Calatrava','Negros Occidental',10.600000,123.483000,0,1,'Terminal directory','Calatrava','2026-11-10 06:37:28.577863','2026-11-10 06:37:28.577878'),(7,'Candoni','CAND','Candoni','Negros Occidental',9.831044,122.642981,0,1,'Tracker Negros Occidental demo fleet','Candoni','2026-11-10 06:37:28.579406','2026-11-10 06:37:28.579422'),(8,'Enrique B. Magalona','EBM','Enrique B. Magalona','Negros Occidental',10.883000,122.967000,0,1,'Terminal directory','Saravia, E.B. Magalona, Enrique B. Magalona','2026-11-10 06:37:28.580790','2026-11-10 06:37:28.580805'),(9,'Escalante','ESC','Escalante City','Negros Occidental',10.833300,123.500000,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Escalante City, Escalante','2026-11-10 06:37:28.582287','2026-11-10 06:37:28.582304'),(10,'Himamaylan','HIM','Himamaylan City','Negros Occidental',10.100300,122.870200,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Himamaylan City, Himamaylan','2026-11-10 06:37:28.583990','2026-11-10 06:37:28.584014'),(11,'Hinigaran','HIN','Hinigaran','Negros Occidental',10.041700,122.856700,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Hinigaran','2026-11-10 06:37:28.592762','2026-11-10 06:37:28.592805'),(12,'Hinoba-an','HINOB','Hinoba-an','Negros Occidental',9.583000,122.467000,0,1,'Tracker Negros Occidental demo fleet','Hinobaan, Hinoba-an','2026-11-10 06:37:28.595615','2026-11-10 06:37:28.595635'),(13,'Ilog','ILOG','Ilog','Negros Occidental',10.033000,122.767000,0,1,'Tracker Negros Occidental demo fleet','Ilog','2026-11-10 06:37:28.597719','2026-11-10 06:37:28.597736'),(14,'Isabela','ISAB','Isabela','Negros Occidental',10.200000,122.983000,0,1,'Terminal directory','Isabela Negros','2026-11-10 06:37:28.599934','2026-11-10 06:37:28.599958'),(15,'Kabankalan','KAB','Kabankalan City','Negros Occidental',9.991700,122.812800,1,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Kabankalan City Bus Terminal, Kabnakalan, Kabankalan','2026-11-10 06:37:28.601849','2026-11-10 06:37:28.601866'),(16,'La Carlota','LAC','La Carlota City','Negros Occidental',10.416700,122.916700,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','La Carlota City, La Carlota','2026-11-10 06:37:28.603723','2026-11-10 06:37:28.603738'),(17,'La Castellana','LCAST','La Castellana','Negros Occidental',10.350000,123.067000,0,1,'Terminal directory','La Castellana','2026-11-10 06:37:28.605735','2026-11-10 06:37:28.605750'),(18,'Manapla','MAN','Manapla','Negros Occidental',10.950000,123.120000,0,1,'Terminal directory','Manapla','2026-11-10 06:37:28.607388','2026-11-10 06:37:28.607406'),(19,'Moises Padilla','MPAD','Moises Padilla','Negros Occidental',10.267000,123.083000,0,1,'Terminal directory','Moises Padilla','2026-11-10 06:37:28.609031','2026-11-10 06:37:28.609047'),(20,'Murcia','MUR','Murcia','Negros Occidental',10.600000,123.030000,0,1,'Terminal directory','Murcia','2026-11-10 06:37:28.610577','2026-11-10 06:37:28.610593'),(21,'Narra','NAR','Narra','Negros Occidental',9.967000,122.617000,0,1,'Tracker Negros Occidental demo fleet','Narra','2026-11-10 06:37:28.612070','2026-11-10 06:37:28.612086'),(22,'Pontevedra','PON','Pontevedra','Negros Occidental',10.366700,122.866700,0,1,'https://byahi.ph/negros/routes/NEG-BCD-DGT','Pontevedra','2026-11-10 06:37:28.613568','2026-11-10 06:37:28.613582'),(23,'Pulupandan','PUL','Pulupandan','Negros Occidental',10.517000,122.800000,0,1,'Terminal directory','Pulupandan','2026-11-10 06:37:28.615293','2026-11-10 06:37:28.615314'),(24,'Sagay','SAG','Sagay City','Negros Occidental',10.891700,123.415000,1,1,'https://ceresliner.com/terminal','Sagay Terminal','2026-11-10 06:37:28.618696','2026-11-10 06:37:28.618730'),(25,'Salvador Benedicto','SBEN','Salvador Benedicto','Negros Occidental',10.550000,123.233000,0,1,'Terminal directory','Don Salvador Benedicto, Salvador Benedicto','2026-11-10 06:37:28.621311','2026-11-10 06:37:28.621336'),(26,'San Carlos','SCC','San Carlos City','Negros Occidental',10.496600,123.422400,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','San Carlos City, San Carlos','2026-11-10 06:37:28.623332','2026-11-10 06:37:28.623355'),(27,'San Enrique','SENR','San Enrique','Negros Occidental',10.417000,122.850000,0,1,'Terminal directory','San Enrique','2026-11-10 06:37:28.625177','2026-11-10 06:37:28.625196'),(28,'Silay','SIL','Silay City','Negros Occidental',10.800000,122.967000,0,1,'Terminal directory','Silay City, Silay','2026-11-10 06:37:28.627130','2026-11-10 06:37:28.627155'),(29,'Sipalay','SIP','Sipalay City','Negros Occidental',9.750000,122.400000,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Sipalay City, Sipalay','2026-11-10 06:37:28.628999','2026-11-10 06:37:28.629016'),(30,'Talisay','TAL','Talisay City','Negros Occidental',10.733000,122.967000,0,1,'Terminal directory','Talisay City, Talisay Negros, Talisay','2026-11-10 06:37:28.630741','2026-11-10 06:37:28.630758'),(31,'Toboso','TOB','Toboso','Negros Occidental',10.717000,123.517000,0,1,'Terminal directory','Toboso','2026-11-10 06:37:28.634823','2026-11-10 06:37:28.634860'),(32,'Valladolid','VAL','Valladolid','Negros Occidental',10.466700,122.833300,0,1,'https://byahi.ph/negros/routes/NEG-BCD-DGT','Valladolid','2026-11-10 06:37:28.638039','2026-11-10 06:37:28.638063'),(33,'Victorias','VIC','Victorias City','Negros Occidental',10.900000,123.066700,0,1,'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)','Victorias City, Victorias','2026-11-10 06:37:28.640184','2026-11-10 06:37:28.640202');
/*!40000 ALTER TABLE `tblterminal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblroute`
--

DROP TABLE IF EXISTS `tblroute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblroute` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `validation_status` varchar(30) NOT NULL,
  `validation_note` longtext NOT NULL,
  `source` varchar(255) NOT NULL,
  `aliases` varchar(255) NOT NULL,
  `validated_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `validated_by_id` int(11) DEFAULT NULL,
  `destination_id` bigint(20) NOT NULL,
  `origin_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `tblroute_validated_by_id_6b85d4ec_fk_auth_user_id` (`validated_by_id`),
  KEY `tblroute_destination_id_afb58c95_fk_tblterminal_id` (`destination_id`),
  KEY `tblroute_origin_id_e83eb315_fk_tblterminal_id` (`origin_id`),
  CONSTRAINT `tblroute_destination_id_afb58c95_fk_tblterminal_id` FOREIGN KEY (`destination_id`) REFERENCES `tblterminal` (`id`),
  CONSTRAINT `tblroute_origin_id_e83eb315_fk_tblterminal_id` FOREIGN KEY (`origin_id`) REFERENCES `tblterminal` (`id`),
  CONSTRAINT `tblroute_validated_by_id_6b85d4ec_fk_auth_user_id` FOREIGN KEY (`validated_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblroute`
--

LOCK TABLES `tblroute` WRITE;
/*!40000 ALTER TABLE `tblroute` DISABLE KEYS */;
INSERT INTO `tblroute` VALUES (1,'Bacolod-Kabankalan','source_compiled','Published southern Negros Occidental corridor via Bago, Valladolid, Pontevedra, Hinigaran, Binalbagan, and Himamaylan.','https://byahi.ph/negros/routes/NEG-BCD-DGT','Bacolod-Kabankalan, Bacolod - Kabankalan, Bacolod to Kabankalan, Bacolod–Kabankalan',NULL,'2026-11-10 06:37:28.642051','2026-11-10 06:37:28.642068',NULL,15,2),(2,'Kabankalan-Bacolod','source_compiled','Reverse of the published Bacolod-Kabankalan corridor.','https://byahi.ph/negros/routes/NEG-BCD-DGT','Kabankalan-Bacolod, Kabankalan - Bacolod, Kabankalan to Bacolod, Kabankalan–Bacolod',NULL,'2026-11-10 06:37:28.647781','2026-11-10 06:37:28.647807',NULL,2,15),(3,'Bacolod-Sipalay','source_compiled','Southern Negros Occidental service through Kabankalan and Hinoba-an.','Tracker Negros Occidental demo fleet','Bacolod-Sipalay, Bacolod - Sipalay, Bacolod to Sipalay, Bacolod–Sipalay',NULL,'2026-11-10 06:37:28.652852','2026-11-10 06:37:28.652876',NULL,29,2),(4,'Sipalay-Bacolod','source_compiled','Reverse of the Bacolod-Sipalay service.','Tracker Negros Occidental demo fleet','Sipalay-Bacolod, Sipalay - Bacolod, Sipalay to Bacolod, Sipalay–Bacolod',NULL,'2026-11-10 06:37:28.658208','2026-11-10 06:37:28.658232',NULL,2,29),(5,'Narra-Bacolod','source_compiled','Narra-Ilog-Kabankalan corridor to Bacolod.','Tracker Negros Occidental demo fleet','Narra-Bacolod, Narra - Bacolod, Narra to Bacolod, Narra–Bacolod',NULL,'2026-11-10 06:37:28.662800','2026-11-10 06:37:28.662830',NULL,2,21),(6,'Bacolod-Narra','source_compiled','Reverse of the Narra-Bacolod service.','Tracker Negros Occidental demo fleet','Bacolod-Narra, Bacolod - Narra, Bacolod to Narra, Bacolod–Narra',NULL,'2026-11-10 06:37:28.668899','2026-11-10 06:37:28.668922',NULL,21,2),(7,'Candoni-Bacolod','source_compiled','Candoni-Kabankalan corridor to Bacolod.','Tracker Negros Occidental demo fleet','Candoni-Bacolod, Candoni - Bacolod, Candoni to Bacolod, Candoni–Bacolod',NULL,'2026-11-10 06:37:28.673341','2026-11-10 06:37:28.673362',NULL,2,7),(8,'Bacolod-Candoni','source_compiled','Reverse of the Candoni-Bacolod service.','Tracker Negros Occidental demo fleet','Bacolod-Candoni, Bacolod - Candoni, Bacolod to Candoni, Bacolod–Candoni',NULL,'2026-11-10 06:37:28.677157','2026-11-10 06:37:28.677177',NULL,7,2),(9,'Kabankalan-Candoni','source_compiled','Short Kabankalan-Candoni service.','Tracker Negros Occidental demo fleet','Kabankalan-Candoni, Kabankalan - Candoni, Kabankalan to Candoni, Kabankalan–Candoni',NULL,'2026-11-10 06:37:28.683852','2026-11-10 06:37:28.683877',NULL,7,15),(10,'Candoni-Kabankalan','source_compiled','Reverse of the Kabankalan-Candoni service.','Tracker Negros Occidental demo fleet','Candoni-Kabankalan, Candoni - Kabankalan, Candoni to Kabankalan, Candoni–Kabankalan',NULL,'2026-11-10 06:37:28.687647','2026-11-10 06:37:28.687673',NULL,15,7),(11,'Hinoba-an-Kabankalan','source_compiled','Hinoba-an-Sipalay-Kabankalan service.','Tracker Negros Occidental demo fleet','Hinoba-an-Kabankalan, Hinoba-an - Kabankalan, Hinoba-an to Kabankalan, Hinoba-an–Kabankalan',NULL,'2026-11-10 06:37:28.691059','2026-11-10 06:37:28.691078',NULL,15,12),(12,'Kabankalan-Hinoba-an','source_compiled','Reverse of the Hinoba-an-Kabankalan service.','Tracker Negros Occidental demo fleet','Kabankalan-Hinoba-an, Kabankalan - Hinoba-an, Kabankalan to Hinoba-an, Kabankalan–Hinoba-an',NULL,'2026-11-10 06:37:28.694262','2026-11-10 06:37:28.694283',NULL,12,15),(13,'Sipalay-Kabankalan','source_compiled','Sipalay-Hinoba-an-Kabankalan service.','Tracker Negros Occidental demo fleet','Sipalay-Kabankalan, Sipalay - Kabankalan, Sipalay to Kabankalan, Sipalay–Kabankalan',NULL,'2026-11-10 06:37:28.702651','2026-11-10 06:37:28.702675',NULL,15,29),(14,'Kabankalan-Sipalay','source_compiled','Reverse of the Sipalay-Kabankalan service.','Tracker Negros Occidental demo fleet','Kabankalan-Sipalay, Kabankalan - Sipalay, Kabankalan to Sipalay, Kabankalan–Sipalay',NULL,'2026-11-10 06:37:28.707680','2026-11-10 06:37:28.707703',NULL,29,15),(15,'San Carlos-Sipalay','source_compiled','Northern hub to southern Negros Occidental service.','Tracker Negros Occidental demo fleet','San Carlos-Sipalay, San Carlos - Sipalay, San Carlos to Sipalay, San Carlos–Sipalay',NULL,'2026-11-10 06:37:28.720891','2026-11-10 06:37:28.720915',NULL,29,26),(16,'Sipalay-San Carlos','source_compiled','Reverse of the San Carlos-Sipalay service.','Tracker Negros Occidental demo fleet','Sipalay-San Carlos, Sipalay - San Carlos, Sipalay to San Carlos, Sipalay–San Carlos',NULL,'2026-11-10 06:37:28.725875','2026-11-10 06:37:28.725902',NULL,26,29),(17,'Victorias-Hinoba-an','source_compiled','Northern Victorias corridor to southern Hinoba-an.','Tracker Negros Occidental demo fleet','Victorias-Hinoba-an, Victorias - Hinoba-an, Victorias to Hinoba-an, Victorias–Hinoba-an',NULL,'2026-11-10 06:37:28.733979','2026-11-10 06:37:28.734002',NULL,12,33),(18,'Hinoba-an-Victorias','source_compiled','Reverse of the Victorias-Hinoba-an service.','Tracker Negros Occidental demo fleet','Hinoba-an-Victorias, Hinoba-an - Victorias, Hinoba-an to Victorias, Hinoba-an–Victorias',NULL,'2026-11-10 06:37:28.738481','2026-11-10 06:37:28.738500',NULL,33,12),(19,'Sagay-Kabankalan','source_compiled','Sagay-Cadiz-Bacolod-Kabankalan service.','Tracker Negros Occidental demo fleet','Sagay-Kabankalan, Sagay - Kabankalan, Sagay to Kabankalan, Sagay–Kabankalan',NULL,'2026-11-10 06:37:28.744180','2026-11-10 06:37:28.744214',NULL,15,24),(20,'Kabankalan-Sagay','source_compiled','Reverse of the Sagay-Kabankalan service.','Tracker Negros Occidental demo fleet','Kabankalan-Sagay, Kabankalan - Sagay, Kabankalan to Sagay, Kabankalan–Sagay',NULL,'2026-11-10 06:37:28.750333','2026-11-10 06:37:28.750356',NULL,24,15);
/*!40000 ALTER TABLE `tblroute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblroutestop`
--

DROP TABLE IF EXISTS `tblroutestop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblroutestop` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sequence` int(10) unsigned NOT NULL CHECK (`sequence` >= 0),
  `distance_from_previous_km` decimal(7,2) DEFAULT NULL,
  `average_speed_kmh` int(10) unsigned NOT NULL CHECK (`average_speed_kmh` >= 0),
  `route_id` bigint(20) NOT NULL,
  `terminal_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_route_terminal` (`route_id`,`terminal_id`),
  UNIQUE KEY `uniq_route_sequence` (`route_id`,`sequence`),
  KEY `tblroutestop_terminal_id_131fd906_fk_tblterminal_id` (`terminal_id`),
  CONSTRAINT `tblroutestop_route_id_585f65fd_fk_tblroute_id` FOREIGN KEY (`route_id`) REFERENCES `tblroute` (`id`),
  CONSTRAINT `tblroutestop_terminal_id_131fd906_fk_tblterminal_id` FOREIGN KEY (`terminal_id`) REFERENCES `tblterminal` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblroutestop`
--

LOCK TABLES `tblroutestop` WRITE;
/*!40000 ALTER TABLE `tblroutestop` DISABLE KEYS */;
INSERT INTO `tblroutestop` VALUES (1,1,0.00,50,1,2),(2,2,22.00,50,1,3),(3,3,8.00,50,1,32),(4,4,12.00,50,1,22),(5,5,12.00,50,1,11),(6,6,10.00,50,1,4),(7,7,8.00,50,1,10),(8,8,19.00,50,1,15),(9,1,0.00,50,2,15),(10,2,19.00,50,2,10),(11,3,8.00,50,2,4),(12,4,10.00,50,2,11),(13,5,12.00,50,2,22),(14,6,12.00,50,2,32),(15,7,8.00,50,2,3),(16,8,22.00,50,2,2),(17,1,0.00,50,3,2),(18,2,23.67,50,3,3),(19,3,10.28,50,3,32),(20,4,15.22,50,3,22),(21,5,47.00,50,3,11),(22,6,4.87,50,3,4),(23,7,3.85,50,3,10),(24,8,17.70,50,3,15),(25,9,76.92,50,3,12),(26,10,25.96,50,3,29),(27,1,0.00,50,4,29),(28,2,25.96,50,4,12),(29,3,76.92,50,4,15),(30,4,17.70,50,4,10),(31,5,3.85,50,4,4),(32,6,4.87,50,4,11),(33,7,47.00,50,4,22),(34,8,15.22,50,4,32),(35,9,10.28,50,4,3),(36,10,23.67,50,4,2),(37,1,0.00,50,5,21),(38,2,23.39,50,5,13),(39,3,8.84,50,5,15),(40,4,17.70,50,5,10),(41,5,3.85,50,5,4),(42,6,4.87,50,5,11),(43,7,47.00,50,5,22),(44,8,15.22,50,5,32),(45,9,10.28,50,5,3),(46,10,23.67,50,5,2),(47,1,0.00,50,6,2),(48,2,23.67,50,6,3),(49,3,10.28,50,6,32),(50,4,15.22,50,6,22),(51,5,47.00,50,6,11),(52,6,4.87,50,6,4),(53,7,3.85,50,6,10),(54,8,17.70,50,6,15),(55,9,8.84,50,6,13),(56,10,23.39,50,6,21),(57,1,0.00,50,7,7),(58,2,33.53,50,7,15),(59,3,17.70,50,7,10),(60,4,3.85,50,7,4),(61,5,4.87,50,7,11),(62,6,47.00,50,7,22),(63,7,15.22,50,7,32),(64,8,10.28,50,7,3),(65,9,23.67,50,7,2),(66,1,0.00,50,8,2),(67,2,23.67,50,8,3),(68,3,10.28,50,8,32),(69,4,15.22,50,8,22),(70,5,47.00,50,8,11),(71,6,4.87,50,8,4),(72,7,3.85,50,8,10),(73,8,17.70,50,8,15),(74,9,33.53,50,8,7),(75,1,0.00,50,9,15),(76,2,33.53,50,9,7),(77,1,0.00,50,10,7),(78,2,33.53,50,10,15),(79,1,0.00,50,11,12),(80,2,25.96,50,11,29),(81,3,68.39,50,11,15),(82,1,0.00,50,12,15),(83,2,68.39,50,12,29),(84,3,25.96,50,12,12),(85,1,0.00,50,13,29),(86,2,25.96,50,13,12),(87,3,76.92,50,13,15),(88,1,0.00,50,14,15),(89,2,76.92,50,14,12),(90,3,25.96,50,14,29),(91,1,0.00,50,15,26),(92,2,71.87,50,15,1),(93,3,25.62,50,15,3),(94,4,10.28,50,15,32),(95,5,15.22,50,15,22),(96,6,47.00,50,15,11),(97,7,4.87,50,15,4),(98,8,3.85,50,15,10),(99,9,17.70,50,15,15),(100,10,76.92,50,15,12),(101,11,25.96,50,15,29),(102,1,0.00,50,16,29),(103,2,25.96,50,16,12),(104,3,76.92,50,16,15),(105,4,17.70,50,16,10),(106,5,3.85,50,16,4),(107,6,4.87,50,16,11),(108,7,47.00,50,16,22),(109,8,15.22,50,16,32),(110,9,10.28,50,16,3),(111,10,25.62,50,16,1),(112,11,71.87,50,16,26),(113,1,0.00,50,17,33),(114,2,36.25,50,17,1),(115,3,25.62,50,17,3),(116,4,10.28,50,17,32),(117,5,15.22,50,17,22),(118,6,47.00,50,17,11),(119,7,4.87,50,17,4),(120,8,3.85,50,17,10),(121,9,17.70,50,17,15),(122,10,68.39,50,17,29),(123,11,25.96,50,17,12),(124,1,0.00,50,18,12),(125,2,25.96,50,18,29),(126,3,68.39,50,18,15),(127,4,17.70,50,18,10),(128,5,3.85,50,18,4),(129,6,4.87,50,18,11),(130,7,47.00,50,18,22),(131,8,15.22,50,18,32),(132,9,10.28,50,18,3),(133,10,25.62,50,18,1),(134,11,36.25,50,18,33),(135,1,0.00,50,19,24),(136,2,41.30,50,19,5),(137,3,48.22,50,19,1),(138,4,25.62,50,19,3),(139,5,10.28,50,19,32),(140,6,15.22,50,19,22),(141,7,47.00,50,19,11),(142,8,4.87,50,19,4),(143,9,3.85,50,19,10),(144,10,17.70,50,19,15),(145,1,0.00,50,20,15),(146,2,17.70,50,20,10),(147,3,3.85,50,20,4),(148,4,4.87,50,20,11),(149,5,47.00,50,20,22),(150,6,15.22,50,20,32),(151,7,10.28,50,20,3),(152,8,25.62,50,20,1),(153,9,48.22,50,20,5),(154,10,41.30,50,20,24);
/*!40000 ALTER TABLE `tblroutestop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblbusstop`
--

DROP TABLE IF EXISTS `tblbusstop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblbusstop` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `sequence` int(10) unsigned NOT NULL CHECK (`sequence` >= 0),
  `eta` time(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_bus_stop_sequence` (`bus_id`,`sequence`),
  CONSTRAINT `tblbusstop_bus_id_9073757f_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbusstop`
--

LOCK TABLES `tblbusstop` WRITE;
/*!40000 ALTER TABLE `tblbusstop` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblbusstop` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblbusnextstoplog`
--

DROP TABLE IF EXISTS `tblbusnextstoplog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblbusnextstoplog` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `distance_km` decimal(7,2) NOT NULL,
  `average_speed_kmh` int(10) unsigned NOT NULL CHECK (`average_speed_kmh` >= 0),
  `eta_minutes` int(10) unsigned NOT NULL CHECK (`eta_minutes` >= 0),
  `eta_at` datetime(6) NOT NULL,
  `logged_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `route_id` bigint(20) DEFAULT NULL,
  `current_station_id` bigint(20) NOT NULL,
  `next_stop_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tblbusnextstoplog_bus_id_c4a663ba_fk_tblbus_id` (`bus_id`),
  KEY `tblbusnextstoplog_user_id_38d0d64a_fk_auth_user_id` (`user_id`),
  KEY `tblbusnextstoplog_route_id_915c6706_fk_tblroute_id` (`route_id`),
  KEY `tblbusnextstoplog_current_station_id_f19dd21f_fk_tblterminal_id` (`current_station_id`),
  KEY `tblbusnextstoplog_next_stop_id_fac0430a_fk_tblterminal_id` (`next_stop_id`),
  CONSTRAINT `tblbusnextstoplog_bus_id_c4a663ba_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblbusnextstoplog_current_station_id_f19dd21f_fk_tblterminal_id` FOREIGN KEY (`current_station_id`) REFERENCES `tblterminal` (`id`),
  CONSTRAINT `tblbusnextstoplog_next_stop_id_fac0430a_fk_tblterminal_id` FOREIGN KEY (`next_stop_id`) REFERENCES `tblterminal` (`id`),
  CONSTRAINT `tblbusnextstoplog_route_id_915c6706_fk_tblroute_id` FOREIGN KEY (`route_id`) REFERENCES `tblroute` (`id`),
  CONSTRAINT `tblbusnextstoplog_user_id_38d0d64a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbusnextstoplog`
--

LOCK TABLES `tblbusnextstoplog` WRITE;
/*!40000 ALTER TABLE `tblbusnextstoplog` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblbusnextstoplog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblbusterminaltap`
--

DROP TABLE IF EXISTS `tblbusterminaltap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblbusterminaltap` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `terminal_name` varchar(255) NOT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `tapped_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `left_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tblbusterminaltap_bus_id_aadad349_fk_tblbus_id` (`bus_id`),
  KEY `tblbusterminaltap_user_id_28d809fc_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblbusterminaltap_bus_id_aadad349_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblbusterminaltap_user_id_28d809fc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbusterminaltap`
--

LOCK TABLES `tblbusterminaltap` WRITE;
/*!40000 ALTER TABLE `tblbusterminaltap` DISABLE KEYS */;
INSERT INTO `tblbusterminaltap` VALUES (1,'Kabankalan',9.991700,122.812800,'2026-11-10 06:53:14.095776',2,NULL,NULL),(2,'Bacolod',10.676500,122.950900,'2026-11-10 06:11:14.095776',3,NULL,'2026-11-10 06:52:14.095776'),(3,'Narra',9.967000,122.617000,'2026-11-10 06:50:14.095776',4,NULL,'2026-11-10 07:05:14.095776'),(4,'Sipalay',9.750000,122.400000,'2026-11-10 06:18:14.095776',5,NULL,'2026-11-10 06:54:14.095776'),(5,'Candoni',9.831044,122.642981,'2026-11-10 06:47:14.095776',6,NULL,'2026-11-10 07:02:14.095776'),(6,'Hinoba-an',9.583000,122.467000,'2026-11-10 06:23:14.095776',7,NULL,'2026-11-10 06:55:14.095776'),(7,'Kabankalan',9.991700,122.812800,'2026-11-10 06:44:14.095776',8,NULL,'2026-11-10 06:59:14.095776'),(8,'San Carlos',10.496600,123.422400,'2026-11-10 06:06:14.095776',9,NULL,'2026-11-10 06:51:14.095776'),(9,'Victorias',10.900000,123.066700,'2026-11-10 06:46:14.095776',10,NULL,'2026-11-10 07:01:14.095776'),(10,'Sagay',10.891700,123.415000,'2026-11-10 06:34:14.095776',11,NULL,'2026-11-10 06:49:14.095776');
/*!40000 ALTER TABLE `tblbusterminaltap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbldemoseedstate`
--

DROP TABLE IF EXISTS `tbldemoseedstate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbldemoseedstate` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `seeded_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbldemoseedstate`
--

LOCK TABLES `tbldemoseedstate` WRITE;
/*!40000 ALTER TABLE `tbldemoseedstate` DISABLE KEYS */;
INSERT INTO `tbldemoseedstate` VALUES (1,'static-demo-buses-v1','2026-11-10 06:56:14.227747');
/*!40000 ALTER TABLE `tbldemoseedstate` ENABLE KEYS */;
UNLOCK TABLES;


--
-- ============================================================================
-- 10. DJANGO FRAMEWORK TABLES  (users, permissions, sessions, migrations)
-- ============================================================================
--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (1,'Administrator'),(2,'Conductor'),(3,'Passenger');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (1,1,1);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add info',7,'add_info'),(26,'Can change info',7,'change_info'),(27,'Can delete info',7,'delete_info'),(28,'Can view info',7,'view_info'),(29,'Can add bus',8,'add_bus'),(30,'Can change bus',8,'change_bus'),(31,'Can delete bus',8,'delete_bus'),(32,'Can view bus',8,'view_bus'),(33,'Can add route',9,'add_route'),(34,'Can change route',9,'change_route'),(35,'Can delete route',9,'delete_route'),(36,'Can view route',9,'view_route'),(37,'Can add terminal',10,'add_terminal'),(38,'Can change terminal',10,'change_terminal'),(39,'Can delete terminal',10,'delete_terminal'),(40,'Can view terminal',10,'view_terminal'),(41,'Can add advisory',11,'add_advisory'),(42,'Can change advisory',11,'change_advisory'),(43,'Can delete advisory',11,'delete_advisory'),(44,'Can view advisory',11,'view_advisory'),(45,'Can add trip',12,'add_trip'),(46,'Can change trip',12,'change_trip'),(47,'Can delete trip',12,'delete_trip'),(48,'Can view trip',12,'view_trip'),(49,'Can add prediction log',13,'add_predictionlog'),(50,'Can change prediction log',13,'change_predictionlog'),(51,'Can delete prediction log',13,'delete_predictionlog'),(52,'Can view prediction log',13,'view_predictionlog'),(53,'Can add gps ping',14,'add_gpsping'),(54,'Can change gps ping',14,'change_gpsping'),(55,'Can delete gps ping',14,'delete_gpsping'),(56,'Can view gps ping',14,'view_gpsping'),(57,'Can add feedback',15,'add_feedback'),(58,'Can change feedback',15,'change_feedback'),(59,'Can delete feedback',15,'delete_feedback'),(60,'Can view feedback',15,'view_feedback'),(61,'Can add arrival subscription',16,'add_arrivalsubscription'),(62,'Can change arrival subscription',16,'change_arrivalsubscription'),(63,'Can delete arrival subscription',16,'delete_arrivalsubscription'),(64,'Can view arrival subscription',16,'view_arrivalsubscription'),(65,'Can add favorite route',17,'add_favoriteroute'),(66,'Can change favorite route',17,'change_favoriteroute'),(67,'Can delete favorite route',17,'delete_favoriteroute'),(68,'Can view favorite route',17,'view_favoriteroute'),(69,'Can add stop',18,'add_stop'),(70,'Can change stop',18,'change_stop'),(71,'Can delete stop',18,'delete_stop'),(72,'Can view stop',18,'view_stop'),(73,'Can add bus',19,'add_bus'),(74,'Can change bus',19,'change_bus'),(75,'Can delete bus',19,'delete_bus'),(76,'Can view bus',19,'view_bus'),(77,'Can add driver',20,'add_driver'),(78,'Can change driver',20,'change_driver'),(79,'Can delete driver',20,'delete_driver'),(80,'Can view driver',20,'view_driver'),(81,'Can add conductor',21,'add_conductor'),(82,'Can change conductor',21,'change_conductor'),(83,'Can delete conductor',21,'delete_conductor'),(84,'Can view conductor',21,'view_conductor'),(89,'Can add maintenance record',23,'add_maintenancerecord'),(90,'Can change maintenance record',23,'change_maintenancerecord'),(91,'Can delete maintenance record',23,'delete_maintenancerecord'),(92,'Can view maintenance record',23,'view_maintenancerecord'),(93,'Can add trip',24,'add_trip'),(94,'Can change trip',24,'change_trip'),(95,'Can delete trip',24,'delete_trip'),(96,'Can view trip',24,'view_trip'),(97,'Can add incident',25,'add_incident'),(98,'Can change incident',25,'change_incident'),(99,'Can delete incident',25,'delete_incident'),(100,'Can view incident',25,'view_incident'),(101,'Can add booking',26,'add_booking'),(102,'Can change booking',26,'change_booking'),(103,'Can delete booking',26,'delete_booking'),(104,'Can view booking',26,'view_booking'),(105,'Can add bus terminal tap',27,'add_busterminaltap'),(106,'Can change bus terminal tap',27,'change_busterminaltap'),(107,'Can delete bus terminal tap',27,'delete_busterminaltap'),(108,'Can view bus terminal tap',27,'view_busterminaltap'),(109,'Can add terminal',28,'add_terminal'),(110,'Can change terminal',28,'change_terminal'),(111,'Can delete terminal',28,'delete_terminal'),(112,'Can view terminal',28,'view_terminal'),(113,'Can add route',29,'add_route'),(114,'Can change route',29,'change_route'),(115,'Can delete route',29,'delete_route'),(116,'Can view route',29,'view_route'),(117,'Can add route stop',30,'add_routestop'),(118,'Can change route stop',30,'change_routestop'),(119,'Can delete route stop',30,'delete_routestop'),(120,'Can view route stop',30,'view_routestop'),(121,'Can add bus next stop log',31,'add_busnextstoplog'),(122,'Can change bus next stop log',31,'change_busnextstoplog'),(123,'Can delete bus next stop log',31,'delete_busnextstoplog'),(124,'Can view bus next stop log',31,'view_busnextstoplog'),(125,'Can add demo seed state',32,'add_demoseedstate'),(126,'Can change demo seed state',32,'change_demoseedstate'),(127,'Can delete demo seed state',32,'delete_demoseedstate'),(128,'Can view demo seed state',32,'view_demoseedstate'),(129,'Can add bus stop',33,'add_busstop'),(130,'Can change bus stop',33,'change_busstop'),(131,'Can delete bus stop',33,'delete_busstop'),(132,'Can view bus stop',33,'view_busstop');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(26,'bookings','booking'),(19,'bus','bus'),(31,'bus','busnextstoplog'),(33,'bus','busstop'),(27,'bus','busterminaltap'),(32,'bus','demoseedstate'),(29,'bus','route'),(30,'bus','routestop'),(28,'bus','terminal'),(21,'conductor','conductor'),(5,'contenttypes','contenttype'),(20,'driver','driver'),(25,'incidents','incident'),(7,'info','info'),(23,'maintenance','maintenancerecord'),(6,'sessions','session'),(11,'tracking','advisory'),(16,'tracking','arrivalsubscription'),(8,'tracking','bus'),(17,'tracking','favoriteroute'),(15,'tracking','feedback'),(14,'tracking','gpsping'),(13,'tracking','predictionlog'),(9,'tracking','route'),(18,'tracking','stop'),(10,'tracking','terminal'),(12,'tracking','trip'),(24,'trips','trip');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-15 07:07:24.512107'),(2,'auth','0001_initial','2026-10-15 07:07:24.851872'),(3,'admin','0001_initial','2026-10-15 07:07:24.925903'),(4,'admin','0002_logentry_remove_auto_add','2026-10-15 07:07:24.935883'),(5,'admin','0003_logentry_add_action_flag_choices','2026-10-15 07:07:24.948717'),(6,'contenttypes','0002_remove_content_type_name','2026-10-15 07:07:24.992419'),(7,'auth','0002_alter_permission_name_max_length','2026-10-15 07:07:25.028098'),(8,'auth','0003_alter_user_email_max_length','2026-10-15 07:07:25.044943'),(9,'auth','0004_alter_user_username_opts','2026-10-15 07:07:25.054826'),(10,'auth','0005_alter_user_last_login_null','2026-10-15 07:07:25.081409'),(11,'auth','0006_require_contenttypes_0002','2026-10-15 07:07:25.083830'),(12,'auth','0007_alter_validators_add_error_messages','2026-10-15 07:07:25.092145'),(13,'auth','0008_alter_user_username_max_length','2026-10-15 07:07:25.106537'),(14,'auth','0009_alter_user_last_name_max_length','2026-10-15 07:07:25.121270'),(15,'auth','0010_alter_group_name_max_length','2026-10-15 07:07:25.137288'),(16,'auth','0011_update_proxy_permissions','2026-10-15 07:07:25.146239'),(17,'auth','0012_alter_user_first_name_max_length','2026-10-15 07:07:25.164796'),(18,'info','0001_initial','2026-10-15 07:07:25.209012'),(19,'sessions','0001_initial','2026-10-15 07:07:25.241807'),(21,'bus','0001_initial','2026-10-16 15:06:21.697846'),(22,'bus','0002_bus_current_location_bus_last_gps_update_and_more','2026-10-16 15:06:21.778199'),(23,'bookings','0001_initial','2026-10-16 15:06:21.885937'),(24,'conductor','0001_initial','2026-10-16 15:06:22.006974'),(25,'driver','0001_initial','2026-10-16 15:06:22.077594'),(26,'incidents','0001_initial','2026-10-16 15:06:22.148910'),(27,'maintenance','0001_initial','2026-10-16 15:06:22.222383'),(33,'trips','0001_initial','2026-10-16 15:06:22.815635'),(34,'bus','0003_bus_movement_reason','2026-11-10 06:37:27.188540'),(35,'bus','0004_bus_qr_token_busterminaltap','2026-11-10 06:37:27.430395'),(36,'bus','0005_busterminaltap_left_at','2026-11-10 06:37:27.489467'),(37,'bus','0006_terminal_route_routestop_busnextstoplog_and_more','2026-11-10 06:37:28.061685'),(38,'bus','0007_bus_actual_departure_bus_bay_bus_current_terminal_and_more','2026-11-10 06:37:28.371147'),(39,'bus','0008_demoseedstate_bus_next_terminal_and_more','2026-11-10 06:37:28.464313'),(40,'bus','0009_rename_cauayan_terminal_to_narra','2026-11-10 06:37:28.513301'),(41,'bus','0010_alter_bus_next_stop','2026-11-10 06:37:28.533652'),(42,'bus','0011_scope_negros_occidental','2026-11-10 06:37:28.761903'),(43,'bus','0012_busstop','2026-11-10 06:37:28.820802');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('31bp7qs01qiel5uisgcy12t11c2aozrx','eyJmYWlsZWRfYXR0ZW1wdHMiOjF9:1xI6KZ:9kGAmw8-Q60pUlE3Kv-La8gof7XRLKKZOoVrdn_wJ4Q','2026-10-31 15:28:19.435233'),('4r29oqtja1hudhahdom33o6u5pu7f8ra','.eJxVjMEOgyAQBf9lz4agBFCPvfcbyAJLpSI2gqem_15NvHh9M_O-EDAm8gZrpeVTC4y8gbS62dS4EIx5T6kBg3udzF5oM9HDCAJum0U3Uz6Bf2N-rcytuW7RslNhFy3suXpKj8u9HUxYpqPuOAXRo6SuDU4j8R6Fk0EFT1IGS7rXchB2sKJTSkmrEANHrxEPT7UWfn_T5EYb:1xI6KY:HtshzQniJIrSChsmVBweDPTeQXt_zhMi6Fo9O6GL54o','2026-10-31 15:28:18.890867'),('54prp7oh3avki7v59e1rxuk4dxhvyztv','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xHFt8:7TAjUVWC5weA_XJ7UmnkAC3Hb3haWrUEOVaFs4do9aA','2026-10-29 07:28:30.131981'),('cxj7ru11sldcvmlbb9ea4zedxguocrdd','.eJxVjMsOwiAQRf-FtSFCebQu3fsNZJgZpGogKe3K-O-WpAvdnnPufYsA25rD1ngJM4mLUOL0yyLgk0sX9IByrxJrWZc5yp7IwzZ5q8Sv69H-HWRoua-TSZy0BoRoyaD3itx0psTGRmsQbFTj4FmjM3Eicjj6vWL0ww6AxecLG1M5Kw:1xQfto:jEzI5T2quv394MR19i6h-srJH3Dx5EGP0FczyGT-fRk','2026-11-24 07:04:08.753670'),('dwflf9839u7c1esyyl6xl69gzo4zxmur','.eJxVjMEOgyAQBf9lz4agBFCPvfcbyAJLpSI2gqem_15NvHh9M_O-EDAm8gZrpeVTC4y8gbS62dS4EIx5T6kBg3udzF5oM9HDCAJum0U3Uz6Bf2N-rcytuW7RslNhFy3suXpKj8u9HUxYpqPuOAXRo6SuDU4j8R6Fk0EFT1IGS7rXchB2sKJTSkmrEANHrxEPT7UWfn_T5EYb:1xI6KZ:R6fGUIJHdkbMuWZ0UvYlQy6U_AKL9gheW40MkzNoNcs','2026-10-31 15:28:19.164886'),('ghjcx2l0mebyz4oz6352jwwrbmog4snr','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xHbmI:wsupKRB8Tjs0e0PQoj994A0QzoS4QbPy_Ekuy7tO7Rw','2026-10-30 06:50:54.156384'),('i4v8pac2xj0u1egzlv1lw601ar7k3jvc','.eJxVjEsOAiEQBe_C2hBokI9L956BNHQrowaSYWZlvLtOMgvdvqp6L5FwXWpaB89pInESIA6_W8by4LYBumO7dVl6W-Ypy02ROx3y0omf5939O6g46rd2QYG3PmYOXnm4RnNEKsSagHTwwdsYrbJsKMeiHEU2xgJwZqe1IRTvD8P3N1Q:1xI6JF:kb1ZkmEwBhns2EvPyuEUZXOfSnsUaafGj2-4iN4_UOo','2026-10-31 15:26:57.009694'),('iezsz72fc333nfmye0huun13ldf8an57','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xI6ON:JOF0V8Zl9D7OOqEnzgy0kPwWjitfvZcWxuohXkglSo4','2026-10-31 15:32:15.045079'),('p0lwfyk68kn17his8fqfi0wft8lqgxnv','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xQfw1:3fXGx7g9odwfI4uh4FJ46Hs94zvgrtsLNOvisCvGyu8','2026-11-24 07:06:25.205736'),('s5g55503gw848qyikubgv7f87k52jtx7','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xI6ZW:0Q50CTn-_M1yPB8tQ-6d3APlNWhcIF8GQDCyFREwOLE','2026-10-31 15:43:46.409345'),('v0mb8978xv8l00vrmlu8ezpa55whw4gh','eyJmYWlsZWRfYXR0ZW1wdHMiOjF9:1xHkIn:YRlQ0uI9_iW10Iike2m9TasW3cYTYQrAyfZ3MrCZYMk','2026-10-30 15:57:01.006568'),('vp6b0kmsz94p9f9wi00gkv0sbt2nztwu','.eJxVjMsOwiAQRf-FtSFCebQu3fsNZJgZpGogKe3K-O-WpAvdnnPufYsA25rD1ngJM4mLUOL0yyLgk0sX9IByrxJrWZc5yp7IwzZ5q8Sv69H-HWRoua-TSZy0BoRoyaD3itx0psTGRmsQbFTj4FmjM3Eicjj6vWL0ww6AxecLG1M5Kw:1xQfnp:UsfqY6HaIXYgpZ6wtGDM9kRn-Ime3dDSBnhmMGVa9ag','2026-11-24 06:57:57.701720');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-10 15:06:52
