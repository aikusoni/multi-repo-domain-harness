"""Allowlisted local control-plane spans, without prompt/output or reasoning text."""

from datetime import datetime, timezone
import math
import secrets

NAMES = {"request", "approval", "execution", "cancellation", "verification", "recovery"}
OUTCOMES = {"accepted", "approved", "rejected", "running", "finished", "failed", "interrupted", "timed_out",
            "requested", "prepared", "discarded", "PASS", "FAIL", "PARTIAL", "NOT_RUN"}


def record(job, name, outcome, duration_ms=None):
    if name not in NAMES or outcome not in OUTCOMES:
        raise ValueError("Unknown trace event")
    trace = job.setdefault("trace", {"trace_id": "trace-" + secrets.token_hex(16), "spans": []})
    span = {"span_id": "span-" + secrets.token_hex(8),
            "parent_span_id": trace["spans"][0]["span_id"] if trace["spans"] else None,
            "name": name, "outcome": outcome,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
    if duration_ms is not None:
        if not math.isfinite(duration_ms) or duration_ms < 0:
            raise ValueError("Invalid trace duration")
        span["duration_ms"] = round(duration_ms, 3)
    trace["spans"].append(span)


def project(job):
    trace = job.get("trace")
    if not trace:
        return {"available": False, "reason": "not_collected"}
    spans = []
    for span in trace["spans"]:
        if span.get("name") not in NAMES or span.get("outcome") not in OUTCOMES:
            continue
        spans.append({k: span[k] for k in ("span_id", "parent_span_id", "name", "outcome", "at", "duration_ms") if k in span})
    return {"available": True, "trace_id": trace["trace_id"], "spans": spans,
            "metrics": {"duration_ms": job.get("duration_ms"), "exit_code": job.get("exit_code"),
                        "output_truncated": job.get("output_truncated"),
                        "verification": job.get("verification", {}).get("status", "NOT_RUN")},
            "scope": "room-control-plane; no model tokens, tool spans or reasoning collected"}
