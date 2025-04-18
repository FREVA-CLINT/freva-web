FROM condaforge/mambaforge
ARG CONDA_ENV_DIR=/opt/condaenv
ARG FREVA_WEB_DIR=/opt/freva_web
ARG EMAIL_HOST_PASSWORD=""
ARG VERSION

LABEL org.opencontainers.image.authors="DRKZ-CLINT"
LABEL org.opencontainers.image.source="https://github.com/FREVA-CLINT/freva-web"
LABEL org.opencontainers.image.version="$VERSION"
ARG CONDA_ENV_DIR
ARG FREVA_WEB_DIR

# mamba automatically creates CONDA_ENV_DIR
RUN set -e && \
    mkdir -p /opt/conda/pkgs/cache && \
    mamba update mamba -n base -c conda-forge -y && \
    mamba clean -afy

WORKDIR ${FREVA_WEB_DIR}
COPY . .
ENV PATH=$CONDA_ENV_DIR/bin:$PATH\
    DJANGO_SUPERUSER_EMAIL=freva@dkrz.de\
    EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD
RUN  set -e && \
     mamba env create -y -p ${CONDA_ENV_DIR} -f conda-env.yml --debug &&\
     mamba clean -afy &&\
     npm install && npm run build-production &&\
     rm -rf node_modules
EXPOSE 8000
CMD  ["./init_django.sh"] 
