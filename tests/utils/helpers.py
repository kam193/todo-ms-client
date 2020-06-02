def match_body(expected_json: dict):
    def _matcher(request):
        return request.json() == expected_json

    return _matcher
