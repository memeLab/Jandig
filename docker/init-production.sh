#!/bin/bash

domains=(jandig2.memelab.com.br jandig.app)
rsa_key_size=4096
data_path="../src/data/certbot"
email="" # Adding a valid address is strongly recommended
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits
composefile=docker/docker-compose.deploy.yml


if [ -d "$data_path" ]; then
  read -p "Existing data found for $domains. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    docker-compose -f $composefile up -d postgres
    docker-compose -f $composefile up -d watchtower
    docker-compose -f $composefile up -d django
    docker-compose -f $composefile up -d nginx
    exit
  fi
fi


if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

echo "### Starting postgres ..."
docker-compose -f $composefile up -d postgres

echo "### Starting Watchtower ..."
docker-compose -f $composefile up -d watchtower

echo "### Starting Django ..."
docker-compose -f $composefile up -d django

for domain in ${domains[@]}
do
  echo "### Creating dummy certificate for $domain ..."
  path="/etc/letsencrypt/live/$domain"
  mkdir -p "$data_path/conf/live/$domain"
  docker-compose -f $composefile run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:1024 -days 1\
      -keyout '$path/privkey.pem' \
      -out '$path/fullchain.pem' \
      -subj '/CN=localhost'" certbot
  echo
done

echo "### Starting nginx ..."
docker-compose -f $composefile up --force-recreate -d nginx
echo

for domain in ${domains[@]}
do
  echo "### Deleting dummy certificate for $domain ..."
  docker-compose -f $composefile run --rm --entrypoint "\
    rm -Rf /etc/letsencrypt/live/$domain && \
    rm -Rf /etc/letsencrypt/archive/$domain && \
    rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot
  echo
done



# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

#Join $domains to -d args
for domain in "${domains[@]}"
do
  domain_arg="-d $domain"
  echo "### Requesting Let's Encrypt certificate for $domain ..."
  docker-compose -f $composefile run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
      $staging_arg \
      $email_arg \
      $domain_arg \
      --rsa-key-size $rsa_key_size \
      --agree-tos \
      --force-renewal" certbot
  echo
done

echo "### Reloading nginx ..."
docker-compose -f $composefile exec nginx nginx -s reload
