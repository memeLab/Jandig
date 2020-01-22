BACKUP_DIR = backup_$(shell date +'%d_%m_%Y-%H_%M_%S')
PASSWORD = 
ROOT = 
IP = 
DESTINATION = 

backup:
	#sudo docker-compose -f docker/docker-compose.deploy.yml stop
	mkdir $(BACKUP_DIR)

	sudo cp -r ./docker/media/		$(BACKUP_DIR)/media
	#sudo cp -r /var/lib/docker/volumes/	$(BACKUP_DIR)/volumes

	sudo chmod 755 $(BACKUP_DIR)
	zip -r $(BACKUP_DIR).zip $(BACKUP_DIR)

	sudo cp -r $(BACKUP_DIR).zip ./backups
	sudo rm -rf ./$(BACKUP_DIR).zip
	sudo rm -rf $(BACKUP_DIR)

	#sudo docker-compose -f docker/docker-compose.deploy.yml up
	


	sshpass -p $(PASSWORD) scp ./backups/backup_$(shell date +'%d_%m_%Y-%H_%M_%S').zip $(ROOT)@$(IP):$(DESTINATION)
	echo 'Send via scp'

