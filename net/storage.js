/**
 * Native aMule storage reference model.
 *
 * The physical storage backend can later be local, Hood Storage, IPFS,
 * an aMule node, or another compatible provider.
 */

export function createStorageReference({
  provider = "amule",
  operator,
  key,
  contentHash,
  size = 0,
}) {
  if (!operator) throw new Error("operator is required.");
  if (!key) throw new Error("key is required.");

  return {
    protocol: "amule",
    provider,
    operator,
    key,
    contentHash,
    size,
  };
}

export function isValidStorageReference(ref) {
  return Boolean(
    ref &&
    ref.protocol === "amule" &&
    ref.provider &&
    ref.operator &&
    ref.key
  );
}
