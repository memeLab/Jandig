from django.http import HttpResponse
from PIL import Image
from pymarker import (
    generate_marker_from_image,
)  # Assuming Pymarker is the correct import
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

BLACK_BORDER_PERCENTAGE = 20
WHITE_BORDER_PERCENTAGE = 3
INNER_BORDER_PERCENTAGE = 2


class MarkerGeneratorAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            return Response(
                {"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        inner_border = request.GET.get("inner_border", "false").lower() == "true"
        image = request.FILES["image"]
        pil_image = Image.open(image)
        try:
            # Process the image using Pymarker
            transformed_image = generate_marker_from_image(
                pil_image,
                black_border_percentage=BLACK_BORDER_PERCENTAGE,
                white_border_percentage=WHITE_BORDER_PERCENTAGE,
                inner_border_percentage=INNER_BORDER_PERCENTAGE if inner_border else 0,
            )  # Replace with actual processing method
            response = HttpResponse(content_type="image/png")
            transformed_image.save(response, "PNG")
            response["Content-Disposition"] = 'attachment; filename="marker.png"'
            return response
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
