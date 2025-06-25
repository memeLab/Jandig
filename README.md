# Jandig ARte

ARte is a Progressive Web App for augmented reality artworks. Our goal is to give a way for artists share their artworks in a simple and free way.

You can see these galleries filled with pictures of [exhibitions](http://memelab.com.br/jandig/exposicoes/) created with Jandig. 

## How it works

Jandig ARte uses image pattern detection to detect [augmented reality markers](https://www.kudan.eu/kudan-news/augmented-reality-fundamentals-markers/) through the camera of a device and render a content (currently a GIF) on the device screen, giving the impression that your device is like a virtual window that you are looking at.

![usage](https://user-images.githubusercontent.com/12930004/46251341-770de200-c426-11e8-9671-d870d1b9bd5d.jpg)

Jandig ARte is a Progressive Web App, which means you can open in any device with a browser and a camera. You can also add Jandig ARte to your homescreen and it will run like a native app on your device.

### People

We are a small team based in Brazil :D talk to us on [Telegram](https://t.me/joinchat/HES_ShA6TMPP-aiHxH7thQ). Here's a list of some of the contributors for the development:

* [@pablodiegoss](https://github.com/pablodiegoss) ([Twitter](https://twitter.com/pablodiegosds))
* [@hvalois](https://github.com/hvalois) ([Twitter](https://twitter.com/hebertvalois), [Instagram](https://www.instagram.com/hebertvalois/))
* [@rodrigocam](https://github.com/rodrigocam) ([Twitter](https://twitter.com/sayadiguin))
* [@vjpixel](https://github.com/vjpixel) ([Twitter](https://twitter.com/vjpixel), [Instagram](https://instagram.com/vjpixel))
* [@anacforcelli](https://github.com/anacforcelli)
* [@MatheusBlanco](https://github.com/MatheusBlanco)
* [@hockpond](https://github.com/hockpond)
* [@devsalula](https://github.com/devsalula)
* [@shayanealcantara](https://github.com/shayanealcantara)
* [@victoralvesgomide](https://github.com/victoralvesgomide)
* [@manuengsf](https://github.com/manuengsf)
* [@darmsDD](https://github.com/darmsDD)
* [@luccaepp](https://github.com/luccaepp) ([Twitter](https://twitter.com/luccaepp))
* [@Heloisecs](https://github.com/Heloisecs) ([Twitter](https://twitter.com/heloisecullen))
* [@rhuancpq](https://github.com/Rhuancpq) ([Twitter](https://twitter.com/rhuancpq))
* [@LeoSGomes](https://github.com/LeoSilvaGomes) ([Twitter](https://twitter.com/LeoSGomes), [Instagram](https://www.instagram.com/leonardodasilvagomes/))
* [@kisobral](https://github.com/KiSobral) ([Instagram](https://www.instagram.com/hugsob/))
* [@thiagohersan](https://github.com/thiagohersan)

### Collab

We are looking for artists (both illustrators and animators) to create great content and help us testing the platform, people to translate our website from Portuguese to English (and vice versa), and developers to help us with the platform, please contact us via the Telegram channel or an issue on GitHub!

### Clipping

You can find interviews and references to Jandig in the press [here](https://jandig.app/memories/clipping/).

## Get Started

To contribute to Jandig ARte, it would be awesome if you read [Contributing](https://github.com/memeLab/ARte/blob/master/.github/CONTRIBUTING.md) and our [Code of conduct](https://github.com/memeLab/ARte/blob/master/.github/CODE_OF_CONDUCT.md). After a good read you are ready to move foward!

### Prerequisites

We use docker and docker compose to ensure a consistent development environment and to make the deploy process as painless as possible, so all you need on your development tools to run Jandig ARte is [Docker](https://www.docker.com/) or [UV](https://docs.astral.sh/uv/)

### Installing

Docker has good documentation on their website for installing docker for different operating systems like [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and [Debian](https://docs.docker.com/install/linux/docker-ce/debian/). To install docker-compose choose your operating system [here](https://docs.docker.com/compose/install/). <br>
On Windows, we recommend you use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and follow the linux.

### Running

#### Linux OS

To run Jandig ARte all you need to do is:

* Clone this repo
* Navigate to the repository folder
* Run docker-compose
* Voila!

```bash
git clone https://github.com/memeLab/Jandig
cd Jandig
docker compose up --watch
```

If you get any error saying ``permission denied`` try run the command with sudo or fix your docker environment by doing the linux [post installation steps](https://docs.docker.com/engine/install/linux-postinstall/) to avoid sudo.

```bash
sudo docker compose up --watch
```

Jandig ARte server will run at localhost. To test modifications you just need to run a web browser and access [http://localhost/](http://localhost/). If you don't want to use docker or needs to update CSS files which are quite messy with Gunicorn + MinIO, you can use UV directly to run Django's development server.

```bash
DJANGO_READ_DOT_ENV_FILE=True uv run python src/manage.py runserver
```

If you want to test on a mobile device, you will need a https connection for AR detection, so we recommend [ngrok](https://www.npmjs.com/package/ngrok) to generate an https link for you.

```bash
sudo snap install ngrok
ngrok http 8000
```

ngrok will prompt 3 links:

![usage](https://user-images.githubusercontent.com/12930004/54871980-ab41da00-4d9b-11e9-8b80-bb1d4bec420d.png)

Select the one with `https` at beginning.

#### Windows OS

To run Jandig ARte all you need to do is:

* Install WSL2, Git and Docker
* Clone this repository
* Navigate to the repository folder using WSL2
* Run docker compose
* Voila!

```bash
git clone https://github.com/memeLab/Jandig
cd Jandig
docker compose up --watch
```

### Prototype

The Jandig platform count with a High-Fidelity Prototype which aims the development and documentation of improvements related to usability. To acess and contribute with the prototype, follow the instructions in [Prototype Documentation](/docs/prototype.md).
