/* Only select an existing inquiry category; never submit or alter the payload keys. */
(function () {
  'use strict';
  if (new URLSearchParams(window.location.search).get('service') !== 'development') return;
  var option = document.getElementById('development-inquiry');
  if (option) option.checked = true;
}());
