from healthcheck import HealthCheck


def healthz(config_key="HEALTHZ", pass_code=200, fail_code=503):
    return HealthCheck(
        config_key,
        name="healthz",
        import_name=__name__,
        pass_code=pass_code,
        fail_code=fail_code,
    )
