#!/bin/bash

data_path="../src/data/certbot"

rsa_key_size=4096
email="" # Adding a valid address is strongly recommended
staging=1 # Set to 1 if you're testing your setup to avoid hitting request limits
composefile=./docker-compose.deploy.yml

function fake-cert {
    path="/etc/letsencrypt/live/$1"
    echo "### Creating dummy certificate for $1 ..."
    mkdir -p "$data_path/conf/live/$1"
    docker-compose -f $composefile run --rm --entrypoint "\
      openssl req -x509 -nodes -newkey rsa:1024 -days 1\
        -keyout '$path/privkey.pem' \
        -out '$path/fullchain.pem' \
        -subj '/CN=localhost'" certbot
    echo
    chmod 644 '$path/privkey.pem'
}

function delete-cert {
    echo "### Deleting dummy certificate for $1 ..."
    docker-compose -f $composefile run --rm --entrypoint "\
      rm -Rf /etc/letsencrypt/live/$1 && \
      rm -Rf /etc/letsencrypt/archive/$1 && \
      rm -Rf /etc/letsencrypt/renewal/$1.conf" certbot
    echo
}

function download-params {
    if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
    echo "### Downloading recommended TLS parameters ..."
    mkdir -p "$data_path/conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
    echo
  fi
}

function request-cert {
      # Select appropriate email arg
    case "$email" in
      "") email_arg="--register-unsafely-without-email" ;;
      *) email_arg="--email $email" ;;
    esac

    # Enable staging mode if needed
    if [ $staging != "0" ]; then staging_arg="--staging"; fi

    domain_arg="-d $1"
    echo "### Requesting Let's Encrypt certificate for $1 ..."
    docker-compose -f $composefile run --rm --entrypoint "\
      certbot certonly --webroot -w /var/www/certbot \
        $staging_arg \
        $email_arg \
        $domain_arg \
        --rsa-key-size $rsa_key_size \
        --agree-tos \
        --force-renewal" certbot
    echo
}

function certificate {
  if [ -d "$data_path" ]; then
    read -p "Existing data found for $domains. Continue and replace existing certificate? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
      docker-compose -f $composefile down
      docker rmi jandigarte/django:latest
      docker volume prune
      docker-compose -f $composefile up -d postgres
      docker-compose -f $composefile up -d watchtower
      docker-compose -f $composefile up -d django
      docker-compose -f $composefile up -d nginx
      exit
    fi
  fi


  download-params

  echo "### Starting postgres ..."
  docker-compose -f $composefile up -d postgres

  echo "### Starting Watchtower ..."
  docker-compose -f $composefile up -d watchtower

  echo "### Starting Django ..."
  docker-compose -f $composefile up -d django

  for domain in ${domains[@]}
  do
    fake-cert $domain
  done

  echo "### Starting nginx ..."
  docker-compose -f $composefile up --force-recreate -d nginx
  echo

  for domain in ${domains[@]}
  do
    delete-cert $domain
  done

  #Join $domains to -d args
  for domain in "${domains[@]}"
  do
    request-cert $domain
  done

  echo "### Reloading nginx ..."
  docker-compose -f $composefile exec nginx nginx -s reload
}


"$@"