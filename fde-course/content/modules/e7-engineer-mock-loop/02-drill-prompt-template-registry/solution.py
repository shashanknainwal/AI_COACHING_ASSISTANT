import re

PLACEHOLDER = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


def bucket(user_id):
    """The split bucket for a user: the sum of character codes, mod 100."""
    return sum(ord(c) for c in user_id) % 100


class TemplateRegistry:
    """A prompt-template registry. Timestamps only ever increase between calls."""

    def __init__(self):
        # name -> {"versions": [body, ...], "tags": set, "uses": int}
        self.templates = {}
        # name -> [(time, active_version, split_or_None)]: one entry per config change
        self.timeline = {}

    # --- shared helpers -------------------------------------------------
    def _config(self, name):
        """The current (active_version, split) for a template."""
        _, active, split = self.timeline[name][-1]
        return active, split

    def _record(self, time, name, active, split):
        self.timeline.setdefault(name, []).append((time, active, split))

    def _body(self, name, version):
        versions = self.templates[name]["versions"]
        if version is None:
            version = self._config(name)[0]
        if not isinstance(version, int) or not 1 <= version <= len(versions):
            return None
        return versions[version - 1]

    @staticmethod
    def _pick(active, split, user_id):
        if not split:
            return active
        b = bucket(user_id)
        upper = 0
        for version in sorted(split):
            upper += split[version]
            if b < upper:
                return version
        return active  # unreachable when the split sums to 100

    # --- level 1 --------------------------------------------------------
    def add_version(self, timestamp, name, body):
        tpl = self.templates.setdefault(name, {"versions": [], "tags": set(), "uses": 0})
        tpl["versions"].append(body)
        version = len(tpl["versions"])
        split = self._config(name)[1] if name in self.timeline else None
        self._record(timestamp, name, version, split)
        return version

    def render(self, timestamp, name, variables, version=None):
        if name not in self.templates:
            return None
        body = self._body(name, version)
        if body is None:
            return None
        missing = sorted({v for v in PLACEHOLDER.findall(body) if v not in variables})
        if missing:
            return "error: missing " + ",".join(missing)
        self.templates[name]["uses"] += 1
        return PLACEHOLDER.sub(lambda m: str(variables[m.group(1)]), body)

    def get_variables(self, timestamp, name, version=None):
        if name not in self.templates:
            return None
        body = self._body(name, version)
        if body is None:
            return None
        return sorted(set(PLACEHOLDER.findall(body)))

    # --- level 2 --------------------------------------------------------
    def tag(self, timestamp, name, tags):
        if name not in self.templates:
            return False
        self.templates[name]["tags"].update(tags)
        return True

    def search(self, timestamp, tag, text):
        out = []
        for name in sorted(self.templates):
            tpl = self.templates[name]
            if tag and tag not in tpl["tags"]:
                continue
            if text.lower() not in self._body(name, None).lower():
                continue
            out.append(name)
        return out

    def top_used(self, timestamp, n):
        ranked = sorted(self.templates.items(), key=lambda kv: (-kv[1]["uses"], kv[0]))
        return [f"{name}({t['uses']})" for name, t in ranked if t["uses"] > 0][:n]

    # --- level 3 --------------------------------------------------------
    def set_split(self, timestamp, name, split):
        if name not in self.templates or not split:
            return False
        count = len(self.templates[name]["versions"])
        if any(not isinstance(v, int) or not 1 <= v <= count for v in split):
            return False
        if any(p < 0 for p in split.values()) or sum(split.values()) != 100:
            return False
        active, _ = self._config(name)
        self._record(timestamp, name, active, dict(split))
        return True

    def clear_split(self, timestamp, name):
        if name not in self.templates:
            return False
        active, split = self._config(name)
        if not split:
            return False
        self._record(timestamp, name, active, None)
        return True

    def assign(self, timestamp, name, user_id):
        if name not in self.templates:
            return None
        active, split = self._config(name)
        return self._pick(active, split, user_id)

    def render_for(self, timestamp, name, user_id, variables):
        version = self.assign(timestamp, name, user_id)
        if version is None:
            return None
        return self.render(timestamp, name, variables, version)

    # --- level 4 --------------------------------------------------------
    def rollback(self, timestamp, name, version):
        if name not in self.templates:
            return False
        if not isinstance(version, int) or not 1 <= version <= len(self.templates[name]["versions"]):
            return False
        self._record(timestamp, name, version, None)
        return True

    def version_at(self, timestamp, name, user_id, at):
        config = None
        for time, active, split in self.timeline.get(name, []):
            if time > at:
                break
            config = (active, split)
        if config is None:
            return None
        return self._pick(config[0], config[1], user_id)
