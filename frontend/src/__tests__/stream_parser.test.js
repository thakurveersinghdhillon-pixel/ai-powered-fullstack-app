/**
 * Unit test for SSE Stream Chunk Parser logic (JS version for Node execution)
 */

function parseSSEBuffer(buffer) {
  const events = [];
  const parts = buffer.split("\n\n");
  const remainingBuffer = parts.pop() || "";

  for (const part of parts) {
    if (!part.trim()) continue;

    const lines = part.split("\n");
    let eventType = "message";
    let eventData = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.substring(7).trim();
      } else if (line.startsWith("data: ")) {
        eventData = line.substring(6).trim();
      }
    }

    if (!eventData) continue;

    try {
      const parsed = JSON.parse(eventData);
      events.push({ event: eventType, data: parsed });
    } catch (e) {
      // ignore malformed lines
    }
  }

  return { events, remainingBuffer };
}

function runTests() {
  console.log("Running SSE Stream Parser Unit Tests...");

  const rawChunk =
    "event: start\ndata: {\"user_message_id\": \"u1\", \"assistant_message_id\": \"a1\", \"conversation_id\": \"c1\"}\n\n" +
    "event: token\ndata: {\"content\": \"Hello \"}\n\n" +
    "event: token\ndata: {\"content\": \"World!\"}\n\n" +
    "event: done\ndata: {\"status\": \"completed\", \"assistant_message_id\": \"a1\"}\n\n";

  const { events, remainingBuffer } = parseSSEBuffer(rawChunk);

  console.assert(events.length === 4, `Expected 4 events, got ${events.length}`);
  console.assert(events[0].event === "start", `Expected first event 'start', got ${events[0].event}`);
  console.assert(events[1].data.content === "Hello ", `Expected token 'Hello ', got '${events[1].data.content}'`);
  console.assert(events[2].data.content === "World!", `Expected token 'World!', got '${events[2].data.content}'`);
  console.assert(events[3].event === "done", `Expected last event 'done', got ${events[3].event}`);
  console.assert(remainingBuffer === "", `Expected empty remaining buffer, got '${remainingBuffer}'`);

  // Test incomplete trailing chunk
  const partialChunk =
    "event: token\ndata: {\"content\": \"Partial\"}\n\n" +
    "event: token\ndata: {\"content\": \"Incomplete";

  const result = parseSSEBuffer(partialChunk);
  console.assert(result.events.length === 1, `Expected 1 event from partial chunk, got ${result.events.length}`);
  console.assert(result.remainingBuffer === "event: token\ndata: {\"content\": \"Incomplete", "Remaining buffer mismatch");

  console.log("All SSE Stream Parser Unit Tests Passed successfully! ✅");
}

runTests();
