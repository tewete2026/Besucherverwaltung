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
-- Table structure for table `tVeranst`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tVeranst` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Typ` int(11) DEFAULT NULL COMMENT 'Verweis auf tVeranstTyp',
  `Ort` int(11) DEFAULT NULL COMMENT 'Verweis auf tOrte',
  `Datum` datetime DEFAULT NULL,
  `Von` varchar(10) DEFAULT NULL,
  `Bis` varchar(10) DEFAULT NULL,
  `Dauer` varchar(10) DEFAULT '00:00' COMMENT 'Dauer der Veranstaltung',
  `Bezeichnung` varchar(255) DEFAULT NULL,
  `Thema` int(11) DEFAULT NULL,
  `Spenden` decimal(18,0) DEFAULT NULL,
  `VorNach` varchar(10) DEFAULT NULL,
  `TagInt` smallint(6) DEFAULT NULL,
  `Monat` smallint(6) DEFAULT NULL,
  `Jahr` smallint(6) DEFAULT NULL,
  `Sortier` int(11) DEFAULT NULL,
  `Sperre` decimal(20,0) unsigned DEFAULT NULL COMMENT 'Enthält Timestamp, wenn Satz gesperrt ist',
  PRIMARY KEY (`id`),
  KEY `index_ort` (`Ort`),
  KEY `index_datum` (`Datum`),
  KEY `index_von` (`Von`),
  KEY `index_bis` (`Bis`)
) ENGINE=InnoDB AUTO_INCREMENT=871 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
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
