# kubecamp-app

This repository contains a sample Python Flask application, along with the various glue to mimic an end-to-end workflow for a containerized application to run in a production Kubernetes cluster, with support from a central platform organization.

The tooling utilized incldues:
* Python
* [Skaffold](https://skaffold.dev)
* [Kustomize](https://kustomize.io)
* [GitHub](https://github.com)
* [Cloud Build](https://cloud.google.com/build)
* [Secret Manager](https://cloud.google.com/secret-manager)
* [git](https://git-scm.com/)

It utilizes two additional repos:
* [kubecamp-env](https://github.com/agmsb/kubecamp-blueprints) for providing a separate environment focused repository around candidate Kubernetes manifests as well as applied Kubernetes manifests.
* [kubecamp-blueprints](https://github.com/agmsb/kubecamp-blueprints) for providing upstream Kubernetes manifests outside of an individual team's app repository.

The overall workflow is as follows:
* Developer will work in `kubecamp-app` repo on any branch that is not `main`, utilizing `skaffold dev` to iterate with a development Kubernetes cluster, either locally or in the cloud. 
  * `skaffold dev` will utilize Kustomize as a deployer, with base in `kubecamp-blueprints/team-a/resources` and applying `kubecamp-app/app/config` to generate a ConfigMap where they can change an environment variable.
* Once the developer is happy with the state of `kubecamp-app` they will push to remote on their feature branch. 
* This will trigger `kubecamp-app/builds/create-pr-main.yaml`, a Cloud Build that will run unit tests defined in `kubecamp-app/test_main.py`, triggered off of any push to a branch that is not `main`. _You will need to create the Cloud Build trigger yourself should you want to replicate this._
* Assuming tests pass, the developer can then merge their feature branch into `main`, ready to prepare their application to run in production. 
* This merge (_you will need to create the Cloud Build trigger yourself should you want to replicate this._) will trigger a Cloud Build defined in `kubecamp-app/builds/merge-into-main.yaml`, which will do two things:
  * It will run `skaffold render -p prod`, which will build, tag, and push the container images for `kubecamp-app`. Then it will render Kubernetes manifests in `resources.yaml` after utilizing the Kustomize stanza defined in the Skaffold Profile `prod` to pull from overlays that contain a new ConfigMap for production and will expose `kubecamp-app` via a LoadBalancer rather than ClusterIP. 
  * Then, it will run the `gcloud` container as a build step defined in `kubecamp-blueprints/shared/git`, which will take the rendered manifest, and push it to a candidate branch for `kubeecamp-env`, tagging the candidate branch with the `SHORT_SHA` from the commit in `kubecamp-app` that triggered this build. That way we can identify candidate manifests with the specific code changes made in the app repo. You will need to configure Secret Manager to use an SSH key you generated for your GitHub, customize `configure_git.sh` and then build a gcloud container using `build_git.yaml` with your custom script. 
* Once a candidate branch is opened in `kubecamp-env`, this will trigger a Cloud Build defined in `kubecamp-env/tests/integration_test.yaml`, which mocks automation for integration tests you may want to run in a pre-prod environment (it doesn't actually do this, rather demonstrates where you could do it). _You will need to create the Cloud Build trigger yourself should you want to replicate this._
* Finally, with integration tests passing, you can then merge your candidate branch into `main` for `kubecamp-env`, which will trigger the final Cloud Build defined in `deploy.yaml` This will use `skaffold apply` with your rendered manifests to your production Kubernetes cluster. _You will need to update this with your proper Kubernetes cluster_.

TODO 
* Add automated creation of build triggers.
* Add cluster creation instructions.
* Add IAM requirements.
* Add specific instructions for customizing `configure_git.sh`. 
* Add workflow diagram.
* Use Cloud Build support for integration with Secret Manager, rather than hacking it together.