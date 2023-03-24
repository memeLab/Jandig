import React, { useState, useEffect } from "react";

export const ArViewer = (props) => {
   const [markers, setMarkers] = useState([]);


   useEffect(() => {
      const getExhibitData = async () => {
         const exhibit = await fetch(props.exhibitUrl, {
            headers : { 
               'Content-Type': 'application/json',
               'Accept': 'application/json'
            }
          }).then(res => res.json());

         const artworks = await Promise.all(
            exhibit.artworks.map(async (id) => {
               return await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/v1/artworks/${id}`, {
                  headers : { 
                     'Content-Type': 'application/json',
                     'Accept': 'application/json'
                  }
               }).then(res => res.json());
            })
         );
         
         const markers = await Promise.all(
            artworks.map(async (artwork) => {
               return [await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/v1/markers/${artwork.marker}`, {
                  headers : { 
                     'Content-Type': 'application/json',
                     'Accept': 'application/json'
                  }
               }).then(res => res.json()),
                await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/v1/objects/${artwork.augmented}`, {
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
      getExhibitData();
  }, [props.exhibitUrl]);

   return (
      <div>
      {markers.length > 0 && <ar-scene>{markers && markers.map(([marker, content], i) => (<ar-marker patt={marker.patt} key={marker.id}><ar-content src={content.source} scale={content.scale} position={content.position} rotation={content.rotation}></ar-content></ar-marker>))}</ar-scene>}
      </div>
   );
}
