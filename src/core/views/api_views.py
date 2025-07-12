import base64
from io import BytesIO

from django.http import HttpResponse
from fast_html import img, render
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

    @staticmethod
    def generate_marker(image, inner_border=False):
        """
        Generate a marker from the provided image.
        :param image: PIL Image object
        :param inner_border: Boolean indicating if the white inner border should be applied
        :return: PIL Image object of the generated marker
        """
        try:
            transformed_image = generate_marker_from_image(
                image,
                black_border_percentage=BLACK_BORDER_PERCENTAGE,
                white_border_percentage=WHITE_BORDER_PERCENTAGE,
                inner_border_percentage=INNER_BORDER_PERCENTAGE if inner_border else 0,
            )
            return transformed_image
        except Exception as e:
            raise ValueError(f"Error generating marker: {str(e)}")

    def post(self, request, *args, **kwargs):
        if "source" not in request.FILES:
            return Response(
                {"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        inner_border = request.POST.get("inner_border", "false").lower() == "true"
        image = request.FILES["source"]
        pil_image = Image.open(image)
        try:
            # Process the image using Pymarker
            transformed_image = self.generate_marker(pil_image, inner_border)
            # Convert PIL image to base64
            in_mem_file = BytesIO()
            transformed_image.save(in_mem_file, format="PNG")
            # reset file pointer to start
            in_mem_file.seek(0)
            img_bytes = in_mem_file.read()

            base64_encoded_result_bytes = base64.b64encode(img_bytes)
            base64_encoded_result_str = base64_encoded_result_bytes.decode("ascii")

            # Create an HTML image tag with the base64 data
            transformed_image = f"data:image/jpeg;base64,{base64_encoded_result_str}"

            return HttpResponse(
                render(
                    img(
                        src=transformed_image,
                    )
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
