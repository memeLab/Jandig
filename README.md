# Jandig ARte
ARte is a Progressive Web App for augmented reality artworks. Our goal is to give a way for artists share their artworks in a simple way.

## How it works
Jandig ARte uses [AR.js](https://github.com/jeromeetienne/AR.js) to detect [augmented reality markers](https://www.kudan.eu/kudan-news/augmented-reality-fundamentals-markers/) through the camera of a device and render an image on the device screen, giving the impression that your device is like a virtual window that you looking at.

![usage](https://user-images.githubusercontent.com/12930004/46251341-770de200-c426-11e8-9671-d870d1b9bd5d.jpg)

We decided to go for a PWA because it really seems the future for mobile development and AR.js give us good ways to do augmented reality on web browsers.

## Get Started
To contribute to Jandig ARte it would be awesome if you read [Developers.md](https://github.com/memeLab/ARte/blob/master/Developers.md) and our [Code of conduct](https://github.com/memeLab/ARte/blob/master/CODE_OF_CONDUCT.md). After a good read you are ready to move foward!

### Prerequisites
We use docker and docker-compose to ensure a consistent development environment and to make the deploy process as painless possible, so all you need on your development tools to run Jandig ARte is [Docker](https://www.docker.com/) and [Docker-Compose](https://docs.docker.com/compose/overview/).

### Installing
Docker has good documentation on their website for installing docker and docker-compose for different operating systems like [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and [Debian](https://docs.docker.com/install/linux/docker-ce/debian/). To install docker-compose choose your operating system [here](https://docs.docker.com/compose/install/)

### Running
To run Jandig ARte all you need to do is:
- Clone this repo
- Navigate to the repository folder
- Run docker
- Voila!

```
git clone https://github.com/memeLab/ARte
cd ARte
docker-compose up
```
Jandig ARte server will use a self signed certificate to emulate a HTTPS connection to allow us use getUserMedia API on development server and you can access from the machine running the server through https://localhost and for other devices like cellphones you will need to discover the ip or the hostname of your server machine and access through the mobile browser https://{ip-of-server} or https://{hostname-of-server} e.g. https://shelby.local for a server with hostname 'shelby'.

### People
We are a small team based in Brazil :D talk to us on [Telegram](https://t.me/joinchat/HES_ShA6TMPP-aiHxH7thQ) and follow us on Twitter: [Heloise Cullen](https://twitter.com/heloisecullen), [Pablo Diego](https://twitter.com/pablodiegosds), [VJ Pixel](https://twitter.com/vjpixel) and [Rodrigo Oliveira](https://twitter.com/ShamanRoh)
