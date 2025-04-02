#!python

import sys

from recurl import parse_context, WebTemplate

def accumulate_pages(template: WebTemplate, qty_per_page: int) -> list[dict]:
    """
    Iterate through the pages of a web template, accumulating the list together

    :param template: A web template instance
    :param qty_per_page: the number of records to expect on each page
    :return: An accumulated list of the page contents
    """
    accumulated = []
    keep_looking = True
    page = 0

    while keep_looking:
        res = template.request(url=template.request_url.params({"page": page}))
        res.raise_for_status()

        accumulated.extend(found := res.json())
        keep_looking = len(found) == qty_per_page

    return accumulated

def main(argument_list: list[str]) -> int:
    """
    Run the show
    :param argument_list: List of command line arguments provided

    :return: Status code to return to shell
    """
    if len(argument_list) < 2:
        print("Please supply a curl request as the only parameter!")
        return 1

    # Read the curl request from file
    template = parse_context(argument_list[1])

    # Fire that request directly
    res = template.send()

    # Execute the request with no changes
    res.raise_for_status()

    # Print the output
    print(res.content)

    # Iterate through each page
    all_data = accumulate_pages(template, 10)

    print(all_data)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
