## Welcome to the development server guide

Run the local development server using sqlite as database and serving static files with whitenoise (-w flag). The server will be available at http://localhost:8000.

```shell
$ inv db collect run -w
```

With the previous command you can use ARte only on the local machine running the server. Because of security protocols, other devices must access through a ssl (https) connection. To do this, we use [ngrok](https://ngrok.com/download). The ngrok will generate a https url pointing to your local server, so you can access ARte through external devices.

```shell
$ ngrok http 8000
```

### Generating translation (.po) files

To collect and be able to translate new strings inside our django and jinja2 files, you can use our tasks.py for inv if configured correctly or docker directly without having much more than docker-compose, like so:

```
// Requires installing src/requirements.
$inv i18n

// or inside the docker folder.
$docker-compose run --rm django inv i18n

```