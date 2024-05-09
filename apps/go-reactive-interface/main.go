import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"

    "github.com/dapr/go-sdk/service/common"
    daprd "github.com/dapr/go-sdk/service/http"
)

type ConversationData struct {
    Message string `json:"message"`
    Name    string `json:"name"`
}

type ConversationEvent struct {
    Data            ConversationData `json:"data"`
    DataContentType string           `json:"datacontenttype"`
    ID              string           `json:"id"`
    PubsubName      string           `json:"pubsubname"`
    Source          string           `json:"source"`
    SpecVersion     string           `json:"specversion"`
    Time            string           `json:"time"`
    Topic           string           `json:"topic"`
    TraceID         string           `json:"traceid"`
    TraceParent     string           `json:"traceparent"`
    TraceState      string           `json:"tracestate"`
    Type            string           `json:"type"`
}

var (
    subscribers = make(map[chan ConversationEvent]bool)
)

func handleEvents(w http.ResponseWriter, r *http.Request) {
    // Set headers necessary for SSE
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")

    // Create a channel to send data to the client
    ch := make(chan ConversationEvent)
    subscribers[ch] = true

    // Make sure to remove this client from the map when the function returns
    defer func() {
        delete(subscribers, ch)
    }()

    // Keep the connection open and send events
    for {
        select {
        case event := <-ch:
            data, err := json.Marshal(event)
            if err != nil {
                log.Printf("Failed to marshal event: %v", err)
                return
            }
            fmt.Fprintf(w, "data: %s\n\n", data)
            if f, ok := w.(http.Flusher); ok {
                f.Flush()
            }
        case <-r.Context().Done():
            return
        }
    }
}

func eventHandler(ctx context.Context, e *common.TopicEvent) (retry bool, err error) {
    var event ConversationEvent
    if err := json.Unmarshal(e.Data, &event); err != nil {
        log.Printf("Error unmarshalling event data: %v", err)
        return false, err
    }

    // Broadcast event to all subscribers
    for ch := range subscribers {
        ch <- event
    }
    return false, nil
}

func main() {
    s := daprd.NewService(":6002")
    sub := &common.Subscription{
        PubsubName: "pubsub",
        Topic:      "conversations",
        Route:      "/conversations",
    }

    if err := s.AddTopicEventHandler(sub, eventHandler); err != nil {
        log.Fatalf("error adding topic subscription: %v", err)
    }

    http.HandleFunc("/events", handleEvents)
    if err := http.ListenAndServe(":8080", nil); err != nil {
        log.Fatal("ListenAndServe: ", err)
    }
}
