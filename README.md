# Item Catalog Project

## Project Overview
Project is basically a dynamic web application that provides a list of items within a list of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

### Getting started

1- Install [Python](https://www.python.org/)
2- Install [Vagrant](https://www.vagrantup.com/)
3- Install [VirtualBox](https://www.virtualbox.org/)
4- Open the command-line
for windows users, you can [download Git](http://git-scm.com/downloads) and Install the version for your operating system to have a Unix-style terminal.
for linux and Mac users, you can use the regular terminal program.

### Launch Project

1- Go to the project directory and launch the Vagrant VM using command:

  ```
    $ vagrant up
  ```
2- Go to the application files directory by using command:
  ```
    $ cd /vagrant/catalog/
  ```
3- Run the application using

  ```
    $ ./project.py
  ```
4- Access and test your application by visiting [Item-Catalog-Project](http://localhost:5000).


## Note:

If by mistake you delete the database file "itemcatalog.db" you have to initiate the categories and install them in database again using:
  ```
    $ ./initiate_categories.py
  ```

## JSON Endpoint:

application can provide and JSON endpoint to show all categories with their items from [here](http://localhost:5000/category.json/)
