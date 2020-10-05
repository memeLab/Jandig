# Software Architecture Document (SAD)
## Use-Case View
### Account Access and Management

The diagram below shows how account access and management is done, with users and system as actors. Please note that Visitor is an user that hasn't log in the app.

![](images/use-case-diagram-user.png)


### Exhibition Creation

The following diagram points out all of the steps for creating a new exhibition in Jandig ARte, from the point of view of the Artist and of any other user of the app.

![](images/use-case-diagram-artist.png)


### Other Features

Below are shown some other interesting features from Jandig ARte:

![](images/use-case-diagram-features.png)


## Logical View

### Overview

 Since the software is django-based , it contains projects, apps and layers . in janding Arte cases , we have two main apps: core and users .
 
 ![](images/package-diagram-logical-view.png)    
 
 
### Architecturally Significant Design Packages

#### "Profile" Class Diagram 
![](images/class-diagram-profile.png)

#### "Marker" Class Diagram 
![](images/class-diagram-marker.png)

#### "Artwork" Class Diagram 
![](images/class-diagram-artwork.png)

#### "Object" Class Diagram 
![](images/class-diagram-object.png)

#### "Artwork2" Class Diagram 
![](images/class-diagram-artwork2.png)

#### "Exhibit" Class Diagram 
![](images/class-diagram-exhibit.png)

