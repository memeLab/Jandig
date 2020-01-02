BACKUP_DIR = backup_$(shell date +'%d_%m_%Y-%H_%M_%S')
backup:
        #sudo docker-compose -f docker/docker-compose.deploy.yml stop
        mkdir $(BACKUP_DIR)

        sudo cp -r ./docker/media/              $(BACKUP_DIR)/media
        sudo cp -r /var/lib/docker/volumes/     $(BACKUP_DIR)/volumes

        sudo chmod 755 $(BACKUP_DIR) -R
        zip -r $(BACKUP_DIR).zip $(BACKUP_DIR)

        sudo rm -rf $(BACKUP_DIR)
        #sudo docker-compose -f docker/docker-compose.deploy.yml up