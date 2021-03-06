--USER TABLE SCHEMA
DROP TABLE IF EXISTS USER_TABLE CASCADE;
CREATE TABLE USER_TABLE (
	STD_ID INTEGER NOT NULL,
	FULL_NAME VARCHAR(100) NOT NULL,
	NICK_NAME VARCHAR(20),
	PASSWORD VARCHAR(256) NOT NULL,
	EMAIL VARCHAR(50) NOT NULL,
	MOBILE VARCHAR(15), 
	DATE_OF_BIRTH DATE,
	PRIMARY KEY(STD_ID)
);


 --PROFILE SCHEMA
DROP TABLE IF EXISTS PROFILE;
CREATE TABLE PROFILE(
	STD_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
	HOUSE_NO VARCHAR(10),
	ROAD_NO VARCHAR(10),
	ZIP_CODE VARCHAR(10),
	CITY VARCHAR(30),
	COUNTRY VARCHAR(30),
	HOME_TOWN VARCHAR(100),
	PHOTO VARCHAR(100),
	FACEBOOK VARCHAR(100),
	TWITTER VARCHAR(100),
	LINKEDIN VARCHAR(100),
	GOOGLE_SCHOLAR VARCHAR(100),
	RESEARCHGATE VARCHAR(100),
	ABOUT VARCHAR(512),
	PRIMARY KEY(STD_ID)
);

--EXPERTISE
DROP TABLE IF EXISTS EXPERTISE CASCADE;
CREATE TABLE EXPERTISE(
	STD_ID INTEGER NOT NULL,
	TOPIC VARCHAR(30) NOT NULL,
	PRIMARY KEY(STD_ID,TOPIC),
	CONSTRAINT STD_ID_EXPERTISE FOREIGN KEY(STD_ID) REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE
);


--ENDORSE
DROP TABLE IF EXISTS ENDORSE;
CREATE TABLE ENDORSE (
	GIVER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
	TAKER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
	TOPIC VARCHAR(30) NOT NULL,
	TIMESTAMP DATE,
	PRIMARY KEY(GIVER_ID,TAKER_ID,TOPIC),
	CONSTRAINT TOPIC_CONS FOREIGN KEY(TAKER_ID, TOPIC) REFERENCES EXPERTISE(STD_ID,TOPIC) ON DELETE CASCADE
);
--INSTITUTE
DROP TABLE IF EXISTS INSTITUTE CASCADE;
CREATE TABLE INSTITUTE (
	INSTITUTE_ID SERIAL NOT NULL,
	NAME VARCHAR(100) NOT NULL,
	CITY VARCHAR(30),
	COUNTRY VARCHAR(50),
	TYPE VARCHAR(15),
	PRIMARY KEY(INSTITUTE_ID)
);

--POSTGRAD
DROP TABLE IF EXISTS POSTGRAD;
CREATE TABLE POSTGRAD(
	STD_ID INTEGER NOT NULL,
	MSC VARCHAR(100),
	PHD VARCHAR(100),
	PRIMARY KEY(STD_ID),
	CONSTRAINT STD_POSTGRAD FOREIGN KEY(STD_ID) REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE
);

--UNDERGRAD
DROP TABLE IF EXISTS UNDERGRAD;
CREATE TABLE UNDERGRAD(
	STD_ID INTEGER NOT NULL,
	HALL VARCHAR(20),
	DEPT VARCHAR(20),
	LVL SMALLINT,
	TERM SMALLINT,
	PRIMARY KEY(STD_ID),
	CONSTRAINT STD_ID_UNDERGRAD FOREIGN KEY(STD_ID) REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
	CONSTRAINT LEVEL_CONSTRAINT CHECK (LVL BETWEEN 1 AND 5),
	CONSTRAINT TERM_CONS CHECK (TERM BETWEEN 1 AND 2)
);


--WORKS
DROP TABLE IF EXISTS WORKS CASCADE;
CREATE TABLE WORKS(
	STD_ID INTEGER NOT NULL,
	INSTITUTE_ID SERIAL NOT NULL,
	FROM_ DATE NOT NULL,
	TO_ DATE,
	DESIGNATION VARCHAR(50) NOT NULL,
	PRIMARY KEY(STD_ID,INSTITUTE_ID,FROM_),
	CONSTRAINT INSTITUTE_FK FOREIGN KEY(INSTITUTE_ID) REFERENCES INSTITUTE(INSTITUTE_ID) ON DELETE CASCADE,
	CONSTRAINT STD_ID_FK FOREIGN KEY(STD_ID) REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE
	-- CONSTRAINT JOIN_VALIDITY CHECK (FROM_ < TO_)
);
--PROFILE VIEW
DROP VIEW IF EXISTS USER_PROFILE;
CREATE OR REPLACE VIEW USER_PROFILE AS 
SELECT STD_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,DATE_OF_BIRTH,DATE_PART('year',AGE(DATE_OF_BIRTH))::int AS AGE,
HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,COUNTRY,HOME_TOWN,PHOTO,FACEBOOK,TWITTER,LINKEDIN,
GOOGLE_SCHOLAR,RESEARCHGATE,ABOUT,HALL,DEPT,LVL,TERM,MSC,PHD,DESIGNATION,COMPANY
FROM USER_TABLE LEFT JOIN PROFILE USING(STD_ID) 
LEFT JOIN UNDERGRAD USING(STD_ID)
LEFT JOIN POSTGRAD USING(STD_ID) 
LEFT JOIN 
		   (SELECT STD_ID,DESIGNATION,NAME AS COMPANY 
		   FROM WORKS JOIN INSTITUTE USING(INSTITUTE_ID) 
		   WHERE TO_ IS NULL ORDER BY FROM_) AS CURRENT_WORK
USING(STD_ID);

--POST
DROP TABLE IF EXISTS POST CASCADE;
CREATE TABLE POST(
	POST_ID SERIAL PRIMARY KEY,
	DATE_OF_POST TIMESTAMP NOT NULL,
	DESCRIPTION VARCHAR(512) NOT NULL
);

--USER POST
DROP TABLE IF EXISTS USER_POSTS CASCADE;
CREATE TABLE USER_POSTS(
	USER_ID INTEGER REFERENCES USER_TABLE(STD_ID),
	POST_ID SERIAL REFERENCES POST(POST_ID) ON DELETE CASCADE,
	PRIMARY KEY(USER_ID,POST_ID)
);

--USER REPLIES
DROP TABLE IF EXISTS USER_REPLIES;
CREATE TABLE USER_REPLIES(
	USR_REPLS_ROW SERIAL PRIMARY KEY,
	USER_ID INTEGER REFERENCES USER_TABLE(STD_ID),
	POST_ID SERIAL REFERENCES POST(POST_ID) ON DELETE CASCADE,
	TEXT VARCHAR(512) NOT NULL,
	TIMESTAMP TIMESTAMP NOT NULL
);

--RESEARCH
DROP TABLE IF EXISTS RESEARCH;
CREATE TABLE RESEARCH(
	POST_ID SERIAL REFERENCES POST(POST_ID) ON DELETE CASCADE PRIMARY KEY,
	TOPIC_NAME VARCHAR(100) NOT NULL,
	DATE_OF_PUBLICATION DATE,
	JOURNAL VARCHAR(100),
	DOI VARCHAR(256)
);


--JOB POST
DROP TABLE IF EXISTS JOB_POST;
CREATE TABLE JOB_POST(
	POST_ID SERIAL REFERENCES POST(POST_ID)  ON DELETE CASCADE PRIMARY KEY,
	COMPANY_NAME VARCHAR(128) NOT NULL,
	LOCATION VARCHAR(128) NOT NULL,
	REQUIREMENTS VARCHAR(512) NOT NULL,
	DESIGNATION VARCHAR(100) NOT NULL,
	SALARY INTEGER
);

--HELP
DROP TABLE IF EXISTS HELP;
CREATE TABLE HELP(
	POST_ID SERIAL REFERENCES POST(POST_ID) ON DELETE CASCADE PRIMARY KEY,
	TYPE_OF_HELP VARCHAR(64) NOT NULL,
	REASON VARCHAR(128) NOT NULL,
	CELL_NO VARCHAR(15)
);

--CAREER
DROP TABLE IF EXISTS CAREER;
CREATE TABLE CAREER (
  POST_ID SERIAL REFERENCES POST(POST_ID)  ON DELETE CASCADE PRIMARY KEY,
  PHOTO VARCHAR(50),
  VIDEO VARCHAR(50)
);

--COMMUNITY
DROP TABLE IF EXISTS COMMUNITY CASCADE;
CREATE TABLE COMMUNITY(
    COMMUNITY_ID SERIAL PRIMARY KEY,
    COMMUNITY_NAME VARCHAR(200) NOT NULL,
    DESCRIPTION VARCHAR(500) NOT NULL,
    CRITERIA VARCHAR(500) NOT NULL,
    DATE_OF_CREATION TIMESTAMP NOT NULL
);


--MODERATOR
DROP TABLE IF EXISTS MODERATOR CASCADE;
CREATE TABLE MODERATOR(
    COMMUNITY_ID SERIAL NOT NULL REFERENCES COMMUNITY(COMMUNITY_ID) ON DELETE CASCADE,
    USER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
    PRIMARY KEY(COMMUNITY_ID, USER_ID)
);

--COMMUNITY MEMBER
DROP TABLE IF EXISTS COMM_MEMBERS;
CREATE TABLE COMM_MEMBERS(
    COMMUNITY_ID SERIAL NOT NULL REFERENCES COMMUNITY(COMMUNITY_ID) ON DELETE CASCADE,
    USER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
    JOIN_DATE TIMESTAMP NOT NULL,
    PRIMARY KEY(COMMUNITY_ID, USER_ID)
);

--JOIN REQUEST
DROP TABLE IF EXISTS JOIN_REQUEST;
CREATE TABLE JOIN_REQUEST(
    COMMUNITY_ID SERIAL NOT NULL REFERENCES COMMUNITY(COMMUNITY_ID) ON DELETE CASCADE,
    USER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
    REQUEST_TIME TIMESTAMP NOT NULL,
    PRIMARY KEY(COMMUNITY_ID, USER_ID)
);


--COMMUNITY POST
DROP TABLE IF EXISTS COMMUNITY_POST CASCADE;
CREATE TABLE COMMUNITY_POST(
    POST_ID SERIAL,
    DATE_OF_POST DATE NOT NULL,
    DESCRIPTION VARCHAR(512) NOT NULL,
    PRIMARY KEY (POST_ID)
);

--COMMUNITY HELP POST
DROP TABLE IF EXISTS COMMUNITY_HELP;
CREATE TABLE COMMUNITY_HELP(
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE,
    TYPE_OF_HELP VARCHAR(100) NOT NULL,
    REASON VARCHAR(300) NOT NULL,
    CELL_NO VARCHAR(15),
    PHOTO VARCHAR(200),
    PRIMARY KEY (POST_ID)
);

--COMMUNITY CAREER POST
DROP TABLE IF EXISTS COMMUNITY_CAREER;
CREATE TABLE COMMUNITY_CAREER(
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE,
    TOPIC_NAME VARCHAR(100) NOT NULL,
    PHOTO VARCHAR(50),
    VIDEO VARCHAR(50),
    PRIMARY KEY (POST_ID)
);

--COMMUNITY RESEARCH POST
DROP TABLE IF EXISTS COMMUNITY_RESEARCH;
CREATE TABLE COMMUNITY_RESEARCH(
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE,
    TOPIC_NAME VARCHAR(100) NOT NULL,
    DATE_OF_PUBLICATION DATE ,
    JOURNAL VARCHAR(50) ,
    DOI VARCHAR(100),
    PHOTO VARCHAR(200),
    PRIMARY KEY (POST_ID)
);

--COMMUNITY JOB POST
DROP TABLE IF EXISTS COMMUNITY_JOB_POST;
CREATE TABLE COMMUNITY_JOB_POST(
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE,
    COMPANY_NAME VARCHAR(100) NOT NULL,
    LOCATION VARCHAR(300) NOT NULL,
    REQUIREMENTS VARCHAR(500) NOT NULL,
    DESIGNATION VARCHAR(50) NOT NULL,
    SALARY INTEGER,
    PHOTO VARCHAR(200),
    PRIMARY KEY (POST_ID)
);

--COMMUNITY USER POST
DROP TABLE IF EXISTS COMMUNITY_USER_POSTS;
CREATE TABLE COMMUNITY_USER_POSTS(
    USER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE,
    COMMUNITY_ID SERIAL NOT NULL REFERENCES COMMUNITY(COMMUNITY_ID) ON DELETE CASCADE,
    PRIMARY KEY(POST_ID)
);

--COMMUNITY USER REPLIES
DROP TABLE IF EXISTS COMMUNITY_USER_REPLIES;
CREATE TABLE COMMUNITY_USER_REPLIES(
    USR_REPLS_ROW SERIAL,
    USER_ID INTEGER NOT NULL REFERENCES USER_TABLE(STD_ID) ON DELETE CASCADE,
    POST_ID SERIAL NOT NULL REFERENCES COMMUNITY_POST(POST_ID) ON DELETE CASCADE ,
    COMMUNITY_ID SERIAL NOT NULL REFERENCES COMMUNITY(COMMUNITY_ID) ON DELETE CASCADE,
    TEXT VARCHAR(256) NOT NULL,
    TIMESTAMP TIMESTAMP NOT NULL,
    PRIMARY KEY(USR_REPLS_ROW)
);

--EVENT
DROP TABLE IF EXISTS EVENT CASCADE;
CREATE TABLE EVENT(
EVENT_ID SERIAL PRIMARY KEY,
EVENT_NAME VARCHAR(128) NOT NULL,
EVENT_START TIMESTAMP NOT NULL,
EVENT_END TIMESTAMP NOT NULL,
PHOTO VARCHAR(100),
LOCATION VARCHAR(128) NOT NULL,
DESCRIPTION VARCHAR(500) NOT NULL
);

--EVENT_ARRANGE
DROP TABLE IF EXISTS EVENT_ARRANGE;
CREATE TABLE EVENT_ARRANGE(
USER_ID SERIAL REFERENCES USER_TABLE(STD_ID),
EVENT_ID SERIAL REFERENCES EVENT(EVENT_ID) ON DELETE CASCADE,
CONSTRAINT EVENT_ARRANGE_PK PRIMARY KEY(USER_ID,EVENT_ID)
);

--EVENT PARTICIPATES
DROP TABLE IF EXISTS EVENT_PARTICIPATES;
CREATE TABLE EVENT_PARTICIPATES(
USER_ID INTEGER REFERENCES USER_TABLE(STD_ID),
EVENT_ID SERIAL REFERENCES EVENT(EVENT_ID) ON DELETE CASCADE,
CONSTRAINT EVENT_PARTICIPATES_PK PRIMARY KEY(USER_ID, EVENT_ID)
);

-- TIME DIFFERENCE FUNCTION
CREATE OR REPLACE FUNCTION TIME_DIFF(INP TIMESTAMP) RETURNS VARCHAR 
language plpgsql
as
$$
declare
	DIFF INTEGER;
	TEMP INTEGER;
BEGIN
	DIFF :=EXTRACT (EPOCH FROM (NOW() - INP))/60;
	raise notice 'DIFF : %', DIFF;  -- DIFFERENCES IN MINUTES
	TEMP := DIFF/60;
	IF TEMP < 1 THEN
		IF DIFF < 1 THEN
			RETURN 'Just Now';
		ELSE
			RETURN ( ROUND(DIFF, 0)|| ' Minutes');
		END IF;
	ELSE
		TEMP := TEMP/24;
		IF TEMP < 1 THEN
			RETURN ( ROUND(DIFF/60, 0) || ' Hours');
		ELSE
			TEMP := TEMP/30;
			IF TEMP < 1 THEN
				RETURN ( ROUND(DIFF/1440, 0) || ' Days');
			ELSE
				TEMP := TEMP/12;
				IF TEMP < 1 THEN
					RETURN ( ROUND(DIFF/43200, 0) || ' Months');
				ELSE
					RETURN ( ROUND(TEMP,0) || ' Years');
				END IF;
			END IF;
		END IF;
	END IF;
END;
$$
;

--COUNT COMMUNITY MEMBER
CREATE OR REPLACE FUNCTION COUNT_COMM_MEMBER(ID INTEGER) RETURNS INTEGER
language plpgsql
as 
$$
DECLARE
	VAR INTEGER;
BEGIN
	SELECT COUNT(*) INTO VAR FROM COMM_MEMBERS WHERE COMMUNITY_ID = ID;
	RETURN VAR;
END;
$$;