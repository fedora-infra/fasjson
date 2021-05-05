import math

from flask import current_app, request
from flask_restx import marshal, reqparse

page_request_parser = reqparse.RequestParser()
page_request_parser.add_argument("page_size", type=int, help="Page size.")
page_request_parser.add_argument(
    "page_number", type=int, default=1, help="Page number."
)


def add_page_data(output, result, model):
    """Use the pagination data from the LDAP result to add page info to the output.

    This function adds a dictionary with pagination info in a ``page`` key in the output dictionary.
    The pagination dictionary contains:

      * ``page_number``: the current page number
      * ``page_size``: the number of items per page
      * ``total_results``: the total number of items in the entire recordset
      * ``total_pages``: the number of pages available
      * ``next_page``: the URL to the next page if there is one. On the last page, this key
        is absent.

    If the query was not paginated, this ``page`` dictionary is not added to the output dictionary.

    This function does not return anything, the output dictionary is modified in-place.
    """
    if not result.page_size:
        return
    total_pages = math.ceil(result.total / result.page_size)
    output["page"] = {
        "total_results": result.total,
        "page_size": result.page_size,
        "page_number": result.page_number,
        "total_pages": total_pages,
    }
    if result.page_number < total_pages:
        qs = {
            "page_size": result.page_size,
            "page_number": result.page_number + 1,
        }
        qs = "&".join(f"{k}={v}" for k, v in qs.items())
        base_url = request.base_url
        output["page"]["next_page"] = f"{base_url}?{qs}"


def paged_marshal(result, model, **kwargs):
    if kwargs.get("mask") is None:
        mask_header = current_app.config["RESTX_MASK_HEADER"]
        kwargs["mask"] = request.headers.get(mask_header)
    output = marshal(result.items, model, envelope="result", **kwargs)
    add_page_data(output, result, model)
    return output
