import mariadb, re
from flask import Blueprint
from flask import render_template
from flask import current_app
from flask import request

from .db import get_db
from . import version

bp = Blueprint("ax_default", __name__, url_prefix=f"/{version.Configs.APP_NAME}")

@bp.route("/ax-up-error-msg/", methods=['POST'])
def ax_up_error_msg():
    result = request.get_json()
    current_app.logger.debug("Empfangene JavaScript-Meldungen: " + request.headers.get('Content-Type') + "; Remote-Addr=" + request.remote_addr + "; Method=" + request.method + "; Content-length=" + str(request.content_length) + "; Remote-User=" + str(request.remote_user))
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    if "alert" in result:
        for err_text in result["alert"]:
            current_app.logger.error("Javascript-Fehlermeldung: %s",err_text)
    if "init" in result:
        for err_text in result["init"]:
            current_app.logger.debug("Init-Meldung: %s",err_text)
    if "init_err" in result:
        for err_text in result["init_err"]:
            current_app.logger.error("Init-Error-Meldung: %s",err_text)
    return rc_code


def mx_get_overview(request, current_app, **kwargs):
    search_field = kwargs['search_field']
    sql = kwargs['sql']
    html_template = kwargs['html_template_body']
    primary="id"
    if "primary" in kwargs:
        primary=kwargs['primary']


    result_map = dict(request.get_json())
    rc_code = {"status":"OK", "contentlength":request.content_length, "contentype":request.content_type, "remoteaddr":request.remote_addr}
    overview_search = result_map["overview-search"]
    overview_page = int(result_map["overview-page"])
    overview_maxlines = int(current_app.config["max-line-overview"])
    overview_offset = (overview_page - 1) * overview_maxlines
    overview_readlines = overview_maxlines + 1

    sql_parms = ""
    if overview_search is not None and len(overview_search) > 0 and overview_search != "ALL":
        if re.match(r"[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}", overview_search):
            sql_parms = f"WHERE {search_field[0]}<='{overview_search}'"
        elif overview_search.isnumeric():
            sql_parms = f"WHERE a.{primary}={overview_search}"
        elif not overview_search.isspace():
            search_like = "'%" +  overview_search + "%'"
            sql_parms = f"WHERE {search_field[0]} like {search_like}"
            if len(search_field) > 1:
                sql_parms += f" or {search_field[1]} like {search_like}"

    dbdata={}
    try:
        db = get_db()
        if not db:
            raise mariadb.PoolError()
        cur = db.cursor(dictionary=True)
        is_more_lines = False

        cur.execute(f'{sql[0]} {sql_parms} {sql[1]} LIMIT {overview_offset}, {overview_readlines}')
        dbdata.update({"entries":cur.fetchall()})
        len_vis = len(dbdata["entries"])
        show_lines = len_vis
        if len_vis > overview_maxlines:
            show_lines = overview_maxlines
            is_more_lines = True
            
        rc_code["html"] = render_template(html_template, entries=dbdata["entries"][0:show_lines])
        rc_code["pagination"] = is_more_lines
        cur.close()
        db.close()
    except mariadb.Error as err:
        db.close()
        current_app.logger.error("Datenbank-Fehler: %s/%s", bp.name, err)
        rc_code["status"] = "ERR"

    return rc_code
