"""Typed relation validation and a small deterministic message-passing primitive."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence


class GraphContractError(ValueError):
    """Raised when an edge violates schema, provenance or temporal rules."""


@dataclass(frozen=True)
class Node:
    node_id: str
    node_type: str


@dataclass(frozen=True)
class Edge:
    source_id: str
    target_id: str
    relation: str
    observed_at: date | None
    provenance: str


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_edges(
    nodes: Sequence[Node],
    edges: Sequence[Edge],
    schema: Mapping,
    index_date: date,
) -> None:
    node_map = {node.node_id: node for node in nodes}
    if len(node_map) != len(nodes):
        raise GraphContractError("node identifiers must be unique")
    allowed_node_types = set(schema["node_types"])
    if any(node.node_type not in allowed_node_types for node in nodes):
        raise GraphContractError("graph contains an unknown node type")

    rules = schema["relations"]
    for edge in edges:
        if edge.source_id not in node_map or edge.target_id not in node_map:
            raise GraphContractError("every edge endpoint must exist")
        if edge.relation not in rules:
            raise GraphContractError(f"unknown relation: {edge.relation}")
        rule = rules[edge.relation]
        if not rule.get("allowed_for_prediction", False):
            raise GraphContractError(f"relation is prohibited for prediction: {edge.relation}")
        if node_map[edge.source_id].node_type != rule["source"]:
            raise GraphContractError("relation source type does not match schema")
        if node_map[edge.target_id].node_type != rule["target"]:
            raise GraphContractError("relation target type does not match schema")
        if rule.get("provenance_required") and not edge.provenance.strip():
            raise GraphContractError("relation provenance is required")
        if rule.get("temporal_guard"):
            if edge.observed_at is None:
                raise GraphContractError("temporally guarded edges require observed_at")
            if edge.observed_at > index_date:
                raise GraphContractError("post-index edge rejected")


def relation_message_pass(
    features: Mapping[str, Sequence[float]],
    edges: Sequence[Edge],
    relation_weights: Mapping[str, float],
) -> dict[str, tuple[float, ...]]:
    """Mean-aggregate typed source messages into target vectors with a residual."""

    if not features:
        return {}
    dimensions = {len(vector) for vector in features.values()}
    if len(dimensions) != 1:
        raise GraphContractError("all node feature vectors must share one dimension")
    dimension = next(iter(dimensions))
    sums = {node_id: [0.0] * dimension for node_id in features}
    counts = {node_id: 0 for node_id in features}

    for edge in edges:
        if edge.source_id not in features or edge.target_id not in features:
            raise GraphContractError("message-passing edges require features at both endpoints")
        weight = float(relation_weights.get(edge.relation, 1.0))
        for index, value in enumerate(features[edge.source_id]):
            sums[edge.target_id][index] += weight * float(value)
        counts[edge.target_id] += 1

    output: dict[str, tuple[float, ...]] = {}
    for node_id, vector in features.items():
        if counts[node_id]:
            message = [value / counts[node_id] for value in sums[node_id]]
        else:
            message = [0.0] * dimension
        output[node_id] = tuple(float(base) + update for base, update in zip(vector, message))
    return output

