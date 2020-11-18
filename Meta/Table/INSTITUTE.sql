/*
 Navicat Premium Data Transfer

 Source Server         : SYSTEM
 Source Server Type    : Oracle
 Source Server Version : 110200
 Source Schema         : PROJECT

 Target Server Type    : Oracle
 Target Server Version : 110200
 File Encoding         : 65001

 Date: 02/11/2020 22:42:28
*/


-- ----------------------------
-- Table structure for INSTITUTE
-- ----------------------------
DROP TABLE "PROJECT"."INSTITUTE";
CREATE TABLE "PROJECT"."INSTITUTE" (
  "INSTITUTE_ID" NUMBER(15,0) NOT NULL,
  "NAME" VARCHAR2(50 BYTE) NOT NULL,
  "CITY" VARCHAR2(30 BYTE),
  "COUNTRY" VARCHAR2(30 BYTE),
  "TYPE" VARCHAR2(15 BYTE)
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
-- Records of INSTITUTE
-- ----------------------------
INSERT INTO "PROJECT"."INSTITUTE" VALUES ('1', 'Bangladesh University of Engineering & Technology', 'Dhaka', 'Bangladesh', 'University');
INSERT INTO "PROJECT"."INSTITUTE" VALUES ('5', 'Mohammadpur Government High School', 'Dhaka', 'Bangladesh', 'School');
INSERT INTO "PROJECT"."INSTITUTE" VALUES ('2', 'Khulna University of Engineering & Technology', 'Khulna', 'Bangladesh', 'University');
INSERT INTO "PROJECT"."INSTITUTE" VALUES ('3', 'ACI Limited', 'Dhaka', 'Bangladesh', 'Drug Company');
INSERT INTO "PROJECT"."INSTITUTE" VALUES ('4', 'Notre Dame College', 'Dhaka', 'Bangladesh', 'College');
