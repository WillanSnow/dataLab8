/*
 Navicat Premium Data Transfer

 Source Server         : lab2
 Source Server Type    : MySQL
 Source Server Version : 80030
 Source Host           : localhost:3306
 Source Schema         : lab8

 Target Server Type    : MySQL
 Target Server Version : 80030
 File Encoding         : 65001

 Date: 21/12/2023 22:15:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for account
-- ----------------------------
DROP TABLE IF EXISTS `account`;
CREATE TABLE `account`  (
  `account_id` int NOT NULL,
  `password` char(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `phone_num` char(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  PRIMARY KEY (`account_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for changes
-- ----------------------------
DROP TABLE IF EXISTS `changes`;
CREATE TABLE `changes`  (
  `change_id` int NOT NULL AUTO_INCREMENT,
  `change_time` datetime NOT NULL,
  `cust_id` int NOT NULL,
  `trade_id` int NOT NULL,
  `action` int NOT NULL,
  PRIMARY KEY (`change_id`) USING BTREE,
  INDEX `CHANGE_CUST`(`cust_id` ASC) USING BTREE,
  INDEX `CHANGE_TRADE`(`trade_id` ASC) USING BTREE,
  CONSTRAINT `CHANGE_CUST` FOREIGN KEY (`cust_id`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `CHANGE_TRADE` FOREIGN KEY (`trade_id`) REFERENCES `trade` (`trade_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for customer
-- ----------------------------
DROP TABLE IF EXISTS `customer`;
CREATE TABLE `customer`  (
  `cust_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `balance` float NOT NULL,
  `limit` float NOT NULL,
  `account_id` int NOT NULL,
  PRIMARY KEY (`cust_id`) USING BTREE,
  INDEX `CUST_ACCOUNT`(`account_id` ASC) USING BTREE,
  CONSTRAINT `CUST_ACCOUNT` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for manager
-- ----------------------------
DROP TABLE IF EXISTS `manager`;
CREATE TABLE `manager`  (
  `manager_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `account_id` int NOT NULL,
  PRIMARY KEY (`manager_id`) USING BTREE,
  INDEX `MANAGER_ACCOUNT`(`account_id` ASC) USING BTREE,
  CONSTRAINT `MANAGER_ACCOUNT` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for trade
-- ----------------------------
DROP TABLE IF EXISTS `trade`;
CREATE TABLE `trade`  (
  `trade_id` int NOT NULL AUTO_INCREMENT,
  `amount` float NOT NULL,
  `status` int NOT NULL,
  `cust_a` int NOT NULL,
  `cust_b` int NOT NULL,
  PRIMARY KEY (`trade_id`) USING BTREE,
  INDEX `BEGIN_CUST`(`cust_a` ASC) USING BTREE,
  INDEX `DST_CUST`(`cust_b` ASC) USING BTREE,
  CONSTRAINT `BEGIN_CUST` FOREIGN KEY (`cust_a`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `DST_CUST` FOREIGN KEY (`cust_b`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
