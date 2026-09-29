import os

import pytest
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

pytestmark = pytest.mark.live


def test_official_sdk_quickstart(gateway_url):
    with TypeSafeClient(api_key=os.environ.get("GATEWAY_API_KEY") or "local", base_url=gateway_url) as client:
        response = client.system_one(
            state="Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. "
            "I'm losing sales. Please help ASAP.",
            questions={
                "department": Choice(
                    instructions="Which team should handle this",
                    criteria={
                        "billing": "Payment or subscription issues",
                        "technical": "Bugs or integration problems",
                        "sales": "Pricing or account questions",
                    },
                ),
                "frustration": Score(
                    instructions="How frustrated the customer appears",
                    criteria=["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
                ),
                "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
            },
        )
    answers = response.answers
    assert answers["department"].choice == "technical"
    assert 0 <= answers["frustration"].score <= 2
    assert answers["is_urgent"].noul > 0.5
