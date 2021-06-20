# Jandig ARte
ARte is a Progressive Web App for augmented reality artworks. Our goal is to give a way for artists share their artworks in a simple and free way.

You can see galleries with pictures of [exhibitions](http://memelab.com.br/jandig/exposicoes/) created with Jandig.

## How it works
Jandig ARte uses image pattern detection to detect [augmented reality markers](https://www.kudan.eu/kudan-news/augmented-reality-fundamentals-markers/) through the camera of a device and render a content (currently a GIF) on the device screen, giving the impression that your device is like a virtual window that you are looking at.

![usage](https://user-images.githubusercontent.com/12930004/46251341-770de200-c426-11e8-9671-d870d1b9bd5d.jpg)

Jandig ARte is a Progressive Web App, which means you can open in every device with a browser and a camera. Also you can add Jandig ARte to your homescreen and it will run like a native app on your device.

### People
We are a small team based in Brazil :D talk to us on [Telegram](https://t.me/joinchat/HES_ShA6TMPP-aiHxH7thQ). There's a list of the main contributors of Jandig development:
* @vjpixel - [GitHub](https://github.com/vjpixel), [Twitter](https://twitter.com/vjpixel), [Instagram](https://instagram.com/vjpixel), 
* @pablodiegoss - [GitHub](https://github.com/pablodiegoss), [Twitter](https://twitter.com/pablodiegosds)
* @rodrigocam - [GitHub](https://github.com/rodrigocam), [Twitter](https://twitter.com/sayadiguin)
* @hvalois - [GitHub](https://github.com/hvalois), [Twitter](https://twitter.com/hebertvalois), [Instagram](https://www.instagram.com/hebertvalois/)
* @hockpond - [GitHub](https://github.com/hockpond)
* @anacforcelli - [GitHub](https://github.com/anacforcelli)
* @luccaepp - [GitHub](https://github.com/luccaepp), [Twitter](https://twitter.com/luccaepp)
* @Heloisecs - [GitHub](https://github.com/Heloisecs), [Twitter](https://twitter.com/heloisecullen)
* @LeoSGomes - [GitHub](https://github.com/LeoSilvaGomes), [Twitter](https://twitter.com/LeoSGomes), [Instagram](https://www.instagram.com/leonardodasilvagomes/)
* @kisobral - [GitHub](https://github.com/KiSobral), [Instagram](https://www.instagram.com/hugsob/)
* @rhuancpq - [GitHub](https://github.com/Rhuancpq), [Twitter](https://twitter.com/rhuancpq)
* @thiagohersan - [GitHub](https://github.com/thiagohersan)
* @manuengsf - [Github](https://github.com/manuengsf)
* @darmsDD - [Github](https://github.com/darmsDD)
* @MatheusBlanco - [Github](https://github.com/MatheusBlanco)
* @devsalula - [Github](https://github.com/devsalula)
* @shayanealcantara [Github](https://github.com/shayanealcantara)
* @victoralvesgomide - [Github](https://github.com/victoralvesgomide)

### Collab
We are looking for artists (both illustrators and animators) to create great content and help us testing the platform, people to translate our website from Portuguese to English (and vice versa), and developers to help us with the platform, please contact us via the Telegram channel or an issue on GitHub!

### Clipping
You can find interviews and references to Jandig in the press [here](http://memelab.com.br/jandig/clipping/).

## Get Started
To contribute to Jandig ARte it would be awesome if you read [Contributing](https://github.com/memeLab/ARte/blob/master/.github/CONTRIBUTING.md) and our [Code of conduct](https://github.com/memeLab/ARte/blob/master/.github/CODE_OF_CONDUCT.md). After a good read you are ready to move foward!

### Prerequisites
We use docker and docker-compose to ensure a consistent development environment and to make the deploy process as painless as possible, so all you need on your development tools to run Jandig ARte is [Docker](https://www.docker.com/) and [Docker-Compose](https://docs.docker.com/compose/overview/).

### Installing
Docker has good documentation on their website for installing docker and docker-compose for different operating systems like [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and [Debian](https://docs.docker.com/install/linux/docker-ce/debian/). To install docker-compose choose your operating system [here](https://docs.docker.com/compose/install/).

### Running
To run Jandig ARte all you need to do is:
- Clone this repo
- Navigate to the repository folder
- Run docker-compose passing the docker-compose.yml
- Voila!

```
git clone https://github.com/memeLab/Jandig
cd Jandig
docker-compose -f docker/docker-compose.yml up
```
If you get any error saying ``permission denied`` try run the command with sudo.
```
sudo docker-compose -f docker/docker-compose.yml up
```

Jandig ARte server will run at localhost. To test modifications you just need to run a web browser and access [localhost:8000](localhost:8000). If you want to test on a mobile device, you will need a https connection, we recommend [ngrok](https://www.npmjs.com/package/ngrok) to generate a https link for you.

```
sudo snap install ngrok
ngrok http 8000
```

ngrok will prompt 3 links:

![usage](https://user-images.githubusercontent.com/12930004/54871980-ab41da00-4d9b-11e9-8b80-bb1d4bec420d.png)

Select the one with `https` at beginning.
