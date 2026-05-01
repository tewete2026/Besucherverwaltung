function performExport(elem, link, disable=false) {
  if (disable) {
    elem.setAttribute('disabled', true);
  }
  window.location.assign(link);
}
