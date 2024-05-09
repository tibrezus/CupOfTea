package main

import (
    "context"
    "encoding/json"
    "net/http"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/require"
    "github.com/dapr/go-sdk/service/common"
    "github.com/jarcoal/httpmock"
)

type DaprClient interface {
    InvokeService(ctx context.Context, serviceID, method string, data interface{}) (out []byte, err error)
}

type MockDaprClient struct {
    mock.Mock
}

func (m *MockDaprClient) InvokeService(ctx context.Context, serviceID, method string, data interface{}) (out []byte, err error) {
    args := m.Called(ctx, serviceID, method, data)
    return args.Get(0).([]byte), args.Error(1)
}

// TestHandleAgentEvent tests the handling of agent events
func TestHandleAgentEvent(t *testing.T) {
    // Setup
    ctx := context.Background()
    agentData := `{"name":"John","description":"A reliable agent","tea_amount_ml":300}`
    event := &common.TopicEvent{Data: []byte(agentData)}

    // Execute
    retry, err := handleAgentEvent(ctx, event)

    // Assert
    require.NoError(t, err)
    assert.False(t, retry)
    assert.Equal(t, 300, agents["John"].TeaAmount)
}

// TestHandleConversationEvent tests the handling of conversation events
func TestHandleConversationEvent(t *testing.T) {
    // Initial setup
    ctx := context.Background()
    agents["John"] = Agent{Name: "John", Description: "A reliable agent", TeaAmount: 300}
    conversationData := `{"name":"Doe","message":"Hello, world!"}`
    event := &common.TopicEvent{Data: []byte(conversationData)}

    // Setup HTTP mock
    httpmock.ActivateNonDefault(httpClient)
    defer httpmock.DeactivateAndReset()

    url := "http://localhost:3500/v1.0/invoke/dialogue-generator/method/generate"
    httpmock.RegisterResponder("POST", url, func(req *http.Request) (*http.Response, error) {
        // Check the request body
        body := map[string]interface{}{}
        json.NewDecoder(req.Body).Decode(&body)
        assert.Equal(t, "John", body["agent"].(map[string]interface{})["name"])
        return httpmock.NewStringResponse(200, "Success"), nil
    })

    mockClient := new(MockDaprClient)
    mockClient.On("InvokeService", mock.Anything, "dialogue-generator", "generate", mock.Anything).Return([]byte("Success"), nil)
    // Pass the mock client to the function you're testing
    retry, err := handleConversationEvent(ctx, event, mockClient)
 
    // Assert
    require.NoError(t, err)
    assert.False(t, retry)
    // Check that the correct endpoint was called
    assert.Equal(t, 1, httpmock.GetTotalCallCount())
    info := httpmock.GetCallCountInfo()
    assert.Equal(t, 1, info["POST "+url])
}

