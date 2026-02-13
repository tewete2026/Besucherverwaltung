import mariadb
from flask import Blueprint
from flask import current_app
from flask import request

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
