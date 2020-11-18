/*
 Navicat Premium Data Transfer

 Source Server         : SYSTEM
 Source Server Type    : Oracle
 Source Server Version : 110200
 Source Schema         : PROJECT

 Target Server Type    : Oracle
 Target Server Version : 110200
 File Encoding         : 65001

 Date: 02/11/2020 22:42:49
*/


-- ----------------------------
-- Table structure for EXPERTISE
-- ----------------------------
DROP TABLE "PROJECT"."EXPERTISE";
CREATE TABLE "PROJECT"."EXPERTISE" (
  "STD_ID" NUMBER(7,0) NOT NULL,
  "TOPIC" VARCHAR2(30 BYTE) NOT NULL
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
-- Records of EXPERTISE
-- ----------------------------
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705002', 'Algorithm');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705004', 'Algorithm');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Algorithm');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Computer Vision');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Deep Learning');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Machine Learning');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Natural Language Processing');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705008', 'Networking');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705015', 'Machine Learning');
INSERT INTO "PROJECT"."EXPERTISE" VALUES ('1705056', 'Algorithm');
