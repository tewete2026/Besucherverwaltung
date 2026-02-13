//
// const meinObjekt = {
//   meineFunktion: function() {
//     // ...
//   }
// };

// if (typeof meinObjekt.meineFunktion === 'function') {
//   // Die Funktion "meineFunktion" existiert als Eigenschaft von "meinObjekt"
//   console.log("Die Funktion meineFunktion existiert im Objekt.");
//   meinObjekt.meineFunktion(); // Funktion aufrufen
// } else {
//   // Die Funktion existiert nicht oder ist kein Funktionstyp
//   console.log("Die Funktion meineFunktion existiert nicht im Objekt oder ist kein Funktionstyp.");
// }

// if (typeof meineVariable === 'undefined') {
//   // Die Variable ist nicht definiert
// } else {
//   // Die Variable ist definiert
// }

// if (typeof window.ihreFunktion === 'function') {
//   // Funktion ist verfügbar
//   window.ihreFunktion();
// } else if ('ihreFunktion' in window && typeof window.ihreFunktion !== 'function') {
//   // Die Eigenschaft exists, ist aber kein Funktionstyp
//   console.log("Eigenschaft 'ihreFunktion' existiert, ist aber keine Funktion.");
// } else {
//   // Die Eigenschaft existiert gar nicht
//   console.log("Funktion 'ihreFunktion' existiert nicht.");
// }

const appendAlert = (message, type) => {
  const wrapper = document.createElement('header');
  wrapper.innerHTML = [
    `<div class="alert alert-${type} alert-dismissible" role="alert">`,
    `   <p>${message}</p>`,
    '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
    '</div>'
  ].join('');
  
  btn_main_finish.append(wrapper);
  if (type == "danger") {
    appendError(message);
  }
}


const appendError = (message, type="alert") => {
  const wrapper = this.document.createElement('p');
  wrapper.setAttribute("role", type);
  wrapper.innerText = message;
  main_errors_flashed.append(wrapper);
}


function removeDismissible() {
  const list = btn_main_finish.getElementsByTagName("header");
  while (list.length > 0) {
    list[0].remove();
  }
}


async function execFetch(url, parms=null) {
  let rt_json = {"status":"", "message":"", "content":""};
  const options = {
    "method":"POST",
    "headers": {"Content-Type": "application/json"},
    "body":parms
  }
  try {
    const response = parms ? await fetch(url, options) : await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }
    try {
      rt_json = response.json();
    } catch (err) {
      if (err instanceof SyntaxError) {
        rt_json.content = response.text();
      }
      else {
        rt_json.status = "ERR";
        rt_json.content = err.name;
        rt_json.message = err.message;
      }
    }
  } catch (error) {
    rt_json.status = "ERR";
    rt_json.message = error.message;
    appendError(`execFetch-Error: ${error.message}`);
  }
  return rt_json;
}


function arrayifyMap(m){
  if (!m) return m;
  return m.constructor === Map ? [...m].map(([v,k]) => [arrayifyMap(v),arrayifyMap(k)]) : m;
}


function table_coaches_clear(coaches) {
  if (coaches.rows.length > 1) {
    while (coaches.rows[0].cells[1].firstElementChild.getAttribute("data-index") != "-1") {
      coaches.deleteRow(0);
    }
  }
}


function add_To_Array(arr, value, condition=null) {
  if (value) {
    if (value != "-1") {
      if (condition !== null) {
        if (condition) {
          arr.push(value);
          return true;
        } else return false;
      } 
      else {
        arr.push(value);
      }
    }
  }
}


function storageAvailable(type) {
  let storage;
  try {
    storage = window[type];
    const x = "__storage_test__";
    storage.setItem(x, x);
    storage.removeItem(x);
    console.log(`Storage-Typ ${type} ist verfügbar`);
    return true;
  } catch (e) {
    console.log(`Storage-Typ ${type} ist NICHT verfügbar! ${e}`);
    return (
      e instanceof DOMException &&
      e.name === "QuotaExceededError" &&
      // acknowledge QuotaExceededError only if there's something already stored
      storage &&
      storage.length !== 0
    );
  }
}


function validateNumber(number, allowZero=false, strict=false) {
  if (!number) return !strict;
  const re = allowZero ? /^([0-9]{1}|[0-9]{2,3})$/ : /^([1-9]{1}|[0-9]{2,3})$/;
  return re.test(number);
}


function validatePhone(phone, strict=false) {
  if (!phone) return !strict;
  const re = /^((\+\d{2,3})|(0\d{3,5}))\d{3,}$/;
  return re.test(phone.replace(/\s+/g, ''));
}


function validateEmail(email, strict=false) {
  if (!email) return !strict;
  const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}


function validatePLZ(plz, strict=false) {
  if (!plz) return !strict;
  const re = /^\d{5}$/;
  return re.test(plz);
}


function setDomField(field) {
  const stg_value = extStorage.getItem(field.name);
  if (field.type == 'checkbox') {
    if (stg_value != null && stg_value == "1") {
      field.checked = true;
    }
    else {
      if (stg_value != null && (stg_value == '' || stg_value == '0')) {
        field.checked = false;
      }
    }
  }
  else if (field.type == 'select-one') {
    if (!stg_value) {
      field.value = "-1";
    }
    else {
      field.value = stg_value;
    }
  }
  else {
    if (stg_value != null) {
      field.value = stg_value;
    }
    else {
      const deflt = field.getAttribute("data-default");
      if (deflt) {
        field.value = deflt;
      }
    }
  }
}


function getDomField(field) {
  let stg_value;
  if (field.type == 'checkbox') {
    if (field.checked) stg_value = "1";
    else stg_value = "0";
  }
  else {
    stg_value = field.value;
  }
  extStorage.setItem(field.name, stg_value);
}


async function uploadScriptError() {
  const err_elements = main_errors_flashed.getElementsByTagName("p");
  if (err_elements.length > 0) {
    const stored_errors = {"alert":[], "init":[], "init_err":[]};
    for (const errtext of err_elements) {
      const type = errtext.getAttribute("role");
      stored_errors[type].push(errtext.innerText);
    }
    const submit_str = JSON.stringify(stored_errors);
    // Durchführen Hochladen der Fehlermeldungen
    const result_data = await execFetch(HTTP.getURL("ax-up-error-msg/"), submit_str);
    if (result_data.status == "OK") {
      main_errors_flashed.replaceChildren();
    }
  }
}


function showAlertsAfterInit() {
  if (STORAGE_AVAILABLE) {
    appendError("STORAGE_OK", "init");
    for (let key of extStorage.keys()) {
      key = key.concat("=", extStorage.getItem(key).substring(0, 80));
      appendError(key, "init");
    }
    uploadScriptError();
    
    const last_stored = extStorage.getItem("last_stored");
    const last_mode = extStorage.getItem("last_stored_mode");
    const last_kdnr = extStorage.getItem("last_stored_kdnr");
    const lastItem = last_kdnr ? last_kdnr : extStorage.getItem("last_stored_id");
    const nbr_text = last_kdnr ? "Kunden-Nr." : "Nr.";
    if (last_stored) {
      btn_main_store.removeAttribute("disabled");
      if (last_mode && last_mode == "LOCK") {
        appendAlert(`Eintrag ${nbr_text} ${lastItem} ist schreibgeschützt.`, 'warning');
        btn_main_store.setAttribute("disabled", true);
      }
      if (last_stored  == "OK") {
        if (last_mode == "INS") {
          appendAlert(`Das Hinzufügen von ${nbr_text} ${lastItem} war erfolgreich.`, 'success');
        }
        else if (last_mode == "CHG") {
          appendAlert(`Das Aktualisieren von ${nbr_text} ${lastItem} war erfolgreich.`, 'success');
        }
        extStorage.setItem("last_stored", "CONFIRMED");
      }
      else if(last_stored  == "CLEAR") {
        appendAlert('Alle Eingaben sind zurückgesetzt; neue Daten können eingegeben werden.', 'info')
        extStorage.setItem("last_stored", "CLEARED");
      }
      else if(last_stored  == "RELOAD") {
        appendAlert(`Daten für ${nbr_text} ${lastItem} sind bereitgestellt.`, 'success');
        extStorage.setItem("last_stored", "RELOADED");
      }
      else if(last_stored  == "ERR") {
        appendAlert('Das letzte Speichern war nicht erfolgreich.', 'danger');
        extStorage.setItem("last_stored", "RESET");
      }
    }
  } else {
    appendError("STORAGE_NOT_AVAILABLE", "init_err");
    appendAlert("Dieses Tool kann in diesem Browser nur sehr eingeschränkt verwendet werden, da 'Session-Storage' nicht verfügbar ist.", "warning")
    uploadScriptError();
  }
}

 
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----HTML-Funktionen-----------------------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
function static_coaches_rows (fieldname, data_index, html_options, tr_elem, data_index_remove="-1") {
  tr_elem.innerHTML = `<td><select class="form-select" name="frm-main-${fieldname}" data-init-frm="false" data-collect="tb-${fieldname}" \
    data-index="${data_index}" style="font-size: 0.9rem;" required>${html_options}</select></td><td style="width: 2em;"><figure class="text-body-secondary \
    frm-main-${fieldname}-remove d-none" data-index="${data_index_remove}" title="Eintrag entfernen"> \
    <svg class="bi" width="1.5em" height="1.5em" title="Eintrag entfernen"><use xlink:href="#bi-trash-fill" title="Eintrag entfernen"/></svg></figure></td>`;
}


function static_coaches_list (row, tr_elem, data_index_remove="-1") {
  tr_elem.innerHTML = `<td>${row[1]} ${row[2]}</td><td>${row[3]}</td><td>${row[4]}</td> \
    <td><figure class="text-body-secondary" data-id="${row[0]}" data-index="${data_index_remove}" title="Eintrag entfernen"> \
    <svg class="bi" width="1em" height="1em" title="Eintrag entfernen"><use xlink:href="#bi-trash-fill" title="Eintrag entfernen"/></svg></figure></td>`;
}
 

function static_visiter (dbdata, tr_elem, data_index_remove="-1") {
  tr_elem.innerHTML = `<td>${dbdata.vorname}<br>${dbdata.nachname}</td><td>${dbdata.telefon}<br>${dbdata.email}</td> \
    <td><input type="number" class="form-control" name="frm-main-spende" data-collect="tb-visiter" data-id="${dbdata.id}" value="0" step="5" style="font-size: 0.7rem; width: 6em;" required></td> \
    <td><select class="form-select" name="frm-main-thema" data-collect="tb-visiter" data-id="${dbdata.id}" style="font-size: 0.7rem; width: 13em;" required> \
    <option value="-1">keine Auswahl</option> \
    ${SERVER_OPTIONS.themes} \
    </select></td> \
    <td><select class="form-select" name="frm-main-geraet" data-collect="tb-visiter" data-id="${dbdata.id}" style="font-size: 0.7rem; width: 12em;" required> \
    <option value="-1">keine Auswahl</option> \
    ${SERVER_OPTIONS.devices} \
    </select></td> \
    <td><figure class="text-body-secondary frm-main-besucher-remove" data-id="${dbdata.id}" data-index="${data_index_remove}" title="Eintrag entfernen"> \
    <svg class="bi" width="1em" height="1em" title="Eintrag entfernen"><use xlink:href="#bi-trash-fill" title="Eintrag entfernen"/></svg></figure></td>`;
}


function static_event (id, dbdata, tr_elem, data_index_remove="-1", wl=null) {
  let cell_bg = "";
  if (wl) cell_bg = " class='" + SERVER_OPTIONS.style_bg_visiter_wl + "'";
  let td3 = "", ind = 3;
  if (dbdata[3]) {
    td3 = `<td${cell_bg}>${dbdata[3]}</td>`;
    ind = 4;
  }
  tr_elem.innerHTML = `<td${cell_bg}>${id}</td><td${cell_bg}>${dbdata[1]}</td><td${cell_bg}>${dbdata[2]}</td>${td3} \
    <td${cell_bg}><figure class="text-body-secondary" data-id="${id}" data-index="${data_index_remove}" data-rowid="${dbdata[0]}" title="Eintrag entfernen"> \
    <svg class="bi" width="1em" height="1em" title="Eintrag entfernen"><use xlink:href="#bi-trash-fill" title="Eintrag entfernen"/></svg></figure></td>`;
  return ind;
}
