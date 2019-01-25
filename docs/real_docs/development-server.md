## Welcome to the development server guide

Run the local development server using sqlite as database and serving static files with whitenoise (-w flag). The server will be available at http://localhost:8000.

```shell
$ inv db collect run -w
```

With the previous command you can use ARte only on the local machine running the server. Because of security protocols, other devices must access through a ssl (https) connection. To do this, we use [ngrok](https://ngrok.com/download). The ngrok will generate a https url pointing to your local server, so you can access ARte through external devices.

```shell
$ ngrok http 8000
```
