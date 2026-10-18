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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add info',7,'add_info'),(26,'Can change info',7,'change_info'),(27,'Can delete info',7,'delete_info'),(28,'Can view info',7,'view_info'),(29,'Can add bus',8,'add_bus'),(30,'Can change bus',8,'change_bus'),(31,'Can delete bus',8,'delete_bus'),(32,'Can view bus',8,'view_bus'),(33,'Can add route',9,'add_route'),(34,'Can change route',9,'change_route'),(35,'Can delete route',9,'delete_route'),(36,'Can view route',9,'view_route'),(37,'Can add terminal',10,'add_terminal'),(38,'Can change terminal',10,'change_terminal'),(39,'Can delete terminal',10,'delete_terminal'),(40,'Can view terminal',10,'view_terminal'),(41,'Can add advisory',11,'add_advisory'),(42,'Can change advisory',11,'change_advisory'),(43,'Can delete advisory',11,'delete_advisory'),(44,'Can view advisory',11,'view_advisory'),(45,'Can add trip',12,'add_trip'),(46,'Can change trip',12,'change_trip'),(47,'Can delete trip',12,'delete_trip'),(48,'Can view trip',12,'view_trip'),(49,'Can add prediction log',13,'add_predictionlog'),(50,'Can change prediction log',13,'change_predictionlog'),(51,'Can delete prediction log',13,'delete_predictionlog'),(52,'Can view prediction log',13,'view_predictionlog'),(53,'Can add gps ping',14,'add_gpsping'),(54,'Can change gps ping',14,'change_gpsping'),(55,'Can delete gps ping',14,'delete_gpsping'),(56,'Can view gps ping',14,'view_gpsping'),(57,'Can add feedback',15,'add_feedback'),(58,'Can change feedback',15,'change_feedback'),(59,'Can delete feedback',15,'delete_feedback'),(60,'Can view feedback',15,'view_feedback'),(61,'Can add arrival subscription',16,'add_arrivalsubscription'),(62,'Can change arrival subscription',16,'change_arrivalsubscription'),(63,'Can delete arrival subscription',16,'delete_arrivalsubscription'),(64,'Can view arrival subscription',16,'view_arrivalsubscription'),(65,'Can add favorite route',17,'add_favoriteroute'),(66,'Can change favorite route',17,'change_favoriteroute'),(67,'Can delete favorite route',17,'delete_favoriteroute'),(68,'Can view favorite route',17,'view_favoriteroute'),(69,'Can add stop',18,'add_stop'),(70,'Can change stop',18,'change_stop'),(71,'Can delete stop',18,'delete_stop'),(72,'Can view stop',18,'view_stop'),(73,'Can add bus',19,'add_bus'),(74,'Can change bus',19,'change_bus'),(75,'Can delete bus',19,'delete_bus'),(76,'Can view bus',19,'view_bus'),(77,'Can add driver',20,'add_driver'),(78,'Can change driver',20,'change_driver'),(79,'Can delete driver',20,'delete_driver'),(80,'Can view driver',20,'view_driver'),(81,'Can add conductor',21,'add_conductor'),(82,'Can change conductor',21,'change_conductor'),(83,'Can delete conductor',21,'delete_conductor'),(84,'Can view conductor',21,'view_conductor'),(85,'Can add passenger',22,'add_passenger'),(86,'Can change passenger',22,'change_passenger'),(87,'Can delete passenger',22,'delete_passenger'),(88,'Can view passenger',22,'view_passenger'),(89,'Can add maintenance record',23,'add_maintenancerecord'),(90,'Can change maintenance record',23,'change_maintenancerecord'),(91,'Can delete maintenance record',23,'delete_maintenancerecord'),(92,'Can view maintenance record',23,'view_maintenancerecord'),(93,'Can add trip',24,'add_trip'),(94,'Can change trip',24,'change_trip'),(95,'Can delete trip',24,'delete_trip'),(96,'Can view trip',24,'view_trip'),(97,'Can add incident',25,'add_incident'),(98,'Can change incident',25,'change_incident'),(99,'Can delete incident',25,'delete_incident'),(100,'Can view incident',25,'view_incident'),(101,'Can add booking',26,'add_booking'),(102,'Can change booking',26,'change_booking'),(103,'Can delete booking',26,'delete_booking'),(104,'Can view booking',26,'view_booking');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

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
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$720000$bOj5VBWtCXUDkvqS0bEcbq$LYdO8A8VA9CspX3XllYy93oquLorg67N4qI9+oeIoxo=','2026-10-17 15:43:46.404800',1,'admin','','','admin@vallacar.local',1,1,'2026-10-15 07:26:55.224965');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(26,'bookings','booking'),(19,'bus','bus'),(21,'conductor','conductor'),(5,'contenttypes','contenttype'),(20,'driver','driver'),(25,'incidents','incident'),(7,'info','info'),(23,'maintenance','maintenancerecord'),(22,'passengers','passenger'),(6,'sessions','session'),(11,'tracking','advisory'),(16,'tracking','arrivalsubscription'),(8,'tracking','bus'),(17,'tracking','favoriteroute'),(15,'tracking','feedback'),(14,'tracking','gpsping'),(13,'tracking','predictionlog'),(9,'tracking','route'),(18,'tracking','stop'),(10,'tracking','terminal'),(12,'tracking','trip'),(24,'trips','trip');
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
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-10-15 07:07:24.512107'),(2,'auth','0001_initial','2026-10-15 07:07:24.851872'),(3,'admin','0001_initial','2026-10-15 07:07:24.925903'),(4,'admin','0002_logentry_remove_auto_add','2026-10-15 07:07:24.935883'),(5,'admin','0003_logentry_add_action_flag_choices','2026-10-15 07:07:24.948717'),(6,'contenttypes','0002_remove_content_type_name','2026-10-15 07:07:24.992419'),(7,'auth','0002_alter_permission_name_max_length','2026-10-15 07:07:25.028098'),(8,'auth','0003_alter_user_email_max_length','2026-10-15 07:07:25.044943'),(9,'auth','0004_alter_user_username_opts','2026-10-15 07:07:25.054826'),(10,'auth','0005_alter_user_last_login_null','2026-10-15 07:07:25.081409'),(11,'auth','0006_require_contenttypes_0002','2026-10-15 07:07:25.083830'),(12,'auth','0007_alter_validators_add_error_messages','2026-10-15 07:07:25.092145'),(13,'auth','0008_alter_user_username_max_length','2026-10-15 07:07:25.106537'),(14,'auth','0009_alter_user_last_name_max_length','2026-10-15 07:07:25.121270'),(15,'auth','0010_alter_group_name_max_length','2026-10-15 07:07:25.137288'),(16,'auth','0011_update_proxy_permissions','2026-10-15 07:07:25.146239'),(17,'auth','0012_alter_user_first_name_max_length','2026-10-15 07:07:25.164796'),(18,'info','0001_initial','2026-10-15 07:07:25.209012'),(19,'sessions','0001_initial','2026-10-15 07:07:25.241807'),(21,'bus','0001_initial','2026-10-16 15:06:21.697846'),(22,'bus','0002_bus_current_location_bus_last_gps_update_and_more','2026-10-16 15:06:21.778199'),(23,'bookings','0001_initial','2026-10-16 15:06:21.885937'),(24,'conductor','0001_initial','2026-10-16 15:06:22.006974'),(25,'driver','0001_initial','2026-10-16 15:06:22.077594'),(26,'incidents','0001_initial','2026-10-16 15:06:22.148910'),(27,'maintenance','0001_initial','2026-10-16 15:06:22.222383'),(28,'passengers','0001_initial','2026-10-16 15:06:22.306503'),(29,'passengers','0002_passenger_passenger_type','2026-10-16 15:06:22.336868'),(30,'passengers','0003_remove_passenger_bus','2026-10-16 15:06:22.613153'),(31,'passengers','0004_passenger_bus','2026-10-16 15:06:22.664158'),(32,'passengers','0005_alter_passenger_passenger_type','2026-10-16 15:06:22.685761'),(33,'trips','0001_initial','2026-10-16 15:06:22.815635');
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
INSERT INTO `django_session` VALUES ('31bp7qs01qiel5uisgcy12t11c2aozrx','eyJmYWlsZWRfYXR0ZW1wdHMiOjF9:1xI6KZ:9kGAmw8-Q60pUlE3Kv-La8gof7XRLKKZOoVrdn_wJ4Q','2026-10-31 15:28:19.435233'),('4r29oqtja1hudhahdom33o6u5pu7f8ra','.eJxVjMEOgyAQBf9lz4agBFCPvfcbyAJLpSI2gqem_15NvHh9M_O-EDAm8gZrpeVTC4y8gbS62dS4EIx5T6kBg3udzF5oM9HDCAJum0U3Uz6Bf2N-rcytuW7RslNhFy3suXpKj8u9HUxYpqPuOAXRo6SuDU4j8R6Fk0EFT1IGS7rXchB2sKJTSkmrEANHrxEPT7UWfn_T5EYb:1xI6KY:HtshzQniJIrSChsmVBweDPTeQXt_zhMi6Fo9O6GL54o','2026-10-31 15:28:18.890867'),('54prp7oh3avki7v59e1rxuk4dxhvyztv','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xHFt8:7TAjUVWC5weA_XJ7UmnkAC3Hb3haWrUEOVaFs4do9aA','2026-10-29 07:28:30.131981'),('dwflf9839u7c1esyyl6xl69gzo4zxmur','.eJxVjMEOgyAQBf9lz4agBFCPvfcbyAJLpSI2gqem_15NvHh9M_O-EDAm8gZrpeVTC4y8gbS62dS4EIx5T6kBg3udzF5oM9HDCAJum0U3Uz6Bf2N-rcytuW7RslNhFy3suXpKj8u9HUxYpqPuOAXRo6SuDU4j8R6Fk0EFT1IGS7rXchB2sKJTSkmrEANHrxEPT7UWfn_T5EYb:1xI6KZ:R6fGUIJHdkbMuWZ0UvYlQy6U_AKL9gheW40MkzNoNcs','2026-10-31 15:28:19.164886'),('ghjcx2l0mebyz4oz6352jwwrbmog4snr','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xHbmI:wsupKRB8Tjs0e0PQoj994A0QzoS4QbPy_Ekuy7tO7Rw','2026-10-30 06:50:54.156384'),('i4v8pac2xj0u1egzlv1lw601ar7k3jvc','.eJxVjEsOAiEQBe_C2hBokI9L956BNHQrowaSYWZlvLtOMgvdvqp6L5FwXWpaB89pInESIA6_W8by4LYBumO7dVl6W-Ypy02ROx3y0omf5939O6g46rd2QYG3PmYOXnm4RnNEKsSagHTwwdsYrbJsKMeiHEU2xgJwZqe1IRTvD8P3N1Q:1xI6JF:kb1ZkmEwBhns2EvPyuEUZXOfSnsUaafGj2-4iN4_UOo','2026-10-31 15:26:57.009694'),('iezsz72fc333nfmye0huun13ldf8an57','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xI6ON:JOF0V8Zl9D7OOqEnzgy0kPwWjitfvZcWxuohXkglSo4','2026-10-31 15:32:15.045079'),('s5g55503gw848qyikubgv7f87k52jtx7','.eJxVjDsOgzAQBe-yNbL4GAyU6XMGa727DgRjIjBVlLsHJBramXnvCx7HIGwxJZk_aYM-zyAsNNk0zgJ93EPIwOKeBrtvstqRoYcCbswhTRJPwW-Mr0XREtM6OnUm6rKbei4s4XG1t4MBt-Fce-3FlyUSupo1GVNw0-XsRdeu1oS1K9rKSEmNdh1zQ605KiFTHQAFfn_qRkZX:1xI6ZW:0Q50CTn-_M1yPB8tQ-6d3APlNWhcIF8GQDCyFREwOLE','2026-10-31 15:43:46.409345'),('v0mb8978xv8l00vrmlu8ezpa55whw4gh','eyJmYWlsZWRfYXR0ZW1wdHMiOjF9:1xHkIn:YRlQ0uI9_iW10Iike2m9TasW3cYTYQrAyfZ3MrCZYMk','2026-10-30 15:57:01.006568');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tblbooking`
--

DROP TABLE IF EXISTS `tblbooking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblbooking` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `passenger_name` varchar(255) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `pickup` varchar(255) NOT NULL,
  `seats` int(10) unsigned NOT NULL CHECK (`seats` >= 0),
  `status` varchar(20) NOT NULL,
  `reference` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bus_id` bigint(20) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference` (`reference`),
  KEY `tblbooking_bus_id_21312c4a_fk_tblbus_id` (`bus_id`),
  KEY `tblbooking_user_id_6cb8cea6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblbooking_bus_id_21312c4a_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblbooking_user_id_6cb8cea6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbooking`
--

LOCK TABLES `tblbooking` WRITE;
/*!40000 ALTER TABLE `tblbooking` DISABLE KEYS */;
/*!40000 ALTER TABLE `tblbooking` ENABLE KEYS */;
UNLOCK TABLES;

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `bus_number` (`bus_number`),
  UNIQUE KEY `plate_number` (`plate_number`),
  KEY `tblbus_user_id_c19f51cc_fk_auth_user_id` (`user_id`),
  CONSTRAINT `tblbus_user_id_c19f51cc_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblbus`
--

LOCK TABLES `tblbus` WRITE;
/*!40000 ALTER TABLE `tblbus` DISABLE KEYS */;
INSERT INTO `tblbus` VALUES (1,'t76775','46745',1,'Kabankalan','active','2026-10-17 15:01:37.042480','2026-10-17 15:06:48.141446',1,'Bacolod','2026-10-17 15:06:48.141384',0.000010,0.000001,'en_route');
/*!40000 ALTER TABLE `tblbus` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Table structure for table `tblpassenger`
--

DROP TABLE IF EXISTS `tblpassenger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tblpassenger` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `age` int(10) unsigned NOT NULL CHECK (`age` >= 0),
  `contact` varchar(50) NOT NULL,
  `address` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `passenger_type` varchar(20) NOT NULL,
  `bus_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tblpassenger_user_id_478abf9c_fk_auth_user_id` (`user_id`),
  KEY `tblpassenger_bus_id_2825593a_fk_tblbus_id` (`bus_id`),
  CONSTRAINT `tblpassenger_bus_id_2825593a_fk_tblbus_id` FOREIGN KEY (`bus_id`) REFERENCES `tblbus` (`id`),
  CONSTRAINT `tblpassenger_user_id_478abf9c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tblpassenger`
--

LOCK TABLES `tblpassenger` WRITE;
/*!40000 ALTER TABLE `tblpassenger` DISABLE KEYS */;
INSERT INTO `tblpassenger` VALUES (1,'ffff',23,'8097898','yguygjhg','','2026-10-17 15:03:49.798749','2026-10-17 15:03:49.798772',1,'student',1);
/*!40000 ALTER TABLE `tblpassenger` ENABLE KEYS */;
UNLOCK TABLES;

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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-18 19:38:51
