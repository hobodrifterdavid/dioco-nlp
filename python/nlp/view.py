import json
import time

from flask import Blueprint, request, jsonify, current_app
from flask_basicauth import BasicAuth

from .utils import multi_process_ud, process_mb, process_pkuseg, process_pyThaiNLP, multi_process_jieba, addTranslitOnly
from .supported_languages import languages, UD_PIPE_PROCESSOR

bp = Blueprint('auth', __name__, url_prefix='/api')

print(languages['en'])

basic_auth = BasicAuth()

@bp.route("/nlp/", methods=['POST', 'GET'])
# @basic_auth.required
def endpoint_udpipe():
    """

    :return:
    """
    request_start_time = time.time()
    # current_app.logger.info("udpipe request start time: {}".format(request_start_time))
    json_data = request.get_json() or {}
    lang = json_data.get('lang')
    subtitles = json_data.get("subtitles")

    # Special tokenisers

    if (subtitles and lang == 'ja'):
        processed_subtitles = process_mb(subtitles)
        current_app.logger.info("Mecab request processing time: {}".format(time.time() - request_start_time))
        return jsonify({"is_success": True, 'lang': lang, "subtitles": processed_subtitles})

    if (subtitles and lang == 'zh-CN'):
        processed_subtitles = process_pkuseg(subtitles)
        current_app.logger.info("pkuseg request processing time: {}".format(time.time() - request_start_time))
        return jsonify({"is_success": True, 'lang': lang, "subtitles": processed_subtitles})

    if (subtitles and lang == 'zh-TW'):
        processed_subtitles = multi_process_jieba(subtitles)
        current_app.logger.info("jieba request processing time: {}".format(time.time() - request_start_time))
        return jsonify({"is_success": True, 'lang': lang, "subtitles": processed_subtitles})

    if (subtitles and lang == 'th'):
        processed_subtitles = process_pyThaiNLP(subtitles)
        current_app.logger.info("pyThai request processing time: {}".format(time.time() - request_start_time))
        return jsonify({"is_success": True, 'lang': lang, "subtitles": processed_subtitles})

    # Otherwise we are using UDPipe

    udpipe_lang = languages.get(lang)

    if (udpipe_lang and subtitles and udpipe_lang.get('processor') == UD_PIPE_PROCESSOR
            and udpipe_lang.get('model')):
        processed_subtitles = multi_process_ud(json_data.get('lang'), subtitles)
        current_app.logger.info("udpipe request processing time: {}".format(time.time() - request_start_time))
        return jsonify({"is_success": True, 'lang': lang, "subtitles": processed_subtitles})

    response = {"is_success": False, 'lang': lang, "errors": ["Invalid Request Format"]}
    # Return this in all cases if a model isn't available:
    response["errors"].append("No Model Found")
#     if udpipe_lang:
#         if udpipe_lang.get('processor') != UD_PIPE_PROCESSOR:
#             response["errors"].append("Invalid Language Processor")
#         if udpipe_lang.get('processor') == UD_PIPE_PROCESSOR and not udpipe_lang.get('model'):
#             response["errors"].append("No Model Found")
    return current_app.response_class(
            response=json.dumps(response),
            status=400,
            mimetype='application/json'
    )

@bp.route("/translit/", methods=['POST'])
# @basic_auth.required
def endpoint_pinyin():
    """

    :return:
    """
    json_data = request.get_json() or {}
    tokens = json_data.get("tokens")
    langCode_G = json_data.get("langCode_G")

    return jsonify(addTranslitOnly(tokens, langCode_G))