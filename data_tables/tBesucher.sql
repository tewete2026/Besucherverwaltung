/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: bv
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-1build1 from Ubuntu

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `tBesucher`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tBesucher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `KundenNr` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Besucher Kundennummer',
  `Nachname` varchar(50) NOT NULL DEFAULT '',
  `Vorname` varchar(50) NOT NULL DEFAULT '',
  `Anrede` int(11) DEFAULT NULL COMMENT 'Verweis auf tAnrede',
  `Strasse` varchar(50) DEFAULT NULL,
  `Ort` varchar(50) DEFAULT NULL,
  `PLZ` varchar(5) DEFAULT NULL,
  `EMail` varchar(50) DEFAULT NULL,
  `Telefon` varchar(20) NOT NULL DEFAULT '',
  `Aktiv` bit(1) DEFAULT NULL,
  `Newsletter` bit(1) DEFAULT NULL,
  `Bemerkung` varchar(255) DEFAULT NULL,
  `AufnDatum` datetime NOT NULL DEFAULT curdate(),
  `Gesendet` bit(1) DEFAULT NULL,
  `Sperre` decimal(20,0) unsigned DEFAULT NULL COMMENT 'Enthält Timestamp, wenn Satz gesperrt ist',
  PRIMARY KEY (`id`),
  UNIQUE KEY `KundenNr` (`KundenNr`),
  UNIQUE KEY `personal_names` (`Nachname`,`Vorname`,`Telefon`),
  KEY `personal_date` (`AufnDatum`)
) ENGINE=InnoDB AUTO_INCREMENT=1763 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-02-25 18:10:45
