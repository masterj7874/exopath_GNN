from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.graph import Edge, GraphContractError, Node, load_schema, relation_message_pass, validate_edges


class GraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load_schema(ROOT / "schemas" / "typed_graph_schema.json")
        self.nodes = [Node("p1", "patient"), Node("x1", "exposure")]

    def test_pre_index_edge_is_valid(self) -> None:
        edges = [Edge("p1", "x1", "patient_has_exposure", date(2020, 1, 1), "source-v1")]
        validate_edges(self.nodes, edges, self.schema, date(2021, 1, 1))

    def test_post_index_edge_is_rejected(self) -> None:
        edges = [Edge("p1", "x1", "patient_has_exposure", date(2022, 1, 1), "source-v1")]
        with self.assertRaisesRegex(GraphContractError, "post-index"):
            validate_edges(self.nodes, edges, self.schema, date(2021, 1, 1))

    def test_outcome_derived_relation_is_rejected(self) -> None:
        nodes = [Node("c1", "biological_concept"), Node("p1", "patient")]
        edges = [Edge("c1", "p1", "outcome_derived_association", None, "outcomes")]
        with self.assertRaisesRegex(GraphContractError, "prohibited"):
            validate_edges(nodes, edges, self.schema, date(2021, 1, 1))

    def test_relation_message_pass(self) -> None:
        edges = [Edge("p1", "x1", "patient_has_exposure", date(2020, 1, 1), "source-v1")]
        output = relation_message_pass({"p1": (1.0, 2.0), "x1": (0.5, 0.5)}, edges, {"patient_has_exposure": 2.0})
        self.assertEqual(output["x1"], (2.5, 4.5))


if __name__ == "__main__":
    unittest.main()

