-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.32-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for qr_auth_db
CREATE DATABASE IF NOT EXISTS `qr_auth_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `qr_auth_db`;

-- Dumping structure for table qr_auth_db.registros_acceso
CREATE TABLE IF NOT EXISTS `registros_acceso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(100) NOT NULL,
  `fecha` date NOT NULL,
  `hora_entrada` time NOT NULL,
  `hora_salida` time DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table qr_auth_db.registros_acceso: ~12 rows (approximately)
INSERT INTO `registros_acceso` (`id`, `usuario`, `fecha`, `hora_entrada`, `hora_salida`) VALUES
	(1, 'admin', '2025-05-24', '15:04:07', '15:04:11'),
	(2, 'admin', '2025-05-24', '15:04:18', '15:04:28'),
	(3, 'admin', '2025-05-24', '15:04:57', '15:05:03'),
	(4, 'admin', '2025-05-24', '20:03:53', '20:11:57'),
	(5, 'admin', '2025-05-24', '20:05:13', '20:11:57'),
	(6, 'admin', '2025-05-24', '20:06:37', '20:11:57'),
	(7, 'admin', '2025-05-24', '20:08:16', '20:11:57'),
	(8, 'admin', '2025-05-24', '20:10:10', '20:11:57'),
	(9, 'admin', '2025-05-24', '20:11:28', '20:11:57'),
	(10, 'admin', '2025-05-24', '20:16:54', '20:16:58'),
	(11, 'admin', '2025-05-24', '20:20:16', '20:20:25'),
	(12, 'admin', '2025-05-24', '20:21:03', '20:21:06'),
	(13, 'admin', '2025-05-24', '20:22:57', '21:41:31');

-- Dumping structure for table qr_auth_db.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `qr_token` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `qr_token` (`qr_token`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table qr_auth_db.users: ~6 rows (approximately)
INSERT INTO `users` (`id`, `username`, `qr_token`, `created_at`, `password`) VALUES
	(1, 'admin', 'adm1nT0k3n', '2025-05-08 19:15:45', '12345678'),
	(2, 'empleado1', 'emp1T0k3n', '2025-05-08 19:15:45', NULL),
	(3, 'invitado', '1nv1t3dT0k3n', '2025-05-08 19:15:45', NULL),
	(4, 'usuario_valido', 'token12345', '2025-05-08 19:20:46', NULL),
	(6, 'usuario1', 'user1_qr_token', '2025-05-08 19:34:49', 'password1'),
	(7, 'usuario2', 'user2_qr_token', '2025-05-08 19:34:49', 'password2');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
