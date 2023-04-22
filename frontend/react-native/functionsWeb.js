/*
This function will take expects the response of a JSON file after being parsed with .json()
This will create a link that will wbe autoclicked for users to download the configuration file.
*/
async function saveData(data) {

  try{
  // create a new blob with the JSON data
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });

  // create a new URL object to reference the blob
  const url = URL.createObjectURL(blob);

  // create a new FileReader object to read the blob as text
  const reader = new FileReader();

  reader.readAsText(blob);

  reader.onload = function() {
    // save the JSON data to a file
    const link = document.createElement('a');
    link.href = url;
    link.download = 'data.json';
    link.click();
  };
  
  //return data to caller
  return data;
} catch (err) {
  console.log(err);
}
}
async function getHelper(ip,port,mix,channel,isDummy,path){
  try {
  const response = await fetch(path, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      channel: channel,
      mix: mix,
      HOST: ip,
      PORT: port,
      isDummy:isDummy
    })
  });
  
  const tempData = await response.json();
  const data = saveData(tempData);
  return data;
} catch (err) {
  console.log(err);
}
}
/*
This function will take the listed ip and port to connect to a dummy, or real console
hosted at that location, and return the entire configuration of all mixes, up to 
max number of channels and mixes defined i nthe parameters. Dummy console is launched when isDummy bool
is on.
*/
async function getYamahaProfile(ip, port, mix, channel,isDummy) {

    var hostname = window.location.hostname;
    const yamahaPath = 'http://'+hostname+':5000/getYamahaProfile'

    return getHelper(ip,port,mix,channel,isDummy,yamahaPath)
  
}
/*
This function will take the listed ip and port to connect to a dummy, or real console
hosted at that location, and return the configuration of the selected mix
max number of channels is defined in the parameters. Dummy console is launched when isDummy bool
is on.
*/
async function getSingleYamahaMix(ip, port, mix, channel,isDummy) {

      var hostname = window.location.hostname;
      const yamahaPath = 'http://'+hostname+':5000/getSingleYamahaMix';
      return getHelper(ip,port,mix,channel,isDummy,yamahaPath);
  
}

export { getSingleYamahaMix,getYamahaProfile };