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
-- Table structure for table `tBesuche`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tBesuche` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `BesucherID` int(11) DEFAULT NULL COMMENT 'Verweis auf tBesucher',
  `VeranstID` int(11) DEFAULT NULL COMMENT 'Verweis auf tVeranst',
  `ThemenID` int(11) DEFAULT NULL COMMENT 'Verweis auf tThemen',
  `GeraeteID` int(11) DEFAULT NULL COMMENT 'Verweis auf tGeraete',
  `Spende` decimal(18,2) unsigned DEFAULT NULL COMMENT 'Spende für die Beratung',
  `Dauer` smallint(6) DEFAULT NULL,
  `VorNach` varchar(10) DEFAULT NULL,
  `TagInt` smallint(6) DEFAULT NULL,
  `Monat` smallint(6) DEFAULT NULL,
  `Jahr` smallint(6) DEFAULT NULL,
  `Entf` bit(1) DEFAULT NULL,
  `EMail` bit(1) DEFAULT NULL,
  `BesucherWL` bit(1) DEFAULT b'0' COMMENT 'Besucher auf der Warteliste',
  `Nachname` varchar(50) DEFAULT NULL COMMENT 'Nachname des anwesenden Besuchers',
  `Vorname` varchar(50) DEFAULT NULL COMMENT 'Vorname des anwesenden Besuchers',
  `AnlageDatum` datetime DEFAULT current_timestamp() COMMENT 'Datum der Anlage',
  `AnlageUser` varchar(100) DEFAULT NULL COMMENT 'Durchführender Benutzer',
  `VeranstBez` varchar(255) DEFAULT NULL COMMENT 'Veranstaltung durchgeführte Bezeichnung',
  `VeranstThema` varchar(255) DEFAULT NULL COMMENT 'Veranstaltung durchgeführtes Thema ',
  PRIMARY KEY (`id`),
  KEY `besucher_ids` (`BesucherID`),
  KEY `veranst_ids` (`VeranstID`)
) ENGINE=InnoDB AUTO_INCREMENT=20672 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-05-16 18:40:45
