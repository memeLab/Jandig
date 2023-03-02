import React, { useState, useEffect } from "react";


export const ArViewer = (props) => {
   const [exhibit, setExhibit] = useState({});
   const [artworks, setArtworks] = useState([]);
   const [markers, setMarkers] = useState([]);

   const getExhibitData = async () => {
      const exhibit = await fetch(props.exhibitUrl, {
         headers : { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
         }
       }).then(res => res.json());

      setExhibit(exhibit);

      const artworks = await Promise.all(
         exhibit.artworks.map(async (id) => {
            return await fetch(`http://localhost:8000/api/v1/artworks/${id}`, {
               headers : { 
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
               }
            }).then(res => res.json());
         })
      );
      
      setArtworks(artworks);

      const markers = await Promise.all(
         artworks.map(async (artwork) => {
            return [await fetch(`http://localhost:8000/api/v1/markers/${artwork.marker}`, {
               headers : { 
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
               }
            }).then(res => res.json()),
             await fetch(`http://localhost:8000/api/v1/objects/${artwork.augmented}`, {
               headers : { 
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
               }
            }).then(res => res.json())
            ]
         })
      );
      
      setMarkers(markers)
   }

   useEffect(() => {
      getExhibitData();
   }, []);

   return (
      <div>
         <ar-scene>
      {markers && markers.map(([marker, content], i) => (
         <ar-marker patt={marker.patt} key={marker.id}>
            <ar-content src={content.source}></ar-content>
         </ar-marker>
         )
      )}
         </ar-scene>
      </div>
   );
}
