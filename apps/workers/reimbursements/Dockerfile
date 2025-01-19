FROM golang:1.23

WORKDIR /usr/src/apps/workers/reimbursements

COPY /apps/workers/reimbursements .

RUN go mod download

RUN go build -o main .

CMD ["./main"]
