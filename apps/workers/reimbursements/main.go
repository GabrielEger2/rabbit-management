package main

import (
	"database/sql"
	"encoding/json"
	"log"
	"os"

	_ "github.com/lib/pq"
	"github.com/streadway/amqp"
)

type ReimbursementData struct {
	UserID int `json:"user_id"`
}

func processReimbursement(body []byte) {
	var data ReimbursementData
	err := json.Unmarshal(body, &data)
	if err != nil {
		log.Printf("Failed to parse message body: %v", err)
		return
	}

	usersConnStr := os.Getenv("USERS_DB_URL")
	reimbursementsConnStr := os.Getenv("REIMBURSEMENTS_DB_URL")

	usersDb, err := sql.Open("postgres", usersConnStr)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer usersDb.Close()

	reimbursementsDb, err := sql.Open("postgres", reimbursementsConnStr)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer reimbursementsDb.Close()

	query := "SELECT username, email, level, id, joined, is_active FROM users WHERE id = $1"
	row := usersDb.QueryRow(query, data.UserID)

	var user struct {
		Username string
		Email    string
		Level    int
		ID       int
		Joined   string
		IsActive bool
	}

	err = row.Scan(&user.Username, &user.Email, &user.Level, &user.ID, &user.Joined, &user.IsActive)
	if err != nil {
		log.Printf("Failed to fetch user data: %v", err)
		return
	}

	log.Printf("User found: %+v", user)
}

func main() {
	rabbitmqURL := os.Getenv("RABBITMQ_URL")

	conn, err := amqp.Dial(rabbitmqURL)
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Failed to open a channel: %v", err)
	}
	defer ch.Close()

	queueName := "reimbursements.queue"
	q, err := ch.QueueDeclare(
		queueName,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("Failed to declare a queue: %v", err)
	}

	msgs, err := ch.Consume(
		q.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		log.Fatalf("Failed to register a consumer: %v", err)
	}

	for d := range msgs {
		log.Printf("Received a message: %s", d.Body)
		log.Printf("Received a header: %s", d.Headers)

		eventRaw, ok := d.Headers["event"]
		if !ok {
			log.Println("Event header is missing")
			continue
		}

		eventType, ok := eventRaw.(string)
		if !ok {
			log.Println("Event header is not a string")
			continue
		}

		if eventType == "reimbursement.updated" || eventType == "reimbursement.submitted" {
			processReimbursement(d.Body)
		} else {
			log.Printf("Skipping unrelated event: %s", eventType)
		}
	}
}
