from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config
from importlib import import_module

try:
    AmazonAPI = import_module("amazon.paapi").AmazonAPI
except Exception:  # pragma: no cover - handled via API response
    AmazonAPI = None


class AmazonProductSearchAPIView(APIView):

    @staticmethod
    def _get_amazon_client(country: str = "US"):
        """
        Build AmazonAPI client from environment values.
        Supported env names:
        - ACCESS_KEY / AMAZON_ACCESS_KEY
        - AMAZON_SECRET_KEY (preferred) or SECRET_KEY (legacy)
        - PARTNER_TAG / AMAZON_PARTNER_TAG
        """
        if AmazonAPI is None:
            return None

        access_key = config("AMAZON_ACCESS_KEY", default=config("ACCESS_KEY", default="")).strip()
        secret_key = config("AMAZON_SECRET_KEY", default=config("SECRET_KEY", default="")).strip()
        partner_tag = config("AMAZON_PARTNER_TAG", default=config("PARTNER_TAG", default="")).strip()

        if not access_key or not secret_key or not partner_tag:
            return None

        return AmazonAPI(
            access_key=access_key,
            secret_key=secret_key,
            partner_tag=partner_tag,
            country=country,
        )

    @staticmethod
    def _serialize_item(item):
        images = getattr(item, "images", None)
        large_image = getattr(images, "large", None) if images else None

        return {
            "title": getattr(item, "title", None),
            "price": getattr(item, "price_and_currency", None),
            "image": large_image,
            "affiliate_link": getattr(item, "detail_page_url", None),
        }

    def get(self, request):
        keyword = request.GET.get("keyword", "").strip()
        if not keyword:
            return Response(
                {"status": False, "error": "keyword query param is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        country = request.GET.get("country", "US").strip().upper()
        limit = request.GET.get("limit", 5)

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return Response(
                {"status": False, "error": "limit must be a valid integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Keep response lightweight and avoid abusive queries.
        limit = max(1, min(limit, 20))

        if AmazonAPI is None:
            return Response(
                {
                    "status": False,
                    "error": "Amazon client package is not installed. Install amazon-paapi5.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        amazon = self._get_amazon_client(country=country)
        if amazon is None:
            return Response(
                {
                    "status": False,
                    "error": "Amazon API credentials are missing. Configure ACCESS_KEY, AMAZON_SECRET_KEY, and PARTNER_TAG in environment.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            products = amazon.search_items(keywords=keyword) or []
            results = [self._serialize_item(item) for item in products[:limit]]

            return Response({
                "status": True,
                "data": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }, status=status.HTTP_502_BAD_GATEWAY)