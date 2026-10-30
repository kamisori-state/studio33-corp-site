/* Only select an existing inquiry category; never submit or alter the payload keys. */
(function () {
  'use strict';
  var service = new URLSearchParams(window.location.search).get('service');
  var map = { development: 'development-inquiry', website: 'website-inquiry' };
  var id = map[service];
  if (!id) return;
  var option = document.getElementById(id);
  if (option) option.checked = true;
}());
