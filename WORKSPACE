workspace(name = "sebgoa_kkcd")

git_repository(
    name = "io_bazel_rules_docker",
    commit = "d5f7eb48234a2d03b757b930092c56ceda94fca2",
    remote = "https://github.com/bazelbuild/rules_docker.git",
)

load(
    "@io_bazel_rules_docker//python:image.bzl",
    _py_image_repos = "repositories",
)

load(
    "@io_bazel_rules_docker//container:container.bzl",
    "container_push",
)

_py_image_repos()

git_repository(
    name = "io_bazel_rules_python",
    commit = "c208292d1286e9a0280555187caf66cd3b4f5bed",
    remote = "https://github.com/bazelbuild/rules_python.git",
)

load(
    "@io_bazel_rules_python//python:pip.bzl",
    "pip_import",
    "pip_repositories",
)

pip_repositories()

pip_import(
    name = "kkcd_pip",
    requirements = "//:requirements.txt",
)

load(
    "@kkcd_pip//:requirements.bzl",
    _pip_install = "pip_install",
)

_pip_install()
