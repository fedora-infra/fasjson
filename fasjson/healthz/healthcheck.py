from flask import Blueprint, jsonify


def response(result, code):
    data = {"code": code, "result": result}
    return jsonify(data)


class HealthCheck(Blueprint):
    def __init__(self, config_key, name, import_name, pass_code, fail_code):
        super(HealthCheck, self).__init__(name, import_name)
        self.config_key = config_key
        self.pass_code = pass_code
        self.fail_code = fail_code
        self.record(self._setup_endpoints)

    def _setup_endpoints(self, state):
        health_checks = state.app.config.get(self.config_key, {})
        for health_check_name, health_check in health_checks.items():
            self.add_check(health_check_name, health_check)

    def add_check(self, health_check_name, health_check):
        if callable(health_check):
            self.add_url_rule(
                rule=f"/{health_check_name}",
                endpoint=health_check_name,
                view_func=lambda: self.run_check(health_check),
            )
        else:
            raise Exception(
                "Health check provided does not seem to be a function."
            )

    def run_check(self, health_check):
        passed, result = health_check()
        if passed:
            return response(result, self.pass_code)
        else:
            return response(result, self.fail_code)


class HealthException(Exception):
    def __init__(self, result, code):
        self.result = result
        self.code = code

    def __str__(self):
        return f"Health check failed with exception {self.result} and code {self.code}"
