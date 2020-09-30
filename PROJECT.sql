/*
 Navicat Premium Data Transfer

 Source Server         : TEST
 Source Server Type    : Oracle
 Source Server Version : 110200
 Source Schema         : PROJECT

 Target Server Type    : Oracle
 Target Server Version : 110200
 File Encoding         : 65001

 Date: 01/10/2020 00:45:46
*/


-- ----------------------------
-- Table structure for CAREER
-- ----------------------------
DROP TABLE "PROJECT"."CAREER";
CREATE TABLE "PROJECT"."CAREER" (
  "POST_ID" NUMBER(5,0) NOT NULL,
  "PHOTO" VARCHAR2(50 BYTE),
  "VIDEO" VARCHAR2(50 BYTE)
)
LOGGING
NOCOMPRESS
PCTFREE 10
INITRANS 1
STORAGE (
  BUFFER_POOL DEFAULT
)
PARALLEL 1
NOCACHE
DISABLE ROW MOVEMENT
;

-- ----------------------------
-- Records of CAREER
-- ----------------------------

-- ----------------------------
-- Table structure for COMMUNITY
-- ----------------------------
DROP TABLE "PROJECT"."COMMUNITY";
CREATE TABLE "PROJECT"."COMMUNITY" (
  "COMMUNITY_ID" NUMBER(5,0) NOT NULL,
  "COMMUNITY_NAME" VARCHAR2(50 BYTE) NOT NULL,
  "DATE_OF_CREATION" DATE NOT NULL,
  "DESCRIPTION" VARCHAR2(300 BYTE) NOT NULL,
  "PHOTO" VARCHAR2(100 BYTE)
)
LOGGING
NOCOMPRESS
PCTFREE 10
INITRANS 1
STORAGE (
  INITIAL 65536 
  NEXT 1048576 
  MINEXTENTS 1
  MAXEXTENTS 2147483645
  BUFFER_POOL DEFAULT
)
PARALLEL 1
NOCACHE
DISABLE ROW MOVEMENT
;

-- ----------------------------
-- Records of COMMUNITY
-- ----------------------------
INSERT INTO "PROJECT"."COMMUNITY" VALUES ('1', 'COMM1', TO_DATE('2020-09-28 00:00:00', 'SYYYY-MM-DD HH24:MI:SS'), 'XD', NULL);
