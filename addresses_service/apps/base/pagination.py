from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class HalPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "_embedded": data,
                "_links": {
                    "self": self.request.build_absolute_uri(),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "page_size": self.get_page_size(self.request),
            }
        )
