## Revision History
 
|Version | description| Author(s) | date |
|--------|------------|-----------|------|
|1.0|Initial version|João Victor Valadão|15/07/2022| 


# Installation Guide

## Introduction 

This document provides an assistance guide with the details (step by step) of the installation of the Jandig and how to fix the most common bugs that may appear when beginners are trying to set the environment, and start contributing to the Jandig project. So, as mentioned earlier, the purpose of this document is to help new contributors interact with the code, especially new developers that are interested in the application. Make sure to check the prerequisites to run Jandig ARte, because are tools that you will need in your development workspace that you can access in the [description](http://memelab.com.br/jandig/README.md/) of the repository.

## Step 1 - Cloning the Repository

The first step after downloading the prerequisites is clone the repository, so we are going to need the following code:
```
git clone https://github.com/memeLab/Jandig
cd Jandig
```
If you are having any problems with the git commands consider checking the Github documentation for problems with the [cloning](https://docs.github.com/pt/repositories/creating-and-managing-repositories/troubleshooting-cloning-errors) or your user [authentication](https://docs.github.com/pt/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)

## Step 2 - Running the Docker

Jandig use docker and docker-compose to ensure a consistent development environment and to make the deploy process as painless as possible, so we are going to initialize the docker and then run the docker-compose.yml
```
docker-compose -f docker/docker-compose.yml up
```

### ERROR - Env file not found
If you receive an ERROR message saying they couldn't find env file, you probably don't create the .env file yet. So navigate to **Jandig\src\\.envs\\** and create a file named **.env** and copy the content of **.example** and paste it in this file. Then run the above code again.

### ERROR - System can't found CreateFile
If you are receiving the following ERROR, that means your Docker have problems to initiate. Try to initialize manually the Docker Desktop with admin privileges, you can see if the Docker Desktop is running in your toolbar. If your docker isn't open yet consult the [DockerDesktop](https://docs.microsoft.com/pt-br/windows/wsl/tutorials/wsl-containers) documentation.

### Expected Result
After this steps you should have Jandig ARte running in your localhost, by default the project use the **localhost:8000**. To access you can copy the instruction above and paste in your browser or click [here](http://localhost:8000/)
