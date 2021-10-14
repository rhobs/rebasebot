FROM registry.access.redhat.com/ubi8/python-39

USER root

ENV GO_VERSION=1.16.8
RUN curl -Ls https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz | \
    tar -C /usr/local -zxvf - go/bin go/pkg/linux_amd64 go/pkg/tool go/pkg/include go/src
RUN dnf install -y jq \
  	&& dnf clean all \
  	&& rm -rf /var/cache/yum
ENV PATH="/usr/local/go/bin:$PATH"

WORKDIR /src
COPY . .
RUN python -m pip install --no-cache-dir .

WORKDIR /working
RUN rm -rf /src
RUN chown default .
RUN chmod 0777 .

USER default
ENTRYPOINT [ "/opt/app-root/bin/rebasebot" ]
