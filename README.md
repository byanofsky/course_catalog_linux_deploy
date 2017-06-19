# Course Catalog Deploy to Linux Server

This is a fork of my [Course Catalog project](https://github.com/byanofsky/course_catalog)

This contains the project files and information for deploying to my configured Linux server.

It is a project for Udacity's Full Stack Web Development Nanodegree.

## IP Address of Server

54.202.21.35

## Software Installed on Server

* Python 2.7.12
* Apache2
* mod_wsgi
* PostgreSQL

## Configurations Made to Server

1. Update all packages
2. Change SSH port to 2200
3. Open ports 2200, 80, and 123 on Amazon Lightsail and within UFW
4. Enable UFW
5. Add user `grader` and add grader to `sudo` group
6. Add user `course_catalog`
7. Configure timezone to UTC
8. Install Apache, mod_wsgi, pip, and virtualenv
9. Install PostgreSQL, create user `course_catalog`, and create database `course_catalog`
10. Install Git and push project to server
11. Configure Apache Virtual Host and WSGI to work with Flask application. Found help from [Flask docs](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/) and [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
12. Git push application to server and set up Flask on virtualenv
13. Adjust permissions within project directory

## Third Party Software Used in Application

* Flask
* Flask-SQLAlchemy
* Flask-Bcrypt
* Requests
* Psycopg2

## Useful Resources

* Installing Flask on Apache: [Flask docs](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/) and [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
* Using Git to deploy on Ubuntu: [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-set-up-automatic-deployment-with-git-with-a-vps)
* Installing and Configuring PostreSQL: [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)
* Securing PostgreSQL: [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps)
* Setting permissions within `/var/www`: https://askubuntu.com/a/493401
