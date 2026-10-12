import copy

_T = {"python_tags": ["cp311", "py3"], "abi_tags": ["cp311", "none"], "platforms": ["manylinux_2_17_x86_64", "any"]}


def test_parse_requirements_basic():
    """parse_requirements() reads pins and hashes, normalizing names"""
    reqs, problems = parse_requirements("Foo_Bar==1.0 --hash=sha256:bb --hash=sha256:aa\n")
    assert problems == [], f"expected no problems, got {problems!r}"
    assert reqs == {"foo-bar": {"version": "1.0", "hashes": ["sha256:aa", "sha256:bb"]}}, f"got {reqs!r}"


def test_parse_requirements_continuations_and_comments():
    """parse_requirements() joins backslash continuations and ignores comments and blank lines"""
    text = "# header\n\nalpha==2.0 \\\n    --hash=sha256:a1 \\\n    --hash=sha256:a2  # pinned by ops\n"
    reqs, problems = parse_requirements(text)
    assert reqs == {"alpha": {"version": "2.0", "hashes": ["sha256:a1", "sha256:a2"]}}, f"got {reqs!r}"
    assert problems == [], f"got {problems!r}"


def test_parse_requirements_problems():
    """parse_requirements() reports unpinned and unhashed requirements and leaves them out"""
    reqs, problems = parse_requirements("idna>=3.7\nbeta==1.0\ngamma~=2.1 --hash=sha256:cc\n")
    assert reqs == {}, f"unpinned or unhashed requirements are not in reqs, got {reqs!r}"
    assert problems == ["idna: not pinned with ==", "beta: no hashes", "gamma: not pinned with =="], f"got {problems!r}"


def test_parse_wheel():
    """parse_wheel() splits name, version, python, abi and platform (with or without a build tag)"""
    got = parse_wheel("pydantic_core-2.30.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl")
    assert got == {"name": "pydantic-core", "version": "2.30.1", "python": "cp311", "abi": "cp311",
                   "platform": "manylinux_2_17_x86_64.manylinux2014_x86_64"}, f"got {got!r}"
    built = parse_wheel("thing-1.0-1build-py3-none-any.whl")
    assert built is not None and built["version"] == "1.0" and built["python"] == "py3", f"build tag wheels have 6 parts, got {built!r}"
    for bad in ["thing-1.0.tar.gz", "thing-1.0-py3.whl"]:
        try:
            parse_wheel(bad)
        except ValueError:
            continue
        assert False, f"parse_wheel({bad!r}) should raise ValueError"


def test_compatible():
    """compatible() needs a matching python, abi and platform tag (any of the dotted ones)"""
    def w(py, abi, plat):
        return {"name": "x", "version": "1", "python": py, "abi": abi, "platform": plat}
    assert compatible(w("py3", "none", "any"), _T) is True, "a py3-none-any wheel fits every target"
    assert compatible(w("py2.py3", "none", "any"), _T) is True, "py2.py3 includes py3"
    assert compatible(w("cp311", "cp311", "manylinux_2_28_x86_64.manylinux_2_17_x86_64"), _T) is True, "any one dotted platform tag is enough"
    assert compatible(w("cp312", "cp312", "manylinux_2_17_x86_64"), _T) is False, "wrong Python version"
    assert compatible(w("cp311", "cp311", "macosx_14_0_arm64"), _T) is False, "built on a Mac laptop"


def _wh(*pairs):
    return [{"file": f, "sha256": h} for f, h in pairs]


def test_plan_happy_path():
    """plan() picks the hashed, compatible wheel and reports ready"""
    text = "alpha==1.0 --hash=sha256:aa\nbeta-pkg==2.0 --hash=sha256:b1 --hash=sha256:b2\n"
    wh = _wh(("alpha-1.0-py3-none-any.whl", "aa"),
             ("beta_pkg-2.0-cp312-cp312-manylinux_2_17_x86_64.whl", "b1"),
             ("beta_pkg-2.0-cp311-cp311-manylinux_2_17_x86_64.whl", "b2"))
    got = plan(text, wh, _T)
    assert got is not None, "plan returned None"
    assert got["install"] == [{"name": "alpha", "file": "alpha-1.0-py3-none-any.whl"},
                              {"name": "beta-pkg", "file": "beta_pkg-2.0-cp311-cp311-manylinux_2_17_x86_64.whl"}], f"got {got['install']!r}"
    assert got["ready"] is True, f"everything resolved, so ready should be True: {got!r}"
    assert got["extra"] == [], f"got {got['extra']!r}"


def test_plan_each_failure():
    """plan() sorts requirements into missing, wrong_version, incompatible and hash_mismatch"""
    text = ("a==1.0 --hash=sha256:a1\nb==2.0 --hash=sha256:b1\nc==3.0 --hash=sha256:c1\n"
            "d==4.0 --hash=sha256:d1\nloose>=1\n")
    wh = _wh(("b-1.9-py3-none-any.whl", "b1"), ("b-1.8-py3-none-any.whl", "b0"),
             ("c-3.0-cp311-cp311-win_amd64.whl", "c1"),
             ("d-4.0-py3-none-any.whl", "ffff"),
             ("loose-1.2-py3-none-any.whl", "11"), ("zzz-0.1-py3-none-any.whl", "22"))
    got = plan(text, wh, _T)
    assert got["missing"] == ["a"], f"got {got['missing']!r}"
    assert got["wrong_version"] == ["b==2.0 (wheelhouse has 1.8, 1.9)"], f"got {got['wrong_version']!r}"
    assert got["incompatible"] == ["c"], f"got {got['incompatible']!r}"
    assert got["hash_mismatch"] == ["d"], f"got {got['hash_mismatch']!r}"
    assert got["problems"] == ["loose: not pinned with =="], f"got {got['problems']!r}"
    assert got["extra"] == ["zzz-0.1-py3-none-any.whl"], f"wheels for packages nobody asked for are extra (loose is asked for), got {got['extra']!r}"
    assert got["install"] == [] and got["ready"] is False, f"got install={got['install']!r} ready={got['ready']!r}"


def test_plan_demo_data():
    """On the demo data, three packages install and five things block"""
    before = copy.deepcopy(WHEELHOUSE)
    got = plan(REQUIREMENTS, WHEELHOUSE, TARGET)
    assert [i["name"] for i in got["install"]] == ["anthropic", "httpx2", "pydantic-core"], f"got {got['install']!r}"
    assert (got["missing"], got["incompatible"], got["hash_mismatch"]) == (["sniffio"], ["numpy"], ["certifi"]), f"got {got!r}"
    assert WHEELHOUSE == before, "don't modify the wheelhouse list"
