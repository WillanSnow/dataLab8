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

 Date: 26/12/2023 22:39:12
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for account
-- ----------------------------
DROP TABLE IF EXISTS `account`;
CREATE TABLE `account`  (
  `account_id` int NOT NULL,
  `password` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `phone_num` char(11) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `code` char(4) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL,
  `code_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`account_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for changes
-- ----------------------------
DROP TABLE IF EXISTS `changes`;
CREATE TABLE `changes`  (
  `change_id` int NOT NULL,
  `change_time` datetime NOT NULL,
  `cust_id` int NOT NULL,
  `trade_id` int NOT NULL,
  `action` int NOT NULL,
  PRIMARY KEY (`change_id`) USING BTREE,
  INDEX `CHANGE_CUST`(`cust_id` ASC) USING BTREE,
  INDEX `CHANGE_TRADE`(`trade_id` ASC) USING BTREE,
  CONSTRAINT `CHANGE_CUST` FOREIGN KEY (`cust_id`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `CHANGE_TRADE` FOREIGN KEY (`trade_id`) REFERENCES `trade` (`trade_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for customer
-- ----------------------------
DROP TABLE IF EXISTS `customer`;
CREATE TABLE `customer`  (
  `cust_id` int NOT NULL,
  `name` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `balance` float NOT NULL,
  `limit` float NOT NULL,
  `account_id` int NOT NULL,
  PRIMARY KEY (`cust_id`) USING BTREE,
  INDEX `CUST_ACCOUNT`(`account_id` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for manager
-- ----------------------------
DROP TABLE IF EXISTS `manager`;
CREATE TABLE `manager`  (
  `manager_id` int NOT NULL,
  `name` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `account_id` int NOT NULL,
  PRIMARY KEY (`manager_id`) USING BTREE,
  INDEX `MANAGER_ACCOUNT`(`account_id` ASC) USING BTREE,
  CONSTRAINT `MANAGER_ACCOUNT` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for trade
-- ----------------------------
DROP TABLE IF EXISTS `trade`;
CREATE TABLE `trade`  (
  `trade_id` int NOT NULL,
  `amount` float NOT NULL,
  `status` int NOT NULL,
  `cust_a` int NOT NULL,
  `cust_b` int NOT NULL,
  PRIMARY KEY (`trade_id`) USING BTREE,
  INDEX `BEGIN_CUST`(`cust_a` ASC) USING BTREE,
  INDEX `DST_CUST`(`cust_b` ASC) USING BTREE,
  CONSTRAINT `BEGIN_CUST` FOREIGN KEY (`cust_a`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `END_CUST` FOREIGN KEY (`cust_b`) REFERENCES `customer` (`cust_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Triggers structure for table customer
-- ----------------------------
-- 检查余额
-- CREATE TRIGGER checkenough
-- BEFORE UPDATE ON customer
-- FOR EACH ROW
-- BEGIN
-- 	IF(NEW.balance >= 0) THEN
-- 	BEGIN
-- 		SELECT 'Available balance is ENOUGH' into @cust;
-- 	END;
-- 	ELSE
-- 	SIGNAL SQLSTATE '45000'  
--         SET MESSAGE_TEXT = 'Available balance is NOT ENOUGH';
-- 	END IF;
-- END

-- 余额较少时自动确认
-- CREATE TRIGGER getamount
-- AFTER INSERT ON trade
-- FOR EACH ROW
-- BEGIN
-- 	DECLARE now_balance DECIMAL(10,2);
-- 	select balance INTO now_balance
-- 	from customer
-- 	WHERE NEW.cust_b != 0 and cust_id = NEW.cust_b;
-- 	IF(now_balance <= 50) THEN
-- 	BEGIN
-- 		UPDATE customer
-- 		set balance = balance + NEW.amount;
-- 		UPDATE trade
-- 		SET `status` = 1;
-- 		SET @nowday = CURDATE(); 
-- 		INSERT INTO changes(change_time,cust_id,trade_id,`status`)
-- 		VALUES(@nowday,NEW.cust_b,NEW.trade_id,1);
-- 	END;
-- 	END IF;
-- END

-- CREATE TRIGGER getamount
-- AFTER INSERT ON trade
-- FOR EACH ROW
-- BEGIN
--     IF (NEW.cust_b != 0) THEN
--         SET @now_balance = (SELECT balance FROM customer WHERE cust_id = NEW.cust_b);

--         IF (@now_balance <= 50) THEN
--             UPDATE customer SET balance = balance + NEW.amount WHERE cust_id = NEW.cust_b;
--             UPDATE trade SET `status` = 1 WHERE trade_id = NEW.trade_id;

--             SET @nowday = CURDATE(); 
--             INSERT INTO changes (change_time, cust_id, trade_id, `status`)
--             VALUES (@nowday, NEW.cust_b, NEW.trade_id, 1);
--         END IF;
--     END IF;
-- END;

SET FOREIGN_KEY_CHECKS = 1;

-- 创建客户用户
CREATE ROLE 'cust';
-- 分配权限
-- 可查看所有表
GRANT SELECT ON lab8.* TO 'cust';
-- 对changes、trade可增、改
GRANT INSERT, UPDATE ON lab8.changes TO 'cust';
GRANT INSERT, UPDATE ON lab8.trade TO 'cust';
-- 对customer可改
GRANT UPDATE ON lab8.customer TO 'cust';
-- 创建用户
CREATE USER 'cust'@'localhost' IDENTIFIED BY '87654321';
-- 分配角色
GRANT 'cust' TO 'cust'@'localhost';


-- 创建经理
CREATE ROLE 'manager';
-- 分配权限
-- 可看所有表
GRANT SELECT ON lab8.* TO 'manager';
-- 对customer、account可增、删
GRANT INSERT, DELETE, UPDATE ON lab8.customer TO 'manager';
GRANT INSERT, DELETE ON lab8.account TO 'manager';
-- 创建用户
CREATE USER 'manager'@'localhost' IDENTIFIED BY '12345678';
-- 分配角色
GRANT 'manager' TO 'manager'@'localhost';

-- 创建系统用户
INSERT INTO account(account_id, password, phone_num) VALUES(0, "111111", 11122223333 );
INSERT INTO customer(cust_id, name, balance, `limit`, account_id) VALUES(0, "-", 10000000, 1000000, 0);