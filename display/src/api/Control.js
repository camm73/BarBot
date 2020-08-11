const barbotAddress = 'http://barbot.local:5000/';
const shotSize = 1.5; //fl oz

//Calls the make cocktail function on BarBot API
export async function makeCocktail(name) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'cocktail/' + encodeURI(name.toLowerCase()) + '/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Cocktail Response: ' + responseText);
        if (responseText === 'available') {
          resolve(false);
        } else if (responseText === 'busy') {
          resolve(false);
        } else if (responseText === 'ingredients') {
          resolve(false);
        } else if (responseText === 'error') {
          resolve(false);
        } else {
          resolve(true);
        }
      })
      .catch(error => {
        console.log(error);
        if (error.name !== 'AbortError') {
          resolve(false);
        } else {
          resolve(true); //TODO: May want to change to false
        }
      });
  });
}

//Remove bottles from every pump
export async function removeAllBottles(abortSignal) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'removeAllBottles/', {
      method: 'GET',
      signal: abortSignal,
    })
      .then(response => response.text())
      .then(responseText => {
        if (responseText === 'true') {
          console.log('Successfully removed all bottles!');
        } else if (responseText === 'busy') {
          console.log('Barbot is busy!');
        } else if (responseText === 'error') {
          console.log('Error removing all bottles');
        } else {
          console.log('Failed to remove all bottles');
        }

        resolve(responseText);
      })
      .catch(error => {
        console.log('Issue removing all bottles!');
        console.log(error);
        reject(error);
      });
  });
}

//Removes a specific bottle from the current pump
export async function removeBottle(number, bottleName, abortSignal) {
  var result = '';

  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'removeBottle/' + bottleName, {
      method: 'GET',
      signal: abortSignal,
    })
      .then(response => response.text())
      .then(responseJson => {
        //console.log('Removed bottle: ' + bottleName + '; ' + responseJson);
        result = responseJson;
        resolve(responseJson);
      })
      .catch(error => {
        console.log('Issue removing bottle!');
        console.log(error);
        reject(error); //TODO: May need to check what this is expecting to return
      });
  });
}

//Check whether alcoholMode is enabled or not
export async function checkAlcoholMode() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'getAlcoholMode/', {
      method: 'GET',
    })
      .then(response => response.json())
      .then(responseJson => {
        //console.log('Alcohol Mode: ' + responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log('Error loading Alcohol mode!');
      });
  });
}

//Sets the value of "alcohol mode"
export async function setAlcoholMode(modeSetting, abortSignal) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'alcoholMode/', {
      method: 'POST',
      signal: abortSignal,
      body: JSON.stringify({
        enable: modeSetting,
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(responseJson => {
        //console.log(responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log(error);
        reject(error);
      });
  });
}

//Adds a bottle to a certain pump and sets its details
export async function addBottle(
  bottleName,
  pumpNum,
  volume,
  originalVolume,
  abortSignal,
) {
  return new Promise(function(resolve, reject) {
    fetch(
      barbotAddress +
        'addBottle/' +
        bottleName +
        '/pump/' +
        pumpNum.toString() +
        '/volume/' +
        volume +
        '/originalVolume/' +
        originalVolume +
        '/',
      {
        method: 'GET',
        signal: abortSignal,
      },
    )
      .then(response => response.json())
      .then(responseJson => {
        resolve(responseJson);
      })
      .catch(error => {
        reject(error);
        console.log(error);
      });
  });
}

//Add cocktail recipe to menu hosted on BarBot
export async function addRecipe(recipeName, ingredients, amounts, abortSignal) {
  //Need to process amounts for BarBot's format
  for (var i = 0; i < amounts.length; i++) {
    var oldAmount = amounts[i];
    amounts[i] = parseFloat(oldAmount.replace(/.oz/g, '')) / shotSize;
  }

  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'addRecipe/', {
      method: 'POST',
      signal: abortSignal,
      body: JSON.stringify({
        name: recipeName,
        ingredients: ingredients,
        amounts: amounts,
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(responseJson => {
        //console.log(responseJson);
        if (responseJson.status === 200) {
          console.log('Successfully added new recipe: ' + recipeName);
          resolve(true);
        } else {
          resolve(false);
        }
      })
      .catch(error => {
        reject(false);
        console.log(error);
      });
  });
}

//Gets list of bottles that aren't on pumps yet
export async function getNewBottles() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'getBottles/', {
      method: 'GET',
    })
      .then(response => response.json())
      .then(responseJson => {
        resolve(responseJson);
      })
      .catch(error => {
        reject([]);
        console.log(error);
      });
  });
}

//Gets full list of bottles, both on and off pumps
export async function getAllBottles() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'getAllBottles/', {
      method: 'GET',
    })
      .then(response => response.json())
      .then(responseJson => {
        resolve(responseJson);
      })
      .catch(error => {
        reject([]);
        console.log(error);
      });
  });
}

//Adds new bottle to list of available bottles
export async function addNewBottle(bottleName, isAlcohol, abortSignal) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'newBottle/' + bottleName + '/alcohol=' + isAlcohol, {
      method: 'GET',
      signal: abortSignal,
    })
      .then(response => response.json())
      .then(responseJson => {
        resolve(true);
      })
      .catch(error => {
        console.log(error);
        reject(false);
      });
  });
}

//Reverses polarity for peristaltic pumps
export async function reverse() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'reverse/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Reversed polarity: ' + responseText);
        resolve(responseText);
      })
      .catch(error => {
        console.log('Error reversing polarity');
        reject(error);
      });
  });
}

//Turns on a specific pump
export async function pumpOn(number) {
  fetch(barbotAddress + 'pumpOn/' + number.toString() + '/', {
    method: 'GET',
  })
    .then(response => response.text())
    .then(responseText => {
      //console.log('Pump on: ' + responseText);
    })
    .catch(error => {
      console.log(error);
    });
}

//Turns on air pressure pump
export async function pressureOn(number) {
  fetch(barbotAddress + 'pressureOn/' + number.toString() + '/', {
    method: 'GET',
  })
    .then(res => res.text())
    .then(resText => {
      //console.log('Pressure on: ' + resText);
    })
    .catch(err => {
      console.log(err);
    });
}

//Turns off air pressure pumps
export async function pressureOff(number) {
  fetch(barbotAddress + 'pressureOff/' + number.toString() + '/', {
    method: 'GET',
  })
    .then(res => res.text())
    .then(resText => {
      //console.log('Pressure of: ' + resText);
    })
    .catch(err => {
      console.log(err);
    });
}

//Calibrates pump time for 1 shot
export async function calibratePump(number, time) {
  return new Promise(function(resolve, reject) {
    fetch(
      barbotAddress +
        'calibrate/' +
        number.toString() +
        '/time/' +
        time.replace('.', '%2E'),
      {
        method: 'GET',
      },
    )
      .then(response => response.json())
      .then(responseJson => {
        //console.log(responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log(error);
        reject(false);
      });
  });
}

//Gets the details about all of the pumps
export async function getPumpSupportDetails() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'pumpSupportDetails/', {
      method: 'GET',
    })
      .then(response => response.json())
      .then(responseJson => {
        console.log('Retreieved pump support data');
        //console.log(responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log(error);
        reject([]);
      });
  });
}

//Gets the current volume for a specified bottle
export async function getCurrentBottleVolume(bottleName) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'volume/' + bottleName + '/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Current Volume of ' + bottleName + ' is: ' + responseText);
        resolve(responseText);
      })
      .catch(error => {
        console.log(error);
        reject('There was an error getting current bottle volume: ' + error);
      });
  });
}

//Gets the initial volume for a specified bottle
export async function getInitBottleVolume(bottleName) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'initVolume/' + bottleName + '/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Initial Volume of ' + bottleName + ' is: ' + responseText);
        resolve(responseText);
      })
      .catch(error => {
        console.log(error);
        reject('There was an error getting initial bottle volume: ' + error);
      });
  });
}

//Turns off a specified pump
export async function pumpOff(number) {
  fetch(barbotAddress + 'pumpOff/' + number.toString() + '/', {
    method: 'GET',
  })
    .then(response => response.text())
    .then(responseText => {
      //console.log('Pump off: ' + responseText);
    })
    .catch(error => {
      console.log(error);
    });
}

//Checks whether Barbot is reachable or not
export async function isOnline() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'heartbeat/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(text => {
        //console.log('Heartbeat: ' + text);
        resolve(text);
      })
      .catch(error => {
        console.log(error);
        reject(error);
      });
  });
}

//Cleans all peristaltic pumps by flushing them
export async function cleanPumps(abortSignal) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'clean/', {
      method: 'GET',
      signal: abortSignal,
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Pumping cleaning response: ');
        //console.log(responseText);
        if (responseText === 'busy') {
          resolve(responseText);
        } else {
          resolve(responseText);
        }
      })
      .catch(error => {
        //console.log('Error cleaning pumps: ' + error);
        if (error.name !== 'AbortError') {
          reject(error);
        } else {
          resolve();
        }
      });
  });
}

//Retrieves the current cocktail menu
export async function getCocktailMenu() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'cocktailList/', {
      method: 'GET',
      mode: 'no-cors',
    })
      .then(response => response.json())
      .then(responseJson => {
        //console.log(responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log('getCocktailMenu error: ' + error);
        resolve([]);
      });
  });
}

//Gets the ingredients for a cocktail from the local cache
export async function getLocalIngredients(name) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'ingredients/' + name.toLowerCase() + '/', {
      method: 'GET',
    })
      .then(response => response.json())
      .then(responseJson => {
        resolve(responseJson);
      })
      .catch(error => {
        console.log('getIngredients error: ' + error);
        reject('ERROR');
      });
  });
}

//Gets the percentage full a bottle is
export async function getBottlePercent(bottleName) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'bottlePercent/' + bottleName + '/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseJson => {
        //console.log(responseJson);
        resolve(responseJson);
      })
      .catch(error => {
        console.log('getBottlePercent error: ' + error);
        reject('ERROR');
      });
  });
}

//Get the name of the bottle on a specific pump
export async function getBottleName(number) {
  var address = barbotAddress + 'bottleName/' + number + '/';
  return new Promise(function(resolve, reject) {
    fetch(address, {
      method: 'GET',
    })
      .then(response => response.text())
      .then(responseText => {
        //console.log('Bottle Name Response: ' + responseText);
        resolve(responseText);
      })
      .catch(error => {
        console.log(error);
        reject(error);
      });
  });
}

//Refreshes local recipes on the pi by fetching from dynamo
export async function refreshRecipes() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'refreshRecipes/', {
      method: 'GET',
    })
      .then(response => response.text())
      .then(resText => {
        resolve(resText);
      })
      .catch(error => {
        console.log(error);
        reject('Error refreshing cocktail recipes');
      });
  });
}

//Gets ingredients that should be ignored
export async function getIgnoreIngredients() {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'getIgnoreIngredients/', {
      method: 'GET',
    })
      .then(res => res.json())
      .then(responseJson => {
        resolve(responseJson);
      })
      .catch(error => {
        console.log(error);
        reject('There was an error getting ignored ingredients list');
      });
  });
}

//Updates BarBot's software
export async function updateBarbot() {
  fetch(barbotAddress + 'update/', {
    method: 'GET',
  });
}

//Triggers BarBot restart
export function rebootBarbot() {
  fetch(barbotAddress + 'reboot/', {
    method: 'GET',
  });
}

//Updates ignore ingredients
export async function updateIgnoreIngredients(ingredient, add) {
  return new Promise(function(resolve, reject) {
    fetch(barbotAddress + 'ignoreIngredient/', {
      method: 'POST',
      body: JSON.stringify({
        action: add === true ? 'add' : 'remove',
        ingredient: ingredient,
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(res => res.text())
      .then(responseText => {
        if (responseText === 'true') {
          resolve(true);
        } else {
          resolve(false);
        }
      })
      .catch(err => {
        console.log(err);
        reject('Error setting ignore ingredient!');
      });
  });
}
