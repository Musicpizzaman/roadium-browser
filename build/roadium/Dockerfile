# Build the unchanged pinned Cromite compiler image first (see README.md).
ARG BASE_IMAGE=uazo/cromite-build:153.0.8010.37-11507ac1061b5ea227806f5e84db5a57df6ccf6a
FROM ${BASE_IMAGE}
ENV WORKSPACE=/home/lg/working_dir DEPOT_TOOLS_UPDATE=0 TARGET_ISDEBUG=false
USER lg
WORKDIR /home/lg/working_dir
COPY --chown=lg:lg build/roadium /home/lg/working_dir/roadium/build/roadium
COPY --chown=lg:lg tools/roadium /home/lg/working_dir/roadium/tools/roadium
RUN python3 "$WORKSPACE/roadium/tools/roadium/apply-overlay.py" "$WORKSPACE/chromium/src" "$WORKSPACE/cromite"
