CREATE DATABASE IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8mb3;
USE `mydb`;

-- 1. Table structure for `login`
DROP TABLE IF EXISTS `login`;
CREATE TABLE `login` (
  `login_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`login_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 2. Table structure for `person`
DROP TABLE IF EXISTS `person`;
CREATE TABLE `person` (
  `person_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`person_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 3. Table structure for `date_time`
DROP TABLE IF EXISTS `date_time`;
CREATE TABLE `date_time` (
  `date_time_id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `time` time NOT NULL,
  PRIMARY KEY (`date_time_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 4. Table structure for `team`
DROP TABLE IF EXISTS `team`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 5. Table structure for `harvest_crates`
DROP TABLE IF EXISTS `harvest_crates`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 6. Table structure for `logistics`
DROP TABLE IF EXISTS `logistics`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- 7. Table structure for `operations`
DROP TABLE IF EXISTS `operations`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

-- ==========================================
-- DEFAULT LOGIN INSERT
-- Password is 'admin123' (hashed with SHA2)
-- ==========================================
INSERT INTO `login` (`username`, `password`) VALUES 
('admin', SHA2('admin123', 256));
