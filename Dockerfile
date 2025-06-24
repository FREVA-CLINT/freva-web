FROM docker.io/mambaorg/micromamba
USER root
ARG CONDA_ENV_DIR=/opt/condaenv
ARG FREVA_WEB_DIR=/opt/freva_web
ENV BUNDLE_HOST_PATH=${BUNDLE_HOST_PATH}
ARG EMAIL_HOST_PASSWORD=""
ARG VERSION

LABEL org.opencontainers.image.authors="DRKZ-CLINT"
LABEL org.opencontainers.image.source="https://github.com/FREVA-CLINT/freva-web"
LABEL org.opencontainers.image.version="$VERSION"
ENV PATH=/opt/conda/bin:$PATH\
    DJANGO_SUPERUSER_EMAIL=freva@dkrz.de\
    EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD\
    PYTHONUNBUFFERED=1

RUN  set -xe  && \
    mkdir -p /etc/pamd.d && \
    apt -y update &&\
    DEBIAN_FRONTEND=noninteractive apt -y install sssd libnss-sss libpam-sss \
    sssd-common sssd-tools &&\
    rm -rf /var/lib/apt/lists/* && \
    printf "\n\
auth required pam_sss.so\n\
account required pam_sss.so\n\
password required pam_sss.so\n\
session required pam_sss.so\n\
" > /etc/pam.d/login

WORKDIR ${FREVA_WEB_DIR}

COPY . .

RUN set -eu \
     && for user in sync news uucp irc list lp games gnats ftp man proxy operator talk nobody _apt;do\
       deluser $user 2> /dev/null || true;\
     done \
     && delgroup mambauser || true \
     && rm -rf /home/mambauser || true \
     && delgroup nogroup || true \
     && addgroup --system --gid 65534 nobody || true \
     && adduser \
    --system \
    --uid 65534 \
    --gid 65534 \
    --no-create-home \
    --disabled-password \
    --shell /usr/sbin/nologin \
    nobody



RUN  set -exu && \
     sed -i "s|\"path\": \"${BUNDLE_HOST_PATH}|\"path\": \"${FREVA_WEB_DIR}|g" \
     ${FREVA_WEB_DIR}/webpack-stats.json &&\
     mkdir -p /data/logs ./base/migrations && chmod 1777 -R /data ./base/migrations

RUN  set -exu && \
     micromamba env create -y -q -n freva-web -f conda-env.yml && \
     micromamba run -n freva-web python -m pip cache purge --no-input -q &&\
     rm conda-env.yml &&\
     micromamba clean -y -i -t -l -f

ENV ENV_NAME=freva-web
EXPOSE 8000
CMD  ["./init_django.sh"]
