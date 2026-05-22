import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

async function main() {
  try {
    const response = await client.messages.create({
      model: "claude-opus-4-7",
      max_tokens: 1024,
      messages: [{ role: "user", content: "Hello" }],
    });

    for (const block of response.content) {
      if (block.type === "text") {
        console.log(block.text);
      }
    }
  } catch (error) {
    if (error instanceof Anthropic.APIError) {
      console.error(`API error ${error.status}:`, error.message);
    } else {
      console.error("Unexpected error:", error);
    }
    process.exit(1);
  }
}

main();