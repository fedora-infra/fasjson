from flask import Blueprint, jsonify, current_app


def response(result, code):
    data = {"code": code, "result": result}
    return jsonify(data)


class HealthCheck(Blueprint):
    def __init__(
        self, config_key=None, pass_code=200, fail_code=503, *args, **kwargs
    ):
        super(HealthCheck, self).__init__(*args, **kwargs)
        self.mountpoint = kwargs["name"] or "healthz"
        self.pass_code = pass_code
        self.fail_code = fail_code
        health_checks = current_app.config.get(config_key)
        if type(health_checks) is dict:
            for health_check_name, health_check in health_checks.items():
                self.add_check(health_check_name, health_check)

    def add_check(self, health_check_name, health_check):
        if callable(health_check):
            url = f"/{self.mountpoint}/{health_check_name}/"
            self.add_url_rule(
                rule=url,
                endpoint=health_check_name,
                view_func=lambda: self.run_check(health_check),
            )

    def run_check(self, health_check):
        try:
            passed, result = health_check()
            if passed:
                return response(result, self.pass_code)
            else:
                current_app.logger(
                    f"Health check {health_check.__name__} failed with error {result}"
                )
                return response(result, self.fail_code)
        except Exception as e:
            current_app.logger(
                f"Health check {health_check.__name__} hit exception {str(e)}"
            )
            raise HealthException(str(e), self.fail_code)


class HealthException(Exception):
    def __init__(self, result, code):
        self.result = result
        self.code = code

    def __str__(self):
        return f"Health check failed with exception {self.result} and code {self.code}"
