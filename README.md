# Kubernetes Continous Deployment via a Controller with a CRD

We want to keep all our k8s manifests under version control and have our CVS system be the only interaction point for our deployments in production.

People should just `git push` and review PR

Then the question comes, how do you deploy.

## kkcd

kkcd is a simple CRD based controller written in Python.
Once you create an App using a custom App object kind, the controller creates a CronJob with a gitRepo volume. The manifests repository is cloned by the git-repo volume and the CronJob runs `kubecfg update`

That's it.

Every time you git push, `kubecfg` will apply the updates in a declarative way.

The CRD is just a controller to use `kubectl` to manage your _apps_

## Build

Using Bazel, build the controller image

```
bazel build //:controller
```



