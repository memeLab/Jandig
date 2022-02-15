# Revision History
 
|Version | description| Author(s) | date |
|--------|------------|-----------|------|
|1.0|Initial version|Victor Gomide & Emanuel Holanda|05/10/2020| 
|1.1|New diagrams in  PlantUml| VIctor Gomide & Emanuel Holanda |24/10/2020|
|1.2|Reference the Plant UML source code in the doc|Gabrielle Ribeiro, Gustavo Duarte & Victor Amaral|09/02/2022|
|1.3|Refactor the architectural reference topic|Hugo Sobral, Sofia Patrocínio|10/02/2022|
|1.4|Fix typos|Sofia Patrocínio, Hugo Sobral|10/02/2022|
|1.5| Update package diagram logic view Plant UML | João Pedro Guedes|10/02/2022|
|1.6| Add images to technologies and links to their documentation | João Pedro Guedes|15/02/2022|


# Software Architecture Document (SAD)
## Introduction 

This document provides a complete architectural overview of the Jandig ARte project. In it, you’ll find the goals and constraints of architecture, the use-case view, the logical view, among others.


### Scope 

This document is extremely important for understanding the project as a whole, since architecture is the basis of all software. It is not only suitable for people who want to contribute to the project, but also so that the current team can remember and even change previous architectural decisions.


### Definitions, Acronyms, and Abbreviations

- **SAD:** Software Architecture Document
- **App:** Application
- **MTV:** Model-View-Template
- **PWA:** Progressive Web App
- **MVC:** Model-View-Controller


### References

 - [Jandig ARte's Wiki](https://github.com/memeLab/Jandig/wiki/Jandig-ARte-architecture)
 - [CSUN's Software Architecture Document Template](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjX4638opzsAhXlHrkGHfRtDwkQFjALegQIARAC&url=https%3A%2F%2Fprojects.cecs.pdx.edu%2Fattachments%2Fdownload%2F3180%2FSoftware_Architecture_Document_SF.docx&usg=AOvVaw0aIZsfpWJeIJ52HMgh7nXx)
 - [Documento de Arquitetura de Software - Facom/UFU](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwi9m7T2rpzsAhVuF7kGHVbrBYwQFjACegQIARAC&url=http%3A%2F%2Fwww.facom.ufu.br%2F~flavio%2Fpds1%2Ffiles%2F2016-01%2Frup_sad-template-documento-arquitetura.dot&usg=AOvVaw3qyZZysozErnD64wCX-vOy)
 - [Documento de Arquitetura de Software RDI-AEE](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiE78LEr5zsAhV7GLkGHSWyAVMQFjAAegQIBRAC&url=http%3A%2F%2Frepositorio.aee.edu.br%2Fbitstream%2Faee%2F1106%2F3%2FTCC2_2018_2_GabrielLeiteDias_MatheusLimadeAlbuquerque_Apendice2.pdf&usg=AOvVaw2wXEOkYpBHmN32ChHHDgOh)
- [The Django Book: Django's Structure](https://djangobook.com/mdj2-django-structure/)


### Overview

In order to explain Jandig ARte's architecture from different points of views, here's an approach of the next topics:

- **Architectural Representation:** architecture of the software as a whole.
- **Architectural Goals and Constraints:** non-functional requirements we want to achieve through Jandig.
- **Use-Case View:** expected behavior from users of Jandig's functionalities.
- **Logical View:** the internal organization of code, its packages, layers and classes.


## Architectural Representation

Project's main programming language is Python, through Django framework. Django uses an exclusive architecture called **MVT (Model-View-Template)**, in which **Model** represents the data layer, **Template** represents user's interface and **View** acts as an intermediary layer. Jandig also uses **Jinja** for enhancing Django's Template view for MVT architecture.

Jandig ARte is a **Progressive Web App (PWA)**, which means it is an web app that has a similar use to a native mobile app. It uses **PostgreSQL** as database.

### Django Framework

![django-icon](https://www.djangoproject.com/m/img/logos/django-logo-negative.png)

Django is a Python based web framework that provides a rapid, clean and pragmatic development. Django also offers a bunch of benefits that can take care of the hassle of web development, *i.e.*, Django is a fast, secure and scalable tool. You can read more about it [here](https://www.djangoproject.com/start/overview/)

### Model-View-Template

Model-View-Template (also called MVT) is a specific Django architecture focused on web applications. Although it seems similar to *MVC* architecture, *MVT* is slightly different. The design model determines the workflow of a Django app. The specific Jandig structure can be seen in the following picture:

![mtv-architecture-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/mtv-architecture-diagram.puml)

**Model** stands for the data representation in the app. It's commonly represented as the database tables.   
**View** is responsible for the HTTP communication, including requests as well as responses.    
**Template** stands for the visualization layer and can be seen as the front-end dynamic component of Django.   

### Jinja
![jinja-logo](https://jinja.palletsprojects.com/en/3.0.x/_images/jinja-logo.png)

Jinja is a Python based web template engine. Jinja can generate any markup as source code and also provides Python-like expressions for templates. The engine template allows customization of tags, filters, tests and global settings, and unlike the Django template engine, Jinja allows the template designer to call functions with arguments on objects. You can read more about it [here](https://jinja.palletsprojects.com/en/3.0.x/intro/)

### Progressive Web App

A progressive Web App is a subtype of web software applications that is built to deliver enhanced capabilities, reliability and installability while reaching anyone, anywhere on any device with a standards-compilant browser (this includes desktop as well as mobile devices).

This kind of application offers a bunch of benefits to projects, since PWA's are ever-present, on home screens, docks and taskbars. They can also read and write files from the local file system, interact with data stored on device and even access the device hardware.

### PostgreSQL

![postgreSQL](https://miro.medium.com/max/800/0*z58cqZWxu2_4q5-g.jpg)

PostgreSQL is an advanced version of SQL. In short, PostgreSQL is an open source relational database system that supports both SQL and JSON querying, it also provides support to different functions of SQL-like statements, such as foreign keys, subqueries, triggers and many different user-defined types and functions. You can read more about it [here](https://www.postgresql.org/)


## Architectural Goals and Constraints

Jandig was created for providing a low-cost and easy-to-use augmented reality experience to artists and art contemplators. That said, the software must be:

- Easy to learn, use and memorize;
- Usable through a smartphone, allowing more people to use it;
- No previous knowledge of programming necessary for using it;
- Free, or cheap enough;
- Available in different languages, so people around the world can use it;
- Open Source, so the community can work together to make it awesome!


## Use-Case View
### Account Access and Management

The diagram below shows how account access and management is done, with users and system as actors. Please note that Visitor is a user that hasn't log in the app.

![use-case-diagram-user](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/use-case-diagram-user.puml)

### Artist Role

The following diagram shows the application's features focused on the Artist's role.

![use-case-diagram-artist](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/use-case-diagram-artist.puml)

### Other Features

Below are shown some other interesting features from Jandig ARte:

![use-case-diagram-features](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/use-case-diagram-features.puml)


## Logical View
### Overview

Since the software is Django-based, it contains projects, apps and layers. in Jandig ARte case, we have two main apps: "core" and "users".
 
![package-diagram-logical-view](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/package-diagram-logical-view.puml) 
 
### Architecturally Significant Design Packages
#### "Profile" Class Diagram
![Profile-class-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/class-diagram-profile.puml)

#### "Marker" Class Diagram
![Marker-class-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/class-diagram-marker.puml)

#### "Artwork" Class Diagram
![Artwork-class-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/class-diagram-artwork.puml)

#### "Object" Class Diagram
![Object-class-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/class-diagram-object.puml)

#### "Exhibit" Class Diagram
![Exhibit-class-diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/memeLab/Jandig/develop/docs/images/plantUML/class-diagram-exhibit.puml)
