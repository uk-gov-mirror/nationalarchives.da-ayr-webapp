import datetime
import json
import logging
import os
from datetime import timezone
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")
sqs = boto3.client("sqs")

TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]
WORKER_QUEUE_URL = os.environ["WORKER_QUEUE_URL"]


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:

    run_id = require_text(event, "runId")
    series = require_text(event, "series")
    consignment_reference = require_text(
        event,
        "consignmentReference",
    )

    reason = event.get("reason", "Manual rerun")

    if not isinstance(reason, str):
        raise ValueError("reason must be a string")

    triggered_by = event.get("triggeredBy", "unknown")

    if not isinstance(triggered_by, str):
        raise ValueError("triggeredBy must be a string")

    files = get_files(
        run_id=run_id,
        consignment_reference=consignment_reference,
    )

    if not files:
        raise ValueError(
            f"No files found for consignment {consignment_reference}"
        )

    logger.info(
        "Found %s files for consignment %s",
        len(files),
        consignment_reference,
    )

    include_body_and_series = True
    include_consignment = True

    cleanup_result = prepare_consignment_rerun(
        series=series,
        consignment_reference=consignment_reference,
    )

    for file_item in files:
        payload = {
            "runId": run_id,
            "series": series,
            "reference": file_item["reference"],
            "consignmentReference": consignment_reference,
            "fileId": file_item["fileId"],
            "includeBodyAndSeries": include_body_and_series,
            "includeConsignment": include_consignment,
            "forceRerun": True,
        }

        record_rerun(
            run_id=run_id,
            consignment_reference=consignment_reference,
            reason=reason,
            triggered_by=triggered_by,
            file_count=len(files),
        )

        sqs.send_message(
            QueueUrl=WORKER_QUEUE_URL,
            MessageBody=json.dumps(payload),
        )

        include_body_and_series = False
        include_consignment = False

    logger.info(
        "Queued %s worker messages for %s",
        len(files),
        consignment_reference,
    )

    return {
        "consignmentReference": consignment_reference,
        "filesQueued": len(files),
        **cleanup_result,
    }


def get_files(
    run_id: str,
    consignment_reference: str,
) -> list[dict[str, str]]:

    pk = f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"

    items = []
    last_key = None

    while True:
        request = {
            "TableName": TRACKING_TABLE_NAME,
            "KeyConditionExpression": "PK = :pk",
            "ExpressionAttributeValues": {
                ":pk": {"S": pk},
            },
        }

        if last_key:
            request["ExclusiveStartKey"] = last_key

        response = dynamodb.query(**request)

        items.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")

        if not last_key:
            break

    results = []

    for item in items:
        if item.get("entityType", {}).get("S") != "FILE":
            continue

        results.append(
            {
                "reference": item["reference"]["S"],
                "fileId": item["fileId"]["S"],
            }
        )

    return results


def require_text(
    data: dict[str, Any],
    key: str,
) -> str:

    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip()


def record_rerun(
    run_id: str,
    consignment_reference: str,
    reason: str,
    triggered_by: str,
    file_count: int,
) -> None:

    now = utc_now_text()

    dynamodb.update_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}"},
            "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
        },
        UpdateExpression="""
            SET
                lastRerunAt = :now,
                lastRerunReason = :reason,
                lastRerunTriggeredBy = :triggered_by,
                lastRerunFileCount = :file_count,
                rerunType = :rerun_type,
                updatedAt = :now
            ADD
                rerunCount :one
        """,
        ExpressionAttributeValues={
            ":now": {"S": now},
            ":reason": {"S": reason},
            ":triggered_by": {"S": triggered_by},
            ":file_count": {"N": str(file_count)},
            ":rerun_type": {"S": "WORKER_REPROCESS"},
            ":one": {"N": "1"},
        },
    )


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


s3 = boto3.client("s3")

DDT_TEMP_CSV_BUCKET = os.environ["DDT_TEMP_CSV_BUCKET"]
STAGING_PREFIX = os.getenv("STAGING_PREFIX", "ayr-mds-staging")
OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "ayr-mds-output")


def prepare_consignment_rerun(
    series: str,
    consignment_reference: str,
) -> dict[str, int]:

    deleted_staging = delete_prefix(
        bucket=DDT_TEMP_CSV_BUCKET,
        prefix=join_s3_key(
            series,
            STAGING_PREFIX,
            consignment_reference,
        ),
    )

    deleted_output = delete_prefix(
        bucket=DDT_TEMP_CSV_BUCKET,
        prefix=join_s3_key(
            series,
            OUTPUT_PREFIX,
            consignment_reference,
        ),
    )

    logger.info(
        "Prepared consignment rerun. "
        "consignment=%s "
        "deleted_staging=%s "
        "deleted_output=%s",
        consignment_reference,
        deleted_staging,
        deleted_output,
    )

    return {
        "deletedStagingObjects": deleted_staging,
        "deletedOutputObjects": deleted_output,
    }


def delete_prefix(
    bucket: str,
    prefix: str,
) -> int:

    paginator = s3.get_paginator("list_objects_v2")

    deleted = 0

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=ensure_trailing_slash(prefix),
    ):
        keys = page.get("Contents", [])

        if not keys:
            continue

        objects = [{"Key": item["Key"]} for item in keys]

        s3.delete_objects(
            Bucket=bucket,
            Delete={"Objects": objects},
        )

        deleted += len(objects)

    return deleted


def ensure_trailing_slash(value: str) -> str:
    value = value.strip()
    return value if value.endswith("/") else f"{value}/"


def join_s3_key(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts if part)
