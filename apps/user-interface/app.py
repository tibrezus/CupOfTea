# app.py
import streamlit as st

st.set_page_config(
    page_title="Introduction toEvent-Driven Microservices", layout="wide"
)

# Slide 1: Title Slide
st.title("Introduction Event-Driven Microservices")
st.subheader("A Introduction to Building Responsive and Scalable Systems")
st.write("---")

st.write(
    """
## How Will ne next hour look like

1. **Why do we need events**
   - "Parity between the real world and software models is crucial for building effective systems. We'll explore how event-driven modeling bridges this gap."

2. **What changes with Event-Driven Design**
   - "This  introduces a new way of thinking about system design, which diverges from traditional methods you may be familiar with."

3. **Basic Patterns**
   - "We'll delve into crucial event-driven modeling techniques, including event sourcing,  Command Query Responsibility Segregation (CQRS)."

4. **First steps in moving to Event-Driven Design**
   - "Data liberation is a key aspect of transitioning to event-driven systems. We'll discuss how to free your data from traditional CRUD operations."

5. **Practical Implementation**
   - "Through these methods, a brief demo with DAPR, a distributed application runtime that simplifies the process."
"""
)
st.write("---")

st.write(
    """
### The Real World Modelled in Software

To effectively map real-world processes into a software model, you need a robust coordinate system. This is similar to how scientists use mathematical models to describe physical phenomena. In mathematics, the primary coordinate systems are polar and Cartesian.

**Polar Coordinates**: In this system, positions are defined by an angle and a distance from a central point—akin to a pilot describing a nearby aircraft as being "a half-mile up at 4 o'clock." This method is particularly useful for scenarios where objects revolve around a central point, such as the planets orbiting the sun. The mathematics of polar coordinates simplifies many such rotational dynamics.

**Cartesian Coordinates**: Alternatively, positions can be modeled using two perpendicular dimensions—like longitude and latitude used on maps. This system is highly effective for defining static positions or movements within a grid or along straight paths.

Choosing the right coordinate system can dramatically simplify problem-solving. Some challenges are naturally suited to polar coordinates, while others align better with the Cartesian approach. Understanding and applying the appropriate system is crucial to building an effective and efficient software model.
"""
)

st.image("./images/0-1.png", use_column_width=True)
st.write("---")

st.write(
    """
### State-Based Modeling

In a state-based system, we capture the game's status by documenting the current positions of all the pieces on the board. This approach is akin to taking a snapshot:

- **Snapshot Approach**: Each piece on the chessboard is assigned X and Y coordinates that represent its current position.
- **Database Storage**: These positions are recorded and stored in a database table, much like saving a photograph that freezes everything in time.

This method is straightforward and provides a clear and immediate view of the game at any saved point. It is particularly useful for quickly retrieving the current state without needing to understand how it was reached.

### Event-Based Modeling

Conversely, event-based modeling captures the game in a dynamic, sequential manner:

- **Sequential Replay**: Instead of a snapshot, this method records each chess move as an individual event, starting from the beginning of the game. To understand the current state of the board, you replay each move.
- **Event Log**: Each move (event) details a change from one state to another, focusing only on the pieces involved in that move, not the entire board.

This method allows for a deeper understanding of the game's progression and dynamics. It's particularly powerful for systems that evolve over time, as it not only shows where things stand but also how they got there.

### Comparing the Approaches

**Event-based systems** are advantageous in scenarios where the history or sequence of changes is critical to understanding or reconstructing the current state. They excel in environments with complex interactions and where it is necessary to trace the evolution of the system's state over time.

**State-based systems**, however, are typically simpler and faster for fetching the current state as there is no need to process a history of events. This can be more efficient in scenarios where the path to the current state is irrelevant, and only the current snapshot is needed.

In modern, large-scale applications, especially those distributed across various services and components, event-based systems often provide greater flexibility and scalability. They facilitate a better understanding of the system’s changes and interactions over time, making them suited to complex environments where understanding the sequence of events can be crucial for diagnostics, auditing, or compliance.

This chess analogy provides a clear framework for understanding the fundamental differences between these two modeling paradigms and helps in deciding which approach might be best suited for different types of software systems.
"""
)
st.image("./images/0-2.png", use_column_width=True)
st.write("---")

st.write(
    """

## CRUD vs. Event Sourcing         
         
#### Advantages of CRUD

- **Simplicity**: The CRUD model is straightforward and intuitive, making it easy to implement and understand.
- **Immediate Consistency**: Changes made to data are instantly saved and reflected in the database, ensuring that the data presented to users is always up-to-date.
- **Familiarity**: Most developers are familiar with this model as it is a basic and widely used approach in database management.

#### Disadvantages of CRUD

- **Data Loss**: CRUD operations overwrite existing data, leading to the loss of historical information. This can be problematic for auditing, debugging, or tracking user interactions.
- **Complexity in Tracking Changes**: To maintain a history of changes, additional mechanisms are required, such as triggers or manual logging, which can complicate the system.

### Event Sourcing Explained

#### How It Works
1. **Create Events**:
   - Each user action that alters the state of the system is recorded as an event. For instance, when Sanjana adds a t-shirt to her shopping cart, this action is stored as an "Item Added" event.

2. **Read Events**:
   - To determine the current state of the shopping cart, the system replays all recorded events. This process constructs the present state from the sequence of past actions.

3. **No Update or Delete**:
   - Traditional updates and deletes are not used. Instead, to change a quantity or remove an item, new events are recorded. If Sanjana adds a second t-shirt, a second "Item Added" event is recorded. If she removes a t-shirt, an "Item Removed" event is created.

#### Event Accumulation
- As events accumulate, they form a detailed history or timeline of user interactions. This can be thought of as a comprehensive log or "customer journey" that shows exactly what actions were taken and when.

### Advantages of Event Sourcing

- **Complete History**: Maintains a full, immutable history of all changes, similar to version control systems used for code. This can be invaluable for auditing, debugging, and understanding user behavior over time.

- **Robustness**: By avoiding direct modifications to data, the system can be more robust and less prone to data corruption.

- **Replayability**: The ability to replay events to reconstruct the state at any point in time offers flexibility in viewing historical data, testing, or recovering from system failures.
"""
)
st.image("./images/0-4.png", use_column_width=True)
st.write("---")

st.write(
    """
### Understanding Current State

- **Event Sequence**: Events such as adding or removing pants don't instantly show current numbers. They're just part of a timeline.

- **Computing State**: To find out the current count of pants, we compile all related events (two adds, one remove) and process them in order.

- **Chronological Reduction**: We apply a reduction technique over these events in chronological order to derive the net quantity of pants in the cart.

- **Result Display**: The final count, after processing these events, tells us the current state of the shopping cart.

### Complete Data Retention

- **Unidirectional Transformation**: Transitioning from an event-based view to a table view is a one-way process. 

- **Information Loss**: Moving from recording every event to a summarized table view means losing details—you can't revert to the full event view from the table alone.

- **Advantage of Event Sourcing**: Unlike CRUD, which discards the historical data once states are updated or deleted, event sourcing preserves every detail of what has happened, capturing a complete and accurate history.
"""
)
st.image("./images/0-5.png", use_column_width=True)
st.write("---")

st.write(
    """
### Implementing Event Sourcing: The Shopping Cart Example

- **Event Storage**: Events are sequentially recorded in a database table or managed through a system like Apache Kafka.

- **Event Query**: To determine the cart's current state, we query the event log, typically filtering by identifiers like customer or session ID.

- **Data Transformation**: A chronological reduction of the events filters and consolidates them, turning a sequence of individual events into a few summarized rows in a traditional database format.    
"""
)
st.image("./images/0-6.png", use_column_width=True)
st.write("---")

st.write(
    """
### Why Store Events?

Events offers distinct advantages over traditional data management systems, making it an attractive choice for complex software applications. Here are three primary benefits:

#### 1. Evidentiary Quality
- **Immutable Records**: In event sourcing, each action is logged as an immutable event, similar to double-entry bookkeeping where entries are only added, never altered.
- **Audit and Analysis**: This append-only nature allows for a reliable audit trail. You can always trace back through the event log to understand changes or identify errors, much like reviewing a financial ledger to find discrepancies.

#### 2. Recoverability
- **Replayability**: One of the strongest features of event sourcing is the ability to replay events to restore or reconstruct the state up to any point in time. This is crucial for correcting errors.
- **Data Integrity**: If a bug corrupts data, you can fix the bug in the code, rewind to a time before the bug occurred, and replay the events to correct affected records without losing data integrity.

#### 3. Insightful Data
- **Rich Analytics**: The granular data collected from each event provides a detailed view of user interactions, which is invaluable for analytics.
- **Operational Intelligence**: By analyzing the sequence of events, you can uncover patterns and insights, such as why certain products might not be selling at expected rates or during specific times.
"""
)
st.write("---")

st.write(
    """
### Understanding Command Query Responsibility Segregation (CQRS)

Command Query Responsibility Segregation (CQRS) is a design pattern that addresses some of the challenges posed by event sourcing, particularly when dealing with large volumes of data. This pattern divides the handling of data into two distinct parts: commands that modify data, and queries that retrieve data.

#### Event Sourcing and Data Challenges

In an event-sourced system, to determine the current state from an event log, you typically:
- **Collect Events**: Load all relevant events from the storage.
- **Chronological Reduction**: Perform a reduction process that chronologically applies these events to derive the current state of the system.

This method, while powerful for ensuring data integrity and providing a clear audit trail, can become inefficient when the volume of events is large. For instance, calculating the current balance of a checking account might require processing years of transactions, which is time-consuming and computationally expensive.

#### How CQRS Helps

CQRS simplifies this by separating the read and write operations into different models:
- **Write Model (Command Model)**: Handles all operations that change data. This model focuses on processing commands that add, modify, or delete data entries. Each command is processed only once, and the outcome is stored, typically in a form that's optimized for further commands.
- **Read Model (Query Model)**: Optimized for fetching data, it can be tailored to the specific needs of the user interface or other data consumers. This model can use denormalization and other techniques to improve performance and scalability.

### Applying CQRS

Implementing CQRS can be particularly beneficial in systems where:
- There is a clear distinction between operations that modify data and those that retrieve it.
- The system faces heavy load and requires high performance and scalability.
- Complex business rules that govern how data is created or modified.

"""
)
st.image("./images/0-7.png", use_column_width=True)
st.write("---")

st.write(
    """

"""
)
st.image("./images/0-8.png", use_column_width=True)
st.write("---")

st.write(
    """
### Change Data Capture (CDC)

Change Data Capture (CDC) is another method for achieving event-level data storage without modifying the existing data model.

#### How CDC Works

- **Source**: CDC monitors a mutable database table, such as a shopping cart.
- **Operation**: As rows in the table are added or updated, CDC captures these changes.
- **Integration**: These changes are then pushed into a Kafka topic, allowing them to be consumed by other systems.

#### Benefits of CDC

- **Evidentiary Advantages**: Like event sourcing, CDC provides a detailed record of changes, offering similar audit and historical analysis benefits.
- **Compatibility**: It leverages existing database schemas without requiring restructuring for event-based storage.

#### Limitations

- **Non-Replayable**: Unlike event sourcing, CDC does not inherently support replaying events to rebuild state. This limitation can be overcome with additional patterns like the outbox pattern.
"""
)
st.image("./images/0-9.png", use_column_width=True)
st.write("---")

st.write(
    """
### The Outbox Pattern: Enhancing CDC with Replayability

The Outbox pattern addresses one of the main limitations of Change Data Capture (CDC)—the lack of replayability. It provides a method to extend CDC with the capability to replay events, improving data robustness and integration flexibility.

#### How the Outbox Pattern Works

1. **Dual Tables**:
   - **Main Table**: This is the regular, mutable table where data operations (inserts, updates) occur.
   - **Events Table**: An append-only table that logs changes as events.
   
2. **Event Logging**:
   - **Triggers**: Database triggers are used to append records to the events table whenever changes are made to the main table. This ensures that every change is captured as an event.
   - **Alternative Approach**: If triggers are not supported, the application must manually write to both the main and events tables in a single transaction to ensure consistency.

3. **Event Consumption**:
   - The events from the events table are captured via CDC and streamed into Kafka, allowing other systems to consume these events as needed.

#### Advantages of the Outbox Pattern

- **Replayability**: Events stored in the database can be replayed to restore or reconstruct historical states, which is not typically possible with standard CDC.
- **Simplified Integration**: Storing events in a database table before streaming to Kafka simplifies integration with other systems and ensures data integrity.

#### Comparisons and Use Cases

- **Versus Kafka-only Storage**: Unlike storing all events directly in Kafka, as seen in CQRS, the outbox pattern provides a robust alternative for environments where not all systems require immediate access to the event stream.
- **Suitability**: It's particularly effective for simpler setups where the performance demands are moderate, and where maintaining a historical log within the database itself adds value.
"""
)
st.image("./images/0-10.png", use_column_width=True)
st.write("---")

st.write(
    """
### Using Dapr for Simplification

Dapr (Distributed Application Runtime) simplifies this pattern by abstracting the details of the transaction and message delivery:
- **Dapr’s Transactions API**: Allows applications to seamlessly commit a state change and message sending as a single transaction.
- **Reliability and Scalability**: Dapr handles the transaction complexities and ensures that messages are reliably sent to the message broker, even in high-load situations.

#### Diagrammatic Representation

The process can be visualized as follows:
- **Service A**: Performs the database update and message queueing in a single transaction.
- **Message Broker**: Ensures the delivery of the message to subscribers after the transaction commits.

#### Benefits of the Transactional Outbox Pattern

- **Consistency**: Guarantees that notifications are only sent after the corresponding state change is committed, thus avoiding discrepancies.
- **Reliability**: Reduces the risk of losing messages or sending notifications about uncommitted changes.
- **Simplicity with Dapr**: Leveraging Dapr can reduce the complexity of implementing this pattern across different databases and message brokers.
"""
)
st.image("./images/0-11.png", use_column_width=True)
st.write("---")

st.write(
    """
## Dapr Overview

### Building Blocks
"""
)
st.image("./images/0-12.png", use_column_width=True)

st.image("./images/0-13.png", use_column_width=True)

st.write(
    """
### Components
"""
)

st.image("./images/0-14.png", use_column_width=True)

st.write(
    """
### Service Meshes
"""
)

st.image("./images/0-15.png", use_column_width=True)

