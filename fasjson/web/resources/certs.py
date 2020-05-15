from flask_restx import Resource, fields, reqparse
from python_freeipa.exceptions import BadRequest

from fasjson.web.utils.ipa import rpc_client
from .base import Namespace


api_v1 = Namespace("certs", description="Certificates related operations")


class Base64Dict(fields.String):
    """IPA returns this weird structure in certificate chains"""

    def output(self, key, obj, ordered=False, **kwargs):
        return super().output("__base64__", obj, ordered=ordered, **kwargs)


CertModel = api_v1.model(
    "Cert",
    {
        "cacn": fields.String(),
        "certificate": fields.String(),
        "certificate_chain": fields.List(Base64Dict()),
        "issuer": fields.String(),
        "revoked": fields.Boolean(),
        "san_other": fields.List(fields.String()),
        "san_other_kpn": fields.List(fields.String()),
        "san_other_upn": fields.List(fields.String()),
        "serial_number": fields.Integer(),
        "serial_number_hex": fields.String(),
        "sha1_fingerprint": fields.String(),
        "sha256_fingerprint": fields.String(),
        "subject": fields.String(),
        "valid_not_after": fields.DateTime(dt_format="rfc822"),
        "valid_not_before": fields.DateTime(dt_format="rfc822"),
        "uri": fields.Url("v1.certs_cert", absolute=True),
    },
)


create_request_parser = reqparse.RequestParser()
create_request_parser.add_argument("user", required=True, help="User name.")
create_request_parser.add_argument(
    "csr", required=True, help="Certificate Signing Request."
)


@api_v1.route("/")
@api_v1.response(400, "The CSR could not be signed")
class Certs(Resource):
    @api_v1.doc("sign_csr")
    @api_v1.expect(create_request_parser)
    @api_v1.marshal_with(CertModel)
    def post(self):
        """Send a CSR and get a signed certificate in return"""
        args = create_request_parser.parse_args()
        client = rpc_client()
        result = client.cert_request(args["csr"], args["user"])
        return result["result"]


@api_v1.route("/<int:serial_number>/")
@api_v1.param("serial_number", "The certificate's serial number")
@api_v1.response(404, "Certificate not found")
class Cert(Resource):
    @api_v1.doc("get_cert")
    @api_v1.marshal_with(CertModel)
    def get(self, serial_number):
        """Fetch a certificate given its serial number

        Certificates are also present on users' results, but this method gives more details.
        """
        client = rpc_client()
        try:
            result = client.cert_show(serial_number)
        except BadRequest as e:
            if e.code == 4301:
                api_v1.abort(
                    404,
                    "Certificate not found",
                    serial_number=serial_number,
                    server_message=e.message,
                )
            else:
                raise
        return result["result"]
