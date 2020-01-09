BACKUP_DIR = backup_$(shell date +'%d_%m_%Y-%H_%M_%S')
DOMAIN = staging.jandig.app
CERTPATH = /etc/letsencrypt/live/$(DOMAIN)
EMAIL = email@example.com

backup:
        #sudo docker-compose -f docker/docker-compose.deploy.yml stop
        mkdir $(BACKUP_DIR)

        sudo cp -r ./docker/media/              $(BACKUP_DIR)/media
        sudo cp -r /var/lib/docker/volumes/     $(BACKUP_DIR)/volumes

        sudo chmod 755 $(BACKUP_DIR) -R
        zip -r $(BACKUP_DIR).zip $(BACKUP_DIR)

        sudo rm -rf $(BACKUP_DIR)
        #sudo docker-compose -f docker/docker-compose.deploy.yml up

$(CERTPATH)
fake-cert:
        mkdir -p $(CERTPATH)
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$(CERTPATH)/../../options-ssl-nginx.conf"
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$(CERTPATH)/../../ssl-dhparams.pem"

        openssl req -x509 -nodes -newkey rsa:1024 -days 1 -keyout '$(CERTPATH)/privkey.pem' -out '$(CERTPATH)/fullchain.pem' -subj '/CN=localhost'

cert:
        rm -Rf /etc/letsencrypt/live/$(DOMAIN)
        sudo rm -Rf /etc/letsencrypt/archive/$(DOMAIN)
        sudo rm -Rf /etc/letsencrypt/renewal/$(DOMAIN).conf
        certbot certonly --webroot -w /var/www/certbot --staging --email $(EMAIL) -d $(DOMAIN) --rsa-key-size 4096 --agree-tos --force-renewal