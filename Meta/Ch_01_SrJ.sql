/*
 Navicat Premium Data Transfer

 Source Server         : SYSTEM
 Source Server Type    : Oracle
 Source Server Version : 110200
 Source Schema         : DJANGO_DB

 Target Server Type    : Oracle
 Target Server Version : 110200
 File Encoding         : 65001

 Date: 02/11/2020 22:40:07
*/


-- ----------------------------
-- Table structure for ENDORSE
-- ----------------------------
DROP TABLE "ENDORSE";
CREATE TABLE "ENDORSE" (
  "GIVER_ID" NUMBER(7,0) NOT NULL,
  "TAKER_ID" NUMBER(7,0) NOT NULL,
  "TOPIC" VARCHAR2(30 BYTE) NOT NULL,
  "TIMESTAMP" DATE
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
-- Records of ENDORSE
-- ----------------------------
INSERT INTO "ENDORSE" VALUES ('1705008', '1705002', 'Algorithm', NULL);
INSERT INTO "ENDORSE" VALUES ('1705015', '1705008', 'Deep Learning', NULL);
INSERT INTO "ENDORSE" VALUES ('1705015', '1705008', 'Networking', NULL);
INSERT INTO "ENDORSE" VALUES ('1705002', '1705008', 'Machine Learning', NULL);
INSERT INTO "ENDORSE" VALUES ('1705002', '1705008', 'Natural Language Processing', NULL);
INSERT INTO "ENDORSE" VALUES ('1705008', '1705056', 'Algorithm', NULL);
INSERT INTO "ENDORSE" VALUES ('1705002', '1705008', 'Deep Learning', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705008', 'Computer Vision', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705002', 'Algorithm', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705008', 'Machine Learning', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705008', 'Natural Language Processing', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705008', 'Algorithm', NULL);
INSERT INTO "ENDORSE" VALUES ('1705004', '1705008', 'Deep Learning', NULL);
INSERT INTO "ENDORSE" VALUES ('1705002', '1705008', 'Algorithm', NULL);
INSERT INTO "ENDORSE" VALUES ('1705002', '1705008', 'Computer Vision', NULL);
COMMIT;
COMMIT;
