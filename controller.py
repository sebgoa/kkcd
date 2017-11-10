#!/usr/bin/env python
"""A controller """

import json
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import logging
import os
import time
import httplib

DOMAIN = "bitnami.com"
VERSION = "v1"
PLURAL = "apps"

class App(object):
    def __init__(self, obj, token):
        self._obj = obj
        self._apiversion = obj["apiVersion"]
        self._kind = obj["kind"]
        self._metadata = obj["metadata"]
        self._spec = obj["spec"]
        self._repo = self._spec["repo"]
        self._token = token
        
    def crd_name(self):
        return self._metadata["name"]
    
    def token(self):
        return self._token
        
    def any_versions(self):
        return "name=" + self.crd_name()
        
    def cronjob(self, owner_refs):
        # in 1.8 batch/v1beta1 ? need to check how to handle version change in python client
        return {
                "apiVersion": "batch/v2alpha1",
                "kind": "CronJob",
                "metadata": {
                    "name": self.crd_name(),
                    "ownerReferences": owner_refs,
                    "labels": {
                        "name": self.crd_name(),
                    }
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
                                                            "name": self.token(),
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
                                                "repository": self._repo,
                                            },
                                        },
                                    ]
                                },
                            },
                        },
                    },
                },
            }

def main():
    config.load_incluster_config()
    #config.load_kube_config()

    apps_beta1 = client.AppsV1beta1Api()
    crds = client.CustomObjectsApi()
    v1 = client.CoreV1Api()
    batch = client.BatchV2alpha1Api()

    def create_meta(app):
        controller_ref = {
            "apiVersion": app._apiversion.rstrip("/v1"),
            "blockOwnerDeletion": True,
            "kind": app._kind,
            "name": app.crd_name(),
            "uid": app._metadata["uid"],
        }
        job = batch.create_namespaced_cron_job(namespace="default", body=app.cronjob([controller_ref]))
        logging.warning("Created CronJob for App: %s", job.metadata.name)
        logging.warning("Owner's reference: %s", json.dumps(controller_ref))
        
    def update_meta(app):
        try:
            create_meta(app)
        except ApiException as e:
            if e.status != httplib.CONFLICT:
                raise e

        # Tear down any versions that shouldn't exist.
        #delete_meta(app.other_versions())
        
    def delete_meta(selector):
        # Handle random namespace later...
        namespace = "default"
        for job in batch.list_namespaced_cron_job(
                namespace, label_selector=selector).items:
            batch.delete_namespaced_cron_job(
                job.metadata.name, namespace, body=client.V1DeleteOptions(
                    propagation_policy='Foreground', grace_period_seconds=5))
            logging.warning("Deleted the CronJob for: %s", job.metadata.name)

    def process_meta(t, app, obj):
        if t == "DELETED":
            delete_meta(app.any_versions())
            logging.warning("Deleted CRD, check garbage collection")
        elif t in ["MODIFIED", "ADDED"]:
            update_meta(app)
        else:
            logging.error("Unrecognized type: %s", t)

    # hack, using default namespace, default service account to get a token for kubecfg to work
    token = v1.read_namespaced_service_account(namespace="default",name="default").secrets[0].name
    resource_version = ""
    while True:
        stream = watch.Watch().stream(crds.list_cluster_custom_object,
                                      DOMAIN, VERSION, PLURAL,
                                      resource_version=resource_version)
        for event in stream:
            try:
                t = event["type"]
                obj = event["object"]
                print obj
                app = App(obj, token)
                logging.warning("Apps %s, %s" % (app.crd_name(),t))  
                process_meta(t, app, obj)

                # Configure where to resume streaming.
                metadata = obj.get("metadata")
                if metadata:
                    resource_version = metadata["resourceVersion"]
            except:
                logging.exception("Error handling event")

if __name__ == "__main__":
    main()
