export function createResourceRecord({
  resourceId,
  operator,
  storageRef,
  contentHash = null,
  filename = null,
  contentType = "application/octet-stream",
  size = 0,
  encrypted = true,
  source = null,
  version = 1,
}) {
  if (!resourceId) throw new Error("resourceId is required.");
  if (!operator) throw new Error("operator is required.");
  if (!storageRef) throw new Error("storageRef is required.");

  return {
    protocol: "amule",
    version: 1,
    resourceId,
    contentHash,
    storage: {
      provider: "amule",
      operator,
      ref: storageRef,
    },
    metadata: {
      filename,
      contentType,
      size,
      encrypted,
      source,
      version,
    },
  };
}

export function validateResourceRecord(record) {
  return Boolean(
    record &&
    record.protocol === "amule" &&
    record.version === 1 &&
    record.resourceId &&
    record.storage &&
    record.storage.operator &&
    record.storage.ref
  );
}

export function serializeResourceRecord(record) {
  if (!validateResourceRecord(record)) {
    throw new Error("Invalid aMule resource record.");
  }
  return JSON.stringify(record, null, 2);
}
