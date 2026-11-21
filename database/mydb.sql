CREATE DATABASE  IF NOT EXISTS `mydb` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `mydb`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mydb
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `date_time`
--

DROP TABLE IF EXISTS `date_time`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `date_time` (
  `date_time_id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `time` time NOT NULL,
  PRIMARY KEY (`date_time_id`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `date_time`
--

LOCK TABLES `date_time` WRITE;
/*!40000 ALTER TABLE `date_time` DISABLE KEYS */;
INSERT INTO `date_time` VALUES (1,'2026-11-21','04:30:00'),(2,'2026-11-21','05:10:00'),(3,'2026-11-21','05:55:00'),(4,'2026-11-21','08:30:00'),(5,'2026-11-21','09:00:00'),(6,'2026-11-21','10:20:00'),(7,'2026-11-21','08:47:00'),(8,'2026-11-21','09:05:00'),(9,'2026-11-21','15:09:00'),(10,'2026-11-21','16:00:00'),(11,'2026-11-21','04:30:00'),(12,'2026-11-21','05:10:00'),(13,'2026-11-21','05:55:00'),(14,'2026-11-21','08:30:00'),(15,'2026-11-21','09:00:00'),(16,'2026-11-21','10:20:00'),(17,'2026-11-21','08:47:00'),(18,'2026-11-21','09:05:00'),(19,'2026-11-21','15:09:00'),(20,'2026-11-21','16:00:00'),(21,'2026-11-21','04:30:00'),(22,'2026-11-21','05:10:00'),(23,'2026-11-21','05:55:00'),(24,'2026-11-21','08:30:00'),(25,'2026-11-21','09:00:00'),(26,'2026-11-21','10:20:00'),(27,'2026-11-21','08:47:00'),(28,'2026-11-21','09:05:00'),(29,'2026-11-21','15:09:00'),(30,'2026-11-21','16:00:00'),(31,'2026-11-21','04:30:00'),(32,'2026-11-21','05:10:00'),(33,'2026-11-21','05:55:00'),(34,'2026-11-21','08:30:00'),(35,'2026-11-21','09:00:00'),(36,'2026-11-21','10:20:00'),(37,'2026-11-21','08:47:00'),(38,'2026-11-21','09:05:00'),(39,'2026-11-21','15:09:00'),(40,'2026-11-21','16:00:00'),(41,'2026-11-21','04:30:00'),(42,'2026-11-21','05:10:00'),(43,'2026-11-21','05:55:00'),(44,'2026-11-21','08:30:00'),(45,'2026-11-21','09:00:00'),(46,'2026-11-21','10:20:00'),(47,'2026-11-21','08:47:00'),(48,'2026-11-21','09:05:00'),(49,'2026-11-21','15:09:00'),(50,'2026-11-21','16:00:00'),(51,'2026-11-21','04:30:00'),(52,'2026-11-21','05:10:00'),(53,'2026-11-21','05:55:00'),(54,'2026-11-21','08:30:00'),(55,'2026-11-21','09:00:00'),(56,'2026-11-21','10:20:00'),(57,'2026-11-21','08:47:00'),(58,'2026-11-21','09:05:00'),(59,'2026-11-21','15:09:00'),(60,'2026-11-21','16:00:00'),(61,'2026-11-21','04:30:00'),(62,'2026-11-21','05:10:00'),(63,'2026-11-21','05:55:00'),(64,'2026-11-21','08:30:00'),(65,'2026-11-21','09:00:00'),(66,'2026-11-21','10:20:00'),(67,'2026-11-21','08:47:00'),(68,'2026-11-21','09:05:00'),(69,'2026-11-21','15:09:00'),(70,'2026-11-21','16:00:00'),(71,'2026-11-21','04:30:00'),(72,'2026-11-21','05:10:00'),(73,'2026-11-21','05:55:00'),(74,'2026-11-21','08:30:00'),(75,'2026-11-21','09:00:00'),(76,'2026-11-21','10:20:00'),(77,'2026-11-21','08:47:00'),(78,'2026-11-21','09:05:00'),(79,'2026-11-21','15:09:00'),(80,'2026-11-21','16:00:00'),(81,'2026-11-21','04:30:00'),(82,'2026-11-21','05:10:00'),(83,'2026-11-21','05:55:00'),(84,'2026-11-21','08:30:00'),(85,'2026-11-21','09:00:00'),(86,'2026-11-21','10:20:00'),(87,'2026-11-21','08:47:00'),(88,'2026-11-21','09:05:00'),(89,'2026-11-21','15:09:00'),(90,'2026-11-21','16:00:00'),(91,'2026-11-21','04:30:00'),(92,'2026-11-21','05:10:00'),(93,'2026-11-21','05:55:00'),(94,'2026-11-21','08:30:00'),(95,'2026-11-21','09:00:00'),(96,'2026-11-21','10:20:00'),(97,'2026-11-21','08:47:00'),(98,'2026-11-21','09:05:00'),(99,'2026-11-21','15:09:00'),(100,'2026-11-21','16:00:00'),(101,'2026-11-21','04:30:00'),(102,'2026-11-21','05:10:00'),(103,'2026-11-21','05:55:00'),(104,'2026-11-21','08:30:00'),(105,'2026-11-21','09:00:00'),(106,'2026-11-21','10:20:00'),(107,'2026-11-21','08:47:00'),(108,'2026-11-21','09:05:00'),(109,'2026-11-21','15:09:00'),(110,'2026-11-21','16:00:00'),(111,'2026-11-21','04:30:00'),(112,'2026-11-21','05:10:00'),(113,'2026-11-21','05:55:00'),(114,'2026-11-21','08:30:00'),(115,'2026-11-21','09:00:00'),(116,'2026-11-21','10:20:00'),(117,'2026-11-21','08:47:00'),(118,'2026-11-21','09:05:00'),(119,'2026-11-21','15:09:00'),(120,'2026-11-21','16:00:00'),(121,'2026-11-21','04:30:00'),(122,'2026-11-21','05:10:00'),(123,'2026-11-21','05:55:00'),(124,'2026-11-21','08:30:00'),(125,'2026-11-21','09:00:00'),(126,'2026-11-21','10:20:00'),(127,'2026-11-21','08:47:00'),(128,'2026-11-21','09:05:00'),(129,'2026-11-21','15:09:00'),(130,'2026-11-21','16:00:00'),(131,'2026-11-21','04:30:00'),(132,'2026-11-21','05:10:00'),(133,'2026-11-21','05:55:00'),(134,'2026-11-21','08:30:00'),(135,'2026-11-21','09:00:00'),(136,'2026-11-21','10:20:00'),(137,'2026-11-21','08:47:00'),(138,'2026-11-21','09:05:00'),(139,'2026-11-21','15:09:00'),(140,'2026-11-21','16:00:00'),(141,'2026-11-21','04:30:00'),(142,'2026-11-21','05:10:00'),(143,'2026-11-21','05:55:00'),(144,'2026-11-21','08:30:00'),(145,'2026-11-21','09:00:00'),(146,'2026-11-21','10:20:00'),(147,'2026-11-21','08:47:00'),(148,'2026-11-21','09:05:00'),(149,'2026-11-21','15:09:00'),(150,'2026-11-21','16:00:00');
/*!40000 ALTER TABLE `date_time` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `harvest_crates`
--

DROP TABLE IF EXISTS `harvest_crates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `harvest_crates` (
  `harvest_crates_id` int NOT NULL AUTO_INCREMENT,
  `total_crates_number` int NOT NULL,
  `tree_number` int DEFAULT NULL,
  `rejected_crates_number` int NOT NULL,
  `team_id` int NOT NULL,
  `date_time_id` int NOT NULL,
  PRIMARY KEY (`harvest_crates_id`),
  KEY `fk_harvest crates_team1_idx` (`team_id`),
  KEY `fk_harvest crates_date&time1_idx` (`date_time_id`),
  CONSTRAINT `fk_harvest crates_date&time1` FOREIGN KEY (`date_time_id`) REFERENCES `date_time` (`date_time_id`),
  CONSTRAINT `fk_harvest crates_team1` FOREIGN KEY (`team_id`) REFERENCES `team` (`team_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `harvest_crates`
--

LOCK TABLES `harvest_crates` WRITE;
/*!40000 ALTER TABLE `harvest_crates` DISABLE KEYS */;
INSERT INTO `harvest_crates` VALUES (4,100,20,5,1,4),(5,150,25,10,2,5),(6,120,22,8,3,6),(7,100,20,5,1,4),(8,150,25,10,2,5),(9,120,22,8,3,6),(10,100,20,5,1,4),(11,150,25,10,2,5),(12,120,22,8,3,6),(13,100,20,5,1,4),(14,150,25,10,2,5),(15,120,22,8,3,6);
/*!40000 ALTER TABLE `harvest_crates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login` (
  `login_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`login_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login`
--

LOCK TABLES `login` WRITE;
/*!40000 ALTER TABLE `login` DISABLE KEYS */;
INSERT INTO `login` VALUES (1,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(2,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(3,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(4,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(5,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(6,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(7,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(8,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(9,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(10,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(11,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(12,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(13,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(14,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),(15,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
/*!40000 ALTER TABLE `login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logistics`
--

DROP TABLE IF EXISTS `logistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logistics` (
  `trip_number` int NOT NULL,
  `vehicle_type` enum('Truck','Tractor','Bakkie','Other') NOT NULL,
  `vehicle_registration` varchar(45) NOT NULL,
  `destination` enum('Pack house','Farm shed','Other') NOT NULL,
  `number_crates_loaded` int NOT NULL,
  `number_crates_at_destination` int NOT NULL,
  `driver_id` int NOT NULL,
  `date_time_id` int NOT NULL,
  `block` enum('Block 1','Block 2','Block 3','Block 4','Block 5','Block 6','Block 7') DEFAULT NULL,
  `logistics_id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`logistics_id`),
  KEY `fk_logistics_person1_idx` (`driver_id`),
  KEY `fk_logistics_date&time1_idx` (`date_time_id`),
  CONSTRAINT `fk_logistics_date&time1` FOREIGN KEY (`date_time_id`) REFERENCES `date_time` (`date_time_id`),
  CONSTRAINT `fk_logistics_person1` FOREIGN KEY (`driver_id`) REFERENCES `person` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logistics`
--

LOCK TABLES `logistics` WRITE;
/*!40000 ALTER TABLE `logistics` DISABLE KEYS */;
INSERT INTO `logistics` VALUES (1,'Tractor','XYZ-123','Pack house',100,80,1,7,'Block 1',1),(2,'Truck','ABC-456','Farm shed',150,120,2,8,'Block 1',2),(3,'Truck','JKL-901','Pack house',100,80,4,9,'Block 1',3),(1,'Tractor','PMG-123','Pack house',100,80,1,7,'Block 1',4),(2,'Truck','LXY-456','Farm shed',150,120,2,8,'Block 1',5),(3,'Truck','JKL-901','Pack house',100,80,4,9,'Block 1',6),(1,'Tractor','PMG-123','Pack house',100,80,1,7,'Block 1',7),(2,'Truck','LXY-456','Farm shed',150,120,2,8,'Block 1',8),(3,'Truck','JKL-901','Pack house',100,80,4,9,'Block 1',9),(1,'Tractor','PMG-123','Pack house',100,80,1,7,'Block 1',10),(2,'Truck','LXY-456','Farm shed',150,120,2,8,'Block 1',11),(3,'Truck','JKL-901','Pack house',100,80,4,9,'Block 1',12);
/*!40000 ALTER TABLE `logistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operations`
--

DROP TABLE IF EXISTS `operations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operations` (
  `operations_id` int NOT NULL AUTO_INCREMENT,
  `number_end_shift_crates` int NOT NULL,
  `delays` varchar(255) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `date_time_id` int NOT NULL,
  `block` enum('Block 1','Block 2','Block 3','Block 4','Block 5','Block 6','Block 7') NOT NULL,
  PRIMARY KEY (`operations_id`),
  KEY `fk_operations_date&time1_idx` (`date_time_id`),
  CONSTRAINT `fk_operations_date&time1` FOREIGN KEY (`date_time_id`) REFERENCES `date_time` (`date_time_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operations`
--

LOCK TABLES `operations` WRITE;
/*!40000 ALTER TABLE `operations` DISABLE KEYS */;
INSERT INTO `operations` VALUES (1,120,'Tractor breakdown 30 min','Rain expected tomorrow',10,'Block 1'),(2,120,'Tractor breakdown 30 min','Heavy Rainfall expected tomorrow',10,'Block 1'),(3,120,'Tractor breakdown 30 min','Heavy Rainfall expected tomorrow',10,'Block 1'),(4,120,'Tractor breakdown 30 min','Heavy Rainfall expected tomorrow',10,'Block 1');
/*!40000 ALTER TABLE `operations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `person_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'John Doe'),(2,'Jane Smith'),(3,'Mike Johnson'),(4,'Chantel Davis'),(5,'John Doe'),(6,'Jane Smith'),(7,'Mike Johnson'),(8,'Chantel Davis'),(9,'John Doe'),(10,'Jane Smith'),(11,'Mike Johnson'),(12,'Chantel Davis'),(13,'John Doe'),(14,'Jane Smith'),(15,'Mike Johnson'),(16,'Chantel Davis'),(17,'John Doe'),(18,'Jane Smith'),(19,'Mike Johnson'),(20,'Chantel Davis'),(21,'John Doe'),(22,'Jane Smith'),(23,'Mike Johnson'),(24,'Chantel Davis'),(25,'John Doe'),(26,'Jane Smith'),(27,'Mike Johnson'),(28,'Chantel Davis'),(29,'Chantel Smith'),(30,'Seloko Peters'),(31,'Mfanelo Johnson'),(32,'Livhuwani Davis'),(33,'Chantel Smith'),(34,'Seloko Peters'),(35,'Mfanelo Johnson'),(36,'Livhuwani Davis'),(37,'Chantel Smith'),(38,'Seloko Peters'),(39,'Mfanelo Johnson'),(40,'Livhuwani Davis'),(41,'John Doe'),(42,'Jane Smith'),(43,'Mike Johnson'),(44,'Chantel Davis'),(45,'Chantel Smith'),(46,'Seloko Peters'),(47,'Mfanelo Johnson'),(48,'Livhuwani Davis'),(49,'Chantel Smith'),(50,'Seloko Peters'),(51,'Mfanelo Johnson'),(52,'Livhuwani Davis'),(53,'Chantel Smith'),(54,'Seloko Peters'),(55,'Mfanelo Johnson'),(56,'Livhuwani Davis'),(57,'Chantel Smith'),(58,'Seloko Peters'),(59,'Mfanelo Johnson'),(60,'Livhuwani Davis');
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team` (
  `team_id` int NOT NULL AUTO_INCREMENT,
  `clock_in_time` time NOT NULL,
  `num_workers` int NOT NULL,
  `block` enum('Block 1','Block 2','Block 3','Block 4','Block 5','Block 6','Block 7') NOT NULL,
  `date_time_id` int NOT NULL,
  `team_leader_id` int NOT NULL,
  `clock_out_time` time DEFAULT NULL,
  PRIMARY KEY (`team_id`),
  KEY `fk_team_date&time_idx` (`date_time_id`),
  KEY `fk_team_person1_idx` (`team_leader_id`),
  CONSTRAINT `fk_team_date&time` FOREIGN KEY (`date_time_id`) REFERENCES `date_time` (`date_time_id`),
  CONSTRAINT `fk_team_person1` FOREIGN KEY (`team_leader_id`) REFERENCES `person` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team`
--

LOCK TABLES `team` WRITE;
/*!40000 ALTER TABLE `team` DISABLE KEYS */;
INSERT INTO `team` VALUES (1,'04:30:00',5,'Block 1',1,1,'16:30:00'),(2,'05:10:00',8,'Block 1',2,2,'15:10:00'),(3,'05:55:00',6,'Block 1',3,3,NULL),(4,'04:30:00',5,'Block 1',1,1,'16:30:00'),(5,'05:10:00',8,'Block 1',2,2,'15:10:00'),(6,'05:55:00',6,'Block 1',3,3,NULL),(7,'04:30:00',5,'Block 1',1,1,'16:30:00'),(8,'05:10:00',8,'Block 1',2,2,'15:10:00'),(9,'05:55:00',6,'Block 1',3,3,NULL);
/*!40000 ALTER TABLE `team` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-21  8:15:04
