# Kubernetes Continous Deployment via a CRD Controller 

We want to keep all our k8s manifests under version control and have our _git_ system be the only interaction point for our deployments in production.

People should just `git push` and review PR

Then the question comes, how do you deploy.

## kkcd

kkcd is a simple CRD based controller written in Python, just for rapid prototyping.
Once you create an App using a custom App object kind, the controller creates a CronJob with a gitRepo volume. The manifests repository is cloned by the git-repo volume and the CronJob runs `kubecfg update`. _kubecfg_ is an improved `kubectl apply`.

That's it. See the original [blog post](https://medium.com/bitnami-perspectives/poor-mans-kubernetes-cd-with-a-cronjob-c444e4d2c8d3)

Every time you git push, `kubecfg` will apply the updates in a declarative way follwing the CronJob schedule.

The CRD is just a controller to use `kubectl` to manage your _apps_

## Installation

```
kubectl create -f https://raw.githubusercontent.com/sebgoa/kkcd/master/kkcd.yaml
```

This will create a CRD and launch a controller

Write an _App_

```
apiVersion: bitnami.com/v1
kind: App
metadata:
  name: cookie
spec:
  repo: https://github.com/sebgoa/opencompose-jsonnet
```

We can extend the spec and add the CronJob schedule in there.

Create this app and watch the CronJob being created and soon your app will be running

```
kubectl create -f example.yaml
kubectl get apps
kubectl get cronjobs
kubectl get pods
```


## Build

Using Bazel, build the controller image

```
bazel build :controller
```

push controller image to Docker hub

```
bazel run :push_controller
```

## Note

Code is largely inspired by [warm-image](https://github.com/mattmoor/warm-image)
