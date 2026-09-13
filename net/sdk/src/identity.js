import { createHash, randomBytes } from "node:crypto";

/**
 * Protocol identity rules:
 *
 * resourceId is NOT the content hash.
 * resourceId identifies a logical resource.
 * contentHash identifies the exact content bytes.
 */

export function calculateContentHash(content) {
  const bytes = Buffer.isBuffer(content)
    ? content
    : Buffer.from(content);

  return createHash("sha256").update(bytes).digest("hex");
}

export function createRandomResourceId() {
  return createHash("sha256")
    .update(randomBytes(32))
    .digest("hex");
}

export function createDeterministicResourceId(namespace, stableId) {
  if (!namespace || !stableId) {
    throw new Error("namespace and stableId are required.");
  }

  return createHash("sha256")
    .update(`${namespace}\n${stableId}`, "utf8")
    .digest("hex");
}

export function isValidResourceId(resourceId) {
  return typeof resourceId === "string" && /^[a-f0-9]{64}$/i.test(resourceId);
}

export function hashToBytes32(hexHash) {
  if (!/^[a-f0-9]{64}$/i.test(hexHash)) {
    throw new Error("Expected a 32-byte hexadecimal hash.");
  }

  return `0x${hexHash}`;
}
