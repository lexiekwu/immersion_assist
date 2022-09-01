'use strict';

window.addEventListener('load', function () {

  console.log("Hello World!");

  var en_word_button = document.getElementById("@english_word_button")
  var en_word_input = document.getElementById("@english_word_input")
  en_word_button.addEventListener('click', function () {

    console.log("clicked button")
    console.log(en_word_input.value)

  })

});
