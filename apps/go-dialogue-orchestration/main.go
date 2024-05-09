package main

import (
    "context"
    "encoding/json"
    "log"
    "math/rand"
    "net/http"
    "sync"
    "time"
    "io"
    "bytes"

    "github.com/dapr/go-sdk/client"
    "github.com/dapr/go-sdk/service/common"
    dapr "github.com/dapr/go-sdk/service/http"
)

type Agent struct {
    Name        string `json:"name"`
    Description string `json:"description"`
    TeaAmount   int    `json:"tea_amount_ml"`
}

type Conversation struct {
    Name    string `json:"name"`
    Message string `json:"message"`
}

var (
    agents      = make(map[string]Agent)
    agentsMutex = &sync.Mutex{}
    httpClient  = &http.Client{
        Timeout: 15 * time.Second,
    }
)

func main() {
    rand.Seed(time.Now().UnixNano())  // Seed the random number generator once
    s := dapr.NewService(":5300")

    s.AddTopicEventHandler(&common.Subscription{
        PubsubName: "pubsub",
        Topic:      "agents",
        Route:      "/agents",
    }, handleAgentEvent)

    s.AddTopicEventHandler(&common.Subscription{
        PubsubName: "pubsub",
        Topic:      "conversations",
        Route:      "/conversations",
    }, handleConversationEvent)

    if err := s.Start(); err != nil {
        log.Fatalf("failed to start service: %v", err)
    }
}

func handleAgentEvent(ctx context.Context, e *common.TopicEvent) (retry bool, err error) {
    if e.Data == nil {
        log.Println("Event data is nil")
        return false, nil
    }

    var agent Agent
    if err := json.Unmarshal(e.Data.([]byte), &agent); err != nil {
        log.Printf("Error unmarshalling agent data: %v", err)
        return false, err
    }

    // Create a new Dapr client
    daprClient, err := client.NewClient()
    if err != nil {
        log.Fatalf("Failed to create Dapr client: %v", err)
    }
    defer daprClient.Close()

    // Save/update the agent in the Dapr state store
    key := "agent_" + agent.Name
    agentBytes, err := json.Marshal(agent)
    if err != nil {
        log.Printf("Failed to marshal agent data: %v", err)
        return false, err
    }
    err = daprClient.SaveState(ctx, "statestore", key, agentBytes, nil)
    if err != nil {
        log.Printf("Failed to save agent state: %v", err)
        return false, err
    }

    log.Printf("Agent state saved/updated: %v", agent)
    return false, nil
}

func handleConversationEvent(ctx context.Context, e *common.TopicEvent) (retry bool, err error) {
    var conversation Conversation
    if err := json.Unmarshal(e.Data.([]byte), &conversation); err != nil {
        log.Printf("Error unmarshalling conversation data: %v", err)
        return false, err
    }

    selectedAgent := selectRandomAgent(conversation.Name)
    if selectedAgent == nil {
        log.Println("No available agent to handle the conversation")
        return false, nil
    }

    content := map[string]interface{}{
        "agent": map[string]interface{}{
            "name":        selectedAgent.Name,
            "description": selectedAgent.Description,
            "tea_amount":  selectedAgent.TeaAmount,
        },
        "message": conversation.Message,
    }
    contentBytes, _ := json.Marshal(content)

    req, err := http.NewRequest(http.MethodPost, "http://localhost:3500/v1.0/invoke/dialogue-generator/method/generate", bytes.NewBuffer(contentBytes))
    if err != nil {
        log.Printf("Failed to create HTTP request: %v", err)
        return false, err
    }

    req.Header.Set("Content-Type", "application/json")

    resp, err := httpClient.Do(req)
    if err != nil {
        log.Printf("Failed to invoke dialogue-generator service: %v", err)
        return false, err
    }
    defer resp.Body.Close() // Ensure response body is closed after handling

    b, err := io.ReadAll(resp.Body)
    if err != nil {
        log.Printf("Failed to read response body: %v", err)
        return false, err
    }

    log.Printf("Response from dialogue-generator service: %s", string(b))
    return false, nil
}

func selectRandomAgent(excludeName string) *Agent {
    agentsMutex.Lock()
    defer agentsMutex.Unlock()

    var candidates []Agent
    for _, agent := range agents {
        if agent.Name != excludeName && agent.TeaAmount > 0 {
            candidates = append(candidates, agent)
        }
    }

    if len(candidates) == 0 {
        return nil
    }

    return &candidates[rand.Intn(len(candidates))]
}
