# Mailpit configuration:
Reference: https://mailpit.axllent.org/docs/configuration/certificates/

The following command will generate a self-signed certificate and key (both needed for Mailpit) which is valid for 10 years:

```
openssl req -x509 -newkey rsa:4096 \
-nodes -keyout mailpit_key.pem -out mailpit_cert.pem \
-sha256 -days 3650
```