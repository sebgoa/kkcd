# Simple CD with a Kubernetes CronJob

We want to keep all our k8s manifests under version control and have our CVS system be the only interaction point for our deployments in production.

People should just `git push` and review PR

Then the question comes, how do you deploy.

## kkcd

kkcd is a simple CronJob with a gitRepo volume. The manifests repository is cloned by the git-repo volume and the CronJob runs `kubecfg update`

That's it.


