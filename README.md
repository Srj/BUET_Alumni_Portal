# BUET Alumni Portal

BUET Alumni Portal is implemented by [Saifur Rahman Jony](https://github.com/Srj/) and [Zaber Ibn Abdul Hakim](https://github.com/zaber666) for their CSE 216 Term Project (Session January 2020). This project was motivated by the idea to minimize the increasing gap among BUET Alumni and current students and build a solid connection among Alumni and current students for mutual development. 

__N.B.__ : This is a modified version of the original project where [Oracle DBMS](https://www.oracle.com/database/) has been replaced by [PostgreSQL](https://www.postgresql.org/) for ease of reproducibility. All user data have been erased due to privacy concern. 

### Table of Content
* [Installation](https://github.com/Srj/BUET_Alumni_Portal/blob/master/README.md#installation)
    - [Testing](https://github.com/Srj/BUET_Alumni_Portal#testing)
    - [Local Development](https://github.com/Srj/BUET_Alumni_Portal#local-development)
        - [Virtualenv](https://github.com/Srj/BUET_Alumni_Portal#virtualenv)
        - [Conda Environment](https://github.com/Srj/BUET_Alumni_Portal#conda-environment)
* [Documentation](https://github.com/Srj/BUET_Alumni_Portal#documentation)
    * [Users](https://github.com/Srj/BUET_Alumni_Portal#users)
    * [Post](https://github.com/Srj/BUET_Alumni_Portal#post)
    * [Communities](https://github.com/Srj/BUET_Alumni_Portal#communities)
    * [Events](https://github.com/Srj/BUET_Alumni_Portal#events)

## Installation

### Testing:
If you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine, you can test this project with a single line of code. Refer to [here](https://docs.docker.com/docker-for-windows/install/) for detailed instructions on installation of Docker and Docker Compose.

* Firstly, Clone this repository into a folder in your machine.

````
git clone https://github.com/Srj/BUET_Alumni_Portal.git
````

* After that, run the following command in the BUET_Alumni_Portal directory to instantiate the docker image in your machine.

````
docker-compose up
````

That's all. Now this project is running in your local machine. You need not install anything or initialize any database to run this project. Docker has handled everything for you. Visit http://127.0.0.1:8000/ on Windows (or http://0.0.0.0:8000/ on Linux) to run BUET ALumni Portal on your browser. 


__Caution :__ 
* Make sure Docker Daemon is running in your machine or you won't be able to instantiate this project in your machine.

* Any data produced during your testing will be destroyed when you close the docker image. So Each Docker Compose command will run a fresh version. If you want to persist your data in your local machine, feel free to bind volume in [docker-compose.yml](https://github.com/Srj/BUET_Alumni_Portal/blob/master/docker-compose.yml). Refer to [here](https://docs.docker.com/storage/volumes/#use-a-volume-with-docker-compose) for details on binding volume to docker image.

* Running link and port may vary based on your system. You can find the url in your shell.

### Local Development:
If you want to work on this project and create a local version of it on your local machine follow the instructions below.

* Firstly, Clone this repository into a folder in your machine.

````
git clone https://github.com/Srj/BUET_Alumni_Portal.git
````

* Create a new postgres database for this project and run [DDL.sql](https://github.com/Srj/BUET_Alumni_Portal/blob/master/DDL.sql) in your psql or pgadmin to instantiate all necessary postgres relations and functions required for this project. Feel free to explore [DDL.sql](https://github.com/Srj/BUET_Alumni_Portal/blob/master/DDL.sql) to see the DDL of this project.

* Now create a virtualenv or conda env based on your preferences and activate it.

#### Virtualenv

````
python -m virtualenv venv

#Windows
/venv/Scripts/activate

#Linux
source /venv/bin/activate
````

#### Conda Environment

````
conda create --name myenv
conda activate myenv
````

* Now install the required packages for this project using the following command.

````
pip install -r requirements.txt
````

* Make necessary changes in [Alumni_Portal/utils.py](https://github.com/Srj/BUET_Alumni_Portal/blob/master/Alumni_Portal/utils.py) to connect to your postgres database you have just created.

````python
#--------------------------Connect Database----------------------------- 
def db():
    conn = psycopg2.connect(
                user="YOUR USER NAME",
                password= 'YOUR PASSWORD',                 
                host= "127.0.0.1",          
                port="5432",
                database="YOUR DATABSE NAME"
    )
    return conn
````

* That's all. Now you can make changes to the code and run the django server to see the changes.

````
python manage.py runserver
````

## Documentation

This Portal consists of 4 core modules:
* [Users](https://github.com/Srj/BUET_Alumni_Portal#users)
* [Post](https://github.com/Srj/BUET_Alumni_Portal#post)
* [Communities](https://github.com/Srj/BUET_Alumni_Portal#communities)
* [Events](https://github.com/Srj/BUET_Alumni_Portal#events)

### Users
* If you are a BUET Alumni or current Student, you can register your account with your Student ID and some basic information. 

![alt text](https://github.com/Srj/BUET_Alumni_Portal/blob/master/media/Register.gif "Register")

* After registering you can update your profile information to make it easy for others to find you.

![alt text](https://github.com/Srj/BUET_Alumni_Portal/blob/master/media/Edit.gif "Edit")

* You can search for other alumni based on various criterion

![alt text](https://github.com/Srj/BUET_Alumni_Portal/blob/master/media/Search.gif "Search")


### Post
* You can post various post like Job Post, General Information post, Research Post, Help post on General Section which will appear in everyone's timeline.

### Communities
* You can join different communites based on different criterion to post and see specific posts related to that community. Only members of that community will see your post.

* You can also create communities and invite others to join it or delete the community later.

### Events
* You can find information about various events that are held at BUET here.

![alt text](https://github.com/Srj/BUET_Alumni_Portal/blob/master/media/Event.gif "Event")

* You can also create events of your own.

![alt text](https://github.com/Srj/BUET_Alumni_Portal/blob/master/media/CreateEvent.gif "CreateEvent")

You can find a demonstration video of this project we used during our presentation [here](https://youtu.be/sk0_A8AHL7E).

__For further inquiry, feel free to mail at srj.buet17@gmail.com__

 

