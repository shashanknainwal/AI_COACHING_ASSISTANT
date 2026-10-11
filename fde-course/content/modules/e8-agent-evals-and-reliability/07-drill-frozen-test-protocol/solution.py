import hashlib


class EvalLab:
    """Prompt hill-climbing with a dev split, a validation split and a frozen test split."""

    def __init__(self, case_ids):
        self.case_ids = list(case_ids)
        self.results = {}
        self.best = None
        self._history = []
        self._test_used_by = None
        self._frozen = self.fingerprint("test")

    # Level 1
    def split(self):
        out = {"dev": [], "val": [], "test": []}
        for cid in self.case_ids:
            b = int(hashlib.sha256(cid.encode()).hexdigest(), 16) % 100
            out["dev" if b < 60 else "val" if b < 80 else "test"].append(cid)
        return {k: sorted(v) for k, v in out.items()}

    def fingerprint(self, name):
        ids = self.split()[name]
        return hashlib.sha256("\n".join(ids).encode()).hexdigest()[:12]

    # Level 2
    def record(self, variant, results):
        self.results[variant] = dict(results)
        if self.best is None:
            self.best = variant
        return len(results)

    def _rate(self, variant, name):
        res = self.results.get(variant)
        if res is None:
            return None
        ids = [c for c in self.split()[name] if c in res]
        if not ids:
            return None
        return round(sum(1 for c in ids if res[c]) / len(ids), 3)

    def score(self, variant, name):
        if name == "test":
            raise PermissionError("test split is frozen; use final_test()")
        return self._rate(variant, name)

    # Level 3
    def propose(self, variant, parent, min_gain=0.02):
        dev_gain = round(self.score(variant, "dev") - self.score(parent, "dev"), 3)
        val_gain = round(self.score(variant, "val") - self.score(parent, "val"), 3)
        if dev_gain >= min_gain and val_gain >= 0:
            decision = "accept"
            self.best = variant
        elif dev_gain >= min_gain:
            decision = "overfit"
        else:
            decision = "reject"
        row = {"variant": variant, "parent": parent, "dev_gain": dev_gain, "val_gain": val_gain, "decision": decision}
        self._history.append(row)
        return row

    def history(self):
        return list(self._history)

    # Level 4
    def add_cases(self, ids):
        self.case_ids.extend(ids)

    def final_test(self, variant):
        if self._test_used_by is not None:
            return {"error": f"test split already used for {self._test_used_by}"}
        if self.fingerprint("test") != self._frozen:
            return {"error": "test split changed since it was frozen"}
        self._test_used_by = variant
        test = self._rate(variant, "test")
        dev = self._rate(variant, "dev")
        return {"variant": variant, "test": test, "dev": dev, "gap": round(dev - test, 3)}

    def saturated(self, variant, ceiling=0.95):
        return self.score(variant, "dev") >= ceiling and self.score(variant, "val") >= ceiling


# --- Try it out (not graded) ---
lab = EvalLab(CASE_IDS)
parts = lab.split()
if parts:
    print({k: len(v) for k, v in parts.items()}, "test fingerprint", lab.fingerprint("test"))
for name, res in RESULTS.items():
    lab.record(name, res)
print(lab.propose("v1-pasted-examples", "v0-baseline"))
print(lab.propose("v2-read-back-rule", "v0-baseline"))
print("best:", lab.best)
print(lab.final_test(lab.best))
print(lab.final_test("v1-pasted-examples"))
