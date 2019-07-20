FROM golang:alpine
EXPOSE 1800

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

RUN  mkdir -p /go/src \
  && mkdir -p /go/bin \
  && mkdir -p /go/pkg

ENV GOPATH=/go
ENV PATH=$GOPATH/bin:$PATH

# Download and install the latest release of dep
ADD https://github.com/golang/dep/releases/download/v0.5.0/dep-linux-amd64 /usr/bin/dep
RUN chmod +x /usr/bin/dep

RUN mkdir -p $GOPATH/src/skyfolk_services
ADD src/skyfolk_services $GOPATH/src/skyfolk_services

WORKDIR $GOPATH/src/skyfolk_services

CMD ["go", "run", "cmd/main/main.go"]