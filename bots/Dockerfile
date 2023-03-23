FROM golang:1.18.1-alpine


RUN mkdir /app
WORKDIR /app


COPY go.mod ./
COPY go.sum ./
RUN go mod download && go mod verify

COPY *.go ./
RUN go build bin/bot0/bot0.go
