# Docker interview scenarios (15)

> **Verification status: NOT executed.** There is no Docker or container runtime in my build sandbox, so none of these commands were run by me.
> Answers come from established Docker behaviour; **run each "Lab" yourself on a machine with Docker and fix anything that differs on your version before teaching it.**
> Level: Fresher = 0-3 yrs, Experienced = 3+ yrs.

## D1 - Containers vs VMs  _(Fresher)_
**Interviewer:** What is a container, and how is it different from a VM?
**Strong answer:** A container is an ordinary process on the host kernel, isolated with **namespaces** (pid, net, mnt, uts, ipc, user) and limited with **cgroups** (CPU/memory), on a layered filesystem. A VM runs a full guest OS kernel on a hypervisor. So containers start fast and are light, but share the host kernel (weaker isolation). Docker Desktop on Mac/Windows runs Linux containers inside a hidden Linux VM.
**Follow-up:** Can a Windows container run on a Linux host? (No - needs the matching kernel.)
**Lab:** `docker run -d --name web nginx` then `docker top web` and, on a Linux host, `ps aux | grep nginx`.

## D2 - Image vs container, layers  _(Fresher)_
**Interviewer:** Image vs container? What are layers?
**Strong answer:** An image is a read-only stack of layers plus metadata; a container is a running instance with a thin **writable layer** on top (copy-on-write). Layers are shared and cached, so images pull/build faster. Data written in the writable layer disappears with the container.
**Lab:** `docker history nginx`, `docker image inspect nginx`, write a file in a container, remove the container, show it is gone.

## D3 - CMD vs ENTRYPOINT, exec vs shell form  _(Fresher/Experienced)_
**Interviewer:** CMD vs ENTRYPOINT? Why does my container take 10 seconds to stop?
**Strong answer:** ENTRYPOINT is the executable; CMD supplies default arguments (overridden by args after the image name; ENTRYPOINT is overridden only with `--entrypoint`). **Shell form** (`CMD npm start`) runs via `/bin/sh -c`, so the shell is PID 1 and may not forward SIGTERM; Docker waits the stop timeout (10 s default) then sends SIGKILL. Use **exec form** (`CMD ["node","server.js"]`) so the app is PID 1 and receives signals; use `--init` (tini) to reap zombies if needed.
**Lab:** build two images (shell vs exec form), time `docker stop` on each.

## D4 - Make a 1.2 GB image small  _(Experienced)_
**Interviewer:** Our image is 1.2 GB. How do you shrink it?
**Strong answer:** Multi-stage builds (build tools stay in the builder stage), a slim/distroless base, `.dockerignore`, install only runtime deps, clean caches **in the same RUN** (deleting in a later layer doesn't shrink earlier layers), fewer layers where sensible. Caveat: Alpine uses musl libc - can break some binaries/wheels.
**Lab:** `docker image ls`, `docker history --no-trunc <img>`; compare before/after.

## D5 - Builds always reinstall dependencies  _(Experienced)_
**Interviewer:** Every build takes 5 minutes reinstalling packages. Why, and how do you fix it?
**Strong answer:** Layer cache is invalidated at the first changed instruction. `COPY . .` before the install means any code change busts the cache. Copy only the dependency manifest first, install, *then* copy the code:
```
COPY package*.json ./
RUN npm ci
COPY . .
```
BuildKit cache mounts (`RUN --mount=type=cache,...`) help further.
**Lab:** change one source file and rebuild with both orderings; watch `CACHED` lines.

## D6 - Container exits immediately  _(Fresher)_
**Interviewer:** My container starts and exits. How do you debug?
**Strong answer:** A container lives only as long as its main (foreground) process. `docker ps -a` (status/exit code), `docker logs <c>`, `docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' <c>`. Exit codes: **0** finished normally, **1** app error, **137** SIGKILL (often OOM-kill or stop timeout), **139** segfault, **143** SIGTERM. Don't "fix" a service with `tail -f /dev/null`; run the real process in the foreground.
**Lab:** `docker run --name t alpine echo hi` -> exits 0; `docker run alpine sh -c 'exit 3'`; inspect both.

## D7 - Data persistence  _(Fresher)_
**Interviewer:** My database lost its data when the container was recreated.
**Strong answer:** Writable-layer data is ephemeral. Use a **named volume** (managed by Docker, best for databases), a **bind mount** (host path, good for dev), or **tmpfs** (memory only). Mount at the image's data directory (e.g. Postgres `/var/lib/postgresql/data`). Back up volumes; beware anonymous volumes piling up.
**Lab:** `docker volume create pg`, run postgres with `-v pg:/var/lib/postgresql/data`, create a table, remove and recreate the container, verify it persists.

## D8 - Container networking & "localhost" confusion  _(Fresher/Experienced)_
**Interviewer:** My app container can't reach the DB at `localhost:5432`.
**Strong answer:** Inside a container `localhost` is the container itself. Put both on a **user-defined bridge network** (Compose does this) and use the service name as hostname - user-defined networks have built-in DNS; the *default* bridge does not resolve names. `-p host:container` publishes a port; `EXPOSE` is only documentation. To reach the host from a container use `host.docker.internal` (Docker Desktop; on Linux add `--add-host=host.docker.internal:host-gateway`).
**Lab:** `docker network create app`, run two containers on it, `docker exec a ping b`; repeat on the default bridge and compare.

## D9 - Secrets in images  _(Experienced)_
**Interviewer:** A developer used `ARG`/`ENV` for an API key. Problem?
**Strong answer:** Build args and ENV values are recorded in image metadata/history (`docker history`) and anyone with the image can read them. Use BuildKit secret mounts (`RUN --mount=type=secret,id=...`) for build-time secrets and inject runtime secrets from the platform (ECS secrets from Secrets Manager/SSM, Kubernetes Secrets/external secrets). Never commit `.env`. If it leaked: rotate it.
**Lab:** build an image with `ARG TOKEN`, run `docker history --no-trunc` and find it; then redo with a secret mount.

## D10 - Hardening a container  _(Experienced)_
**Interviewer:** How do you secure containers in production?
**Strong answer:** Non-root `USER`; minimal base images; pin versions/digests; scan images (Trivy, ECR scanning); `--read-only` root filesystem; `--cap-drop=ALL` and add back only what's needed; `--security-opt no-new-privileges`; never `--privileged`; never mount `/var/run/docker.sock`; set CPU/memory limits; keep the host patched.
**Lab:** run a container with `--read-only --cap-drop=ALL --user 1000` and see what breaks.

## D11 - Compose: depends_on and startup order  _(Fresher/Experienced)_
**Interviewer:** `depends_on` is set but the app still crashes because the DB isn't ready.
**Strong answer:** Plain `depends_on` only controls start order, not readiness. Add a `healthcheck` on the DB and `depends_on: db: condition: service_healthy`; also make the app retry connections. Use `restart: unless-stopped` for resilience.
**Lab:** write a compose file with and without the healthcheck condition.

## D12 - OOMKilled  _(Experienced)_
**Interviewer:** A container keeps restarting with exit code 137.
**Strong answer:** 137 = 128 + 9 (SIGKILL). Check `docker inspect -f '{{.State.OOMKilled}}' <c>`. If true the cgroup memory limit was hit: raise `--memory`, fix leaks, and tune runtime heap settings to the limit (modern JVMs are container-aware; Node needs `--max-old-space-size` tuned). `docker stats` shows live usage.
**Lab:** `docker run --memory=50m` a process that allocates more; inspect the result.

## D13 - Disk full on the Docker host  _(Experienced)_
**Interviewer:** The build server's disk is 100% full. What do you check?
**Strong answer:** `docker system df` (images/containers/volumes/build cache). Clean with `docker system prune` (stopped containers, dangling images, unused networks, build cache as applicable); `-a` also removes unused images; **`--volumes` deletes data - be careful**. Container logs with the default `json-file` driver aren't rotated unless you set `--log-opt max-size=10m --log-opt max-file=3` (or use another driver).
**Lab:** `docker system df -v`; `docker builder prune`.

## D14 - Tagging strategy  _(Experienced)_
**Interviewer:** Why is deploying `:latest` a bad idea?
**Strong answer:** Tags are mutable pointers; `latest` is just a default tag, so you can't tell what is running or roll back reliably. Use immutable version tags (git SHA / semver) or pin the image **digest**; enable tag immutability in ECR; keep the SHA in release notes.
**Lab:** `docker pull nginx:1.27` vs `docker inspect --format '{{index .RepoDigests 0}}' nginx:1.27`.

## D15 - Docker vs Kubernetes runtime  _(Experienced)_
**Interviewer:** "Kubernetes dropped Docker" - what does that mean for our images?
**Strong answer:** Kubernetes removed **dockershim** (v1.24) - the kubelet now talks to CRI runtimes such as **containerd** or CRI-O. Images built with Docker are OCI images and still run fine. Docker remains a build/dev tool; `docker` isn't on the node anymore, so use `crictl` for node debugging.
**Lab (on a cluster):** `kubectl get nodes -o wide` and read the CONTAINER-RUNTIME column.
