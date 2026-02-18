/* Main.js */
/*
Map.prototype.toJson = function toJson() {
  return JSON.stringify(Array.from(this.entries()));
}
*/

/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Define Global Values and Functions----------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
const frm_main_aktiv = this.document.getElementById("frm-main-aktiv");
const frm_main_anrede = this.document.getElementById("frm-main-anrede");
const frm_main_berater = this.document.getElementById("frm-main-berater");
const frm_main_berater_nbr = this.document.getElementById("frm-main-berater-nbr");
const frm_main_besucher_nbr = this.document.getElementById("frm-main-besucher-nbr");
const frm_main_besucher_nbr_result = this.document.getElementById("frm-main-besucher-ergebnis-nbr");
const frm_main_besucher_nbrmax = this.document.getElementById("frm-main-besucher-maxnbr");
const frm_main_bezeichnung = this.document.getElementById("frm-main-bezeichnung");
const frm_main_booked_events = this.document.getElementById("frm-main-booked-events");
const frm_main_coached_devices = this.document.getElementById("frm-main-coached-devices");
const frm_main_coached_devices_nbr = this.document.getElementById("frm-main-coached-devices-nbr");
const frm_main_coached_themes = this.document.getElementById("frm-main-coached-themes");
const frm_main_coached_themes_nbr = this.document.getElementById("frm-main-coached-themes-nbr");
const frm_main_coaches = this.document.getElementById("frm-main-coaches");
const frm_main_coaches_nbr = this.document.getElementById("frm-main-coaches-nbr");
const frm_main_datum = this.document.getElementById("frm-main-datum");
const frm_main_veranstdatum = this.document.getElementById("frm-main-veranstdatum");
const frm_main_email = this.document.getElementById("frm-main-email");
const frm_main_info_themes = this.document.getElementById("frm-main-info-themes");
const frm_main_info_themes_nbr = this.document.getElementById("frm-main-info-themes-nbr");
const frm_main_maxbesucher = this.document.getElementById("frm-main-maxbesucher");
const frm_main_nachname = this.document.getElementById("frm-main-nachname");
const frm_main_ort = this.document.getElementById("frm-main-ort");
const frm_main_plz = this.document.getElementById("frm-main-plz");
const frm_main_strasse = this.document.getElementById("frm-main-strasse");
const frm_main_telefon = this.document.getElementById("frm-main-telefon");
const frm_main_veranst_nbr = this.document.getElementById("frm-main-veranst-nbr");
const frm_main_veranstort = this.document.getElementById("frm-main-veranstort");
const frm_main_vorname = this.document.getElementById("frm-main-vorname");
const frm_quick = this.document.getElementsByClassName("frm-quick");
const frm_quick_vorname = this.document.getElementById("frm-quick-vorname");
const frm_search = this.document.getElementsByClassName("frm-search");
const frm_search_msg = this.document.getElementById("frm-search-msg");
const frm_search_ptn = this.document.getElementById("frm-search-ptn");

const tb_visiter = this.document.getElementById("tb-visiter");
const table_visiter = tb_visiter ? tb_visiter.tBodies[0] : null;
const coaches_set = this.document.getElementById("tb-berater");
const table_coaches = coaches_set ? coaches_set.tBodies[0] : null;
const tb_events = this.document.getElementById("tb-events");
const table_events_body = tb_events ? tb_events.tBodies[0]: null;
const visiter_elem_map = new Visiter_Elements(tb_visiter);
const coaches_elem_map = new Coaches_Elements(frm_main_berater, coaches_set);
const events_elem_map = new Events_Elements(tb_events);

const max_visiter_map = typeof SERVER_OPTIONS.max_visiters === 'undefined' ? null : new Map(JSON.parse(SERVER_OPTIONS.max_visiters));

const von_value = this.document.getElementById("frm-main-zeit-von");
const bis_value = this.document.getElementById("frm-main-zeit-bis");
const dauer = this.document.getElementById("frm-main-zeit-dauer");
const btn_insert_visiter = this.document.getElementById("btn-insert-visiter");
const btn_search_visiter = this.document.getElementById("btn-search-visiter");
const html_select = this.document.getElementById("frm-main-besucher-ergebnis");
const html_select_div = this.document.getElementById("frm-main-besucher-ergebnis-head");
const html_select_nbr = this.document.getElementById("frm-main-besucher-ergebnis-nbr");
const quick_email = this.document.getElementById("frm-quick-email");
const quick_nachname = this.document.getElementById("frm-quick-nachname");
const quick_telefon = this.document.getElementById("frm-quick-telefon");
const quick_vorname = this.document.getElementById("frm-quick-vorname");
const tb_overview_events = this.document.getElementById("tb-overview-events");
const tb_overview_coaches = this.document.getElementById("tb-overview-coaches");
const tb_overview_visiter = this.document.getElementById("tb-overview-visiter");
const tb_overview_devices = this.document.getElementById("tb-overview-devices");
const tb_overview_targets = this.document.getElementById("tb-overview-targets");
const table_overview = tb_overview_events ? tb_overview_events : tb_overview_coaches ? tb_overview_coaches : tb_overview_visiter ? tb_overview_visiter : tb_overview_devices ? tb_overview_devices : tb_overview_targets ? tb_overview_targets : null;
const table_overview_body = table_overview ? table_overview.tBodies[0] : null;

const tb_coached_themes = this.document.getElementById("tb-coached-themes");
const table_coached_themes = tb_coached_themes ? tb_coached_themes.tBodies[0] : null;
const tb_info_themes = this.document.getElementById("tb-info-themes");
const table_info_themes = tb_info_themes ? tb_info_themes.tBodies[0] : null;
const tb_coached_devices = this.document.getElementById("tb-coached-devices");
const table_coached_devices = tb_coached_devices ? tb_coached_devices.tBodies[0] : null;
const tb_coaches = this.document.getElementById("tb-coaches");
const table_device_coaches = tb_coaches ? tb_coaches.tBodies[0] : null;
const coaches_themes_elem_map = new Coaches_Elements(frm_main_coached_themes, tb_coached_themes);
const coaches_info_elem_map = new Coaches_Elements(frm_main_info_themes, tb_info_themes);
const coaches_devices_elem_map = new Coaches_Elements(frm_main_coached_devices, tb_coached_devices);
const coaches_devices_map = new Coaches_Elements(frm_main_coaches, tb_coaches);

// const fillOverwiewParms = {"url":HTTP.getURL("ax-get-events-overview/"), "table_target":table_overview_body, "setClickEvent":setClickEventVeranst, "label":"Veranstaltungen"};
// const fillOverwiewParms = {"url":HTTP.getURL("ax-get-coaches-overview/"), "table_target":table_overview, "setClickEvent":setClickEventCoaches, "label":"Berater"};
// const fillOverwiewParms = {"url":HTTP.getURL("ax-get-visiter-overview/"), "table_target":table_overview_body, "setClickEvent":setClickEventVisiter, "label":"Besucher"};
// const fillOverwiewParms = {"url":HTTP.getURL("ax-get-devices-overview/"), "table_target":table_overview, "setClickEvent":setClickEventDevices, "label":"Geräte"};


/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Set all Listener at LOAD-Event--------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
window.addEventListener('load', () => {
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  this.document.getElementById(SERVER_OPTIONS.link_active).classList.add(nav_item_active);

  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  for (const elem of frm_local_storage) {
    elem.addEventListener("change", setChangeEvent);
  }
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  /* -----MAIN Reset----------------------------------------------------------------------------------------------------------------------------------*/
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  btn_main_reset.addEventListener("click", performRelease);
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  /* -----MAIN Submit---------------------------------------------------------------------------------------------------------------------------------*/
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  btn_main_store.addEventListener("click", performSubmit);
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  if (btn_insert_visiter) btn_insert_visiter.addEventListener("click", registQuickInsertVisiter);
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  if (quick_vorname) {
    quick_vorname.addEventListener("keydown", (event) => {
      event.stopImmediatePropagation;
      if (event.code == "Enter") {
        quick_nachname.focus();
      }
    });
    quick_nachname.addEventListener("keydown", (event) => {
      event.stopImmediatePropagation;
      if (event.code == "Enter") {
        quick_telefon.focus();
      }
    });
    quick_telefon.addEventListener("keydown", (event) => {
      event.stopImmediatePropagation;
      if (event.code == "Enter") {
        quick_email.focus();
      }
    });
    quick_email.addEventListener("keydown", registKeyQuickInsertVisiter);
  }

  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  if (btn_search_visiter) btn_search_visiter.addEventListener("click", registSearchPtn);
  
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  if (frm_search_ptn) {
    frm_search_ptn.addEventListener("focus", (event) => {
      event.target.value = null;
    });
    frm_search_ptn.addEventListener("keydown", registKeySearchPtn);
  }

  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  btn_frm_pag_search.addEventListener("click", searchOverview);
  frm_pag_search.addEventListener("keydown", searchOverview);
  frm_pag_search.addEventListener("focus", (event) => {
    event.target.value = null;
  });
  page_pag_back.addEventListener("click", (event) => {
    if (page_pag_back.classList.contains("disabled")) return false;
    const overview_page = parseInt(extStorage.getItem("overview-page", "1"));
    extStorage.setItem("overview-page", overview_page - 1);
    fillOverwiew();
  });
  page_pag_start.addEventListener("click", (event) => {
    if (page_pag_start.classList.contains("disabled")) return false;
    extStorage.setItem("overview-page", 1);
    fillOverwiew();
  });
  page_pag_forw.addEventListener("click", (event) => {
    if (page_pag_forw.classList.contains("disabled")) return false;
    const overview_page = parseInt(extStorage.getItem("overview-page", "1"));
    extStorage.setItem("overview-page", overview_page + 1);
    fillOverwiew();
  });
  
  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  fillOverwiew();
  env_init();
});


async function env_init() {
  removeDismissible();
  showAlertsAfterInit();

  /* -------------------------------------------------------------------------------------------------------------------------------------------------*/
  const item_id_head = extStorage.getItem("frm-main-kdnr") ? extStorage.getItem("frm-main-kdnr") : extStorage.getItem("frm-main-id");
  const header = eval(SERVER_OPTIONS.header);
  if (item_id_head) {
    let headline = header[0] + " " + item_id_head + " ändern";
    const dsabld = btn_main_store.getAttribute("disabled");
    if (dsabld) headline += " (Schreibgeschützt)";
    frm_main_caption.innerText = headline;
    if (frm_main_booked_events) frm_main_booked_events.classList.remove("d-none");
    if (frm_main_coaches) frm_main_coaches.classList.remove("d-none");
  } 
  else {
    frm_main_caption.innerText = header[1];
    if (frm_main_booked_events) frm_main_booked_events.classList.add("d-none");
    if (frm_main_coaches) frm_main_coaches.classList.add("d-none");
  }
  for (const elem of frm_local_storage) {
    elem.classList.remove("is-invalid","is-valid");
    if (elem.nextElementSibling !== null) {
      if (elem.nextElementSibling.classList.contains('invalid-feedback')) elem.nextElementSibling.innerText = "";
    }
    const is_collect = elem.getAttribute("data-collect");
    if (!is_collect) {
      setDomField(elem);
      if (elem.name == "frm-main-veranstort") {
        let max_visiters = -1;
        if (elem.value >= 0) {
          max_visiters = max_visiter_map.get(elem.value);
        }
        max_visiter_map.set("current", max_visiters);
        setVisiterWL();
      }
    }
    else {
      if (visiter_elem_map.match(is_collect)) {
        table_visiter.replaceChildren();
        if (!visiter_elem_map.is_empty()) {
          const rt_code = await fillVisiter(visiter_elem_map.orderString(), visiter_elem_map.map);
          if (rt_code != "OK") {
            appendAlert('Das Übertragen des Besuchers konnte nicht erfolgreich beendet werden!', 'danger');
          }
        }
      }
      else if (coaches_devices_map.match(is_collect)) {
        let row_index = 0;
        frm_main_coaches_nbr.innerText = coaches_devices_map.size();
        table_device_coaches.replaceChildren();
        for (const id of coaches_devices_map.map_order) {
          const newtr = table_device_coaches.insertRow();
          const row = coaches_devices_map.map.get(id);
          static_coaches_list(row, newtr, row_index++);
          const figure = newtr.cells[3].firstElementChild;
          figure.addEventListener("click", setClickForCoach);
        }
      }
      else if (events_elem_map.match(is_collect)) {
        let row_index = 0;
        frm_main_veranst_nbr.innerText = events_elem_map.size();
        table_events_body.replaceChildren();
        for (const id of events_elem_map.map_order) {
          const newtr = table_events_body.insertRow();
          const row = events_elem_map.map.get(id);
          const ind = static_event(id, row, newtr, row_index++, events_elem_map.get_wl_flag(id));
          const figure = newtr.cells[ind].firstElementChild;
          figure.addEventListener("click", setClickForEvents);
        }
      }
      else if (coaches_themes_elem_map.match(is_collect)) {
        fillCoaches(is_collect, coaches_themes_elem_map, frm_main_coached_themes_nbr, table_coached_themes, "coached-themes", setClickEventCoacheTheme);
      }
      else if (coaches_info_elem_map.match(is_collect)) {
        fillCoaches(is_collect, coaches_info_elem_map, frm_main_info_themes_nbr, table_info_themes, "info-themes", setClickEventCoacheInfo);
      }
      else if (coaches_devices_elem_map.match(is_collect)) {
        fillCoaches(is_collect, coaches_devices_elem_map, frm_main_coached_devices_nbr, table_coached_devices, "coached-devices", setClickEventCoacheDevices);
      }
      else if (coaches_elem_map.match(is_collect)) {
        fillCoaches(is_collect, coaches_elem_map, frm_main_berater_nbr, table_coaches, "berater", setClickEventCoach);
      }
    }
  }
  section_input.classList.remove("opacity-50");
}


function fillCoaches(is_collect, elem_map, frm_main_nbr, table_source, static_name, setClickEvent) {
  if (!elem_map.is_empty()) {
    const select_item = this.document.getElementsByName(is_collect)[0];
    const html_options = select_item.innerHTML;
    const Ids = elem_map.reverse();
    const max_ids = Ids.length;
    frm_main_nbr.innerText = max_ids;
    table_coaches_clear(table_source);
    let index = max_ids;
    for (const Id of Ids) {
      const newtr = table_source.insertRow(0);
      static_coaches_rows(static_name, --index, html_options, newtr, index);
      const newsel = newtr.cells[0].firstElementChild;
      newsel.value = Id;
      newsel.setAttribute("data-init-frm", "true");
      const figure_elem = newtr.cells[1].firstElementChild;
      figure_elem.classList.remove("d-none");
      figure_elem.addEventListener("click", setClickEvent);
      const max_row = table_source.rows.length;
      const last_index = max_row - 1;
      table_source.rows[last_index].getElementsByTagName("select")[0].setAttribute("data-index", last_index);
    }
  }
}


/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Füllen der Übersichtsspalte mit Blätterfunktion---------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
async function fillOverwiew() {
  const overview_search = extStorage.getItem("overview-search-item", "ALL");
  const overview_page = extStorage.getItem("overview-page", "1");
  const submit_map = new SubmitParm([["overview-search", overview_search], ["overview-page", overview_page]]);
  const result_data = await execFetch(HTTP.getURL("ax-get-" + SERVER_OPTIONS.APP + "-overview/"), submit_map.getString());
  if (result_data.status == "OK") {
    table_overview_body.innerHTML = result_data.html
    const more_pages = result_data.pagination;
    page_pag_current.firstElementChild.innerText = overview_page;
    for (const elem of btn_overview_edit) {
      elem.addEventListener("click", setClickForEdit);
    }
    if (!more_pages) {
      page_pag_forw.classList.add("disabled");
    }
    else {
      page_pag_forw.classList.remove("disabled");
    }
    if (overview_page == "1") {
      page_pag_back.classList.add("disabled");
      page_pag_start.classList.add("disabled");
    }
    else {
      page_pag_back.classList.remove("disabled");
      page_pag_start.classList.remove("disabled");
    }
  }
  else {
    appendAlert(`Anzeigen der ${SERVER_OPTIONS.overview_label} konnte nicht erfolgreich beendet werden!`, 'danger');
  }
}


/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Änderungssperre zurücksetzen----------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
async function performRelease(event) {
  const rt_code = {"status":"OK", "id":"--"};
  const item_id_head = extStorage.getItem("frm-main-id");
  const item_timestamp = extStorage.getItem("timestamp");
  if (item_timestamp) {
    const submit_map = new SubmitParm([["item-id", item_id_head], ["item-timestamp", item_timestamp]]);
    // Durchführen Release Sprerre
    const result_data = await execFetch(HTTP.getURL("ax-submit-" + SERVER_OPTIONS.APP + "-release/"), submit_map.getString());
    rt_code.status = result_data.status;
    rt_code.id = result_data.id;
  }
  extStorage.clear();
  extStorage.setItem("last_stored", "CLEAR");
  extStorage.setItem("last_clear_status", rt_code.status);
  window.location.reload();
}


/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----MAIN Submit---------------------------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
async function performSubmit(event) {
  btn_main_store.setAttribute("disabled", true);
  btn_main_finish.replaceChildren();
  const item_id_head = extStorage.getItem("frm-main-id");
  let is_error = false, is_plz = false, is_ort = false, is_str = false, is_telef = false, is_mail = false, is_addr = false;
  let summary_berater = true, unknown_value_berater = false, summary_besucher = true, unknown_value_besucher = false, unknown_spende = false;
  let value_von, value_bis, value_veranstort, value_datum;
  for (const elem of frm_main.elements) {
    if (["button", "fieldset", "checkbox"].includes(elem.type)) continue;
    elem.classList.remove("is-invalid","is-valid");
    if (elem.name == "frm-main-typ") {
      if (elem.value == '' || elem.value < 0) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Art der " + SERVER_OPTIONS.category + " ist erforderlich."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-veranstort") {
      value_veranstort = elem;
      if (elem.value == '' || elem.value < 0) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe " + SERVER_OPTIONS.category + "-Ort ist erforderlich."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-zeit-von") {
      value_von = elem;
      if (elem.value == '' || elem.value < "07:00") {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Zeit-von ist keine sinnvoll Uhrzeit."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-zeit-dauer") {
      if (elem.value == '' || elem.value > "08:00") {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Zeit-Dauer ist keine sinnvolle Angabe."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-zeit-bis") {
      value_bis = elem;
      if (elem.value != '' && elem.value < value_von.value) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Zeit-bis ist kleiner als Zeit-von."
        is_error = true;
      }
      if (elem.value == '' || elem.value > "22:00") {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Zeit-bis ist keine sinnvoll Uhrzeit."
        is_error = true;
      }
      if (elem.value == value_von.value) {
        value_von.classList.add("is-invalid");
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Zeit-von und Zeit-bis sind identisch."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-veranstdatum") {
      value_datum = elem;
      if (elem.value == '' || (elem.value < SERVER_OPTIONS.min_date && !item_id_head)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe des Datums liegt zu weit in der Vergangenheit."
        is_error = true;
      } 
      else if (elem.value != '' && elem.value > SERVER_OPTIONS.max_date) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe des Datums liegt zu weit in der Zukunft."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-berater") {
      if (elem.value == '') {
        unknown_value_berater = true;
      }
      else if (elem.value >= 0) {
        summary_berater = false;
      }
    }
    else if (["frm-main-spende", "frm-main-thema", "frm-main-geraet"].includes(elem.name)) {
      if (elem.value == '') {
        unknown_value_besucher = true;
      } else summary_besucher = false;
      if (elem.name == "frm-main-spende") {
        if (!validateNumber(elem.value, allowZero=true)) {
          unknown_spende = true;
        }
      }
    }
    else if (elem.name == "frm-main-vorname") {
      if (!elem.value) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Vorname ist erforderlich."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-nachname") {
      if (!elem.value) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Nachname ist erforderlich."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-mobil") {
      if (!validatePhone(elem.value)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Mobil-Nr. ist nicht korrekt."
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-anrede") {
      if (elem.value < 0) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe der Anrede ist erforderlich.";
        is_error = true;
      }
    }
    else if (SERVER_OPTIONS.PREFIX == "02" && elem.name == "frm-main-datum") {
      if (elem.value > SERVER_OPTIONS.max_date) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe des Datums liegt zu weit in der Zukunft.";
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-plz") {
      is_plz = elem.value != "";
      if (is_plz) is_addr = true;
      if (!validatePLZ(elem.value)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Postleitzahl ist nicht korrekt.";
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-email") {
      is_mail = elem.value != "";
      if (!validateEmail(elem.value)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe E-Mail-Adresse ist nicht korrekt.";
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-telefon") {
      is_telef = elem.value != "";
      if (!validatePhone(elem.value)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Telefon-Nr. ist nicht korrekt.";
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-strasse" && elem.value) {
      is_str = true;
      is_addr = true;
    }
    else if (elem.name == "frm-main-ort" && elem.value) {
      is_ort = true;
      is_addr = true;
    }
    else if (elem.name == "frm-main-maxbesucher") {
      if (!validateNumber(elem.value)) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Anzahl ist nicht korrekt.";
        is_error = true;
      }
    }
    else if (elem.name == "frm-main-bezeichnung") {
      if (!elem.value) {
        elem.classList.add("is-invalid");
        elem.nextElementSibling.innerText = "Die Angabe Bezeichnung ist erforderlich."
        is_error = true;
      }
    }
  }
  if (SERVER_OPTIONS.PREFIX == "01") {
    const elem_berater_set = frm_main.elements.namedItem("frm-main-set-berater");
    const elem_besucher_set = frm_main.elements.namedItem("frm-main-set-besucher");
    elem_berater_set.classList.remove("is-invalid","is-valid");
    elem_besucher_set.classList.remove("is-invalid","is-valid");
    if (summary_berater) {
      elem_berater_set.classList.add("is-invalid");
      elem_berater_set.nextElementSibling.innerText = "Die Angabe mindestens 1 Berater ist erforderlich."
      is_error = true;
    }
    if (unknown_value_berater) {
      elem_berater_set.classList.add("is-invalid");
      elem_berater_set.nextElementSibling.innerText = "Die Angabe enthält mindestens 1 unbekannten Berater."
      is_error = true;
    }
    if (summary_besucher) {
      elem_besucher_set.classList.add("is-invalid");
      elem_besucher_set.nextElementSibling.innerText = "Die Angabe mindestens 1 Besucher ist erforderlich."
      is_error = true;
    }
    if (unknown_spende) {
      elem_besucher_set.classList.add("is-invalid");
      elem_besucher_set.nextElementSibling.innerText = "Die Angabe Spende enthält ungültige Angaben."
      is_error = true;
    }
    if (unknown_value_besucher) {
      elem_besucher_set.classList.add("is-invalid");
      elem_besucher_set.nextElementSibling.innerText = "Die Angabe enthält mindestens 1 ungültigen Wert."
      is_error = true;
    }
  }
  if (SERVER_OPTIONS.PREFIX == "01" && !is_error) {
    const rc_code = await checkVeranstOrt(value_datum, value_veranstort, value_von, value_bis, item_id_head);
    if (rc_code == "ERR") {
      appendAlert("Das Prüfen Ort der " + SERVER_OPTIONS.category + " konnte nicht erfolgreich beendet werden!", 'danger');
      is_error = true;
    }
    else if (rc_code == "INV") {
      value_veranstort.classList.add("is-invalid");
      value_veranstort.nextElementSibling.innerText = "Für Ort ist in dem Zeitraum bereits eine " + SERVER_OPTIONS.category + " vorhanden."
      is_error = true;
    }
  }
  if (SERVER_OPTIONS.PREFIX == "02" && !is_error) {
    if (is_plz && (!is_ort || !is_str)) {
      if (!is_ort) {
        frm_main_ort.nextElementSibling.innerText = "Wenn PLZ angegeben, muss auch Ort angegeben werden.";
        frm_main_ort.classList.add("is-invalid");
        is_error = true;
      }
      if (!is_str) {
        frm_main_strasse.nextElementSibling.innerText = "Wenn PLZ angegeben, muss auch Straße angegeben werden.";
        frm_main_strasse.classList.add("is-invalid");
        is_error = true;
      }
    }
    else if (is_ort && (!is_str || !is_plz)) {
      if (!is_str) {
        frm_main_strasse.nextElementSibling.innerText = "Wenn Ort angegeben, muss auch Straße angegeben werden.";
        frm_main_strasse.classList.add("is-invalid");
        is_error = true;
      }
      if (!is_plz) {
        frm_main_plz.nextElementSibling.innerText = "Wenn Ort angegeben, muss auch PLZ angegeben werden.";
        frm_main_plz.classList.add("is-invalid");
        is_error = true;
      }
    }
    else if (is_str && (!is_ort || !is_plz)) {
      if (!is_ort) {
        frm_main_ort.nextElementSibling.innerText = "Wenn Straße angegeben, muss auch Ort angegeben werden.";
        frm_main_ort.classList.add("is-invalid");
        is_error = true;
      }
      if (!is_plz) {
        frm_main_plz.nextElementSibling.innerText = "Wenn Straße angegeben, muss auch PLZ angegeben werden.";
        frm_main_plz.classList.add("is-invalid");
        is_error = true;
      }
    }
    else if (!is_addr && !is_telef && !is_mail) {
      if (!is_str) frm_main_strasse.classList.add("is-invalid");
      if (!is_ort) frm_main_ort.classList.add("is-invalid");
      if (!is_plz) frm_main_plz.classList.add("is-invalid");
      if (!is_telef) frm_main_telefon.classList.add("is-invalid");
      if (!is_mail) frm_main_email.classList.add("is-invalid");
      appendAlert('Es muss mindestens Adresse oder Telefon oder E-Mail angegeben werden.', 'warning');
      is_error = true;
    }
  }

  if (is_error) {
    appendAlert('Es sind noch Fehler vorhanden; siehe oberhalb. Bitte korrigieren.', 'warning');
  }
  else {
    spinner_btn_store.classList.remove("d-none");
    const submit_map = new SubmitParm();
    const besucher_map = new Map();
    const berater_arr = new Array();
    const coaches_themes_arr = new Array();
    const coaches_info_arr = new Array();
    const coaches_devices_arr = new Array();
    for (const elem of frm_main.elements) {
      if (["BUTTON", "FIELDSET"].includes(elem.nodeName)) continue;
      const data_id = elem.getAttribute("data-id");
      const chk = submit_map.add_if("veranst-datum", elem, "frm-main-veranstdatum") || 
        submit_map.add_if("veranst-zeit-von", elem, "frm-main-zeit-von") ||
        submit_map.add_if("veranst-zeit-bis", elem, "frm-main-zeit-bis") ||
        submit_map.add_if("veranst-zeit-dauer", elem, "frm-main-zeit-dauer") ||
        submit_map.add_if("veranst-typ", elem, "frm-main-typ") ||
        submit_map.add_if("veranst-ort", elem, "frm-main-veranstort") ||
        submit_map.add_if("veranst-thema", elem, "frm-main-thema-head") ||
        submit_map.add_if("vorname", elem, "frm-main-vorname") ||
        submit_map.add_if("nachname", elem, "frm-main-nachname") ||
        submit_map.add_if("email", elem, "frm-main-email") ||
        submit_map.add_if("telefon", elem, "frm-main-telefon") ||
        submit_map.add_if("mobil", elem, "frm-main-mobil") ||
        submit_map.add_if("datum", elem, "frm-main-datum") ||
        submit_map.add_if("anrede", elem, "frm-main-anrede") ||
        submit_map.add_if("strasse", elem, "frm-main-strasse") ||
        submit_map.add_if("plz", elem, "frm-main-plz") ||
        submit_map.add_if("ort", elem, "frm-main-ort") ||
        submit_map.add_if("bemerkung", elem, "frm-main-bemerkung") ||
        submit_map.add_if("bezeichnung", elem, "frm-main-bezeichnung") ||
        submit_map.add_if("maxbesucher", elem, "frm-main-maxbesucher") ||
        submit_map.add_if("tdm", elem, "frm-main-tdm") ||
        submit_map.add_if("ext", elem, "frm-main-ext") ||
        submit_map.add_if("newsl", elem, "frm-main-newsl") ||
        submit_map.add_if("aktiv", elem, "frm-main-aktiv") ||
        add_To_Array(berater_arr, elem.value, elem.name == "frm-main-berater") ||
        add_To_Array(coaches_themes_arr, elem.value, elem.name == "frm-main-coached-themes") ||
        add_To_Array(coaches_info_arr, elem.value, elem.name == "frm-main-info-themes") ||
        add_To_Array(coaches_devices_arr, elem.value, elem.name == "frm-main-coached-devices");
      if (!chk) {
        if (elem.name == "frm-main-spende") {
          if (!besucher_map.has(data_id)) besucher_map.set(data_id, new Map());
          const besucher_inhalt_map = besucher_map.get(data_id);
          if (elem.getAttribute("data-rowid")) besucher_inhalt_map.set("id", elem.getAttribute("data-rowid"));
          besucher_inhalt_map.set("spende", elem.value);
          let wl = false, wl_prev = false;
          if (elem.getAttribute("data-active-wl")) {
            wl_prev = true;
          }
          if (elem.getAttribute("data-WL")) {
            wl = true;
          }
          besucher_inhalt_map.set("wl", wl);
          besucher_inhalt_map.set("wl-prev", wl_prev);
        }
        else if (elem.name == "frm-main-thema") {
          if (!besucher_map.has(data_id)) besucher_map.set(data_id, new Map());
          const besucher_inhalt_map = besucher_map.get(data_id);
          if (elem.getAttribute("data-rowid")) besucher_inhalt_map.set("id", elem.getAttribute("data-rowid"));
          besucher_inhalt_map.set("thema", elem.value);
        }
        else if (elem.name == "frm-main-geraet") {
          if (!besucher_map.has(data_id)) besucher_map.set(data_id, new Map());
          const besucher_inhalt_map = besucher_map.get(data_id);
          if (elem.getAttribute("data-rowid")) besucher_inhalt_map.set("id", elem.getAttribute("data-rowid"));
          besucher_inhalt_map.set("geraet", elem.value);
        }
      }
    }
    if (berater_arr.length > 0) submit_map.add("berater", berater_arr);
    if (besucher_map.size > 0) submit_map.add("besucher", besucher_map);
    if (visiter_elem_map.init) submit_map.add("besucher-remove", visiter_elem_map.map_remove);
    if (coaches_themes_arr.length > 0) submit_map.add("coached-themes", coaches_themes_arr);
    if (coaches_info_arr.length > 0) submit_map.add("info-themes", coaches_info_arr);
    if (coaches_devices_arr.length > 0) submit_map.add("coached-devices", coaches_devices_arr);
    if (events_elem_map.init) submit_map.add("veranst-remove", events_elem_map.map_remove);
    if (coaches_devices_map.init) submit_map.add("coaches-remove", coaches_devices_map.map_remove);
    const item_timestamp = extStorage.getItem("timestamp");
    if (item_id_head) submit_map.add("main-id", item_id_head);
    if (item_timestamp) submit_map.add("item-timestamp", item_timestamp);
    // Durchführen Submit
    const result_data = await execFetch(HTTP.getURL("ax-submit-" + SERVER_OPTIONS.APP + "/"), submit_map.getString());
    spinner_btn_store.classList.add("d-none");
    if (result_data.status == "OK") {
      extStorage.clear(["overview-search-item", "overview-page"]);
      extStorage.setItem("last_stored", result_data.status);
      extStorage.setItem("last_stored_mode", result_data.mode);
      extStorage.setItem("last_stored_id", result_data.id);
      if (typeof result_data.kdnr !== 'undefined') extStorage.setItem("last_stored_kdnr", result_data.kdnr);
      if (typeof result_data.result_WL !== 'undefined') extStorage.setItem("result_WL", result_data.result_WL);
      window.location.reload();
    }
    else if (result_data.status == "NOTALWD") {
      const result_id = typeof result_data.kdnr !== 'undefined' ? result_data.kdnr : result_data.id;
      appendAlert(`${SERVER_OPTIONS.category} Nr.${result_id} wird von jemand anderem bearbeitet!`, 'danger');
      extStorage.setItem("last_stored", result_data.status);
    }
    else if (result_data.status == "DBL") {
      const result_id = typeof result_data.kdnr !== 'undefined' ? result_data.kdnr : result_data.id;
      appendAlert(`Für Beraterin/Berater Nr.${result_id} ist der Name bereits vorhanden!`, 'danger');
      extStorage.setItem("last_stored", result_data.status);
      frm_main_vorname.nextElementSibling.innerText = "Der Name ist bereits vorhanden."
      frm_main_nachname.nextElementSibling.innerText = "Der Name ist bereits vorhanden."
      frm_main_vorname.classList.add("is-invalid");
      frm_main_nachname.classList.add("is-invalid");
    }
    else if (result_data.status == "INVALID") {
      const result_id = typeof result_data.kdnr !== 'undefined' ? result_data.kdnr : result_data.id;
      appendAlert(`${SERVER_OPTIONS.category} Nr.${result_id} wurde inzwischen von jemand anderem bearbeitet, bitte neu zum Ändern auswählen.`, 'warning');
      extStorage.setItem("last_stored", result_data.status);
    }
    else {
      const result_id = typeof result_data.kdnr !== 'undefined' ? result_data.kdnr : result_data.id;
      if (result_id) {
        appendAlert(`Das Speichern von ${result_id} konnte nicht erfolgreich beendet werden!`, 'danger');
      }
      else {
        appendAlert('Das Speichern konnte nicht erfolgreich beendet werden!', 'danger');
      }
      extStorage.setItem("last_stored", "ERR");
    }
  }

  // Hochladen evtl. Fehlermeldungen
  uploadScriptError();

  btn_main_store.removeAttribute("disabled");
}


async function searchPtn(search_ptn) {
  let return_val = "OK";
  if (search_ptn) {
    const result_data = await execFetch(HTTP.getURL("ax-fd-visiter/") + search_ptn);
    if (result_data.status == "OK") {
      html_select_nbr.innerText = result_data.visiter.length;
      html_select.replaceChildren();
      for (const person of result_data.visiter) {
        const html_option = new Option(`${person.vorname} ${person.nachname} * ${person.email} * ${person.telefon}`, person.id);
        html_select.add(html_option);
      }
      html_select_div.classList.remove("d-none");
    }
    else {
      return_val = result_data.status;
      appendError('searchPtn-Error: Suchen von Kunden fehlerhaft beendet.');
    }
  }
  return return_val;
}

function searchOverview(event) {
  let valid = true;
  if (event.type == "keydown") {
    event.stopImmediatePropagation();
    if (event.code != "Enter") {
      valid = false;
    }
  }
  if (valid) {
    if (frm_main_veranstdatum) frm_main_veranstdatum.focus();
    else if (frm_main_anrede) frm_main_anrede.focus();
    else if (frm_main_vorname) frm_main_vorname.focus();
    else if (frm_main_bezeichnung) frm_main_bezeichnung.focus();
    extStorage.setItem("overview-search-item", frm_pag_search.value);
    extStorage.removeItem("overview-page");
    fillOverwiew();
  }
}


async function quickInsertVisiter(vorname, nachname, telefon, email) {
  let return_val = "OK";
  let is_error = false;
  vorname.removeAttribute("title")
  nachname.removeAttribute("title")
  telefon.removeAttribute("title")
  email.removeAttribute("title")
  vorname.classList.remove("is-invalid");
  nachname.classList.remove("is-invalid");
  telefon.classList.remove("is-invalid");
  email.classList.remove("is-invalid");
  if (!vorname.value)  {
    vorname.classList.add("is-invalid");
    vorname.setAttribute("title", "Der Vorname ist erforderlich!")
    is_error = true;
  }
  if (!nachname.value)  {
    nachname.classList.add("is-invalid");
    nachname.setAttribute("title", "Der Nachname ist erforderlich!")
    is_error = true;
  }
  if (telefon.value && !validatePhone(telefon.value))  {
    telefon.classList.add("is-invalid");
    telefon.setAttribute("title", "Keine gültige Telefonnummer!")
    is_error = true;
  }
  if (email.value && !validateEmail(email.value))  {
    email.classList.add("is-invalid");
    email.setAttribute("title", "Keine gültige E-Mail-Adresse!")
    is_error = true;
  }

  if (is_error) {
    return_val = "INV";
  }
  else {
    const submit_map = new SubmitParm([["vorname",vorname.value], ["nachname",nachname.value], ["telefon",telefon.value], ["email",email.value]]);
    // Durchführen Submit
    const result_data = await execFetch(HTTP.getURL("ax-submit-quick-visiter/"), submit_map.getString());
    if (result_data.status == "OK") {
      const elem_id = result_data.last_id.toString();
      const rt_code = await fillVisiter(elem_id);
      if (rt_code == "OK") {
        visiter_elem_map.append(elem_id);
        visiter_elem_map.commit();
        vorname.value = null;
        nachname.value = null;
        telefon.value = null;
        email.value = null;
      }
      else {
        appendAlert('Das Übertragen des Besuchers konnte nicht erfolgreich beendet werden!', 'danger');
        return_val = rt_code;
      }
    }
    else {
      return_val = result_data.status;
      appendError('quickInsertVisiter-Error: Konnte nicht beendet werden.');
    }
  }
  return return_val;
}


async function registKeyQuickInsertVisiter(event) {
  event.stopImmediatePropagation;
  if (event.code == "Enter") {
    if (await quickInsertVisiter(quick_vorname, quick_nachname, quick_telefon, quick_email) == "ERR") {
      appendAlert('Das Speichern der Besucher konnte nicht erfolgreich beendet werden!', 'danger');
    }
  }
}


async function registQuickInsertVisiter(event) {
  if (frm_quick_vorname.classList.contains("d-none")) {
    for (const elem of frm_quick) {
      elem.classList.remove("d-none");
    }
    for (const elem of frm_search) {
      elem.classList.add("d-none");
    }
    html_select_div.classList.add("d-none");
  } 
  else {
    if (await quickInsertVisiter(quick_vorname, quick_nachname, quick_telefon, quick_email) == "ERR") {
      appendAlert('Das Speichern der Besucher konnte nicht erfolgreich beendet werden!', 'danger');
    }
  }
}


async function registSearchPtn(event) {
  if (frm_search_ptn.classList.contains("d-none")) {
    for (const elem of frm_quick) {
      elem.classList.add("d-none");
    }
    for (const elem of frm_search) {
      elem.classList.remove("d-none");
    }
  }
  else {
    const search_ptn = frm_search_ptn.value;
    if (await searchPtn(search_ptn) != "OK") {
      appendAlert('Das Suchen des Besuchers konnte nicht erfolgreich beendet werden!', 'danger');
    }
  }
}


async function registKeySearchPtn(event) {
  event.stopImmediatePropagation;
  if (event.code == "Enter") {
    const search_ptn = event.target.value;
    if (await searchPtn(search_ptn) != "OK") {
      appendAlert('Das Suchen des Besuchers konnte nicht erfolgreich beendet werden!', 'danger');
    }
  }
}


async function checkVeranstOrt(datum, ort, von, bis, veranst_id) {
  let return_val = "OK";
  const submit_map = new SubmitParm([["datum",datum.value], ["ort",ort.value], ["von",von.value], ["bis",bis.value], ["veranst-id", veranst_id]]);
  const result_data = await execFetch(HTTP.getURL("ax-check-veranstort/"), submit_map.getString());
  if (result_data.is_invalid == "YES") {
    return_val = "INV";
  }
  return return_val;
}


async function setChangeEvent(event) {
  const target = event.target;
  const is_collect = target.getAttribute("data-collect");
  const elem_value = target.value.toString();
  const init_attr = target.getAttribute("data-init-frm");
  const index = target.getAttribute("data-index");
  let rtn = true;
  if (!is_collect) {
    getDomField(target);
    if (von_value && (target.name == von_value.name || target.name == bis_value.name || target.name == dauer.name)) {
      calcDuration(von_value, bis_value, dauer, target.name);
      extStorage.setItem(dauer.name, dauer.value);
      extStorage.setItem(bis_value.name, bis_value.value);
    }
    else if (target.name == "frm-main-veranstort") {
      let max_visiters = -1;
      if (target.value >= 0) {
        max_visiters = max_visiter_map.get(target.value);
      }
      max_visiter_map.set("current", max_visiters);
      setVisiterWL();
    }
  }
  else {
    if (is_collect == "populate-visiter") {
      const elem_id = target.value;
      if (!visiter_elem_map.has(elem_id)) {
        const rt_code = await fillVisiter(elem_id);
        if (rt_code == "OK") {
          visiter_elem_map.append(elem_id);
          visiter_elem_map.commit();
          const sel_options = target.options;
          const sel_index = sel_options.selectedIndex;
          if (sel_index >= 0) {
            sel_options.remove(sel_index);
            sel_options.selectedIndex = -1;
            const max_rows = frm_main_besucher_nbr_result.innerText;
            frm_main_besucher_nbr_result.innerText = max_rows-1;
          }
        }
        else {
          appendAlert('Das Übertragen des Besuchers konnte nicht erfolgreich beendet werden!', 'danger');
        }
      }
      else {
        const sel_options = target.options;
        sel_options.selectedIndex = -1;
      }
    }
    else if (visiter_elem_map.match(is_collect)) {
      const elem_name = target.name;
      const elem_id = target.getAttribute("data-id");
      if (visiter_elem_map.has(elem_id)) {
        visiter_elem_map.replaceValue(elem_id, elem_name, elem_value);
        visiter_elem_map.commit();
      }
    }
    else if (coaches_elem_map.match_target(is_collect)) {
      rtn = setCoachesChangeEvent(target, index, init_attr, elem_value, coaches_elem_map, frm_main_berater_nbr, table_coaches, "berater", setClickEventCoach);
    }
    else if (coaches_themes_elem_map.match_target(is_collect)) {
      rtn = setCoachesChangeEvent(target, index, init_attr, elem_value, coaches_themes_elem_map, frm_main_coached_themes_nbr, table_coached_themes, "coached-themes", setClickEventCoacheTheme);
    }
    else if (coaches_info_elem_map.match_target(is_collect)) {
      rtn = setCoachesChangeEvent(target, index, init_attr, elem_value, coaches_info_elem_map, frm_main_info_themes_nbr, table_info_themes, "info-themes", setClickEventCoacheInfo);
    }
    else if (coaches_devices_elem_map.match_target(is_collect)) {
      rtn = setCoachesChangeEvent(target, index, init_attr, elem_value, coaches_devices_elem_map, frm_main_coached_devices_nbr, table_coached_devices, "coached-devices", setClickEventCoacheDevices);
    }
  }
  return rtn;
}


function setCoachesChangeEvent(target, index, init_attr, elem_value, elem_map, frm_main_nbr, table_source, static_name, setClickEvent) {
  if (elem_value == "-1" || !elem_map.has(elem_value)) {
    if (init_attr == "false" && elem_value != "-1") {
      elem_map.append(elem_value);
    }
    else {
      elem_map.replaceByIndex(index, elem_value);
    }
    elem_map.commit();
  }
  else {
    target.value = elem_map.getByIndex(index);
    return false;
  }
  target.setAttribute("data-init-frm", "true");
  if (init_attr == "false") {
    const max_row = table_source.rows.length;
    frm_main_nbr.innerText = max_row;
    const figure_elem = target.parentNode.parentNode.querySelector(`.frm-main-${static_name}-remove`);
    figure_elem.setAttribute("data-index", max_row - 1);
    figure_elem.classList.remove("d-none");
    figure_elem.addEventListener("click", setClickEvent);
    const html_options = target.innerHTML;
    const newrow = table_source.insertRow();
    static_coaches_rows(static_name,max_row, html_options, newrow);
  }
  return true;
}


function setClickForEvents(event) {
  let target = event.target;
  while (target.nodeName != "FIGURE") {
    target = target.parentNode;
  }
  const index = target.getAttribute("data-index");
  table_events_body.deleteRow(index);
  const max_rows = table_events_body.rows.length;
  frm_main_veranst_nbr.innerText = max_rows;
  let row_index = 0;
  for (const row of table_events_body.rows) {
    const max = row.cells.length -1;
    row.cells[max].firstElementChild.setAttribute("data-index", row_index++);
  }
  const event_id = target.getAttribute("data-id");
  const row_id = target.getAttribute("data-rowid");
  if (events_elem_map.has(event_id)) {
    events_elem_map.remove(event_id, row_id);
    events_elem_map.commit();
  }
}


function setClickForCoach(event) {
  let target = event.target;
  while (target.nodeName != "FIGURE") {
    target = target.parentNode;
  }
  const index = target.getAttribute("data-index");
  table_device_coaches.deleteRow(index);
  const max_rows = table_device_coaches.rows.length;
  frm_main_coaches_nbr.innerText = max_rows;
  let row_index = 0;
  for (const row of table_device_coaches.rows) {
    row.cells[3].firstElementChild.setAttribute("data-index", row_index++);
  }
  const item_id = target.getAttribute("data-id");
  if (coaches_devices_map.has(item_id)) {
    coaches_devices_map.remove(item_id);
    coaches_devices_map.commit();
  }
}


function setClickEventCoach(event) {
  setClickEventCoacheElements(event, coaches_elem_map, table_coaches, frm_main_berater_nbr)
}


function setClickEventCoacheTheme(event) {
  setClickEventCoacheElements(event, coaches_themes_elem_map, table_coached_themes, frm_main_coached_themes_nbr)
}


function setClickEventCoacheInfo(event) {
  setClickEventCoacheElements(event, coaches_info_elem_map, table_info_themes, frm_main_info_themes_nbr)
}


function setClickEventCoacheDevices(event) {
  setClickEventCoacheElements(event, coaches_devices_elem_map, table_coached_devices, frm_main_coached_devices_nbr)
}


function setClickEventCoacheElements(event, map, table, nbr) {
  let target;
  if (event instanceof Event) {
    target = event.target;
  }
  else {
    target = event;
  }
  if (map.is_empty()) {
    return false;
  }
  while (target.nodeName != "FIGURE") {
    target = target.parentNode;
  }
  const index = target.getAttribute("data-index");
  if (index == "-1") {
    return false;
  }
  map.removeByIndex(index);
  map.commit();
  
  table.deleteRow(index);
  const max_rows = table.rows.length;
  nbr.innerText = max_rows-1;
  let row_index = 0;
  for (const row of table.rows) {
    for (const cell of row.cells) {
      const elem = cell.firstElementChild;
      const index_elem = elem.getAttribute("data-index");
      if (elem.nodeName == "SELECT" || (elem.nodeName == "FIGURE" && index_elem != "-1")) {
        elem.setAttribute("data-index", row_index);
      }
    }
    row_index++;
  }
}


async function setClickEventVisiter(event) {
  let target = event.target;
  while (target.nodeName != "FIGURE") {
    target = target.parentNode;
  }
  const index = target.getAttribute("data-index");
  table_visiter.deleteRow(index);
  const max_rows = table_visiter.rows.length;
  frm_main_besucher_nbr.innerText = max_rows;
  let row_index = 0;
  for (const row of table_visiter.rows) {
    row.cells[5].firstElementChild.setAttribute("data-index", row_index++);
  }
  const visiter_id = target.getAttribute("data-id");
  if (visiter_elem_map.has(visiter_id)) {
    const id = target.getAttribute("data-rowid");
    visiter_elem_map.remove(visiter_id, id);
    visiter_elem_map.commit();
    setVisiterWL();
  }
}


async function setClickForEdit(event) {
  section_input.classList.add("opacity-50");
  let target = event.target;
  while (target.nodeName != "FIGURE") {
    target = target.parentNode;
  }
  const main_id = target.getAttribute("data-id");
  const submit_map = new SubmitParm([["main-id", main_id]]);
  const timestamp = extStorage.getItem("timestamp");
  if (timestamp) {
    submit_map.add("timestamp", timestamp);
  }
  const item_id_head = extStorage.getItem("frm-main-id");
  if (item_id_head) {
    submit_map.add("item_id_head", item_id_head);
  }
  const result_data = await execFetch(HTTP.getURL("ax-get-" + SERVER_OPTIONS.APP + "-edit/"), submit_map.getString());
  if (["OK", "LCK"].includes(result_data.status)) {
    extStorage.clear(["overview-search-item", "overview-page"]);
    extStorage.setItem("last_stored", "RELOAD");
    extStorage.setItem("last_stored_id", main_id);
    if (result_data.status == "LCK") {
      extStorage.setItem("last_stored_mode", "LOCK");
    }
    else {
      extStorage.setItem("last_stored_mode", "NORM");
    }
    if (result_data.timestamp) extStorage.setItem("timestamp", result_data.timestamp);
    if (typeof result_data.veranst !== 'undefined') {
      extStorage.setItem("frm-main-id", result_data.veranst.id);
      extStorage.setItem("frm-main-veranstdatum", result_data.veranst.datum);
      extStorage.setItem("frm-main-zeit-von", result_data.veranst.von);
      extStorage.setItem("frm-main-zeit-bis", result_data.veranst.bis);
      extStorage.setItem("frm-main-zeit-dauer", result_data.veranst.dauer);
      extStorage.setItem("frm-main-thema-head", result_data.veranst.thema);
      extStorage.setItem("frm-main-typ", result_data.veranst.typ);
      extStorage.setItem("frm-main-veranstort", result_data.veranst.ort);
      coaches_elem_map.clear();
      for (const elem of result_data.berater) {
        coaches_elem_map.append(elem.BeraterID);
      }
      coaches_elem_map.commit();
      visiter_elem_map.clear();
      for (const elem of result_data.besucher) {
        const parmMap = new Map();
        parmMap.set("id", elem.id.toString());
        parmMap.set("frm-main-spende", elem.spende.toString());
        parmMap.set("frm-main-thema", elem.ThemenID.toString());
        parmMap.set("frm-main-geraet", elem.GeraeteID.toString());
        parmMap.set("wl", elem.BesucherWL);
        visiter_elem_map.append(elem.BesucherID.toString(), parmMap);
      }
      visiter_elem_map.commit();
    }
    if (typeof result_data.coache !== 'undefined') {
      extStorage.setItem("frm-main-id", result_data.coache.id);
      extStorage.setItem("frm-main-nachname", result_data.coache.Nachname);
      extStorage.setItem("frm-main-vorname", result_data.coache.Vorname);
      extStorage.setItem("frm-main-email", result_data.coache.EMail);
      extStorage.setItem("frm-main-mobil", result_data.coache.Mobil);
      extStorage.setItem("frm-main-telefon", result_data.coache.Telefon);
      extStorage.setItem("frm-main-tdm", result_data.coache.TdM);
      extStorage.setItem("frm-main-aktiv", result_data.coache.Aktiv);
      extStorage.setItem("frm-main-ext", result_data.coache.BerExt);
      coaches_themes_elem_map.clear();
      for (const elem of result_data.coached_themes) {
        coaches_themes_elem_map.append(elem.ThemenID.toString());
      }
      coaches_themes_elem_map.commit();
      coaches_info_elem_map.clear();
      for (const elem of result_data.info_themes) {
        coaches_info_elem_map.append(elem.ThemenID.toString());
      }
      coaches_info_elem_map.commit();
      coaches_devices_elem_map.clear();
      for (const elem of result_data.coached_devices) {
        coaches_devices_elem_map.append(elem.GeraeteID.toString());
      }
      coaches_devices_elem_map.commit();
    }
    if (typeof result_data.visiter !== 'undefined') {
      extStorage.setItem("last_stored_kdnr", result_data.visiter.KundenNr);
      extStorage.setItem("frm-main-id", result_data.visiter.id);
      extStorage.setItem("frm-main-kdnr", result_data.visiter.KundenNr);
      extStorage.setItem("frm-main-datum", result_data.visiter.datum);
      extStorage.setItem("frm-main-anrede", result_data.visiter.Anrede);
      extStorage.setItem("frm-main-nachname", result_data.visiter.Nachname);
      extStorage.setItem("frm-main-vorname", result_data.visiter.Vorname);
      extStorage.setItem("frm-main-strasse", result_data.visiter.Strasse);
      extStorage.setItem("frm-main-ort", result_data.visiter.Ort);
      extStorage.setItem("frm-main-plz", result_data.visiter.PLZ);
      extStorage.setItem("frm-main-email", result_data.visiter.EMail);
      extStorage.setItem("frm-main-telefon", result_data.visiter.Telefon);
      extStorage.setItem("frm-main-bemerkung", result_data.visiter.Bemerkung);
      extStorage.setItem("frm-main-aktiv", result_data.visiter.Aktiv);
      extStorage.setItem("frm-main-newsl", result_data.visiter.Newsletter);
      events_elem_map.clear();
      for (const elem of result_data.events) {
        events_elem_map.append(elem.VeranstID.toString(), [elem.id.toString(), elem.datum.toString(), elem.Bezeichnung, elem.ort], elem.WL);
      }
      events_elem_map.commit();
    }
    if (typeof result_data.device !== 'undefined') {
      extStorage.setItem("frm-main-id", result_data.device.id);
      extStorage.setItem("frm-main-bezeichnung", result_data.device.Bezeichnung);
      coaches_devices_map.clear();
      for (const elem of result_data.coached_devices) {
        coaches_devices_map.append(elem.id, [elem.id, elem.Vorname, elem.Nachname, elem.Telefon, elem.EMail]);
      }
      coaches_devices_map.commit();
    }
    if (typeof result_data.target !== 'undefined') {
      extStorage.setItem("frm-main-id", result_data.target.id);
      extStorage.setItem("frm-main-bezeichnung", result_data.target.Bezeichnung);
      extStorage.setItem("frm-main-maxbesucher", result_data.target.MaxBesucher);
      events_elem_map.clear();
      for (const elem of result_data.events) {
        events_elem_map.append(elem.id.toString(), [elem.id.toString(), elem.datum.toString(), elem.Bezeichnung, null]);
      }
      events_elem_map.commit();
    }
    env_init();
  }
  else {
    section_input.classList.remove("opacity-50");
    appendAlert("Ändern der " + SERVER_OPTIONS.category + " konnte nicht erfolgreich beendet werden!", 'danger');
  }
}


async function fillVisiter(visiterId, elemMap=null) {
  let return_val = "OK";
  const result_list = await execFetch(HTTP.getURL("ax-get-visiter/") + visiterId);
  if (result_list.status == "OK") {
    for (const result_data of result_list.visiter) {
      if (!result_data) continue;
      const newtr = table_visiter.insertRow();
      const max_rows = table_visiter.rows.length;
      frm_main_besucher_nbr.innerText = max_rows;
      static_visiter(result_data, newtr, max_rows-1);
      const figure_elem = newtr.querySelector(".frm-main-besucher-remove");
      figure_elem.addEventListener("click", setClickEventVisiter);
      /* elemMap ist nur gesetzt, wenn die zugehörigen Besucher bereits gespeichert waren */
      if (elemMap) {
        const valueMap = elemMap.get(result_data.id.toString());
        const id = valueMap.get("id");
        const wl = valueMap.get("wl");
        const spende = valueMap.get("frm-main-spende");
        const thema = valueMap.get("frm-main-thema");
        const geraet = valueMap.get("frm-main-geraet");
        if (spende) {
          const elem = newtr.cells.item(2).firstElementChild;
          if (elem) {
            elem.setAttribute("data-rowid", id);
            elem.value = spende;
            if (wl) {
              elem.setAttribute("data-active-wl", "true");
            }
          }
        }
        if (thema) {
          const elem = newtr.cells.item(3).firstElementChild;
          if (elem) {
            elem.setAttribute("data-rowid", id);
            elem.value = thema;
          }
        }
        if (geraet) {
          const elem = newtr.cells.item(4).firstElementChild;
          if (elem) {
            elem.setAttribute("data-rowid", id);
            elem.value = geraet;
          }
        }
        const elem = newtr.cells.item(5).firstElementChild;
        if (elem) {
          elem.setAttribute("data-rowid", id);
        }
      }
    }
    setVisiterWL();
  }
  else {
    return_val = result_list.status;
    appendError('fillVisiter-Error: Konnte nicht beendet werden.');
  }
  return return_val;
}


function setVisiterWL() {
  const max_visiters = max_visiter_map.get("current");
  for (const row of table_visiter.rows) {
    for (const cell of row.cells) {
      cell.classList.remove(SERVER_OPTIONS.style_bg_visiter_wl);
      const first_elem = cell.querySelector(".form-control");
      if (first_elem) first_elem.removeAttribute("data-WL");
      if (max_visiters >= 0 && row.rowIndex > max_visiters) {
        cell.classList.add(SERVER_OPTIONS.style_bg_visiter_wl);
        if (first_elem) first_elem.setAttribute("data-WL", "true");
      }
    }
  }
  let max_vis = "--";
  if (max_visiters >= 0) max_vis = max_visiters;
  frm_main_besucher_nbrmax.innerText = max_vis;
}


function calcDuration(von, bis, dauer, fieldname) {
  const [von_h, von_m] = von.value.split(":");
  const [bis_h, bis_m] = bis.value.split(":");
  const [dauer_h, dauer_m] = dauer.value.split(":");
  const actual_von = (von_h*60)+parseInt(von_m);
  const actual_bis = (bis_h*60)+parseInt(bis_m);
  const actual_dauer = (dauer_h*60)+parseInt(dauer_m);
  let diff = 0;
  if (fieldname == bis.name) {
    diff = actual_bis - actual_von;
    if (diff >= 0) {
      const h = Math.floor(diff / 60, 0);
      const m = diff % 60;
      dauer.value = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    }
    else {
      dauer.value = "--:--";
    }
  }
  else if (fieldname == von.name || fieldname == dauer.name) {
    diff = actual_von + actual_dauer;
    const h = Math.floor(diff / 60, 0);
    const m = diff % 60;
    bis.value = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
  }
}
