package(default_visibility = ["//visibility:public"])

load("@kkcd_pip//:requirements.bzl", "requirement")
load("@io_bazel_rules_docker//python:image.bzl", "py_image")
load("@io_bazel_rules_docker//container:container.bzl", "container_push")

py_image(
    name = "controller",
    srcs = ["controller.py"],
    main = "controller.py",
    deps = [requirement("kubernetes")],
)

container_push(
   name = "push_controller",
   image = ":controller",
   format = "Docker",
   registry = "index.docker.io",
   repository = "bitnami/kkcd-controller",
   tag = "latest",
)
