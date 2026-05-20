#!/usr/bin/env node
/**
 * Minimal MCP Server Demo
 *
 * A simple MCP server with one 'hello' tool.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create MCP server instance
const server = new McpServer({
  name: "demo-mcp-server",
  version: "1.0.0"
});

// Zod schema for hello tool input
const HelloInputSchema = z.object({
  name: z.string().optional().describe("Optional name to greet")
}).strict();

// Register the hello tool
server.registerTool(
  "hello",
  {
    title: "Hello",
    description: "Returns a greeting message. Use this tool when you need to test the MCP server connection or get a simple greeting.",
    inputSchema: HelloInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    }
  },
  async (params) => {
    const greeting = params.name
      ? `Hello ${params.name} from MCP!`
      : "Hello from MCP";

    return {
      content: [{ type: "text", text: greeting }],
      structuredContent: { message: greeting }
    };
  }
);

// Main function
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Demo MCP server running via stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});