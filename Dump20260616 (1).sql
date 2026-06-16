-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: gs1
-- ------------------------------------------------------
-- Server version	8.0.28

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
-- Table structure for table `administration_logs`
--

DROP TABLE IF EXISTS `administration_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administration_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `server_type` enum('SECURITY_SERVER','GLOBAL_SERVER') NOT NULL,
  `server_id` varchar(100) NOT NULL,
  `action_type` varchar(100) NOT NULL,
  `performed_by` varchar(255) NOT NULL,
  `target_entity` varchar(255) DEFAULT NULL,
  `previous_value` text,
  `new_value` text,
  `status` enum('SUCCESS','FAILED') NOT NULL,
  `error_message` text,
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_admin_server` (`server_id`),
  KEY `idx_admin_action` (`action_type`),
  KEY `idx_admin_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administration_logs`
--

LOCK TABLES `administration_logs` WRITE;
/*!40000 ALTER TABLE `administration_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `administration_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificate_requests`
--

DROP TABLE IF EXISTS `certificate_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificate_requests` (
  `csr_id` int NOT NULL AUTO_INCREMENT,
  `gateway_code` varchar(100) DEFAULT NULL,
  `key_id` int DEFAULT NULL,
  `csr_data` text,
  `cert_type` enum('AUTH','SIGN') DEFAULT NULL,
  `status` enum('PENDING','SIGNED','REJECTED') DEFAULT 'PENDING',
  `requested_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`csr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificate_requests`
--

LOCK TABLES `certificate_requests` WRITE;
/*!40000 ALTER TABLE `certificate_requests` DISABLE KEYS */;
INSERT INTO `certificate_requests` VALUES (5,'as',1,'-----BEGIN CERTIFICATE REQUEST-----\nMIIEoTCCAokCAQAwXDELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVN0YXRlMQ0wCwYD\nVQQHDARDaXR5MRgwFgYDVQQKDA9TZWN1cml0eSBTZXJ2ZXIxFDASBgNVBAMMC2F1\ndGguc2VydmVyMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAuQ+0WlXu\naEjMEJZQbwkAVM3+ZI9ssiwRU7AMex85f0zwV1x4f7X87517oeU8pcAa5/Guq9Sg\n5bWnX16P5q1e3Q3RiOVuMOV7V5u6QDXCmJHMOaYcWuf3utAO5bA4Sui+tBJnkCcl\nzOHABFMMEnttbxZKQXMPJZwASsnVIAsh4OCkFMHIk5/iYkY96EQjR4EGNMV9mRAu\noV5TvJAR7YiAfkviYbGcIYHPg4jvO84GP4cR6CcJL9X8cVP1RR7Ka9OZi8bUJoW8\ntokD0fyfh/QgnUxpfUatUsd8CIW2Hziy+KT4kTcQxIRZBgLAGFVt2Y3aWQenIlz/\nTH22x2VX9uJ70Q7xTTuywd8JwC/3by/cl8cLHlInUEq2lPk6nxtDwuqDnV9Uu/rp\nJJAqooDvyAULwJyfUMQXCYw+z1HLQZawwNgTHEHc+Prsx5VbBCkuWTyhQMHMAGW/\n1FVNPSJqU1ztivL90O88WCNWFG1Vhaf5fWONRXxNqYQ8oGpZrlBOVQ7IVMGETKLG\nz3Y32DfSXdWhuCDIMpM1E7MBV60dsnUPNKAO7P262xAE1PS4qEYq+n5Pj1u95b53\nC9itWAgtfDvimzX7c5vjdqDlKclT8AG1RWoDa6m2JlCFf5d2X+2p1pUjhIjdQLEx\nmh0PnFkcpIM3tifemH/ijaPUHSwWk+D4Pe0CAwEAAaAAMA0GCSqGSIb3DQEBCwUA\nA4ICAQBnHoZxBUDwj7PYddAou7lM88O8d7dwkv4ZwjBl2087MQs4RFshfMHrFMHk\ntq2vy0SDnhtEewhfRNcbdu1sAiE76UMcqo32iY8NCd7nVntjzCiIijTNjNSf7K6g\nqQzKU7UKIg5cpG041V7JpnGQZwNIjkB4YRKjqoUa1QAa+hDJY981G+LRcd6/GXOx\n7vsJvCusQFHbq2cFsydQnM+OuweClcdA088hi3rTvfdagc62wjqn52rfKJknIVdl\nbBtYxpn5g7KcRsYAaqKQRcqmj/HTkB8Zzi1wgJ5gPeWZO2yjsFonoy0GStDl+y0Q\noIz7AhZUwYP4C29YYjivcnjH9MQZ/jSu3d13LyAwhAHHDyhyEnyHHFlnGN4/UpH6\nvgMc/dGsqzkwlvUMaw0TbHDH0jSyh4qvWB6l+xFKkfs9/g+qq5ykordfTLCr7heW\nPIQelUnlCYJtfcBa4dFCDEYl+tcp9bUFFITJFp+CBjc1tiR4Myn8wzcwfdyG6gm5\nfnmdeknTOpQVnIEjXTyXxR+q4Vp3PMygz5DSqX10YZoOVHWYXM9lLZCX39ol4g2u\n6s2WeV2pRBlmAPh9Kh/B8TahZWiqZmwyLlQxh73SmBwt6nUaWClz8TE/dd/VEGY3\nAJdwjC5OLgRSKVjIQxjaFsIU92Z7HPDk9vS8qGrrFiHlit22SA==\n-----END CERTIFICATE REQUEST-----\n','AUTH','SIGNED','2026-04-24 04:15:10'),(6,'as',1,'-----BEGIN CERTIFICATE REQUEST-----\nMIIEoTCCAokCAQAwXDELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVN0YXRlMQ0wCwYD\nVQQHDARDaXR5MRgwFgYDVQQKDA9TZWN1cml0eSBTZXJ2ZXIxFDASBgNVBAMMC3Np\nZ24uc2VydmVyMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA8N6C8nNZ\nkdoyuKWduH5naPdcAkgTEHpJv7YP/UjvMxWgSNCgzDf7mSwm2SPKiUqRQRd21zYV\ns3RkxMiZ1JKnDbEEHpjQFYGVHVlRegNC2dB9hjCyY9vzPjT+IDQjFaCmB98nJIYA\nQ6aSR25JXIwefeWJvWJMO9r1Nb4lJwH0w0BqzhOZ6rEwkHiYuW8wvp/TpQW7SScP\nCc7Oyc97/yMZdgT85kstLxHlb8pPCLLvHnVxD/s0ZDrDVDtqRLQgRfSNLBkM+g5v\nFHirQaYYyEM1nSm4+uqq2fJoywSkBTxZcYWvL0SLCHam1nkv9TULqa2QcfUHFMyz\nEPjo14nEWcNFKWw6F6HEqVCV60auB3wU/0nBmS1AxwJpXlGqSZQq9Jbgc86A3f5L\nyWbQw0Cd+7Ua5jV1pKBrtkp0pb7mHMaLzEQRKhvtTCOao3gLialdcBDUnTfrYGqs\n1o4gbuk0drxO/Nt2IYf+6ovj8UXn6IPKmcS6p6M2d4v6z1YT0y3eRtOs0Z4glNxY\nAKtic2EW76efdtUYJxF0EOVH4XwP91KDlqHM7hiFBHR9Bn8heDWdaDBLs+EedUey\nbEBIf8y0A7YG6ZKeZfVtyMvSLWs9z9SdFx1tGCT1WudBjyukD1ifYlI4CIMSeYGL\n6UT4MjAjw2pMUBnWr74Qz6+0XWsVysWLM58CAwEAAaAAMA0GCSqGSIb3DQEBCwUA\nA4ICAQCJqD63Z+5MpbrcspL9fxUacahetkeqpee7b/WrTdVdCx9QMWuWX4KvCU+J\ngD75HFxm/LqbZmXOOxDc87E756s/ZDi77fj6QXjA1v2fNflIYX0ibN0RqL8dFIBc\nvTOLo+aGtnRXPgN1ZjKNQT0bW6fXZwuW81IG6sKiDJY3NFi5xxILSyBPEYjwucI1\n33qQBqURMwH4FYf2TJ5UPRoLsgm82TLbpA/BPEGtoMBGxHOmqfxN1cGSMmXkpCLv\nEgWPSzU5kLtm6pxXyScEKsVEGLRaHCS/Lda/wiKZcCPviP+r4bt9XO2RzpV71GBT\n/MEMEWLYRIJaGPJ+f4OTu+nx0FDqTOqJAfdtIpr0jtCz32CUGNZd8BLutpGtyXhF\nX6zz+98HtG4ExWXn/7/5mxwp5fh7lI74ebrhuYpLdOig7sE3rZlJnXRqIO9n5298\nPc/oJVoASSMmDJnwaC2NK4u5Pszbl/SPou/IaUrYZ5wP27ZY2enso8//JcoC8082\n4jb/G+AtCLOGgv7hn38IWwcJTMkzTezvR+A6ms4PYC4lSHJbzhWJgKECyo2iKU5d\nu8o0nKWPYihC+8pRzRgn8Co5RoEE0SAmuc8hEqJycziLqGGaye5ejb/oZOnqc08z\ne55GP7L3fdVLfC95/NvGd0ywJY/1Pjm0a+/03v6ApLF6NJsTBg==\n-----END CERTIFICATE REQUEST-----\n','SIGN','SIGNED','2026-04-24 04:15:11'),(11,'TEST_GW001',1,'-----BEGIN CERTIFICATE REQUEST-----\nMIIEoTCCAokCAQAwXDELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVN0YXRlMQ0wCwYD\nVQQHDARDaXR5MRgwFgYDVQQKDA9TZWN1cml0eSBTZXJ2ZXIxFDASBgNVBAMMC2F1\ndGguc2VydmVyMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA0mUjE5FQ\n+2xG8OFDU+bBeiri9GK/kEpgkECZ5l1C/AT2NOo5DxTDzdLuLDOKbC4y0wetEU9f\nXWwHD7PUwOU3vs4LOGMrsSrJe9zhPpSlx+qt55U+gTPdIKFg9MyS7z7TmWDhdprY\niWPNfBuMtRC18ulqpQie9ozriY3LP/TyeplvfBlLHEjUEWyXdVwH51PASB91ak5x\nakG7Y5wj27FWUZ8fB1o2dsV0RRpfBR8DHMS1zYk2X9rUhhwaNZWFRvqrqzI9cH8j\nFu44SqCc6m2j7SMN5bTLVnV5nAQfgGDlBDTiVQzAGgeCt3jjo8wsKZCg2qOssV3F\nysi9U3ViZNS5PnvPRE/gBgJsGP4t9YkbN2XQ6TjIslqRcxHeesQnYprMh4RUXabl\nodmbRYYVyTnTiZvX5Qbg8AFQ9XTYYAnZ5HnAG4icJ2Ba8E/YBO7PrOji7jzxENAp\nyiX8yDs3fk8pvwSu7Dqo4xfV7BAZQW6AsrEKufyGkMUg7dkIhdkQr7lQChc+E3uR\nvRm7HfQBX969w4MfZKv0TpKN/07TKLvZW6ysVtVAD4e6oZvX1ocqlCAgSZ+ZPlkZ\neNOeW7JtMTo5R4YRXPu93VY7NgOX80LIZ5KE+GZD1Iyzo8uEPmEWbPTIcv4MlUVP\nVUjYqVcG1/fyzpDk+JZCOB20lRZG7ley93sCAwEAAaAAMA0GCSqGSIb3DQEBCwUA\nA4ICAQB8dmKGQJHBzYBaV9xyjgCQ2ljfysREHm0cE2+QnjS4vPlK5jBq1zzMqT63\n9yAHT73htGfpWU/dJ+uQV/ul9+Vn+iIrHk00cW/lolFl+dXJU7QGebc3VdK7V4br\nBbuqQrsqveIlrUwc/Q7f/hBfQxBL4Y8978QU9zbbmVqJnPsNSt6sw6pZPzSk4C69\ntkR8g27waTyBTursewXylSIDepWHlwDkzNFBtDsXkkjAPH/Q2qXwU2UGiATubwe5\ngs4XVNWZrzpOorWOlAr5FRAxMbkb9FxAKf0nG2jUm4BvfRcsA1P8/aJyovPqNSMc\n+UU9GxCiT1trOxrcDHrCA+xUDXmykpaDyE5+Osp/KGN+iCf7dAekLb2nKDiEv5BD\nmPI6ZHwqqBFHtCMDBtxwEq69VpE3qNirE6o5FH+XyC4yxWGU2+9XXJUTvwRaJLLE\nYKKttmO70ICsoXgTWQnD0ym32XpmeafTfcA1DoSv0rI8nfURv5ZB5nGAi6L4a4nu\nioakUUyNq5cpq1folThIJ1JDnevOyGLdVZSZNH/H2tWs0IGJy2zkD03UWCsm56CN\nKpPoUG8R6Rvv0nGBjHu1EZt0ZuLxfj4WaVnJzS1c/yFN6oVp43sb+HiwFKy50QEl\nZGWV2aENdrZ28Bkxxd2agPhnpv45ssCgDDhP8B9ve6MXaDR6Jw==\n-----END CERTIFICATE REQUEST-----\n','AUTH','SIGNED','2026-04-30 10:45:20'),(12,'TEST_GW001',1,'-----BEGIN CERTIFICATE REQUEST-----\nMIIEoTCCAokCAQAwXDELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVN0YXRlMQ0wCwYD\nVQQHDARDaXR5MRgwFgYDVQQKDA9TZWN1cml0eSBTZXJ2ZXIxFDASBgNVBAMMC3Np\nZ24uc2VydmVyMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAi/ZY/Dtc\nY4NjhY2Q5baTLZhjNAlItz1nI4odZ6iJrHMQqgqS2Jq0CPUh8kjfYsYvG3pmmF+9\n0h6wiGW6HSmzdW0s6SELwOe23T3Wqzh0j+B4cOn11C6f8wyhpHN/Hd9aDk4M54f6\nuXteWiXDnpDquTK+KEaL0pyhBlFpEQOzdVoHRNqlDU4I01ULAjL5JZA0oucxImdU\nZnoXqjzj2eRHhUlZmFm+UK1J9rKQf4TvFb+g0KUty5J5Ravg0Jqgz2zmhmzcAIuR\nh11MWtl4CdraJqwrcLGOs2zXbHD/VU24MMUnQoYUk5oQmA2NDt6KX2bSXIPPuEuh\nXYJa/MzvToA7Z1oS02dpeVv5i/Hxkt1Sy4k8SoV6tFq7hR020sZkTZweBkZBhiRW\nuCTdaLDXZD2j1KIiPjuazM/0uOG4CIlDlpXxm02e2Qik9wEGrhnFKY34cNzY8jtH\n6mop3rogGtI/Rg1daSgJalBHupwrWYM4S31Pr2GrzeTWe9mkAxhRaf1bYTb35BnX\nkZ0MvRk4JBPlsRutSMwyz1uNfkqXpvXhwOiiX7Jis8xWoL5n2xnLrp2Ov4hq3jHX\nV1N0k69m4kRz/mFDRn5MVgiEy5UuRGt2o+gtkOl+Y8mt41hj6KojbJGI42KfP6u0\nPF8+9rPrpL2/1ee30kW+zqghtM8MgpF/RFECAwEAAaAAMA0GCSqGSIb3DQEBCwUA\nA4ICAQAQOMXao4T9yHuaIH8WIMkDDrRz1pC7mrW2Nn4l8imASJLNCxZ33VTEA4JB\nakMfdDhI5vKfhgIazGHqrVeXSE91QHf2UAt4Crt/vnzA6bnRZJ2HnZCvMC7pgUft\n5OXaEZPW08fiEbzHLXxyoMz3HqoGmHtXtsRtPp/X6J1hJwD+CPRL0urwUBSuUsue\n4b1F+QrF9dkgwnCxoHuicex9oVMItCeW+T9/nqRtyJTKB8Xw9eENYRCfeBdrIh15\n2W7jzRBsP6vmBu/s6/LBGSlhAh3Qd5t2TLzXGTe1z6jgKRjGzSzKV1AU2wt2zHs9\npL8UfQbQ9b8oTvdwqXV7PrHuKUkBbatbbHyWtjGwTUoQqLWuz//3LOeqB5fAUwrH\nbZYG+zCtoAI5UesCWVgx/zu37mc8P/YIGunWuxYqVl6DWlWCMu2d1s7Ji3ITQz/t\nj8oU1H0x02q/ZAOrqaGzJRAo8VNyjBmy/7PbQTLwNrH88yxSG1iRb8W3fYQw4rgO\nG9lUA3p6adSx69DavDADPLeLWd/CowGbGz2045OrIZbTH2DVWeB98Jp3/2rindBy\nPFAi03vSLvYhKXeC9XY0T+bLODpAaEUBUF9S6KKCkRENAnJHk+vItb6W2elazhwT\nv4uiWmhrYKZtkleWufdEfgoSeKIJVYUXnvEiWUrCcEJVuhoPjw==\n-----END CERTIFICATE REQUEST-----\n','SIGN','SIGNED','2026-04-30 10:45:20');
/*!40000 ALTER TABLE `certificate_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificates`
--

DROP TABLE IF EXISTS `certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `certificates` (
  `cert_id` int NOT NULL AUTO_INCREMENT,
  `gateway_code` varchar(100) DEFAULT NULL,
  `key_id` int DEFAULT NULL,
  `cert_type` enum('AUTH','SIGN') DEFAULT NULL,
  `certificate` text,
  `issued_by` varchar(255) DEFAULT NULL,
  `valid_from` datetime DEFAULT NULL,
  `valid_to` datetime DEFAULT NULL,
  `status` enum('ACTIVE','EXPIRED','REVOKED') DEFAULT 'ACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cert_id`),
  KEY `key_id` (`key_id`),
  CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`key_id`) REFERENCES `server_keys` (`key_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificates`
--

LOCK TABLES `certificates` WRITE;
/*!40000 ALTER TABLE `certificates` DISABLE KEYS */;
INSERT INTO `certificates` VALUES (8,'	TEST_GW001',NULL,'SIGN','-----BEGIN CERTIFICATE-----\nMIIEsDCCApigAwIBAgIUEu0MlagVa82U2fEjaBXn9kuNvL0wDQYJKoZIhvcNAQEL\nBQAwczELMAkGA1UEBhMCRUUxETAPBgNVBAgMCEhhcmp1bWFhMRAwDgYDVQQHDAdU\nYWxsaW5uMRgwFgYDVQQKDA9UcnVzdCBBdXRob3JpdHkxJTAjBgNVBAMMHFJvb3Qg\nQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMjYwNDIwMTg1MjQ1WhcNMjcwNDIw\nMTg1MjQ1WjA3MQswCQYDVQQGEwJFRTEOMAwGA1UECgwFQXBjb2cxGDAWBgNVBAMM\nD1NlcnZlcl8wMDEtU0lHTjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB\nAL/N94nCGsujGSUGu0p/2zP+Pj7CVflJOSPRmfpkxwwdzp1GWQAp4EItkVrAilft\n9iHY/qFGJ/XTPcTpVSUWH9YhCc0Y8JUSGok5aUakdiYgHc2YAP3TEBKSN//1lezD\nMEIrlIgCAJP9+rOH5PK/wIUObPEXFOFFTKQk4CzGceaQBM7U3AWox0ztotPypWMd\n6i+3uJqt2WoPnJhsc6RPEzC2iSiRcI+1SKPdR8Cu8Pdpu+H5EYWyi1tVnQPE6+H/\nDq8u/vDJnBjYHKpYwT91fOu9gYLL35azXgOI9ea0eHT7/tU9uEKL80jTA1KNQwTC\nodjjJdCCqBCgbnlFJHKRsk8CAwEAAaN4MHYwDAYDVR0TAQH/BAIwADAOBgNVHQ8B\nAf8EBAMCBsAwFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwMwHQYDVR0OBBYEFKZFYTih\nus9b7hFd8sm40YdH6qe6MB8GA1UdIwQYMBaAFDIm4fkRjgH6XWS7o3W5/OPIWgpL\nMA0GCSqGSIb3DQEBCwUAA4ICAQACi4DBYZSj2iKdYA/J52CqV64/Ca6kp0vW3ITo\n8/vlLqgudHmUc1PLqjhMUjJLHgX0LUXi2Lk5Yd+nKry8/aV7qWbJyjYkZNyJbmSN\n7r+rMgZOXJMvCfmGneKAUHPoQFuZ+3U7FfRrXhRuoXWwHcXRs7k5gicwvOw16udP\n2EbUCA/AyXSMG/EKxavC9d25VI+SIpb58hJ0/fqN4g1Hnp1MiZYcgwMtB3JWNs3I\n32mvx9qnNZiycTRgGq2PIjViV0RVBTo7S1m6HZSfhfP37yz1+TcCxZ8CvawA0fUb\nGvEFzlso2lBo7eLNgsJV7r8CbLad6ihrYDb8uhPSwvjdiGsvjXNOk/lB3uEwkEVJ\nJ9mblgnf5gkE9iS6g1VHPINYneF/2pTKP5aQ/SMwy8/KZBc42CR7vSvUc+KQs6ZW\n/yO3Fuz3NcZiqe3bTrWQf4u7951ni8P7E9vXhIv6ZzzQwkAkbtUALadq4GNHut4T\nkjQK9mrORJG5JB7Q7Wd69IRqWDLltoBDOUkJxvqoUs1+s2NoEgxPBvvNULoVdn/z\njpOXHgcViVm/EqyzRG+U9ygomY1oEMnrEnRE1WmEzsWaEBqdRiU+nAIyKUxv7ZpL\ngaRqOp49UUq3Tmd5Mk/Tp1j9p2tfdKtMYQbu7re9DHLnH2jriZVfT/7Vw88TXOXk\nNjS0kw==\n-----END CERTIFICATE-----\n','CA Authority','2026-04-20 18:52:45','2027-04-20 18:52:45','ACTIVE','2026-04-20 18:52:45'),(9,'as',NULL,'AUTH','-----BEGIN CERTIFICATE-----\nMIIF1TCCA72gAwIBAgIUBE5cNHl5jU5vEhaDN5P3wG2z5BEwDQYJKoZIhvcNAQEL\nBQAwczELMAkGA1UEBhMCRUUxETAPBgNVBAgMCEhhcmp1bWFhMRAwDgYDVQQHDAdU\nYWxsaW5uMRgwFgYDVQQKDA9UcnVzdCBBdXRob3JpdHkxJTAjBgNVBAMMHFJvb3Qg\nQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMjYwNDI0MDQ0MzM5WhcNMjcwNDI0\nMDQ0MzM5WjBcMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFU3RhdGUxDTALBgNVBAcM\nBENpdHkxGDAWBgNVBAoMD1NlY3VyaXR5IFNlcnZlcjEUMBIGA1UEAwwLYXV0aC5z\nZXJ2ZXIwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC5D7RaVe5oSMwQ\nllBvCQBUzf5kj2yyLBFTsAx7Hzl/TPBXXHh/tfzvnXuh5TylwBrn8a6r1KDltadf\nXo/mrV7dDdGI5W4w5XtXm7pANcKYkcw5phxa5/e60A7lsDhK6L60EmeQJyXM4cAE\nUwwSe21vFkpBcw8lnABKydUgCyHg4KQUwciTn+JiRj3oRCNHgQY0xX2ZEC6hXlO8\nkBHtiIB+S+JhsZwhgc+DiO87zgY/hxHoJwkv1fxxU/VFHspr05mLxtQmhby2iQPR\n/J+H9CCdTGl9Rq1Sx3wIhbYfOLL4pPiRNxDEhFkGAsAYVW3ZjdpZB6ciXP9MfbbH\nZVf24nvRDvFNO7LB3wnAL/dvL9yXxwseUidQSraU+TqfG0PC6oOdX1S7+ukkkCqi\ngO/IBQvAnJ9QxBcJjD7PUctBlrDA2BMcQdz4+uzHlVsEKS5ZPKFAwcwAZb/UVU09\nImpTXO2K8v3Q7zxYI1YUbVWFp/l9Y41FfE2phDygalmuUE5VDshUwYRMosbPdjfY\nN9Jd1aG4IMgykzUTswFXrR2ydQ80oA7s/brbEATU9LioRir6fk+PW73lvncL2K1Y\nCC18O+KbNftzm+N2oOUpyVPwAbVFagNrqbYmUIV/l3Zf7anWlSOEiN1AsTGaHQ+c\nWRykgze2J96Yf+KNo9QdLBaT4Pg97QIDAQABo3gwdjAMBgNVHRMBAf8EAjAAMA4G\nA1UdDwEB/wQEAwIFoDAWBgNVHSUBAf8EDDAKBggrBgEFBQcDATAdBgNVHQ4EFgQU\nwaNkz5SLqUpPjtC6/ED3vYxMyEAwHwYDVR0jBBgwFoAUMibh+RGOAfpdZLujdbn8\n48haCkswDQYJKoZIhvcNAQELBQADggIBACdaiYHMlSpm32p7PETmykJCMr6jTcZP\nBwQ/ZLknupMNRVjH9ScUKyHyBS8zP9GHBLIvOx/vIcHtoCzqINfQbynKGsSYmX+P\n8n+fTnVUB60t32QUPsSy2CNZYQYmGoAKejCwlV/dCmy+BOTgIkf3x6fE0ml8M7aH\nrEVEZyiaQMSVv7Nadx/j19t9NAxjm8t378eQh//1q93rx1b6xfhS0hBXVNPBC9o8\nRowDWv0wa7Znlxbe1QEZTp/5FY9hxcM7LlmQyyiNyc9kto8/i0s9EVdc6cqLgDfx\n8qMetl5tw3CTL2aHPlP5Em6PRgjiQPFtG3fIzkfiR/cXmgtqLgmBTQ6+YC838gqR\na51t/bfroS2hFYZ1OlQvj21i98amxI8ZNSJEWIA+52cfSIQSwtNlWdOsxcw6OsYz\nKFXCloxeYmDkAg7jGl4IAljopgZaEmVHUC/XJ3H8mZPjw/AHRAHQtEk5L1A0FzDl\nTN5pEs6PG9Rk4kR8g48TREJFWObs/7fUcIs8PlWIWEchiS6RYb1NZQUJtl/wdJ0g\nXRU24ZbePAEEhcwr8NJTDJ440VRg0IjE3aSKDtClxaXct2dgAr1xkBFOstj2EkmO\ne/z0rN37JM+To0DTnsV57dtEG+qDXMGBOE4puhViGFuL6cSO1X19Vb/I0c/EKz98\nIREmyX2RURF9\n-----END CERTIFICATE-----\n','CA Authority','2026-04-24 04:43:39','2027-04-24 04:43:39','ACTIVE','2026-04-24 04:43:40'),(10,'as',NULL,'SIGN','-----BEGIN CERTIFICATE-----\n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\nFRc7t8kOG08x\n-----END CERTIFICATE-----\n','CA Authority','2026-04-24 04:44:01','2027-04-24 04:44:01','ACTIVE','2026-04-24 04:44:01'),(11,'TEST_GW001',NULL,'AUTH','-----BEGIN CERTIFICATE-----\nMIIF1TCCA72gAwIBAgIUUN3XPf9uGIJOMxnBP8WPHOtnHOcwDQYJKoZIhvcNAQEL\nBQAwczELMAkGA1UEBhMCRUUxETAPBgNVBAgMCEhhcmp1bWFhMRAwDgYDVQQHDAdU\nYWxsaW5uMRgwFgYDVQQKDA9UcnVzdCBBdXRob3JpdHkxJTAjBgNVBAMMHFJvb3Qg\nQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMjYwNDMwMTA0ODE3WhcNMjcwNDMw\nMTA0ODE3WjBcMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFU3RhdGUxDTALBgNVBAcM\nBENpdHkxGDAWBgNVBAoMD1NlY3VyaXR5IFNlcnZlcjEUMBIGA1UEAwwLYXV0aC5z\nZXJ2ZXIwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDSZSMTkVD7bEbw\n4UNT5sF6KuL0Yr+QSmCQQJnmXUL8BPY06jkPFMPN0u4sM4psLjLTB60RT19dbAcP\ns9TA5Te+zgs4YyuxKsl73OE+lKXH6q3nlT6BM90goWD0zJLvPtOZYOF2mtiJY818\nG4y1ELXy6WqlCJ72jOuJjcs/9PJ6mW98GUscSNQRbJd1XAfnU8BIH3VqTnFqQbtj\nnCPbsVZRnx8HWjZ2xXRFGl8FHwMcxLXNiTZf2tSGHBo1lYVG+qurMj1wfyMW7jhK\noJzqbaPtIw3ltMtWdXmcBB+AYOUENOJVDMAaB4K3eOOjzCwpkKDao6yxXcXKyL1T\ndWJk1Lk+e89ET+AGAmwY/i31iRs3ZdDpOMiyWpFzEd56xCdimsyHhFRdpuWh2ZtF\nhhXJOdOJm9flBuDwAVD1dNhgCdnkecAbiJwnYFrwT9gE7s+s6OLuPPEQ0CnKJfzI\nOzd+Tym/BK7sOqjjF9XsEBlBboCysQq5/IaQxSDt2QiF2RCvuVAKFz4Te5G9Gbsd\n9AFf3r3Dgx9kq/ROko3/TtMou9lbrKxW1UAPh7qhm9fWhyqUICBJn5k+WRl4055b\nsm0xOjlHhhFc+73dVjs2A5fzQshnkoT4ZkPUjLOjy4Q+YRZs9Mhy/gyVRU9VSNip\nVwbX9/LOkOT4lkI4HbSVFkbuV7L3ewIDAQABo3gwdjAMBgNVHRMBAf8EAjAAMA4G\nA1UdDwEB/wQEAwIFoDAWBgNVHSUBAf8EDDAKBggrBgEFBQcDATAdBgNVHQ4EFgQU\nM28RVtkTRkAhir5t4gdm0vur5WkwHwYDVR0jBBgwFoAUMibh+RGOAfpdZLujdbn8\n48haCkswDQYJKoZIhvcNAQELBQADggIBABiX8fEwOJuz/oHDai4gkPxKBhxMyFBC\nF9qvjm5NVhIxb6ADWH9ZMWq29/EVv0ZfyCqZ6aJl88z0HMNyv3uNigjRUpoOEEml\nTYgSOWUYDGFZr+Dim0YHVHCjvIY6IG4NZ2utSjnWnqthE91uitICE49cBSuqxq6o\nKqVgiO4VdtUiSM+Zz89TpDqzG+ooWQSe2Ib8e+PV/96M+7kjm8mFFFtebgSTxo3b\nDJRdtrkiExUHHKJLqBA6K+v0AyPyZvGc3lybM3Wdyt/6vpLAoFF8C6c5yUlUfjd1\n2U0zPvjv4P4qpk9o5Z57cFZ26nMdAFgEnl3afRjg+/KUnJHI2n2q9erV5JLmKupk\nzTe/mezGEMAijuHkfEb1x0XWgM+ScPA9Rvxm8pc8SUHGsiFizNLSwEqzw8MHCdRT\nk36Bwe9baSjBsmHjzstKojgSgZQIvC/+9/OkfrHQSeoTuZZeO0S92csPS9j+oi3O\nulgk4ycUzMSq5VlPs6tOlAdZNDYusbj3EEULRgI9I+uQ6v7vd5PzxoaN0GaooCgL\nqPr4/KG7vGm+7Fq9FBfNZVgzNGFd02Ldbp8PqcT5irHlbhW8Rk3I+Ba79dq1j3H5\nmc0HCTdxzQKJ7AJOFuXBf5j1HuD10/O+ii4yi0Jsnn+7iBJFXgLRJq1IpZqw2ht2\n5fpqExp/+Ixt\n-----END CERTIFICATE-----\n','CA Authority','2026-04-30 10:48:17','2027-04-30 10:48:17','ACTIVE','2026-04-30 10:48:18'),(12,'TEST_GW001',NULL,'SIGN','-----BEGIN CERTIFICATE-----\nMIIF1TCCA72gAwIBAgIUaES5E9Vr/ZsN1Swm2Sp5zSosAyIwDQYJKoZIhvcNAQEL\nBQAwczELMAkGA1UEBhMCRUUxETAPBgNVBAgMCEhhcmp1bWFhMRAwDgYDVQQHDAdU\nYWxsaW5uMRgwFgYDVQQKDA9UcnVzdCBBdXRob3JpdHkxJTAjBgNVBAMMHFJvb3Qg\nQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMjYwNDMwMTA0OTIxWhcNMjcwNDMw\nMTA0OTIxWjBcMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFU3RhdGUxDTALBgNVBAcM\nBENpdHkxGDAWBgNVBAoMD1NlY3VyaXR5IFNlcnZlcjEUMBIGA1UEAwwLc2lnbi5z\nZXJ2ZXIwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCL9lj8O1xjg2OF\njZDltpMtmGM0CUi3PWcjih1nqImscxCqCpLYmrQI9SHySN9ixi8bemaYX73SHrCI\nZbodKbN1bSzpIQvA57bdPdarOHSP4Hhw6fXULp/zDKGkc38d31oOTgznh/q5e15a\nJcOekOq5Mr4oRovSnKEGUWkRA7N1WgdE2qUNTgjTVQsCMvklkDSi5zEiZ1Rmeheq\nPOPZ5EeFSVmYWb5QrUn2spB/hO8Vv6DQpS3LknlFq+DQmqDPbOaGbNwAi5GHXUxa\n2XgJ2tomrCtwsY6zbNdscP9VTbgwxSdChhSTmhCYDY0O3opfZtJcg8+4S6Fdglr8\nzO9OgDtnWhLTZ2l5W/mL8fGS3VLLiTxKhXq0WruFHTbSxmRNnB4GRkGGJFa4JN1o\nsNdkPaPUoiI+O5rMz/S44bgIiUOWlfGbTZ7ZCKT3AQauGcUpjfhw3NjyO0fqaine\nuiAa0j9GDV1pKAlqUEe6nCtZgzhLfU+vYavN5NZ72aQDGFFp/VthNvfkGdeRnQy9\nGTgkE+WxG61IzDLPW41+Spem9eHA6KJfsmKzzFagvmfbGcuunY6/iGreMddXU3ST\nr2biRHP+YUNGfkxWCITLlS5Ea3aj6C2Q6X5jya3jWGPoqiNskYjjYp8/q7Q8Xz72\ns+ukvb/V57fSRb7OqCG0zwyCkX9EUQIDAQABo3gwdjAMBgNVHRMBAf8EAjAAMA4G\nA1UdDwEB/wQEAwIGwDAWBgNVHSUBAf8EDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQU\nCvr2+uVtOqvc8eKxbruHKlKvdrUwHwYDVR0jBBgwFoAUMibh+RGOAfpdZLujdbn8\n48haCkswDQYJKoZIhvcNAQELBQADggIBAJBkpY5b4BfJEZ9cqbKlus7FNsVGI1Jm\nePuMX/qmt5atPWU3CyTSfOMXXr6PxSBhJOpYwc3lfkj+OPJnDEF7HYWS5urtif3A\nxhqqUwIuqlyl+mn+3FYMOn1DmYdbdy0oj+GzEE+NrU23fqi05iHVxQDwwiAfGa63\nOuPU92cOj5W7toukyPD5cvnLjiA/kTUKHKL4KdFWwPIWjrvb4bJKWjirKywtEneV\n3qvyOnVSs/VqjQ9ctVRX4O+7u24mZt5JHTi7SmRYjtz1gQVbLQBXwcM7rSPf59et\n9DYOU+0ZbOjA6XWK6RyfMXj2zXs7ZegulQWm8hAP7KzJNtPtT/S8Ct6zD0rBKaNp\nyaGHbbCZ6ImBd2Wxc20Ctyp+EF3yFFVhATQi2IZ1B6r+cgDTWPnQxo0YIWFWCg49\nG1WMe4T3SLVL9iYAY1uRoQ7CfOZ+l5vO72sD+V5sQQvdaPnDk7PSgRwFIPMM+wsX\nGk8mAHAu1xQkB4HJiG9yqQRowL5vd3pdOVDXPRC6WWYipa6XsNr0tQwXUSpJ29yp\nrBDJ9IBfcB0xVWJV3XXQQ9gl1F9wBy9uxZGSoEE8B3ZTLU6B134o27AEOO43zhK+\nQ3psqJUHkmdMPK2DXFAaLpvfMWkJ5IiNDCk60GSBo+wQ61ugvX8ZmzVWMe/wAPIN\nxImoqYDvfWx+\n-----END CERTIFICATE-----\n','CA Authority','2026-04-30 10:49:21','2027-04-30 10:49:21','ACTIVE','2026-04-30 10:49:22');
/*!40000 ALTER TABLE `certificates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entities`
--

DROP TABLE IF EXISTS `entities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entities` (
  `entity_id` int NOT NULL AUTO_INCREMENT,
  `entity_code` varchar(50) NOT NULL,
  `entity_name` varchar(255) NOT NULL,
  `entity_type` varchar(50) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'INACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `request_status` enum('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
  PRIMARY KEY (`entity_id`),
  UNIQUE KEY `entity_code` (`entity_code`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entities`
--

LOCK TABLES `entities` WRITE;
/*!40000 ALTER TABLE `entities` DISABLE KEYS */;
INSERT INTO `entities` VALUES (1,'TEST_ORG','Test Organization','organization','ACTIVE','2026-04-14 08:58:26','APPROVED'),(2,'ENTITY001','TEST ORG','organization','ACTIVE','2026-04-23 07:24:47','APPROVED'),(11,'ENTITY02','Apcog','organization','ACTIVE','2026-04-30 01:08:15','APPROVED');
/*!40000 ALTER TABLE `entities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `global_directory`
--

DROP TABLE IF EXISTS `global_directory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `global_directory` (
  `directory_id` int NOT NULL AUTO_INCREMENT,
  `entity_code` varchar(50) DEFAULT NULL,
  `gateway_code` varchar(100) DEFAULT NULL,
  `service_url` varchar(255) DEFAULT NULL,
  `auth_cert_id` int DEFAULT NULL,
  `sign_cert_id` int DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  PRIMARY KEY (`directory_id`),
  KEY `auth_cert_id` (`auth_cert_id`),
  KEY `sign_cert_id` (`sign_cert_id`),
  CONSTRAINT `global_directory_ibfk_1` FOREIGN KEY (`auth_cert_id`) REFERENCES `certificates` (`cert_id`),
  CONSTRAINT `global_directory_ibfk_2` FOREIGN KEY (`sign_cert_id`) REFERENCES `certificates` (`cert_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `global_directory`
--

LOCK TABLES `global_directory` WRITE;
/*!40000 ALTER TABLE `global_directory` DISABLE KEYS */;
INSERT INTO `global_directory` VALUES (1,'1','TEST_GW001',NULL,11,12,'ACTIVE'),(2,'UNKNOWN','	TEST_GW001',NULL,NULL,8,'ACTIVE'),(3,'1','as',NULL,9,10,'ACTIVE');
/*!40000 ALTER TABLE `global_directory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `global_service_register`
--

DROP TABLE IF EXISTS `global_service_register`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `global_service_register` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `entity_id` int NOT NULL,
  `subsystem_id` int NOT NULL,
  `service_code` varchar(100) NOT NULL,
  `service_name` varchar(255) DEFAULT NULL,
  `service_version` varchar(50) DEFAULT 'v1',
  `full_service_id` varchar(500) DEFAULT NULL,
  `service_url` varchar(500) DEFAULT NULL,
  `http_method` varchar(10) DEFAULT NULL,
  `protocol` varchar(20) DEFAULT 'REST',
  `security_server_id` int DEFAULT NULL,
  `description` text,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`),
  UNIQUE KEY `unique_service` (`entity_id`,`subsystem_id`,`service_code`,`service_version`),
  KEY `fk_service_subsystem` (`subsystem_id`),
  KEY `fk_service_security_server` (`security_server_id`),
  CONSTRAINT `fk_service_entity` FOREIGN KEY (`entity_id`) REFERENCES `entities` (`entity_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_service_security_server` FOREIGN KEY (`security_server_id`) REFERENCES `network_config` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_service_subsystem` FOREIGN KEY (`subsystem_id`) REFERENCES `subsystems` (`subsystem_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `global_service_register`
--

LOCK TABLES `global_service_register` WRITE;
/*!40000 ALTER TABLE `global_service_register` DISABLE KEYS */;
INSERT INTO `global_service_register` VALUES (2,1,1,'getEmployee','Get Employee Details','v1','DEV/GOV/ORG1/HR/getEmployee/v1','http://hr-service/api/employee','GET','REST',1,NULL,'ACTIVE','2026-04-20 20:38:05','2026-04-20 20:38:05'),(10,1,1,'getEmployee2','Get Employee Details','v1','getEmployee2/vv1','HTTP://localhost:5000/api/get/employee','GET','HTTP',1,'test description','ACTIVE','2026-04-27 03:16:39','2026-04-27 03:16:39'),(11,11,2,'XT220MFH7E','hello world','v1','apcog/app2/health','http://106.51.108.71:9090/app2/health','GET','HTTP',1,'test','ACTIVE','2026-06-15 10:46:12','2026-06-15 10:46:12');
/*!40000 ALTER TABLE `global_service_register` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `network_config`
--

DROP TABLE IF EXISTS `network_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `version` varchar(50) DEFAULT NULL,
  `network_instance` varchar(100) DEFAULT NULL,
  `gateway_code` varchar(100) DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `host` varchar(100) DEFAULT NULL,
  `port` int DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `ip_address` varchar(50) DEFAULT NULL,
  `environment` varchar(50) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'INACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gateway_code_UNIQUE` (`gateway_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_config`
--

LOCK TABLES `network_config` WRITE;
/*!40000 ALTER TABLE `network_config` DISABLE KEYS */;
INSERT INTO `network_config` VALUES (1,'Test Security Gateway','2.0','TEST','TEST_SS001',1,'192.168.1.100',9001,'test-gateway.local','192.168.1.100','Testing','ACTIVE','2026-04-14 09:15:36','2026-04-22 03:51:42'),(2,'sd','d','ff','as',1,'ghh',9236,'ghh','127.03.12.02','STAGING','ACTIVE','2026-04-24 04:15:02','2026-04-24 04:15:02'),(4,'Test Security Gateway 1','2.0','TEST2','TEST_GW001',11,'127.0.0.1',8000,'127.0.0.1','test-gateway.local','STAGING','ACTIVE','2026-04-30 10:45:16','2026-04-30 17:43:43');
/*!40000 ALTER TABLE `network_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `performance_logs`
--

DROP TABLE IF EXISTS `performance_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `performance_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `server_type` enum('SECURITY_SERVER','GLOBAL_SERVER') NOT NULL,
  `server_id` varchar(100) NOT NULL,
  `cpu_usage_percent` decimal(5,2) DEFAULT NULL,
  `memory_usage_percent` decimal(5,2) DEFAULT NULL,
  `total_memory_mb` int DEFAULT NULL,
  `used_memory_mb` int DEFAULT NULL,
  `disk_total_gb` decimal(10,2) DEFAULT NULL,
  `disk_used_gb` decimal(10,2) DEFAULT NULL,
  `disk_free_gb` decimal(10,2) DEFAULT NULL,
  `active_connections` int DEFAULT NULL,
  `request_per_second` decimal(10,2) DEFAULT NULL,
  `status` enum('NORMAL','WARNING','CRITICAL') DEFAULT 'NORMAL',
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_server` (`server_id`),
  KEY `idx_time` (`recorded_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `performance_logs`
--

LOCK TABLES `performance_logs` WRITE;
/*!40000 ALTER TABLE `performance_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `performance_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_log`
--

DROP TABLE IF EXISTS `registration_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `gateway_code` varchar(100) DEFAULT NULL,
  `action` enum('SUBMITTED','APPROVED','REJECTED') DEFAULT NULL,
  `performed_by` varchar(100) DEFAULT NULL,
  `remarks` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_log`
--

LOCK TABLES `registration_log` WRITE;
/*!40000 ALTER TABLE `registration_log` DISABLE KEYS */;
INSERT INTO `registration_log` VALUES (1,'TEST_GW001','SUBMITTED','security_server',NULL,'2026-04-14 09:15:36'),(2,'as','SUBMITTED','security_server',NULL,'2026-04-24 04:15:03'),(3,'TEST_GW001','SUBMITTED','security_server',NULL,'2026-04-30 01:10:58'),(4,'TEST_GW001','SUBMITTED','security_server',NULL,'2026-04-30 10:45:17'),(5,'','SUBMITTED','system','','2026-06-15 09:16:06'),(6,'','SUBMITTED','system','','2026-06-15 09:45:10');
/*!40000 ALTER TABLE `registration_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `security_logs`
--

DROP TABLE IF EXISTS `security_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `server_type` enum('SECURITY_SERVER','GLOBAL_SERVER') NOT NULL,
  `server_id` varchar(100) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `severity` enum('LOW','MEDIUM','HIGH','CRITICAL') DEFAULT 'LOW',
  `user_id` varchar(255) DEFAULT NULL,
  `subsystem` varchar(255) DEFAULT NULL,
  `resource` varchar(255) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL,
  `status` enum('SUCCESS','FAILED') NOT NULL,
  `failure_reason` text,
  `ip_address` varchar(50) DEFAULT NULL,
  `geo_location` varchar(255) DEFAULT NULL,
  `certificate_id` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sec_server` (`server_id`),
  KEY `idx_sec_event` (`event_type`),
  KEY `idx_sec_severity` (`severity`),
  KEY `idx_sec_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_logs`
--

LOCK TABLES `security_logs` WRITE;
/*!40000 ALTER TABLE `security_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `security_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_keys`
--

DROP TABLE IF EXISTS `server_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server_keys` (
  `key_id` int NOT NULL AUTO_INCREMENT,
  `gateway_code` varchar(100) DEFAULT NULL,
  `key_type` enum('AUTH','SIGN') DEFAULT NULL,
  `public_key` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`key_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_keys`
--

LOCK TABLES `server_keys` WRITE;
/*!40000 ALTER TABLE `server_keys` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subsystems`
--

DROP TABLE IF EXISTS `subsystems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subsystems` (
  `subsystem_id` int NOT NULL AUTO_INCREMENT,
  `entity_id` int NOT NULL,
  `subsystem_code` varchar(100) NOT NULL,
  `subsystem_name` varchar(255) DEFAULT NULL,
  `description` text,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`subsystem_id`),
  UNIQUE KEY `unique_entity_subsystem` (`entity_id`,`subsystem_code`),
  CONSTRAINT `fk_subsystem_entity` FOREIGN KEY (`entity_id`) REFERENCES `entities` (`entity_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subsystems`
--

LOCK TABLES `subsystems` WRITE;
/*!40000 ALTER TABLE `subsystems` DISABLE KEYS */;
INSERT INTO `subsystems` VALUES (1,1,'AXT569AE49','HR','application for hr','ACTIVE','2026-04-20 20:06:22','2026-04-20 20:06:22'),(2,1,'HR','Human Resource System','Human Resource System - Host: localhost','ACTIVE','2026-04-25 03:11:55','2026-04-25 03:11:55');
/*!40000 ALTER TABLE `subsystems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactional_logs`
--

DROP TABLE IF EXISTS `transactional_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactional_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `request_id` varchar(255) NOT NULL,
  `client_subsystem` varchar(255) NOT NULL,
  `provider_subsystem` varchar(255) NOT NULL,
  `client_server_id` varchar(100) DEFAULT NULL,
  `provider_server_id` varchar(100) DEFAULT NULL,
  `service_code` varchar(255) NOT NULL,
  `service_version` varchar(50) DEFAULT NULL,
  `request_time` timestamp NULL DEFAULT NULL,
  `response_time` timestamp NULL DEFAULT NULL,
  `duration_ms` int DEFAULT NULL,
  `response_status` enum('SUCCESS','FAILED','TIMEOUT') NOT NULL,
  `http_status_code` int DEFAULT NULL,
  `request_size_bytes` int DEFAULT NULL,
  `response_size_bytes` int DEFAULT NULL,
  `correlation_id` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tx_request` (`request_id`),
  KEY `idx_tx_client` (`client_subsystem`),
  KEY `idx_tx_provider` (`provider_subsystem`),
  KEY `idx_tx_time` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactional_logs`
--

LOCK TABLES `transactional_logs` WRITE;
/*!40000 ALTER TABLE `transactional_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `transactional_logs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-16 18:03:14
