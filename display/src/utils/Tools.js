//Formats cocktail names with first letter of each word capitalized
export function toUpper(name) {
  if (name === null || name === undefined || name === '') {
    return '';
  }

  var upperName = '';
  upperName += name[0].toUpperCase();
  for (var i = 1; i < name.length; ) {
    if (name[i] === ' ' && i < name.length - 1) {
      upperName += ' ';
      upperName += name[i + 1].toUpperCase();
      i += 2;
    } else {
      upperName += name[i];
      i++;
    }
  }

  return upperName;
}
