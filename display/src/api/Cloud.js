import {toUpper} from '../utils/Tools';

var AWS = require('aws-sdk');
var awsCreds = require('../config/awsCreds.json');
var s3 = new AWS.S3({
  accessKeyId: awsCreds.accessKeyId,
  secretAccessKey: awsCreds.secretAccessKey,
  region: awsCreds.region,
});
var dynamodb = new AWS.DynamoDB({
  accessKeyId: awsCreds.accessKeyId,
  secretAccessKey: awsCreds.secretAccessKey,
  region: awsCreds.region,
});

//Retrieves s3 URL for a cocktail thumbnail image
export function getThumbnail(cocktailName) {
  //console.log('GETTING THUMBNAIL for ' + cocktailName);
  var params = {
    Bucket: awsCreds.imageBucket,
    Key: toUpper(cocktailName) + '.jpg',
    Expires: 86400,
  };
  var url = s3.getSignedUrl('getObject', params);
  //console.log(url);
  return url;
}

//Makes sure cocktail thumbnail exists in S3 bucket by checking head object
export function verifyImageExists(cocktailName, callback) {
  var params = {
    Bucket: awsCreds.imageBucket,
    Key: toUpper(cocktailName) + '.jpg',
  };

  s3.headObject(params, (err, metadata) => {
    if (err && err.code === 'NotFound') {
      callback(false);
    } else {
      callback(true);
    }
  });
}

//Uploads cocktail image to S3 bucket
export function uploadImage(name, imgSource, callback) {
  var params = {
    Bucket: awsCreds.imageBucket,
    Key: toUpper(name) + '.jpg',
    ContentType: 'image/jpeg',
  };

  s3.getSignedUrl('putObject', params, function(err, url) {
    if (err) {
      console.log(err);
      return;
    } else {
      //console.log('Upload URL: ' + url);
    }
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', url);
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          console.log('Image successfully uploaded to S3');
          callback();
        } else {
          console.log('Error while uploading image to S3');
        }
      }
    };
    xhr.setRequestHeader('Content-Type', 'image/jpeg');
    xhr.send(imgSource);
  });
}

//Load set of cocktail names from Dynamodb
export function loadCocktailNames(number, lastKey) {
  //Add ability to consider lastKey
  var params = {
    TableName: 'BarBot-Recipe',
    ExpressionAttributeNames: {
      '#c': 'cocktailName',
    },
    ProjectionExpression: '#c',
    Limit: number,
    ExclusiveStartKey:
      Object.keys(lastKey).length === 0 && lastKey.constructor === Object
        ? undefined
        : lastKey,
  };

  return new Promise(function(resolve, reject) {
    dynamodb.scan(params, (err, data) => {
      if (err) {
        console.log(err, err.stack);
        reject('Failed to retreived cocktail names. ' + err);
      } else {
        //console.log(data);
        resolve(data);
      }
    });
  });
}

//Delete recipe from dynamo table
export function deleteRecipe(recipeName) {
  var params = {
    Key: {
      cocktailName: {
        S: recipeName.toLowerCase(),
      },
    },
    TableName: 'BarBot-Recipe',
  };

  return new Promise(function(resolve, reject) {
    dynamodb.deleteItem(params, (err, data) => {
      if (err) {
        console.log(err, err.stack);
        reject(false);
      } else {
        //console.log(data);
        resolve(true);
      }
    });
  });
}

//Uses push_item since we have the full object to replace it
export function updateRecipe(recipeName, ingredients) {
  var ingredArr = [];
  var amountObj = {};

  //Create ingredient array and amount object
  for (var name in ingredients) {
    ingredArr.push({S: name.toLowerCase()});
    amountObj[name] = {N: ingredients[name].toString()};
  }

  var itemVal = {
    cocktailName: {
      S: recipeName.toLowerCase(),
    },
    ingredients: {
      L: ingredArr,
    },
    amounts: {
      M: amountObj,
    },
  };

  //console.log(itemVal);

  var params = {
    Item: itemVal,
    TableName: 'BarBot-Recipe',
  };

  return new Promise(function(resolve, reject) {
    dynamodb.putItem(params, (err, data) => {
      if (err) {
        console.log(err, err.stack);
        reject('There was an error updating recipe: ' + recipeName);
      } else {
        resolve(true);
      }
    });
  });
}

//Get ingredients for recipe from dynamo
export function getIngredients(recipeName) {
  var params = {
    Key: {
      cocktailName: {
        S: recipeName.toLowerCase(),
      },
    },
    TableName: 'BarBot-Recipe',
  };

  return new Promise(function(resolve, reject) {
    dynamodb.getItem(params, (err, data) => {
      if (err) {
        console.log(err, err.stack);
        reject('Error loading recipe ' + recipeName + ' from dynamo!');
      } else {
        var newObj = {};
        if (Object.keys(data).length === 0) {
          reject('Recipe: ' + recipeName + " doesn't exist in database");
          return;
        }
        var rawObj = data.Item.amounts.M;
        var ingredNames = Object.keys(data.Item.amounts.M);

        for (var i = 0; i < ingredNames.length; i++) {
          newObj[ingredNames[i]] = parseFloat(rawObj[ingredNames[i]].N);
        }

        resolve(newObj);
      }
    });
  });
}
