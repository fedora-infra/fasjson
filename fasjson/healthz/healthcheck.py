def response(result, code):
    data = {"code": code, "result": result}
    return data


class HealthCheck:
    def __init__(self, app, pass_code=200, fail_code=503):
        self.app = app
        self.pass_code = pass_code
        self.fail_code = fail_code

    def add_check(self, url, endpoint, check):
        self.app.add_url_rule(
            url, endpoint, view_func=lambda: self.run_check(check)
        )

    def run_check(self, check):
        try:
            passed, result = check()
            if passed:
                return response(result, self.pass_code)
            else:
                self.app.logger(
                    f"Health check {check.__name__} failed with error {result}"
                )
                return response(result, self.fail_code)
        except Exception as e:
            self.app.logger(
                f"Health check {check.__name__} hit exception {str(e)}"
            )
            return response(str(e), self.fail_code)
