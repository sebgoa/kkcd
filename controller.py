#!/usr/bin/env python
"""A controller """

import json
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import logging
import os
import time

DOMAIN = "bitnami.com"
VERSION = "v1"
PLURAL = "apps"

class App(object):
    def __init__(self, obj):
    def cronjob(self, owner_refs):
        return {
  "apiVersion": "batch/v2alpha1",
  "kind": "CronJob",
  "metadata": {
    "name": "cookie-app"
  },
  "spec": {
    "schedule": "*/1 * * * *",
    "jobTemplate": {
      "spec": {
        "template": {
          "spec": {
            "containers": [
              {
                "name": "app",
                "image": "bitnami/kubecfg:0.0.5",
                "workingDir": "/tmp/cookie/opencompose-jsonnet",
                "env": [
                  {
                    "name": "TOKEN",
                    "valueFrom": {
                      "secretKeyRef": {
                        "name": "default-token-rtw2m",
                        "key": "token"
                      }
                    }
                  }
                ],
                "command": [
                  "kubecfg"
                ],
                "args": [
                  "--certificate-authority",
                  "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
                  "--token",
                  "$(TOKEN)",
                  "--server",
                  "https://kubernetes:443",
                  "update",
                  "cookieapp-opencompose.jsonnet"
                ],
                "volumeMounts": [
                  {
                    "name": "cookie",
                    "mountPath": "/tmp/cookie"
                  }
                ]
              }
            ],
            "restartPolicy": "OnFailure",
            "volumes": [
              {
                "name": "cookie",
                "gitRepo": {
                  "repository": "https://github.com/sebgoa/opencompose-jsonnet"
                }
              }
            ]
          }
        }
      }
    }
  }
}

def main():
    """config.load_incluster.config()"""
    config.load_kube_config()

    apps_beta1 = client.AppsV1beta1Api()
    crds = client.CustomObjectsApi()

    def process_meta(t, app, obj):
        if t == "DELETED":
            delete_meta(app.any_versions())
        elif t in ["MODIFIED", "ADDED"]:
            update_meta(app)
        else:
            logging.error("Unrecognized type: %s", t)

    resource_version = ""
    while True:
        stream = watch.Watch().stream(crds.list_cluster_custom_object,
                                      DOMAIN, VERSION, PLURAL,
                                      resource_version=resource_version)
        for event in stream:
            try:
                t = event["type"]
                obj = event["object"]
                logging.warning("Apps %s" % t)                

                # Configure where to resume streaming.
                metadata = obj.get("metadata")
                if metadata:
                    resource_version = metadata["resourceVersion"]
            except:
                logging.exception("Error handling event")

if __name__ == "__main__":
    main()
