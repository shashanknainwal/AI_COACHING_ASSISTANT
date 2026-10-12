import unittest

from app import config
from app.costs import BudgetExceeded, CostMeter, cost_usd, usage_to_dict
from app.retrieval import BM25Index, chunk_markdown, recall_at_k, reciprocal_rank, tokenize, unique_docs


class RetrievalTests(unittest.TestCase):
    def test_tokenize_keeps_order_ids(self):
        self.assertIn("qf-1042", tokenize("Where is QF-1042?"))
        self.assertNotIn("the", tokenize("the order"))

    def test_chunks_carry_title(self):
        chunks = chunk_markdown("doc", "# Title\n\n## A\nalpha beta\n\n## B\ngamma")
        self.assertEqual(len(chunks), 2)
        self.assertTrue(all(c.text.startswith("Title.") for c in chunks))
        self.assertEqual(chunks[1].id, "doc#1")

    def test_bm25_ranks_the_matching_chunk_first(self):
        a = chunk_markdown("ship", "# Shipping\n\n## Express\nexpress shipping costs money")
        b = chunk_markdown("ret", "# Returns\n\n## Window\nreturn within 30 days")
        hits = BM25Index(a + b).search("express shipping", k=2)
        self.assertEqual(hits[0][0].doc_id, "ship")

    def test_recall_and_rr(self):
        self.assertEqual(recall_at_k(["a", "b", "c"], ["c"], 2), 0.0)
        self.assertEqual(recall_at_k(["a", "b", "c"], ["c"], 3), 1.0)
        self.assertEqual(recall_at_k(["a"], ["a", "z"], 5), 0.5)
        self.assertEqual(reciprocal_rank(["x", "y"], ["y"]), 0.5)
        self.assertEqual(reciprocal_rank(["x"], ["y"]), 0.0)
        self.assertEqual(unique_docs(["a#0", "a#1", "b#0"]), ["a", "b"])


class CostTests(unittest.TestCase):
    def test_sonnet_cost_with_cache(self):
        u = {"input_tokens": 1_000_000, "output_tokens": 100_000, "cache_creation_input_tokens": 0,
             "cache_read_input_tokens": 1_000_000, "thinking_tokens": 0}
        # $2 input + $1 output + $0.10 cache reads
        self.assertAlmostEqual(cost_usd(config.SONNET, u), 3.10)

    def test_haiku_long_prompt_price(self):
        short = usage_to_dict({"input_tokens": 100_000, "output_tokens": 0})
        long = usage_to_dict({"input_tokens": 100_001, "output_tokens": 0})
        self.assertAlmostEqual(cost_usd(config.HAIKU, short), 0.01)
        self.assertAlmostEqual(cost_usd(config.HAIKU, long), 100_001 * 0.50 / 1e6)

    def test_unknown_model_raises(self):
        with self.assertRaises(KeyError):
            cost_usd("claude-made-up", {"input_tokens": 1})

    def test_meter_enforces_budget(self):
        m = CostMeter(budget_usd=0.01)
        m.add(config.HAIKU, {"input_tokens": 1000, "output_tokens": 1000})
        with self.assertRaises(BudgetExceeded):
            m.add(config.OPUS, {"input_tokens": 10_000, "output_tokens": 10_000})


if __name__ == "__main__":
    unittest.main()
