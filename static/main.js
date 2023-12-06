// Get the user's latitude and longitude
function getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(sendLocationData);
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  }
  
  // Callback function to send location data to the server
  function sendLocationData(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
  
    // Create an object with location data
    const locationData = {
      latitude: latitude,
      longitude: longitude,
    };
  
    // Send a POST request to your Flask server
    fetch('/record', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', // Set the content type to JSON
      },
      body: JSON.stringify(locationData),
    })
      .then(response => response.json())
      .then(data => {
        // Handle the response from the server
        console.log(data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
  getLocation();
