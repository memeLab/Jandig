import logging

import requests
from django.conf import settings

# The minimum score threshold to consider the action as legitimate.
BOT_SCORE = 0.6

logger = logging.getLogger(__name__)


def create_assessment(token: str, recaptcha_action: str):
    """Create an assessment to analyze the risk of a UI action.
    Args:
        project_id: Your Google Cloud Project ID.
        recaptcha_key: The reCAPTCHA key associated with the site/app
        token: The generated token obtained from the client.
        recaptcha_action: Action name corresponding to the token.
    """
    if not token:
        logger.error(
            "The token is missing. Recaptcha may be enabled but not configured correctly."
        )
        return

    payload = {
        "event": {
            "token": token,
            "expectedAction": recaptcha_action,
            "siteKey": settings.RECAPTCHA_SITE_KEY,
        }
    }

    response = requests.post(
        f"https://recaptchaenterprise.googleapis.com/v1/projects/{settings.RECAPTCHA_PROJECT_ID}/assessments?key={settings.RECAPTCHA_GCLOUD_API_KEY}",
        json=payload,
    )
    response_data = response.json()
    logger.info(response.json())

    # Check if the token is valid.
    if not response_data["tokenProperties"]["valid"]:
        logger.info(
            "The CreateAssessment call failed because the token was "
            + "invalid for the following reasons: "
            + str(response_data["tokenProperties"]["invalidReason"])
        )
        return {}

    # Check if the expected action was executed.
    if response_data["tokenProperties"]["action"] != recaptcha_action:
        logger.info(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s).
        # For more information on interpreting the assessment, see:
        # https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment

        for reason in response_data["riskAnalysis"].get("reasons", []):
            logger.info(reason)
        logger.info(
            "The reCAPTCHA score for this token is: "
            + str(response_data["riskAnalysis"]["score"])
        )
        # Get the assessment name (id). Use this to annotate the assessment.
        assessment_name = response_data["name"].split("/")[-1]
        logger.info(f"Assessment name: {assessment_name}")
    return response_data
