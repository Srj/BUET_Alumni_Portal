/*
 Navicat Premium Data Transfer

 Source Server         : PROJ
 Source Server Type    : Oracle
 Source Server Version : 110200
 Source Schema         : DJANGO_DB

 Target Server Type    : Oracle
 Target Server Version : 110200
 File Encoding         : 65001

 Date: 18/11/2020 22:29:58
*/


-- ----------------------------
-- Table structure for CAREER
-- ----------------------------
DROP TABLE "DJANGO_DB"."CAREER";
CREATE TABLE "DJANGO_DB"."CAREER" (
  "POST_ID" NUMBER(5,0) NOT NULL,
  "PHOTO" VARCHAR2(50 BYTE),
  "VIDEO" VARCHAR2(50 BYTE)
)
TABLESPACE "DJANGO_DB_TBSP_PERM"
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
-- Records of CAREER
-- ----------------------------
INSERT INTO "DJANGO_DB"."CAREER" VALUES ('7', NULL, NULL);

-- ----------------------------
-- Primary Key structure for table CAREER
-- ----------------------------
ALTER TABLE "DJANGO_DB"."CAREER" ADD CONSTRAINT "CAREER_PK" PRIMARY KEY ("POST_ID");

-- ----------------------------
-- Checks structure for table CAREER
-- ----------------------------
ALTER TABLE "DJANGO_DB"."CAREER" ADD CONSTRAINT "SYS_C0016074" CHECK ("POST_ID" IS NOT NULL) NOT DEFERRABLE INITIALLY IMMEDIATE NORELY VALIDATE;
