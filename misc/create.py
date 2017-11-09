#!/usr/bin/env python

import yaml
from kubernetes import client,config

config.load_kube_config()

crd = client.ApiextensionsV1beta1Api()

with open("app.yaml", 'r') as stream:
    body = yaml.load(stream)

res = crd.create_custom_resource_definition(body)
