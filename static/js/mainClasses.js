/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Define important Classes--------------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
class HttpUrl {
  url="";
  prefix="";
  sep="?";
  delim="";
  constructor(prefix="", url="") {
    this.prefix = prefix;
    this.url = url;
  }
  addParm(key, value) {
    this.url += this.sep + this.delim + key + "=" + value;
    if (this.sep) this.sep = "";
    if (!this.delim) this.delim = "&";
  }
  getURL(uri="") {
    return this.prefix + this.url + uri;
  }
}


class SessionStorage {
  inner_map = new Map();
  has_storage = true;
  write_storage = true;
  prefix_str = "";
  
  constructor(prefix_str="", has_storage=true) {
    this.has_storage = has_storage;
    this.prefix_str = prefix_str;
  }
  getItem(key, default_value="") {
    if (this.has_storage) {
      const storedKey = this.prefix_str + key;
      const value = window.sessionStorage.getItem(storedKey);
      if (value) {
        if (["true", "false"].includes(value)) {
          if (value == "true") return true;
             else return false;
        }
        return value;
      } else {
        if (default_value) {
          return default_value;
        }
        else {
          return value;
        }
      }
    } else {
      return this.inner_map.get(key);
    }
  }
  setItem(key, value) {
    if (this.has_storage && this.write_storage) {
      try {
        const storedKey = this.prefix_str + key;
        window.sessionStorage.setItem(storedKey, value);
      } catch (e) {
        appendError("Fehler bei sessionStorage.setItem: " + e);
        this.inner_map.set(key, value);
        this.write_storage = false;
      }
    } else {
      this.inner_map.set(key, value);
    }
  }
  removeItem(key) {
    if (this.has_storage && this.write_storage) {
      try {
        const storedKey = this.prefix_str + key;
        window.sessionStorage.removeItem(storedKey);
      } catch (e) {
        appendError("Fehler bei sessionStorage.setItem: " + e);
        this.inner_map.delete(key);
        this.write_storage = false;
      }
    } else {
      this.inner_map.delete(key);
    }
  }
  keys(prefix=true) {
    let rt_keys = [];
    if (this.has_storage && this.write_storage) {
      try {
        for (let i = 0; i < window.sessionStorage.length; i++) {
          const key = window.sessionStorage.key(i);
          if (prefix && !key.startsWith(this.prefix_str)) {
            continue;
          }
          else {
            if (prefix && key.startsWith(this.prefix_str)) {
              rt_keys.push(key.replace(this.prefix_str, ''));
            } else {
              rt_keys.push(key);
            }
          }
        }
      } catch (e) {
        appendError("Fehler bei sessionStorage.keys: " + e);
        rt_keys = this.inner_map.keys();
      }
    } else {
      rt_keys = this.inner_map.keys();
    }
    return rt_keys;
  }
  clear(exclude=[]) {
    if (this.has_storage) {
      const storedKeys = this.keys();
      for (const key of storedKeys) {
        if (exclude.length == 0 || !exclude.includes(key)) {
          window.sessionStorage.removeItem(this.prefix_str + key);
        }
      }
    } else {
      this.inner_map.clear();
    }
  }
}

/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Define Global Values and Functions----------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
const STORAGE_AVAILABLE = storageAvailable("sessionStorage");
const HTTP = new HttpUrl(prefix=SERVER_OPTIONS.modname);

const extStorage = new SessionStorage(SERVER_OPTIONS.PREFIX + "_", STORAGE_AVAILABLE);
const nav_item_active = "bg-secondary-subtle";
const section_input = this.document.getElementById('sec-form-input');
const btn_main_finish = this.document.getElementById('btn-main-finish');
const btn_overview_edit = this.document.getElementsByClassName("frm-main-overview-edit");
const btn_main_store = this.document.getElementById("btn-frm-main-store");
const btn_main_reset = this.document.getElementById("btn-frm-main-reset");
const spinner_btn_store = btn_main_store.firstElementChild;
const frm_local_storage = this.document.getElementsByClassName("storaged-elem");
const frm_main = this.document.getElementById("frm-main");
const frm_main_caption = this.document.getElementById("frm-main-caption");
const main_errors_flashed = this.document.getElementById("main-errors-flashed");
const frm_pag_search = this.document.getElementById("frm-pag-search");
const btn_frm_pag_search = this.document.getElementById("btn-frm-pag-search");
const page_pag_back = this.document.getElementById("page-pag-back");
const page_pag_forw = this.document.getElementById("page-pag-forw");
const page_pag_start = this.document.getElementById("page-pag-start");
const page_pag_current = this.document.getElementById("page-pag-current");


/* -------------------------------------------------------------------------------------------------------------------------------------------------*/
/* -----Define Classes------------------------------------------------------------------------------------------------------------------------------*/
/* -------------------------------------------------------------------------------------------------------------------------------------------------*/


class SubmitParm {
  submit_map;
  constructor(initparms=[]) {
    this.submit_map = new Map(initparms);
  }
  add(key, value) {
    this.submit_map.set(key, value);
  }
  add_if(key, elem, compare) {
    if (compare == elem.name) {
      if (elem.type == 'checkbox') {
        this.submit_map.set(key, elem.checked);
      }
      else this.submit_map.set(key, elem.value);
      return true;
    } else return false;
  }
  getString() {
    return JSON.stringify(arrayifyMap(this.submit_map));
  }
}


class Visiter_Elements {
  init=false;
  map;
  map_order;
  map_remove;
  source;

  constructor(source) {
    if (source) {
      this.init = true;
      this.source = source;
      if (extStorage.getItem(this.source.id)) {
        this.map = new Map(JSON.parse(extStorage.getItem(this.source.id)));
        this.map.forEach((value, key, map) => {
          if (!["order", "remove"].includes(key)) {
            map.set(key, new Map(value));
          }
        });
        this.map_order = this.map.get("order");
        this.map_remove = this.map.get("remove");
      }
      else {
        this.clear();
      }
    }
  }
  orderString() {
    return this.map_order.join(",");
  }
  has(key) {
    return this.map.has(key);
  }
  size() {
    return this.map_order.length;
  }
  match(value) {
    return this.init && this.source.id == value;
  }
  is_empty() {
    if (this.size() == 0) return true;
      else return false;
  }
  remove(key, id) {
    if (this.map.has(key)) {
      this.map.delete(key);
      const ind = this.map_order.indexOf(key);
      this.map_order.splice(ind, 1);
      if (id) this.map_remove.push(id);
    }
  }
  append(key, value=new Map()) {
    if (!this.map.has(key)) {
      this.map.set(key, value);
      this.map_order.push(key);
    }
  }
  replaceValue(key, name, value) {
    if (this.map.has(key)) {
      const map_value = this.map.get(key);
      map_value.set(name, value);
    }
  }
  clear() {
    this.map = new Map();
    this.map.set("order", new Array());
    this.map.set("remove", new Array());
    this.map_order = this.map.get("order");
    this.map_remove = this.map.get("remove");
  }
  commit() {
    extStorage.setItem(this.source.id, JSON.stringify(arrayifyMap(this.map)));
  }
  
}


class Coaches_Elements {
  init=false;
  map;
  map_order;
  map_remove;
  source;
  target;
  
  constructor(source, target) {
    if (source) {
      this.init = true;
      this.source = source;
      this.target = target;
      const saved = extStorage.getItem(this.source.id);
      if (saved) {
        this.map = new Map(JSON.parse(saved));
        this.map_order = this.map.get("order");
        this.map_remove = this.map.get("remove");
      }
      else {
        this.clear();
      }
    }
  }
  orderString() {
    return this.map_order.join(",");
  }
  has(value) {
    return this.map_order.includes(value);
  }
  reverse() {
    return this.map_order.toReversed();
  }
  size() {
    return this.map_order.length;
  }
  match(value) {
    return this.init && this.source.id == value;
  }
  match_target(value) {
    return this.init && this.target.id == value;
  }
  is_empty() {
    if (this.size() == 0) return true;
      else return false;
  }
  getByIndex(index) {
    let val = this.map_order[index];
    if (!val) val = "-1";
    return val;
  }
  remove(value) {
    if (this.has(value)) {
      const ind = this.map_order.indexOf(value);
      this.removeByIndex(ind);
      if (this.map.has(value)) {
        this.map.delete(value);
        this.map_remove.push(value);
      }
    }
  }
  removeByIndex(index) {
    if (this.size() > index) {
      this.map_order.splice(index, 1);
    }
  }
  append(key, value) {
    if (typeof value === 'undefined') {
      if (!this.has(key.toString())) {
        this.map_order.push(key.toString());
      }
    }
    else {
      if (!this.map.has(key.toString())) {
        this.map.set(key.toString(), value);
        this.map_order.push(key.toString());
      }
    }
  }
  replace(key, value) {
    if (this.has(key)) {
      const ind = this.map_order.indexOf(key);
      this.replaceByIndex(ind, value);
    }
  }
  replaceByIndex(index, value) {
    if (this.size() > index) {
      this.map_order[index] = value;
    }
  }
  clear() {
    this.map = new Map();
    this.map.set("order", new Array());
    this.map.set("remove", new Array());
    this.map_order = this.map.get("order");
    this.map_remove = this.map.get("remove");
  }
  commit() {
    extStorage.setItem(this.source.id, JSON.stringify(arrayifyMap(this.map)));
  }
}


class Events_Elements {
  init=false;
  map;
  map_order;
  map_remove;
  map_WL;
  source;

  constructor(source) {
    if (source) {
      this.init = true;
      this.source = source;
      if (extStorage.getItem(this.source.id)) {
        this.map = new Map(JSON.parse(extStorage.getItem(this.source.id)));
        this.map_order = this.map.get("order");
        this.map_remove = this.map.get("remove");
        this.map_WL = new Map(this.map.get("WL"));
      }
      else {
        this.clear();
      }
    }
  }
  orderString() {
    return this.map_order.join(",");
  }
  has(key) {
    return this.map.has(key);
  }
  size() {
    return this.map_order.length;
  }
  match(value) {
    return this.init && this.source.id == value;
  }
  is_empty() {
    if (this.size() == 0) return true;
      else return false;
  }
  remove(key, id) {
    if (this.map.has(key)) {
      this.map.delete(key);
      const ind = this.map_order.indexOf(key);
      this.map_order.splice(ind, 1);
      if (typeof id !== 'undefined') this.map_remove.push([key,id]);
    }
  }
  get_wl_flag(key) {
    if (this.map_WL.has(key)) {
      return this.map_WL.get(key);
    }
    else {
      return null;
    }
  }
  append(key, value=new Array(), wl_flag=null) {
    if (!this.map.has(key)) {
      this.map.set(key, value);
      this.map_order.push(key);
      if (wl_flag) {
        this.map_WL.set(key, wl_flag);
      }
    }
  }
  clear() {
    this.map = new Map();
    this.map.set("order", new Array());
    this.map.set("remove", new Array());
    this.map.set("WL", new Map());
    this.map_order = this.map.get("order");
    this.map_remove = this.map.get("remove");
    this.map_WL = this.map.get("WL");
  }
  commit() {
    extStorage.setItem(this.source.id, JSON.stringify(arrayifyMap(this.map)));
  }
  
}
