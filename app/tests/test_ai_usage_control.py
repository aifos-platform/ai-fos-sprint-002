from app.services.ai_usage_control import (
    AIUsageControlService,
)


def _service(tmp_path):
    return AIUsageControlService(
        storage_root=tmp_path / "ai_usage"
    )


def test_default_policy_is_available(
    tmp_path,
):
    service = _service(tmp_path)

    policy = service.get_policy("acss")

    assert policy["organisation_id"] == "acss"
    assert policy["enabled"] is True

    assert (
        policy["monthly_token_allowance"]
        == service.DEFAULT_MONTHLY_TOKEN_ALLOWANCE
    )

    assert (
        policy["daily_token_allowance"]
        == service.DEFAULT_DAILY_TOKEN_ALLOWANCE
    )

    assert (
        policy["max_output_tokens_per_request"]
        == service.DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST
    )

    assert (
        policy["general_cfo_enabled"]
        is True
    )

    assert (
        policy["verified_cfo_reasoning_enabled"]
        is True
    )


def test_custom_policy_is_persisted(
    tmp_path,
):
    service = _service(tmp_path)

    saved = service.set_policy(
        organisation_id="ACSS",
        plan="professional",
        monthly_token_allowance=500_000,
        daily_token_allowance=75_000,
        max_output_tokens_per_request=2_500,
        general_cfo_enabled=True,
        verified_cfo_reasoning_enabled=True,
    )

    assert saved["organisation_id"] == "acss"
    assert saved["plan"] == "professional"

    assert (
        saved["monthly_token_allowance"]
        == 500_000
    )

    assert (
        saved["daily_token_allowance"]
        == 75_000
    )

    assert (
        saved["max_output_tokens_per_request"]
        == 2_500
    )

    reloaded = AIUsageControlService(
        storage_root=tmp_path / "ai_usage"
    )

    policy = reloaded.get_policy("acss")

    assert policy == saved


def test_disabled_ai_is_blocked(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        enabled=False,
    )

    result = service.authorize(
        organisation_id="acss",
        request_type="general_cfo",
    )

    assert result["allowed"] is False
    assert result["reason"] == "ai_disabled"


def test_general_cfo_can_be_disabled_separately(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        general_cfo_enabled=False,
        verified_cfo_reasoning_enabled=True,
    )

    general = service.authorize(
        organisation_id="acss",
        request_type="general_cfo",
    )

    verified = service.authorize(
        organisation_id="acss",
        request_type="verified_cfo_reasoning",
    )

    assert general["allowed"] is False
    assert (
        general["reason"]
        == "general_cfo_disabled"
    )

    assert verified["allowed"] is True


def test_verified_reasoning_can_be_disabled_separately(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        general_cfo_enabled=True,
        verified_cfo_reasoning_enabled=False,
    )

    verified = service.authorize(
        organisation_id="acss",
        request_type="verified_cfo_reasoning",
    )

    assert verified["allowed"] is False

    assert (
        verified["reason"]
        == "verified_cfo_reasoning_disabled"
    )


def test_record_usage_updates_summary(
    tmp_path,
):
    service = _service(tmp_path)

    entry = service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=100,
        output_tokens=25,
        total_tokens=125,
    )

    assert entry["organisation_id"] == "acss"
    assert entry["input_tokens"] == 100
    assert entry["output_tokens"] == 25
    assert entry["total_tokens"] == 125

    summary = service.get_usage_summary(
        "acss"
    )

    assert (
        summary["today"]["requests"]
        == 1
    )

    assert (
        summary["today"]["total_tokens"]
        == 125
    )

    assert (
        summary["month"]["requests"]
        == 1
    )

    assert (
        summary["month"]["total_tokens"]
        == 125
    )


def test_multiple_usage_entries_are_accumulated(
    tmp_path,
):
    service = _service(tmp_path)

    service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
    )

    service.record_usage(
        organisation_id="acss",
        request_type="verified_cfo_reasoning",
        model="test-model",
        input_tokens=300,
        output_tokens=80,
        total_tokens=380,
    )

    summary = service.get_usage_summary(
        "acss"
    )

    assert (
        summary["today"]["requests"]
        == 2
    )

    assert (
        summary["today"]["input_tokens"]
        == 400
    )

    assert (
        summary["today"]["output_tokens"]
        == 100
    )

    assert (
        summary["today"]["total_tokens"]
        == 500
    )


def test_usage_is_isolated_by_organization(
    tmp_path,
):
    service = _service(tmp_path)

    service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=100,
        output_tokens=20,
        total_tokens=120,
    )

    service.record_usage(
        organisation_id="naacss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=500,
        output_tokens=100,
        total_tokens=600,
    )

    acss = service.get_usage_summary(
        "acss"
    )

    naacss = service.get_usage_summary(
        "naacss"
    )

    assert (
        acss["month"]["total_tokens"]
        == 120
    )

    assert (
        naacss["month"]["total_tokens"]
        == 600
    )


def test_monthly_limit_blocks_new_openai_request(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        monthly_token_allowance=100,
        daily_token_allowance=1_000,
    )

    service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=80,
        output_tokens=20,
        total_tokens=100,
    )

    result = service.authorize(
        organisation_id="acss",
        request_type="general_cfo",
    )

    assert result["allowed"] is False

    assert (
        result["reason"]
        == "monthly_token_limit_reached"
    )


def test_daily_limit_blocks_new_openai_request(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        monthly_token_allowance=10_000,
        daily_token_allowance=100,
    )

    service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=75,
        output_tokens=25,
        total_tokens=100,
    )

    result = service.authorize(
        organisation_id="acss",
        request_type="general_cfo",
    )

    assert result["allowed"] is False

    assert (
        result["reason"]
        == "daily_token_limit_reached"
    )


def test_authorized_response_contains_output_cap(
    tmp_path,
):
    service = _service(tmp_path)

    service.set_policy(
        organisation_id="acss",
        max_output_tokens_per_request=2_000,
    )

    result = service.authorize(
        organisation_id="acss",
        request_type="general_cfo",
    )

    assert result["allowed"] is True

    assert (
        result["max_output_tokens"]
        == 2_000
    )


def test_negative_token_values_are_never_recorded(
    tmp_path,
):
    service = _service(tmp_path)

    entry = service.record_usage(
        organisation_id="acss",
        request_type="general_cfo",
        model="test-model",
        input_tokens=-10,
        output_tokens=-20,
        total_tokens=-30,
    )

    assert entry["input_tokens"] == 0
    assert entry["output_tokens"] == 0
    assert entry["total_tokens"] == 0