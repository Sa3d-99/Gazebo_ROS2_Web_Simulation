# CI/CD: test and publish both Ubuntu editions

[Open the workflow](https://github.com/Sa3d-99/Gazebo_ROS2_Web_Simulation/actions/workflows/ci-cd.yml).

The pipeline publishes container images to GitHub Container Registry (GHCR) and,
when its token is configured, Docker Hub. Cloud servers and Pods are managed
through the deployment steps in the README.

## What runs automatically

| Event | Checks and container tests | Publication |
|---|---|---|
| Pull request | Both Ubuntu runner versions; container changes test both images | None; no registry login or publishing token |
| Push to `main` | Same checks; container changes test both images | GHCR, plus Docker Hub when configured, for container changes |
| Push a tag such as `v1.0.0` | Same checks and both container editions | Versioned release tags |
| Manual run | Same checks and both container editions | Choose with the `publish` input; publishing is limited to `main` |

1. **Scope and checks:** compare the complete pushed range or PR base with the
   tested commit, parse every Bash script, lint workflow definitions, validate
   documentation commands/links and run the unit tests on Ubuntu 22.04 and 24.04.
2. **Build and test:** independently build Humble/Fortress on Ubuntu 22.04 and
   Jazzy/Harmonic on Ubuntu 24.04. Each image runs the existing 19-check suite,
   including a rendered noVNC desktop, simulation progress, offline startup,
   authentication, persistence, restart, failure detection and shutdown.
3. **Stage:** on trusted publishing events, save each successful image on GHCR
   under its commit tag. A failed edition blocks release promotion for both.
4. **Publish:** only after both image jobs and all checks pass, promote the
   tested registry digests. The publication job does not rebuild images.
5. **CI result:** one final status verifies that the expected jobs succeeded.
   This is the check to require in a branch ruleset if you enable one.

Pull-request jobs have read-only repository permissions and receive no publishing
secrets. Actions are pinned to verified release commit SHAs. Runs on `main` are
serialized; an older rerun cannot move the main-branch release tags backward.

Documentation-only changes run the script, unit and documentation checks and
skip image builds/publication. Unknown source paths and workflow changes trigger
the full image pipeline. Tags and manual runs always test both editions. If the
base revision cannot be compared, the pipeline conservatively builds both.

Docker builds pin `ros2-apt-source` to release `1.3.0` through the
`ROS_APT_SOURCE_VERSION` build argument. This avoids unauthenticated GitHub
`releases/latest` requests from shared runners. Update that build argument when
adopting a newer repository-bootstrap release; ROS/Gazebo apt packages are still
installed from their configured repositories. Direct non-Docker installation
keeps automatic release lookup unless that environment variable is set.

## Enable Docker Hub publication once

GHCR works with GitHub's built-in `GITHUB_TOKEN`; no additional secret is needed.
For Docker Hub:

1. Sign in to Docker Hub as `sa3d99`.
2. Create a [personal access token](https://docs.docker.com/security/access-tokens/)
   with **Read & Write** repository permission.
3. Open the GitHub repository → **Settings → Secrets and variables → Actions**.
4. Choose **New repository secret**. Name it **`DOCKERHUB_TOKEN`** and paste the
   token into its value. Save it; keep the token out of source files and chat.
5. The username defaults to `sa3d99`. If needed, set the repository **variable**
   `DOCKERHUB_USERNAME` to a different namespace you own.
6. Push to `main`, or manually run **CI / CD** on `main` with `publish` enabled.

Without that secret, GHCR still publishes and the release summary explicitly
reports that Docker Hub was skipped. When the token exists, Docker Hub login
or push failures fail the publication job.

## Image tags

| Registry | Ubuntu 22.04 | Ubuntu 24.04 |
|---|---|---|
| GHCR moving tags | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu22.04:latest` and `:humble` | `ghcr.io/sa3d-99/gazebo-ros2-web-ubuntu24.04:latest` and `:jazzy` |
| Docker Hub moving tags | `sa3d99/gazebo-ros2-web:ubuntu22.04` and `:humble` | `sa3d99/gazebo-ros2-web:ubuntu24.04` and `:jazzy` |

Every published edition has a commit tag: GHCR uses `sha-<full-commit>`, and
Docker Hub uses `ubuntu22.04-sha-<full-commit>` or `ubuntu24.04-sha-<full-commit>`.
These are useful source references. Pin the digest shown in the job summary
when you need an exact image; a rebuild can fetch newer system packages.

A Git tag `v1.0.0` produces GHCR `:v1.0.0` and Docker Hub
`:ubuntu22.04-v1.0.0` / `:ubuntu24.04-v1.0.0`. Release-tag builds preserve the
moving `latest`, ROS and Ubuntu tags established by `main`.

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Run or troubleshoot the pipeline

1. Open the repository's **Actions → CI / CD** page.
2. Choose a run and inspect **checks**, the two image jobs and **publish**.
3. For a manual run, choose **Run workflow**, select `main`, and set `publish`.
4. For tests without publication, turn `publish` off. Manual runs on other
   branches also run tests without publishing.
5. Check the release summary for the image digest and Docker Hub status.

Test JSON and desktop screenshots are uploaded as small artifacts for **one
day**. No image tarballs or persistent Docker build caches are uploaded.
Container jobs use disposable hosted runners, and local development does not
need to download images to edit or validate this pipeline.

To investigate a failed run, use its logs and smoke artifact. Both images must
pass before stable tags update. After a publication-only failure, rerun the
failed jobs; they reuse the tested commit-tag images from GHCR.

Workflow source: [ci-cd.yml](../.github/workflows/ci-cd.yml).
Shared container test action: [build-test](../.github/actions/build-test/action.yml).
Sources: [GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token),
[registry digest promotion](https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/).
